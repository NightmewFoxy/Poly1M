"""Sniper-specific env-loaded config.

The shared `config.py` carries Polymarket credentials, the data dir, Telegram
tokens, etc. We import it (transitively, via polymarket_client / telegram_notif)
but keep all sniper-specific tunables on the module below so the esports bot
can ignore us entirely.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

import config as _shared

load_dotenv()


def _opt(name: str, default: str) -> str:
    return os.getenv(name) or default


def _bool(name: str, default: str) -> bool:
    return _opt(name, default).strip().lower() not in ("false", "0", "no", "off", "")


SNIPER_ENABLED: bool = _bool("SNIPER_ENABLED", "true")
SNIPER_DRY_RUN: bool = _bool("SNIPER_DRY_RUN", "true")
SNIPER_STAKE_USD: float = float(_opt("SNIPER_STAKE_USD", "2"))
SNIPER_MOVE_THRESHOLD_PCT: float = float(_opt("SNIPER_MOVE_THRESHOLD_PCT", "0.3"))
SNIPER_LOOKBACK_SECONDS: int = int(_opt("SNIPER_LOOKBACK_SECONDS", "20"))
SNIPER_COOLDOWN_SECONDS: int = int(_opt("SNIPER_COOLDOWN_SECONDS", "60"))
SNIPER_DAILY_LOSS_LIMIT_USD: float = float(_opt("SNIPER_DAILY_LOSS_LIMIT_USD", "20"))
SNIPER_MIN_EDGE_CENTS: float = float(_opt("SNIPER_MIN_EDGE_CENTS", "3"))
SNIPER_BINANCE_SYMBOL: str = _opt("SNIPER_BINANCE_SYMBOL", "btcusdt").lower()

# Operational knobs (not in the spec, but needed for the loop). Keep defaults
# sensible; only override if you know why.
SNIPER_MARKET_CACHE_TTL_SECONDS: float = 30.0
SNIPER_MIN_TIME_TO_RESOLUTION_SECONDS: float = 90.0
SNIPER_RESOLUTION_POLL_SECONDS: float = 30.0
SNIPER_HEARTBEAT_SECONDS: float = 300.0

# Sniper-specific state file — separate from the esports bot's positions.json
# so two processes can't race on the same write.
SNIPER_STATE_FILE = _shared.DATA_DIR / "sniper_positions.json"
