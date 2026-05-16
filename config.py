"""Centralised config: load env vars once, expose typed constants."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# --- Outbound proxy (Polymarket geoblocks Railway and most cloud IPs) ---
# If OUTBOUND_PROXY is set (e.g. http://user:pass@host:port), export it as the
# standard HTTPS_PROXY/HTTP_PROXY env vars *before* requests/httpx initialise
# their sessions. py-clob-client uses `requests.request()`, which honours these
# vars via trust_env=True; httpx's AsyncClient does the same by default.
_OUTBOUND_PROXY = os.getenv("OUTBOUND_PROXY") or os.getenv("POLYMARKET_PROXY_URL")
if _OUTBOUND_PROXY:
    os.environ["HTTPS_PROXY"] = _OUTBOUND_PROXY
    os.environ["HTTP_PROXY"] = _OUTBOUND_PROXY
    os.environ.setdefault("https_proxy", _OUTBOUND_PROXY)
    os.environ.setdefault("http_proxy", _OUTBOUND_PROXY)
OUTBOUND_PROXY = _OUTBOUND_PROXY or ""


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
# Signature types (py-clob-client-v2 SignatureTypeV2):
#   0 = EOA              (maker == signer, ECDSA)
#   1 = POLY_PROXY       (Polymarket Magic.link / email proxy — most legacy accounts)
#   2 = POLY_GNOSIS_SAFE (Polymarket browser-wallet account, Gnosis Safe)
#   3 = POLY_1271        (EIP-1271 deposit wallet — new accounts post April 2026)
# Default is 1 (POLY_PROXY) — covers the common legacy email/Magic.link signup.
# IMPORTANT: for sig_type 1 or 2, POLYMARKET_FUNDER_ADDRESS must be your
# derived proxy/safe address (NOT the deposit address shown in the UI's Cash
# tab). To find it, place one trade manually in the Polymarket UI and read
# `maker_address` from the trade history endpoint, or call
# `getPolyProxyWalletAddress(your_relayer_eoa)` on the CTF Exchange contract.
POLYMARKET_SIGNATURE_TYPE = int(_opt("POLYMARKET_SIGNATURE_TYPE", "1"))

CLOB_HOST = "https://clob.polymarket.com"
GAMMA_HOST = "https://gamma-api.polymarket.com"
DATA_API_HOST = "https://data-api.polymarket.com"
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
# Lifetime $ volume floor for a candidate to enter research. Rule from spec:
# "as long as the game hasn't started, the bot can execute trades" — volume
# isn't supposed to gate. Default 0 lets the live-match check and the
# order-time best-ask check do the gating. Set higher via env if you want to
# avoid researching markets with paper-thin trading history.
MIN_VOLUME_USD = float(_opt("MIN_VOLUME_USD", "0"))
MAX_PRICE = float(_opt("MAX_PRICE", "0.80"))
# Floor on the price we'll buy: any side cheaper than this is almost certainly a
# market that's already been decided. The CLOB keeps near-resolved markets open
# at $0.001 for residual liquidity; pairing that with Claude's clamp at
# true_prob_yes >= 0.02 produces wildly +EV phantom trades on dead outcomes.
MIN_PRICE = float(_opt("MIN_PRICE", "0.10"))
# Sanity cap on EV. Anything above this is almost always a stale/resolved market
# fooling the EV formula -- a real soft-edge trade on Polymarket esports is in
# the single-digit to low-double-digit cents-per-dollar range.
MAX_EV_CENTS_PER_DOLLAR = float(_opt("MAX_EV_CENTS_PER_DOLLAR", "50"))
MIN_HOURS_TO_RESOLUTION = float(_opt("MIN_HOURS_TO_RESOLUTION", "2"))
POLYMARKET_FEE = float(_opt("POLYMARKET_FEE", "0.02"))

# Kill switch: when "false", bot still runs cycles + research (so cache stays warm)
# but skips the actual order POST. Lets you pause trading without burning API credits
# on a broken trade path while you fix it.
TRADING_ENABLED = _opt("TRADING_ENABLED", "true").lower() not in ("false", "0", "no", "off")


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
    "iem", "esl", "blast", "the international", "ti12", "ti13", "ti14",
    "cs major", "csgo major", "cs2 major", "esl major", "rlcs major",
    "worlds 2025", "worlds 2026", "msi 2025", "msi 2026",
)
