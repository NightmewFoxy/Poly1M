"""Sniper signal: should we fire right now, on which side, at what price?

A fire is gated by:
  1. Cooldown since last fire (SNIPER_COOLDOWN_SECONDS)
  2. Sufficient BTC move in the lookback window (SNIPER_MOVE_THRESHOLD_PCT)
  3. Live Polymarket ask still lags our expected post-move price by at least
     SNIPER_MIN_EDGE_CENTS

Fair-value heuristic (from the spec):
    expected = 0.5 + (|move_pct| / 100) * 50
clamped to [0.05, 0.95]. The "50" coefficient is a rough mapping from
percent-move to probability-shift over a 5-minute window; tune via
SNIPER_MOVE_THRESHOLD_PCT and the edge floor.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import sniper_config as scfg
from logger_setup import get_logger
from polymarket_client import get_best_ask
from sniper_binance import BinanceFeed
from sniper_market import BtcMarket

log = get_logger("sniper.signal")


@dataclass
class Decision:
    fire: bool
    reason: str
    side: Optional[str] = None             # "UP" or "DOWN"
    token_id: Optional[str] = None
    live_ask: Optional[float] = None
    expected_fair: Optional[float] = None
    edge_cents: float = 0.0
    move_pct: float = 0.0


def _expected_fair_for_side(move_pct: float) -> float:
    """Spec formula, applied to whichever side we'd buy."""
    raw = 0.5 + (abs(move_pct) / 100.0) * 50.0
    return max(0.05, min(0.95, raw))


async def evaluate(
    feed: BinanceFeed,
    market: BtcMarket,
    last_fire_monotonic: Optional[float],
) -> Decision:
    # Cooldown
    if last_fire_monotonic is not None:
        elapsed = time.monotonic() - last_fire_monotonic
        if elapsed < scfg.SNIPER_COOLDOWN_SECONDS:
            return Decision(
                fire=False,
                reason=f"cooldown ({elapsed:.0f}s/{scfg.SNIPER_COOLDOWN_SECONDS}s)",
            )

    # Time-to-resolution gate: don't fire when there's no headroom for the
    # market to actually reprice + settle after we buy.
    secs_left = market.seconds_to_end()
    if secs_left < scfg.SNIPER_MIN_TIME_TO_RESOLUTION_SECONDS:
        return Decision(
            fire=False,
            reason=f"market ends in {secs_left:.0f}s",
        )

    # Move detection
    move_pct = feed.move_pct_over(scfg.SNIPER_LOOKBACK_SECONDS)
    if move_pct is None:
        return Decision(fire=False, reason="insufficient_buffer")
    if abs(move_pct) < scfg.SNIPER_MOVE_THRESHOLD_PCT:
        return Decision(
            fire=False,
            reason=f"below_threshold ({move_pct:+.3f}%)",
            move_pct=move_pct,
        )

    side = "UP" if move_pct > 0 else "DOWN"
    token_id = market.up_token_id if side == "UP" else market.down_token_id

    # Edge check
    live_ask = await get_best_ask(token_id)
    if live_ask is None:
        return Decision(
            fire=False, reason="no_ask",
            side=side, token_id=token_id, move_pct=move_pct,
        )

    expected_fair = _expected_fair_for_side(move_pct)
    edge_cents = (expected_fair - live_ask) * 100.0
    if edge_cents < scfg.SNIPER_MIN_EDGE_CENTS:
        return Decision(
            fire=False,
            reason=f"edge {edge_cents:.2f}c < min {scfg.SNIPER_MIN_EDGE_CENTS:.1f}c",
            side=side, token_id=token_id,
            live_ask=live_ask, expected_fair=expected_fair,
            edge_cents=edge_cents, move_pct=move_pct,
        )

    return Decision(
        fire=True,
        reason="fire",
        side=side, token_id=token_id,
        live_ask=live_ask, expected_fair=expected_fair,
        edge_cents=edge_cents, move_pct=move_pct,
    )
