"""Sniper signal: fire when either side's ask reaches SNIPER_TRIGGER_PRICE.

Polymarket-only trigger. No Binance / no edge math / no fair-value heuristic.
The caller polls the market (via get_active_market) on a short cadence and
hands the resulting BtcMarket plus the timestamp of the last fire to
`evaluate()`. If either UP or DOWN ask has crossed the trigger and we're
past the cooldown window, we return a Decision; otherwise None.
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


def evaluate(market, last_fire_ts: float) -> Decision | None:
    if market is None:
        return None
    if time.time() - last_fire_ts < scfg.SNIPER_COOLDOWN_SECONDS:
        return None
    if market.up_ask is not None and market.up_ask >= scfg.SNIPER_TRIGGER_PRICE:
        return Decision("UP", market.up_token, market.up_ask)
    if market.down_ask is not None and market.down_ask >= scfg.SNIPER_TRIGGER_PRICE:
        return Decision("DOWN", market.down_token, market.down_ask)
    return None
