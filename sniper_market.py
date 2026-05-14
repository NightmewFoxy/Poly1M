"""Find the currently-tradeable 'BTC Up or Down 5m' Polymarket market.

Polymarket creates these markets on a rotating 5-minute cadence. The one we
want is the active, not-yet-closed market whose endDate is in the future and
closest to now. Refresh every SNIPER_MARKET_CACHE_TTL_SECONDS; cache between
refreshes.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import sniper_config as scfg
from logger_setup import get_logger
from polymarket_client import _gamma_get, get_market_meta

log = get_logger("sniper.market")


@dataclass
class BtcMarket:
    condition_id: str
    question: str
    slug: str
    end_date_iso: str
    end_dt: datetime
    up_token_id: str
    down_token_id: str
    neg_risk: bool
    tick_size: float

    def seconds_to_end(self) -> float:
        return (self.end_dt - datetime.now(timezone.utc)).total_seconds()


# ---------------------------------------------------------------------------
# Parsing helpers (kept local so polymarket_client.py stays untouched)
# ---------------------------------------------------------------------------


def _decode_json_list(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            v = json.loads(raw)
            return v if isinstance(v, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _looks_like_btc_5m(slug: str, question: str) -> bool:
    text = f"{slug} {question}".lower()
    if "btc" not in text and "bitcoin" not in text:
        return False
    five_min_markers = ("5m", "5-min", "5 min", "5-minute", "5 minute")
    return any(k in text for k in five_min_markers)


def _resolve_up_down(m: dict) -> Optional[tuple[str, str]]:
    """Return (up_token_id, down_token_id) from a Gamma market row, or None."""
    outcomes = _decode_json_list(m.get("outcomes"))
    tokens = _decode_json_list(m.get("clobTokenIds"))
    if len(outcomes) != 2 or len(tokens) != 2:
        return None
    up_idx: Optional[int] = None
    down_idx: Optional[int] = None
    for i, o in enumerate(outcomes):
        s = str(o).strip().lower()
        if s in ("up", "higher", "yes") or s.startswith("up "):
            up_idx = i
        elif s in ("down", "lower", "no") or s.startswith("down "):
            down_idx = i
    if up_idx is None or down_idx is None or up_idx == down_idx:
        return None
    return str(tokens[up_idx]), str(tokens[down_idx])


# ---------------------------------------------------------------------------
# Public: cached lookup
# ---------------------------------------------------------------------------


class BtcMarketCache:
    """Caches the active BTC 5m market for SNIPER_MARKET_CACHE_TTL_SECONDS."""

    def __init__(self, ttl: float = scfg.SNIPER_MARKET_CACHE_TTL_SECONDS) -> None:
        self.ttl = ttl
        self._current: Optional[BtcMarket] = None
        self._fetched_at: float = 0.0
        self._lock = asyncio.Lock()

    async def get(self) -> Optional[BtcMarket]:
        async with self._lock:
            now = time.monotonic()
            cached_fresh = (
                self._current is not None
                and (now - self._fetched_at) < self.ttl
                and self._current.seconds_to_end() > 0
            )
            if cached_fresh:
                return self._current
            new = await _find_active_btc_5m_market()
            if new is not None:
                self._current = new
                self._fetched_at = now
            elif self._current is not None and self._current.seconds_to_end() <= 0:
                # Existing cache is stale and refresh failed — drop it.
                self._current = None
            return self._current

    def invalidate(self) -> None:
        self._current = None
        self._fetched_at = 0.0


async def _find_active_btc_5m_market() -> Optional[BtcMarket]:
    now = datetime.now(timezone.utc)
    # Gamma caps the response at 100 rows. Without an end_date_min filter,
    # the ascending-endDate result is full of stale "active but actually
    # past" markets and the fresh ones get pushed off the page. Filter
    # server-side to ending-in-the-future so the top of the list is the
    # currently-tradeable 5-min slot.
    params = {
        "active": "true",
        "closed": "false",
        "archived": "false",
        "limit": "100",
        "order": "endDate",
        "ascending": "true",
        "end_date_min": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        rows = await _gamma_get("/markets", params)
    except Exception as exc:
        log.warning("Gamma BTC market fetch failed: %s", exc)
        return None
    if not isinstance(rows, list):
        return None
    best: tuple[float, dict] | None = None
    for m in rows:
        slug = m.get("slug") or ""
        question = m.get("question") or ""
        if not _looks_like_btc_5m(slug, question):
            continue
        end_iso = m.get("endDate") or ""
        try:
            end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if end <= now:
            continue
        delta = (end - now).total_seconds()
        if best is None or delta < best[0]:
            best = (delta, m)

    if best is None:
        log.info("No active BTC 5m market found in Gamma response")
        return None

    _, m = best
    tokens = _resolve_up_down(m)
    if tokens is None:
        log.warning(
            "Couldn't resolve UP/DOWN tokens for %s (outcomes=%r)",
            m.get("slug"), m.get("outcomes"),
        )
        return None
    up_token_id, down_token_id = tokens

    condition_id = m.get("conditionId") or ""
    if not condition_id:
        return None

    # CLOB is canonical for neg_risk + tick_size (Gamma occasionally wrong).
    meta = await get_market_meta(condition_id)
    if meta is None:
        log.warning("CLOB get_market(%s) returned no meta; skipping", condition_id)
        return None

    end_iso = m.get("endDate") or ""
    try:
        end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None

    return BtcMarket(
        condition_id=condition_id,
        question=m.get("question") or "",
        slug=m.get("slug") or "",
        end_date_iso=end_iso,
        end_dt=end_dt,
        up_token_id=up_token_id,
        down_token_id=down_token_id,
        neg_risk=bool(meta["neg_risk"]),
        tick_size=float(meta["tick_size"]),
    )


# ---------------------------------------------------------------------------
# Resolution lookup for sniper positions
# ---------------------------------------------------------------------------


async def get_btc_market_resolution(
    condition_id: str, up_token_id: str
) -> Optional[dict[str, Any]]:
    """Like polymarket_client.get_market_resolution, but returns winner as
    'UP'/'DOWN' (or None for invalid) by matching outcome prices to the
    cached up_token_id.
    """
    try:
        rows = await _gamma_get("/markets", {"condition_ids": condition_id})
    except Exception as exc:
        log.warning("Gamma resolution lookup failed for %s: %s", condition_id, exc)
        return None
    if not rows:
        return None
    m = rows[0]
    closed_val = m.get("closed")
    closed = (
        bool(closed_val)
        if isinstance(closed_val, bool)
        else str(closed_val).strip().lower() in ("true", "1", "yes")
    )
    if not closed:
        return None

    tokens = _decode_json_list(m.get("clobTokenIds"))
    prices = _decode_json_list(m.get("outcomePrices"))
    winner: Optional[str] = None
    if len(tokens) == 2 and len(prices) == 2:
        try:
            p0 = float(prices[0])
            p1 = float(prices[1])
        except (TypeError, ValueError):
            p0 = p1 = 0.0
        winning_idx: Optional[int] = None
        if p0 == 1 and p1 == 0:
            winning_idx = 0
        elif p0 == 0 and p1 == 1:
            winning_idx = 1
        if winning_idx is not None:
            up_idx = 0 if str(tokens[0]) == up_token_id else 1
            winner = "UP" if winning_idx == up_idx else "DOWN"

    return {
        "closed": True,
        "winner": winner,
        "resolved_at": m.get("closedTime") or m.get("endDate"),
    }
