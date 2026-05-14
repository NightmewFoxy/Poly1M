"""Sniper signal: fire when either side's ask is INSIDE the trigger window.

Polymarket-only trigger. No Binance / no edge math / no fair-value heuristic.
The caller polls the market on a short cadence and hands the resulting
BtcMarket plus the timestamp of the last fire to `evaluate()`.

Trigger semantics: fire when an ask is within
`SNIPER_TRIGGER_TOLERANCE_TICKS` ticks of `SNIPER_TRIGGER_PRICE`. With the
defaults (trigger 0.69, tolerance 1 tick, tick 0.01) that's [0.68, 0.70].
Set tolerance to 0 for exact-only. Anything strictly outside the window —
i.e., the book has moved past the trigger — does NOT fire; we wait for the
ask to settle back inside the window.
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


def _in_window(ask: float | None, trigger: float, tick_size: float) -> bool:
    if ask is None:
        return False
    # Ask is quantized to tick_size. Accept anything within
    # (tolerance_ticks + 0.5) * tick of the trigger: the integer-tick window
    # plus half a tick of slack for float jitter. With tolerance_ticks=1 and
    # tick=0.01 that's |ask - 0.69| < 0.015, i.e. {0.68, 0.69, 0.70}.
    tol = (scfg.SNIPER_TRIGGER_TOLERANCE_TICKS + 0.5) * max(tick_size, 0.001)
    return abs(ask - trigger) < tol


def evaluate(market, last_fire_ts: float) -> Decision | None:
    if market is None:
        return None
    if time.time() - last_fire_ts < scfg.SNIPER_COOLDOWN_SECONDS:
        return None
    trigger = scfg.SNIPER_TRIGGER_PRICE
    tick = getattr(market, "tick_size", 0.01) or 0.01
    if _in_window(market.up_ask, trigger, tick):
        return Decision("UP", market.up_token, market.up_ask)
    if _in_window(market.down_ask, trigger, tick):
        return Decision("DOWN", market.down_token, market.down_ask)
    return None
