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
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
from py_clob_client_v2.client import ClobClient
from py_clob_client_v2.clob_types import (
    ApiCreds,
    MarketOrderArgs,
    OrderArgs,            # OrderArgsV2 alias
    OrderType,
    PartialCreateOrderOptions,
)
from py_clob_client_v2.exceptions import PolyApiException
from py_clob_client_v2.order_builder.constants import BUY
from py_clob_client_v2.order_utils.model.signature_type_v2 import SignatureTypeV2
from py_clob_client_v2.order_utils import exchange_order_builder_v2 as _eob_v2
from eth_abi import encode as _abi_encode
from eth_account import Account as _EthAccount
from eth_utils import keccak as _keccak
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
        # Word-boundary match so short tokens like "lec" / "lcs" / "esl" / "iem"
        # don't fire on substrings ("lec" inside "election", "esl" inside "wrestler").
        # Slugs use '-' as separator, so we treat '-' as a word boundary too.
        haystack = " ".join(
            [self.question or "", self.category or "", (self.slug or "").replace("-", " ")]
        ).lower()
        tokens = set(re.findall(r"[a-z0-9]+", haystack))
        for kw in config.ESPORTS_KEYWORDS:
            kw_tokens = re.findall(r"[a-z0-9]+", kw.lower())
            if not kw_tokens:
                continue
            if len(kw_tokens) == 1:
                if kw_tokens[0] in tokens:
                    return True
            else:
                # Multi-word keyword: require all tokens present (close-enough heuristic).
                if all(t in tokens for t in kw_tokens):
                    return True
        return False


# ---------------------------------------------------------------------------
# Client construction
# ---------------------------------------------------------------------------


def _patch_poly_1271_for_relayer_flow() -> None:
    """Make py-clob-client-v2's POLY_1271 path work for relayer-key accounts.

    The library assumes the user controls the deposit wallet's signing key
    directly: it sets order.signer = funder (deposit wallet) and builds the
    Solady inner domain with that same address as the verifying contract.

    Polymarket Privy/Magic accounts split this in two: the user only has a
    separate "Relayer API Key" private key whose EOA is authorized by the
    deposit wallet's EIP-1271 implementation. For the CLOB's off-chain check
    (`order.signer == API_KEY_EOA`) to pass we must set order.signer to the
    relayer EOA. But the Solady inner domain still needs to reference the
    deposit wallet (maker), since that's the contract whose isValidSignature
    will verify the wrapped blob.

    These two monkey-patches do exactly that:
      1. OrderBuilder._v2_order_signer  -> returns signer.address() (relayer EOA)
         even for POLY_1271.
      2. ExchangeOrderBuilderV2._build_poly_1271_order_signature -> uses
         message["maker"] (deposit wallet) instead of message["signer"] as the
         Solady inner verifying contract.
    """
    from py_clob_client_v2.order_builder.builder import OrderBuilder as _OB

    def _v2_order_signer_relayer(self) -> str:
        # For POLY_1271 the library returns self.funder; we always want the
        # actual EOA derived from the relayer PK so it matches the API key.
        return self.signer.address()

    _OB._v2_order_signer = _v2_order_signer_relayer

    _ORDER_TYPE_HASH = _eob_v2.ORDER_TYPE_HASH
    _SOLADY_TYPE_HASH = _eob_v2.SOLADY_TYPE_HASH
    _DEPOSIT_WALLET_NAME_HASH = _eob_v2.DEPOSIT_WALLET_NAME_HASH
    _DEPOSIT_WALLET_VERSION_HASH = _eob_v2.DEPOSIT_WALLET_VERSION_HASH
    _DEPOSIT_WALLET_DOMAIN_SALT = _eob_v2.DEPOSIT_WALLET_DOMAIN_SALT
    _hex_to_bytes32 = _eob_v2._hex_to_bytes32
    _bytes32 = _eob_v2._bytes32

    def _build_poly_1271_relayer(self, typed_data: dict) -> str:
        message = typed_data["message"]
        # The order's "signer" field carries the relayer EOA in our flow; the
        # Solady inner domain's verifying contract must still be the wallet.
        verifying_contract = message["maker"]
        contents_hash = _keccak(
            primitive=_abi_encode(
                [
                    "bytes32", "uint256", "address", "address", "uint256",
                    "uint256", "uint256", "uint8", "uint8", "uint256",
                    "bytes32", "bytes32",
                ],
                [
                    _ORDER_TYPE_HASH,
                    int(message["salt"]),
                    message["maker"],
                    message["signer"],
                    int(message["tokenId"]),
                    int(message["makerAmount"]),
                    int(message["takerAmount"]),
                    int(message["side"]),
                    int(message["signatureType"]),
                    int(message["timestamp"]),
                    _bytes32(message["metadata"]),
                    _bytes32(message["builder"]),
                ],
            )
        )
        typed_data_sign_struct_hash = _keccak(
            primitive=_abi_encode(
                [
                    "bytes32", "bytes32", "bytes32", "bytes32",
                    "uint256", "address", "bytes32",
                ],
                [
                    _SOLADY_TYPE_HASH,
                    contents_hash,
                    _DEPOSIT_WALLET_NAME_HASH,
                    _DEPOSIT_WALLET_VERSION_HASH,
                    self.chain_id,
                    verifying_contract,
                    _DEPOSIT_WALLET_DOMAIN_SALT,
                ],
            )
        )
        digest = _keccak(
            primitive=(
                b"\x19\x01" + self.app_domain_separator + typed_data_sign_struct_hash
            )
        )
        signed = _EthAccount._sign_hash(digest, private_key=self.signer.private_key)
        inner_signature = signed.signature.hex()
        if inner_signature.startswith("0x"):
            inner_signature = inner_signature[2:]
        contents_type = _eob_v2.ORDER_TYPE_STRING.encode("utf-8").hex()
        contents_type_len = len(_eob_v2.ORDER_TYPE_STRING).to_bytes(2, "big").hex()
        return (
            "0x"
            + inner_signature
            + self.app_domain_separator.hex()
            + contents_hash.hex()
            + contents_type
            + contents_type_len
        )

    _eob_v2.ExchangeOrderBuilderV2._build_poly_1271_order_signature = _build_poly_1271_relayer


_patch_poly_1271_for_relayer_flow()


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


def _row_to_candidate(m: dict[str, Any]) -> MarketCandidate | None:
    try:
        token_ids = _parse_token_ids(m.get("clobTokenIds"))
        prices = _parse_outcome_prices(m.get("outcomePrices"))
        if len(token_ids) != 2 or len(prices) != 2:
            return None  # not a binary market
        return MarketCandidate(
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
    except (KeyError, TypeError, ValueError) as exc:
        log.debug("Skipping malformed market row: %s", exc)
        return None


async def discover_markets() -> list[MarketCandidate]:
    """Fetch active binary markets across multiple sort orders + paginate.

    Gamma caps `limit` at 100 per request regardless of what you send. Esports
    markets are short-lived (single matches) so they don't reach the top by
    lifetime `volumeNum` but dominate `volume24hr` while a tournament is live.
    We pull from both lists (and a couple of pages each) and de-dupe by
    conditionId so the bot sees both the active games and the long-tail
    high-volume markets.
    """
    common = {"active": "true", "closed": "false", "archived": "false", "ascending": "false"}
    queries: list[dict[str, str]] = []
    for sort_key in ("volume24hr", "volume1wk", "volumeNum"):
        for offset in ("0", "100", "200"):
            queries.append({**common, "order": sort_key, "limit": "100", "offset": offset})

    seen: dict[str, MarketCandidate] = {}
    for params in queries:
        try:
            raw = await _gamma_get("/markets", params)
        except Exception as exc:
            log.warning("Gamma query %s failed: %s", params, exc)
            continue
        for m in raw:
            cand = _row_to_candidate(m)
            if cand is None or not cand.condition_id:
                continue
            # Prefer the row whose volumeNum is higher — keeps liquidity data sane.
            existing = seen.get(cand.condition_id)
            if existing is None or cand.volume_usd > existing.volume_usd:
                seen[cand.condition_id] = cand

    out = list(seen.values())
    log.info("Gamma returned %d unique binary markets (across %d queries)", len(out), len(queries))
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
        # We'll trade whichever side is cheaper, so require it to sit in
        # [MIN_PRICE, MAX_PRICE]. Too-cheap (~$0.001) means the market is almost
        # certainly already resolved; trading the dead side is just donating.
        cheaper = min(m.yes_price, m.no_price)
        if cheaper <= 0 or cheaper < config.MIN_PRICE or cheaper > config.MAX_PRICE:
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
    """Best ask price for `token_id` in dollars (e.g. 0.62). None if no asks.

    v2's `get_order_book` returns a dict shaped {"asks": [{"price","size"}, ...], "bids": [...]}.
    """
    def _call() -> Any:
        return clob().get_order_book(token_id)

    try:
        book = await asyncio.to_thread(_call)
    except Exception as exc:
        log.warning("orderbook fetch failed for %s: %s", token_id, exc)
        return None
    asks = book.get("asks") if isinstance(book, dict) else getattr(book, "asks", None)
    if not asks:
        return None
    prices: list[float] = []
    for a in asks:
        try:
            if isinstance(a, dict):
                prices.append(float(a["price"]))
            else:
                prices.append(float(a.price))
        except (AttributeError, ValueError, KeyError):
            continue
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


async def get_market_meta(condition_id: str) -> dict[str, Any] | None:
    """Ask the CLOB itself for a market's neg_risk and tick_size.

    Gamma's `negRisk` is occasionally wrong, missing, or string-typed. CLOB's
    response is the canonical source. Returns None on lookup failure (caller
    falls back to the Gamma-derived values).
    """
    def _call() -> Any:
        return clob().get_market(condition_id)

    try:
        info = await asyncio.to_thread(_call)
    except Exception as exc:
        log.warning("CLOB get_market(%s) failed: %s", condition_id, exc)
        return None
    if not isinstance(info, dict):
        return None
    return {
        "neg_risk": bool(info.get("neg_risk", False)),
        "tick_size": float(info.get("minimum_tick_size") or 0.01),
        "enable_order_book": bool(info.get("enable_order_book", True)),
        "accepting_orders": bool(info.get("accepting_orders", True)),
    }


async def place_market_buy(
    token_id: str,
    target_price: float,
    stake_usd: float,
    neg_risk: bool = False,
    tick_size: float = 0.01,
) -> dict[str, Any]:
    """Place a $-denominated market BUY, fill-or-kill.

    Switched from limit-with-FOK to create_market_order because CLOB rejects
    limit orders whose makerAmount exceeds 2 decimal places (size*price on a
    0.001-tick market produces up to 5 decimals; CLOB caps market-style fills
    at 2). create_market_order takes the dollar amount directly so the maker
    amount is always whole-cent-aligned.

    `neg_risk` must match the market's exchange (True for Neg-Risk, False for
    standard CTF). The pre-trade MAX_PRICE check still runs in main.py via
    get_best_ask, so we don't let market FOK chase an unbounded price.

    Returns a result dict mirroring the old signature so positions.py keeps
    working: limit_price (effective fill price), size_shares, stake_usd, response.
    """
    if stake_usd <= 0:
        raise ValueError(f"invalid stake {stake_usd}")
    tick_str = _tick_size_str(tick_size)
    args = MarketOrderArgs(
        token_id=token_id,
        amount=round(stake_usd, 2),       # whole-cent precision; CLOB enforces this
        side=BUY,
        order_type=OrderType.FOK,
    )
    options = PartialCreateOrderOptions(neg_risk=neg_risk, tick_size=tick_str)
    log.info(
        "Signing market BUY: token=%s amount=$%.2f neg_risk=%s tick=%s",
        token_id, stake_usd, neg_risk, tick_str,
    )

    def _call() -> Any:
        signed = clob().create_market_order(args, options=options)
        return clob().post_order(signed, OrderType.FOK)

    def _is_retryable(exc: BaseException) -> bool:
        # Geoblock is permanent until the egress IP changes — don't waste attempts.
        if isinstance(exc, GeoblockedError):
            return False
        # 4xx from CLOB means the request is *malformed* (bad signature, wrong fee
        # rate, version mismatch, etc.). Retrying with the same signed body produces
        # the same 4xx. Only retry transient network/5xx.
        if isinstance(exc, PolyApiException):
            code = getattr(exc, "status_code", None)
            if isinstance(code, int) and 400 <= code < 500:
                return False
        return True

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
    # Parse the CLOB response. v2 returns:
    #   {'makingAmount': '0.999999', 'takingAmount': '15.151514', 'status': 'matched', ...}
    # makingAmount = USDC spent; takingAmount = shares received.
    try:
        usd_spent = float(resp.get("makingAmount", stake_usd))
        shares_filled = float(resp.get("takingAmount", 0))
        fill_price = (usd_spent / shares_filled) if shares_filled > 0 else target_price
    except (TypeError, ValueError):
        usd_spent = stake_usd
        shares_filled = stake_usd / target_price if target_price > 0 else 0
        fill_price = target_price
    log.info(
        "Order filled token=%s fill_price=%.4f shares=%.4f spent=$%.4f resp=%s",
        token_id, fill_price, shares_filled, usd_spent, resp,
    )
    return {
        "limit_price": round(fill_price, 6),
        "size_shares": round(shares_filled, 6),
        "stake_usd": round(usd_spent, 4),
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
