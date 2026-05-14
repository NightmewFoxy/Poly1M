"""Wrapper around py-clob-client + Gamma REST for everything we need:

- discover_markets: list active esports markets with volume/end-time/price
- get_orderbook_price: best ask for a given outcome token
- place_order: $10 limit buy, IOC, at the displayed price (+1 tick slip)
- get_market_status: check whether a market is closed/resolved and which side won

py-clob-client is sync; we wrap the hot calls behind asyncio.to_thread so the loop
in main.py stays async.
"""
from __future__ import annotations

import asyncio
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    ApiCreds,
    OrderArgs,
    OrderType,
    PartialCreateOrderOptions,
)
from py_clob_client.exceptions import PolyApiException
from py_clob_client.order_builder.constants import BUY
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Friendlier name for predicate-style retry.
tenacity_retry_if = retry_if_exception


class GeoblockedError(RuntimeError):
    """Polymarket CLOB refused the request because the egress IP is in a blocked region."""


def _is_geoblock(exc: BaseException) -> bool:
    if not isinstance(exc, PolyApiException):
        return False
    if getattr(exc, "status_code", None) != 403:
        return False
    msg = getattr(exc, "error_msg", "")
    text = msg if isinstance(msg, str) else str(msg)
    return "Trading restricted" in text or "geoblock" in text.lower()

import config
from logger_setup import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class MarketCandidate:
    condition_id: str          # market id used in CLOB
    question_id: str           # event grouping key (skip duplicates within same event)
    question: str
    end_date_iso: str
    volume_usd: float
    liquidity_usd: float
    yes_token_id: str
    no_token_id: str
    yes_price: float           # current "best ask" on YES
    no_price: float            # current "best ask" on NO
    category: str | None
    slug: str
    neg_risk: bool             # Negative-Risk exchange contract vs standard CTF Exchange
    tick_size: float           # min price increment ($0.01 most markets, $0.001 some)
    enable_order_book: bool    # only CLOB-tradeable markets — AMM-only markets can't be ordered

    def hours_to_resolution(self) -> float:
        try:
            end = datetime.fromisoformat(self.end_date_iso.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
        now = datetime.now(timezone.utc)
        return (end - now).total_seconds() / 3600.0

    def is_esports(self) -> bool:
        haystack = " ".join(
            [self.question or "", self.category or "", self.slug or ""]
        ).lower()
        return any(kw in haystack for kw in config.ESPORTS_KEYWORDS)


# ---------------------------------------------------------------------------
# Client construction
# ---------------------------------------------------------------------------


def _build_clob_client() -> ClobClient:
    creds = ApiCreds(
        api_key=config.POLYMARKET_API_KEY,
        api_secret=config.POLYMARKET_API_SECRET,
        api_passphrase=config.POLYMARKET_API_PASSPHRASE,
    )
    client = ClobClient(
        host=config.CLOB_HOST,
        key=config.POLYMARKET_WALLET_PRIVATE_KEY,
        chain_id=config.POLYGON_CHAIN_ID,
        creds=creds,
        signature_type=config.POLYMARKET_SIGNATURE_TYPE,
        funder=config.POLYMARKET_FUNDER_ADDRESS,
    )
    return client


_clob: ClobClient | None = None


def clob() -> ClobClient:
    global _clob
    if _clob is None:
        _clob = _build_clob_client()
    return _clob


# ---------------------------------------------------------------------------
# Market discovery via Gamma REST (richer metadata than CLOB /markets)
# ---------------------------------------------------------------------------


_HTTP_RETRY = dict(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((httpx.HTTPError,)),
    reraise=True,
)


@retry(**_HTTP_RETRY)
async def _gamma_get(path: str, params: dict[str, Any]) -> Any:
    async with httpx.AsyncClient(timeout=30) as ac:
        r = await ac.get(f"{config.GAMMA_HOST}{path}", params=params)
        r.raise_for_status()
        return r.json()


def _parse_token_ids(raw: Any) -> list[str]:
    """Gamma returns clobTokenIds as a JSON-encoded string in some responses."""
    if isinstance(raw, list):
        return [str(t) for t in raw]
    if isinstance(raw, str):
        try:
            return [str(t) for t in json.loads(raw)]
        except json.JSONDecodeError:
            return []
    return []


def _parse_outcome_prices(raw: Any) -> list[float]:
    if isinstance(raw, list):
        return [float(p) for p in raw]
    if isinstance(raw, str):
        try:
            return [float(p) for p in json.loads(raw)]
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def _parse_tick_size(raw: Any) -> float:
    """Gamma returns tick size as either a number or a stringified decimal."""
    if raw is None:
        return 0.01
    try:
        v = float(raw)
        return v if v > 0 else 0.01
    except (TypeError, ValueError):
        return 0.01


async def discover_markets() -> list[MarketCandidate]:
    """Fetch active, non-closed binary markets and return parsed candidates.

    Filters at the API level: active=true, closed=false, ordered by volume desc.
    We pull up to 500 then narrow further in Python (esports keyword, price, time).
    """
    params = {
        "active": "true",
        "closed": "false",
        "archived": "false",
        "limit": "500",
        "order": "volumeNum",
        "ascending": "false",
    }
    raw = await _gamma_get("/markets", params)
    out: list[MarketCandidate] = []
    for m in raw:
        try:
            token_ids = _parse_token_ids(m.get("clobTokenIds"))
            prices = _parse_outcome_prices(m.get("outcomePrices"))
            if len(token_ids) != 2 or len(prices) != 2:
                continue  # not a binary market
            out.append(
                MarketCandidate(
                    condition_id=m.get("conditionId") or "",
                    question_id=m.get("questionID") or m.get("groupSlug") or m.get("conditionId") or "",
                    question=m.get("question") or "",
                    end_date_iso=m.get("endDate") or "",
                    volume_usd=float(m.get("volumeNum") or 0),
                    liquidity_usd=float(m.get("liquidityNum") or 0),
                    yes_token_id=token_ids[0],
                    no_token_id=token_ids[1],
                    yes_price=prices[0],
                    no_price=prices[1],
                    category=m.get("category"),
                    slug=m.get("slug") or "",
                    neg_risk=bool(m.get("negRisk") or False),
                    tick_size=_parse_tick_size(m.get("orderPriceMinTickSize")),
                    enable_order_book=bool(m.get("enableOrderBook", True)),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            log.debug("Skipping malformed market row: %s", exc)
            continue
    log.info("Gamma returned %d binary markets", len(out))
    return out


def filter_esports_tradeable(
    markets: list[MarketCandidate],
) -> list[MarketCandidate]:
    """Apply the four hard filters from the spec."""
    kept: list[MarketCandidate] = []
    for m in markets:
        if not m.is_esports():
            continue
        if not m.enable_order_book:
            # AMM-only market; can't place CLOB orders against it
            continue
        if m.volume_usd < config.MIN_VOLUME_USD:
            continue
        # We'll trade whichever side is cheaper, so require the *cheaper* side <= MAX_PRICE.
        cheaper = min(m.yes_price, m.no_price)
        if cheaper <= 0 or cheaper > config.MAX_PRICE:
            continue
        if m.hours_to_resolution() < config.MIN_HOURS_TO_RESOLUTION:
            continue
        if not m.yes_token_id or not m.no_token_id:
            continue
        kept.append(m)
    log.info("Filtered to %d tradeable esports markets", len(kept))
    return kept


# ---------------------------------------------------------------------------
# Orderbook + order placement
# ---------------------------------------------------------------------------


async def get_best_ask(token_id: str) -> float | None:
    """Best ask price for `token_id` in dollars (e.g. 0.62). None if no asks."""
    def _call() -> Any:
        return clob().get_order_book(token_id)

    try:
        book = await asyncio.to_thread(_call)
    except Exception as exc:
        log.warning("orderbook fetch failed for %s: %s", token_id, exc)
        return None
    asks = getattr(book, "asks", None) or []
    if not asks:
        return None
    # py-clob-client returns asks sorted descending; best ask is the lowest price.
    try:
        prices = [float(a.price) for a in asks]
    except (AttributeError, ValueError):
        return None
    return min(prices) if prices else None


def _round_to_tick(price: float, tick: float) -> float:
    """Snap price down to the nearest valid tick (must be a multiple of `tick`)."""
    if tick <= 0:
        return round(price, 4)
    return round(round(price / tick) * tick, 6)


def _tick_size_str(tick: float) -> str:
    """py-clob-client's PartialCreateOrderOptions.tick_size is a Literal of strings.

    Passing a float triggers `KeyError: 0.001` in its internal ROUNDING_CONFIG dict
    which is keyed on those exact strings. Pick the closest canonical value.
    """
    for canonical in ("0.0001", "0.001", "0.01", "0.1"):
        if abs(float(canonical) - tick) < 1e-9:
            return canonical
    # Fallback: pick the nearest canonical
    canonicals = ["0.0001", "0.001", "0.01", "0.1"]
    return min(canonicals, key=lambda s: abs(float(s) - tick))


async def place_market_buy(
    token_id: str,
    target_price: float,
    stake_usd: float,
    neg_risk: bool = False,
    tick_size: float = 0.01,
) -> dict[str, Any]:
    """Place a marketable limit buy. Crosses the spread by ~2 cents (tick-aligned) to ensure fill.

    `neg_risk` must match the market's exchange: True for Neg-Risk markets, False
    for the standard CTF Exchange. Wrong value -> CLOB returns order_version_mismatch.

    Returns the order response dict; raises on hard failure.
    """
    # Buy slightly above the best ask to fill immediately; cap at MAX_PRICE.
    limit_price = min(_round_to_tick(target_price + 0.02, tick_size), config.MAX_PRICE)
    if limit_price <= 0:
        raise ValueError(f"invalid limit price {limit_price}")
    size_shares = math.floor((stake_usd / limit_price) * 100) / 100  # 2 decimals
    if size_shares <= 0:
        raise ValueError("computed zero share size")

    args = OrderArgs(token_id=token_id, price=limit_price, size=size_shares, side=BUY)
    options = PartialCreateOrderOptions(neg_risk=neg_risk, tick_size=_tick_size_str(tick_size))

    def _call() -> Any:
        signed = clob().create_order(args, options=options)
        # FOK = fill-or-kill; immediate execution at the limit, no resting order left behind.
        return clob().post_order(signed, OrderType.FOK)

    def _is_retryable(exc: BaseException) -> bool:
        # Geoblock is permanent until the egress IP changes — don't waste attempts.
        return not isinstance(exc, GeoblockedError)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        retry=tenacity_retry_if(_is_retryable),
        reraise=True,
    )
    def _do() -> Any:
        try:
            return _call()
        except PolyApiException as exc:
            if _is_geoblock(exc):
                raise GeoblockedError(
                    "Polymarket CLOB returned 403 (region blocked). "
                    "Set OUTBOUND_PROXY to a proxy in a permitted region."
                ) from exc
            raise

    resp = await asyncio.to_thread(_do)
    log.info(
        "Order posted token=%s price=%.3f size=%.2f resp=%s",
        token_id, limit_price, size_shares, resp,
    )
    return {
        "limit_price": limit_price,
        "size_shares": size_shares,
        "stake_usd": round(limit_price * size_shares, 4),
        "response": resp,
    }


# ---------------------------------------------------------------------------
# Resolution polling
# ---------------------------------------------------------------------------


@retry(**_HTTP_RETRY)
async def get_market_resolution(condition_id: str) -> dict[str, Any] | None:
    """Look up a market by conditionId; return resolution info if closed/resolved.

    Returns None while still active.
    """
    params = {"condition_ids": condition_id}
    rows = await _gamma_get("/markets", params)
    if not rows:
        return None
    m = rows[0]
    closed = bool(m.get("closed"))
    if not closed:
        return None
    # outcomePrices ends up [1, 0] or [0, 1] once resolved; UMA-resolved markets carry it.
    prices = _parse_outcome_prices(m.get("outcomePrices"))
    winner = None
    if len(prices) == 2:
        if prices[0] == 1 and prices[1] == 0:
            winner = "YES"
        elif prices[0] == 0 and prices[1] == 1:
            winner = "NO"
    return {
        "closed": True,
        "winner": winner,
        "resolved_at": m.get("closedTime") or m.get("endDate") or _now_iso(),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
