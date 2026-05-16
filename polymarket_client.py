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
    is_live_market: bool       # Gamma event.live flag — Polymarket's authoritative "match in progress"
    game_start_time: "datetime | None"  # parser fallback when event.live is missing/null

    def hours_to_resolution(self) -> float:
        try:
            end = datetime.fromisoformat(self.end_date_iso.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
        now = datetime.now(timezone.utc)
        return (end - now).total_seconds() / 3600.0

    def is_live(self) -> bool:
        """True if the underlying esports match is currently in progress.

        Prefers Polymarket's own `events[].live` flag (set by their data feed
        during the actual match window). Falls back to comparing
        game_start_time to now if Gamma didn't provide a live flag.

        Claude's web search can't see live in-game state, so any +EV estimate
        on a live match is stale and dangerous — the market has already
        re-priced on game-by-game results Claude doesn't see.
        """
        if self.is_live_market:
            return True
        if self.game_start_time is not None:
            return self.game_start_time <= datetime.now(timezone.utc)
        return False

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
# USDC balance (so we don't burn Claude tokens researching when we can't afford to trade)
# ---------------------------------------------------------------------------


def _get_usdc_balance_sync() -> float | None:
    """Returns available USDC balance in dollars, or None if lookup failed.

    Polymarket's balance_allowance endpoint sometimes 404s on fresh accounts;
    callers should treat None as "unknown" and fall back to position-count slots
    rather than refusing to trade.
    """
    from py_clob_client_v2.clob_types import AssetType, BalanceAllowanceParams
    try:
        params = BalanceAllowanceParams(
            asset_type=AssetType.COLLATERAL,
            signature_type=config.POLYMARKET_SIGNATURE_TYPE,
        )
        bal = clob().get_balance_allowance(params)
    except Exception as exc:
        log.warning("USDC balance lookup failed: %s", exc)
        return None
    raw = bal.get("balance") if isinstance(bal, dict) else None
    if raw is None:
        log.warning("USDC balance response missing 'balance' field: %s", bal)
        return None
    try:
        return int(raw) / 1_000_000  # USDC has 6 decimals
    except (TypeError, ValueError):
        log.warning("USDC balance raw value unparseable: %r", raw)
        return None


async def get_usdc_balance() -> float | None:
    return await asyncio.to_thread(_get_usdc_balance_sync)


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


def _parse_game_start(m: dict) -> "datetime | None":
    """Parse the underlying match start time. Gamma uses several field names
    inconsistently; treat them all as best-effort hints. Returns None if absent
    or unparseable (caller falls through to the time-to-resolution filter).
    """
    raw = m.get("gameStartTime") or m.get("startTime") or m.get("game_start_time")
    if raw is None:
        # The parent event sometimes has it under `startTime` instead.
        for ev in (m.get("events") or []):
            raw = ev.get("startTime") or ev.get("gameStartTime")
            if raw:
                break
    if not raw:
        return None
    try:
        s = str(raw).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _truthy(v: Any) -> bool:
    """Coerce Gamma boolean-ish values. Field comes back as bool / "true" /
    "1" / 1 depending on context, and None/missing means we don't know."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "yes", "y")
    return False


def _parse_is_live(m: dict) -> bool:
    """Return True if Polymarket flags the parent event as currently live.

    The flag lives on the embedded `events` array (event.live), not at market
    level. Markets typically belong to exactly one event in this data model.
    Conservative fallback: market-level `live` keys, if a future schema move
    surfaces it there.
    """
    for ev in (m.get("events") or []):
        if _truthy(ev.get("live")):
            return True
    return _truthy(m.get("live")) or _truthy(m.get("isLive"))


async def fetch_market_trade_safety(condition_id: str) -> dict[str, bool] | None:
    """Re-fetch a single market from Gamma and return fresh tradeability flags.

    Used right before order placement so we trust Polymarket's *current* state
    rather than the snapshot taken at discovery (which can be tens of minutes
    stale). Returns a dict with `live`, `closed`, `archived`, `active`, or None
    if the lookup fails after retries — the caller treats None as "can't
    verify, skip to be safe".
    """
    try:
        raw = await _gamma_get("/markets", {"condition_ids": condition_id})
    except Exception as exc:
        log.warning("Fresh trade-safety lookup failed for %s: %s", condition_id, exc)
        return None
    for m in (raw or []):
        if (m.get("conditionId") or "") == condition_id:
            return {
                "live": _parse_is_live(m),
                "closed": _truthy(m.get("closed")),
                "archived": _truthy(m.get("archived")),
                # `active` defaults to True when missing — we don't want to
                # block trading on a field that Gamma sometimes omits.
                "active": True if m.get("active") is None else _truthy(m.get("active")),
            }
    return None


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
            is_live_market=_parse_is_live(m),
            game_start_time=_parse_game_start(m),
        )
    except (KeyError, TypeError, ValueError) as exc:
        log.debug("Skipping malformed market row: %s", exc)
        return None


async def discover_markets() -> list[MarketCandidate]:
    """Walk Polymarket's esports events via Gamma's tag filter and flatten to
    per-market candidates.

    Querying `/events?tag_slug=esports` is far more efficient than the old
    volume-sorted /markets scan: it returns only esports events (no keyword
    guessing) including the long-tail of low-volume pre-match markets — which
    the volume-sorted scan never reached, because a $300-volume R6 market
    sits ~600 entries deep in any of the volume orders. Per the spec, the
    "is the game live?" check is the gate, not lifetime volume.

    The events endpoint embeds each event's `markets[]` array; we copy that
    out, inject the event-level `live` flag and `slug` into each market dict
    so the existing `_row_to_candidate` parser (which reads `events[].live`
    and `groupSlug`) just works without per-row Gamma roundtrips.

    Gamma caps `limit` at 100 per request; we paginate up to offset 1500 so
    even deep long-tail events surface. De-duped by conditionId at the end.
    """
    seen: dict[str, MarketCandidate] = {}
    pages_fetched = 0
    for offset in range(0, 1500, 100):
        try:
            events = await _gamma_get("/events", {
                "tag_slug": "esports",
                "closed": "false",
                "archived": "false",
                "limit": "100",
                "offset": str(offset),
            })
        except Exception as exc:
            log.warning("Gamma esports events offset=%d failed: %s", offset, exc)
            continue
        if not events:
            break
        pages_fetched += 1
        for e in events:
            if _truthy(e.get("closed")) or _truthy(e.get("archived")):
                continue
            event_live = _truthy(e.get("live"))
            event_slug = e.get("slug") or ""
            event_start = e.get("startDate")
            for raw in (e.get("markets") or []):
                # Defensive copy + inject the parent-event flags so the
                # existing parser (which expects events[].live + groupSlug)
                # behaves the same as on the /markets endpoint.
                m = dict(raw)
                m["events"] = [{"live": event_live, "startTime": event_start}]
                m.setdefault("groupSlug", event_slug)
                cand = _row_to_candidate(m)
                if cand is None or not cand.condition_id:
                    continue
                # First write wins (events endpoint is the canonical source).
                seen.setdefault(cand.condition_id, cand)

    out = list(seen.values())
    log.info(
        "Gamma esports events: %d unique markets across %d pages",
        len(out), pages_fetched,
    )
    return out


def filter_esports_tradeable(
    markets: list[MarketCandidate],
) -> list[MarketCandidate]:
    """Apply the four hard filters from the spec."""
    kept: list[MarketCandidate] = []
    live_skipped = 0
    for m in markets:
        if not m.is_esports():
            continue
        # Skip matches that have already started — Claude's pre-match research is
        # blind to live game state. MIN_HOURS_TO_RESOLUTION below stays as a
        # backup for markets where Gamma didn't provide a start time.
        if m.is_live():
            live_skipped += 1
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
    if live_skipped:
        log.info("Skipped %d markets as currently live (game already started)",
                 live_skipped)
    log.info("Filtered to %d tradeable esports markets", len(kept))
    return kept


# ---------------------------------------------------------------------------
# Orderbook + order placement
# ---------------------------------------------------------------------------


async def get_best_ask(token_id: str) -> float | None:
    """Best ask price for `token_id` in dollars (e.g. 0.62). None if no asks.

    v2's `get_order_book` returns a dict shaped {"asks": [{"price","size"}, ...], "bids": [...]}.

    Retries up to 3 times on connection-layer errors (`status_code is None`).
    The sniper missed a $0.69 crossing on 2026-05-14 because CLOB dropped the
    keep-alive connection at that exact instant and a single-shot fetch gave
    up. HTTP-level errors (4xx/5xx) are NOT retried — those won't clear in
    a few tens of ms.
    """
    def _call() -> Any:
        return clob().get_order_book(token_id)

    book: Any = None
    for attempt in range(3):
        try:
            book = await asyncio.to_thread(_call)
            break
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status is not None:
                # Real HTTP error — fail fast.
                log.warning(
                    "orderbook fetch failed for %s (http %s): %s",
                    token_id, status, exc,
                )
                return None
            if attempt == 2:
                log.warning(
                    "orderbook fetch failed for %s after 3 tries: %s",
                    token_id, exc,
                )
                return None
            # Connection drop — quick retry on a fresh connection.
            await asyncio.sleep(0.05 * (attempt + 1))
    if book is None:
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

    Retries up to 3 times on connection-layer errors (status_code is None)
    — CLOB intermittently times out from the Railway/iproyal path and a
    quick re-attempt usually succeeds. HTTP-level errors fail fast.
    """
    def _call() -> Any:
        return clob().get_market(condition_id)

    info: Any = None
    for attempt in range(3):
        try:
            info = await asyncio.to_thread(_call)
            break
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status is not None:
                log.warning(
                    "CLOB get_market(%s) failed (http %s): %s",
                    condition_id, status, exc,
                )
                return None
            if attempt == 2:
                log.warning(
                    "CLOB get_market(%s) failed after 3 tries: %s",
                    condition_id, exc,
                )
                return None
            await asyncio.sleep(0.3 * (attempt + 1))
    if not isinstance(info, dict):
        return None
    return {
        "neg_risk": bool(info.get("neg_risk", False)),
        "tick_size": float(info.get("minimum_tick_size") or 0.01),
        "enable_order_book": bool(info.get("enable_order_book", True)),
        "accepting_orders": bool(info.get("accepting_orders", True)),
    }


class NoFillError(RuntimeError):
    """Order signed and submitted but the CLOB returned zero fill. Not a
    bug or a config issue — the book moved past our cap before the order
    landed, or there was simply nothing available at our price. Sniper
    callers treat this as "tried, missed" (info-level), not as a system
    error to alert on.
    """


async def place_market_buy(
    token_id: str,
    target_price: float,
    stake_usd: float,
    neg_risk: bool = False,
    tick_size: float = 0.01,
    max_slippage_ticks: int = 2,
) -> dict[str, Any]:
    """Place a $-denominated market BUY using FAK (Fill-And-Kill / IOC).

    Why FAK and not FOK: the sniper's all-or-nothing FOK orders were getting
    killed at the CLOB because BTC 5m books are typically thin around the
    trigger — by the time our order lands, the top of book has stepped past
    our slippage cap and no atomic fill is possible. FAK accepts any partial
    fill that's available at <=cap and cancels the rest, so we capture what
    we can instead of getting zero.

    Slippage protection: we sign with `price = target_price + max_slippage_ticks*tick_size`
    and pass that to MarketOrderArgs. The CLOB enforces this as a hard ceiling
    on the effective fill price. Without it, the SDK walks the *current* book
    at sign time and a thin book lets a $10 order at "best ask $0.10" sweep
    up to $0.99 if only 1 share sits at the top level.

    `neg_risk` must match the market's exchange (True for Neg-Risk, False for
    standard CTF).

    Returns a result dict mirroring the old signature so positions.py keeps
    working: limit_price (effective fill price), size_shares, stake_usd, response.
    Raises NoFillError if shares_filled == 0 — caller must NOT record a
    position, but should also not treat it as a system-level error.
    """
    if stake_usd <= 0:
        raise ValueError(f"invalid stake {stake_usd}")
    tick_str = _tick_size_str(tick_size)
    # Best ask + slippage buffer, clamped to MAX_PRICE so we never sign above
    # the strategy's hard price ceiling.
    price_cap = round(
        min(target_price + max_slippage_ticks * tick_size, config.MAX_PRICE), 6
    )
    args = MarketOrderArgs(
        token_id=token_id,
        amount=round(stake_usd, 2),       # whole-cent precision; CLOB enforces this
        side=BUY,
        price=price_cap,                  # hard ceiling on effective fill price
        order_type=OrderType.FAK,
    )
    options = PartialCreateOrderOptions(neg_risk=neg_risk, tick_size=tick_str)
    log.info(
        "Signing market BUY: token=%s amount=$%.2f target=%.4f cap=%.4f neg_risk=%s tick=%s",
        token_id, stake_usd, target_price, price_cap, neg_risk, tick_str,
    )

    def _call() -> Any:
        signed = clob().create_market_order(args, options=options)
        return clob().post_order(signed, OrderType.FAK)

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

    try:
        resp = await asyncio.to_thread(_do)
    except PolyApiException as exc:
        # FOK/FAK time-in-force errors are the CLOB's way of saying "the book
        # moved past your cap before this order landed" — same outcome as a
        # zero-fill response, just delivered as a 400 instead of a payload.
        # Map to NoFillError so the sniper treats it as a soft "tried, missed"
        # instead of paging Telegram on every spike.
        err_text = str(exc).lower()
        status = getattr(exc, "status_code", None)
        soft_miss_markers = (
            "no orders found to match",   # FAK with empty match set
            "fak orders are",              # generic FAK kill text
            "fok orders are",              # FOK kill (legacy, in case server reverts)
            "couldn't be fully filled",    # FOK
            "couldn't be partially filled",
        )
        if status == 400 and any(s in err_text for s in soft_miss_markers):
            raise NoFillError(
                f"CLOB rejected order — book moved past cap "
                f"(target={target_price}, cap={price_cap}): {exc}"
            ) from exc
        raise
    # Parse the CLOB response. v2 returns:
    #   {'makingAmount': '0.999999', 'takingAmount': '15.151514', 'status': 'matched', ...}
    # makingAmount = USDC spent; takingAmount = shares received.
    if not isinstance(resp, dict):
        raise RuntimeError(f"Unexpected CLOB response type: {type(resp).__name__}: {resp!r}")
    try:
        usd_spent = float(resp.get("makingAmount") or 0)
        shares_filled = float(resp.get("takingAmount") or 0)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Couldn't parse fill amounts from CLOB response: {resp!r}") from exc

    # FAK can return takingAmount=0 when the book moved past our cap before
    # the order landed (or was empty at <=cap to begin with). That's a "tried
    # and missed", not a system error — raise the typed NoFillError so the
    # sniper can treat it as a soft skip instead of paging on it.
    if shares_filled <= 0 or usd_spent <= 0:
        status = resp.get("status")
        raise NoFillError(
            f"Order returned zero fill (status={status!r} shares={shares_filled} "
            f"spent=${usd_spent}). Book moved past cap or empty at <=cap "
            f"(target={target_price}, cap={price_cap})."
        )

    fill_price = usd_spent / shares_filled
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

    Treats a market as resolved if ANY of:
      - Gamma's `closed` field is true
      - `archived` is true
      - outcomePrices already shows a clear winner ([1,0] or [0,1])
      - umaResolutionStatus indicates settled

    Returns None only if there's genuinely no resolution signal.
    """
    params = {"condition_ids": condition_id}
    rows = await _gamma_get("/markets", params)
    if not rows:
        return None
    m = rows[0]
    closed = bool(m.get("closed"))
    archived = bool(m.get("archived"))
    uma_status = str(m.get("umaResolutionStatus") or "").lower()
    uma_settled = uma_status in ("resolved", "settled")

    # outcomePrices is the strongest signal — once UMA settles, it's set to [1,0] or [0,1]
    prices = _parse_outcome_prices(m.get("outcomePrices"))
    winner = None
    if len(prices) == 2:
        try:
            p0, p1 = float(prices[0]), float(prices[1])
        except (TypeError, ValueError):
            p0, p1 = -1.0, -1.0
        if p0 >= 0.99 and p1 <= 0.01:
            winner = "YES"
        elif p1 >= 0.99 and p0 <= 0.01:
            winner = "NO"

    resolved_via_prices = winner is not None
    if not (closed or archived or uma_settled or resolved_via_prices):
        return None

    return {
        "closed": True,
        "winner": winner,
        "resolved_at": m.get("closedTime") or m.get("endDate") or _now_iso(),
    }


@retry(**_HTTP_RETRY)
async def get_token_outcome_map(condition_ids: list[str]) -> dict[str, dict[str, str]]:
    """For each condition_id, return {"yes_token": str, "no_token": str,
    "condition_id": ...}. Sourced from Gamma's clobTokenIds (authoritative)
    so we don't have to trust data-api's per-trade `outcome` field, which
    in practice can be missing or misformatted.
    """
    out: dict[str, dict[str, str]] = {}
    for i in range(0, len(condition_ids), 50):
        batch = condition_ids[i : i + 50]
        try:
            rows = await _gamma_get("/markets", {"condition_ids": ",".join(batch)})
        except Exception:
            continue
        for m in rows or []:
            cid = m.get("conditionId") or m.get("condition_id")
            if not cid:
                continue
            tokens = _parse_token_ids(m.get("clobTokenIds"))
            if len(tokens) >= 2:
                out[str(cid)] = {"yes_token": tokens[0], "no_token": tokens[1]}
    return out


@retry(**_HTTP_RETRY)
async def get_market_game_start_times(condition_ids: list[str]) -> dict[str, str]:
    """Batch-fetch gameStartTime for a set of condition_ids from Gamma.
    Returns {condition_id: iso_or_unix_ts}. Missing markets just omit.
    """
    out: dict[str, str] = {}
    # Gamma accepts comma-separated condition_ids; batch in groups of 50
    for i in range(0, len(condition_ids), 50):
        batch = condition_ids[i : i + 50]
        try:
            rows = await _gamma_get("/markets", {"condition_ids": ",".join(batch)})
        except Exception:
            continue
        for m in rows or []:
            cid = m.get("conditionId") or m.get("condition_id")
            gst = m.get("gameStartTime") or m.get("startTime") or m.get("game_start_time")
            if cid and gst:
                out[str(cid)] = str(gst)
    return out


@retry(**_HTTP_RETRY)
async def get_user_trades(user_address: str) -> list[dict[str, Any]]:
    """All on-chain trades for this proxy address, newest first.

    Each row carries at least: conditionId, asset (token_id), side ("BUY"/"SELL"),
    price (float), size (shares), timestamp. Used to compute realised PnL for
    positions the bot opened but the user exited via the UI.
    """
    url = f"{config.DATA_API_HOST}/trades"
    params = {"user": user_address, "limit": 500}
    async with httpx.AsyncClient(timeout=30) as ac:
        r = await ac.get(url, params=params)
        r.raise_for_status()
        rows = r.json()
    return rows or []


@retry(**_HTTP_RETRY)
async def get_onchain_position_tokens(user_address: str) -> set[str]:
    """Return the set of token_ids the user currently holds shares of (size > 0).

    Hits Polymarket's data-api /positions endpoint. Used at boot to reconcile
    positions.json against on-chain reality — entries the bot recorded but the
    user has since sold/redeemed via the UI get pruned.
    """
    url = f"{config.DATA_API_HOST}/positions"
    params = {"user": user_address, "sizeThreshold": "0.0001"}
    async with httpx.AsyncClient(timeout=30) as ac:
        r = await ac.get(url, params=params)
        r.raise_for_status()
        rows = r.json()
    held: set[str] = set()
    for row in rows or []:
        token_id = row.get("asset") or row.get("tokenId")
        size = row.get("size")
        if token_id and size is not None and float(size) > 0:
            held.add(str(token_id))
    return held


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
