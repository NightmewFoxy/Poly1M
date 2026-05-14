"""Centralised config: load env vars once, expose typed constants."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _req(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def _opt(name: str, default: str) -> str:
    return os.getenv(name) or default


# --- Polymarket ---
POLYMARKET_API_KEY = _req("POLYMARKET_API_KEY")
POLYMARKET_API_SECRET = _req("POLYMARKET_API_SECRET")
POLYMARKET_API_PASSPHRASE = _req("POLYMARKET_API_PASSPHRASE")
POLYMARKET_WALLET_PRIVATE_KEY = _req("POLYMARKET_WALLET_PRIVATE_KEY")
POLYMARKET_FUNDER_ADDRESS = _req("POLYMARKET_FUNDER_ADDRESS")
POLYMARKET_SIGNATURE_TYPE = int(_opt("POLYMARKET_SIGNATURE_TYPE", "1"))

CLOB_HOST = "https://clob.polymarket.com"
GAMMA_HOST = "https://gamma-api.polymarket.com"
POLYGON_CHAIN_ID = 137

# --- Anthropic ---
ANTHROPIC_API_KEY = _req("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = _opt("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = _req("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _req("TELEGRAM_CHAT_ID")

# --- Strategy parameters ---
LOOP_INTERVAL_SECONDS = int(_opt("LOOP_INTERVAL_SECONDS", "1800"))
MAX_OPEN_POSITIONS = int(_opt("MAX_OPEN_POSITIONS", "10"))
STAKE_USD = float(_opt("STAKE_USD", "10"))
MIN_VOLUME_USD = float(_opt("MIN_VOLUME_USD", "10000"))
MAX_PRICE = float(_opt("MAX_PRICE", "0.80"))
MIN_HOURS_TO_RESOLUTION = float(_opt("MIN_HOURS_TO_RESOLUTION", "2"))
POLYMARKET_FEE = float(_opt("POLYMARKET_FEE", "0.02"))

# --- Storage (Railway volume mount point) ---
DATA_DIR = Path(_opt("DATA_DIR", "./data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
POSITIONS_FILE = DATA_DIR / "positions.json"
LOG_FILE = DATA_DIR / "bot.log"

# Esports keyword filter (case-insensitive substring match against question/category/tags)
ESPORTS_KEYWORDS = (
    "esports", "e-sports",
    "cs2", "cs:go", "csgo", "counter-strike", "counterstrike",
    "dota", "dota 2", "dota2",
    "league of legends", "lol esports", " lol ", "lck", "lec", "lcs", "lpl",
    "valorant", "vct",
    "overwatch", "owl",
    "rocket league", "rlcs",
    "starcraft", "sc2",
    "rainbow six", "r6 ", "siege",
    "apex legends",
    "call of duty", "cod ",
    "pubg",
    "mobile legends", "mlbb",
    "fortnite",
    "iem", "esl", "blast", "major", "the international", "ti12", "ti13", "ti14",
    "worlds 2025", "worlds 2026", "msi 2025", "msi 2026",
)
