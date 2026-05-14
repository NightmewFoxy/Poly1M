"""Sniper signal: fire when either side's ask is AT SNIPER_TRIGGER_PRICE.

Polymarket-only trigger. No Binance / no edge math / no fair-value heuristic.
The caller polls the market (via get_active_market) on a short cadence and
hands the resulting BtcMarket plus the timestamp of the last fire to
`evaluate()`.

Trigger semantics: fire only when an ask is *exactly* at the trigger (within
half a tick). If the book has already moved past the trigger, do NOT chase —
wait for it to settle back to the trigger before firing.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import sniper_config as scfg


@dataclass
class Decision:
    side: str        # "UP" or "DOWN"
    token_id: str
    price: float     # observed ask at trigger time


def _at_trigger(ask: float | None, trigger: float, tick_size: float) -> bool:
    if ask is None:
        return False
    # Ask is quantized to the tick; accept anything within half a tick of the
    # trigger so float jitter doesn't miss the exact match. Anything strictly
    # above the trigger (next tick or higher) does NOT qualify.
    tol = max(tick_size, 0.001) / 2
    return abs(ask - trigger) < tol


def evaluate(market, last_fire_ts: float) -> Decision | None:
    if market is None:
        return None
    if time.time() - last_fire_ts < scfg.SNIPER_COOLDOWN_SECONDS:
        return None
    trigger = scfg.SNIPER_TRIGGER_PRICE
    tick = getattr(market, "tick_size", 0.01) or 0.01
    if _at_trigger(market.up_ask, trigger, tick):
        return Decision("UP", market.up_token, market.up_ask)
    if _at_trigger(market.down_ask, trigger, tick):
        return Decision("DOWN", market.down_token, market.down_ask)
    return None
