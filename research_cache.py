"""Cache Claude+web-search verdicts so we don't re-research the same market every 30 min.

Cache hit conditions:
  - entry exists for this condition_id
  - cached entry is younger than TTL_SECONDS
  - current YES price is within PRICE_TOLERANCE of the cached YES price
    (a big price move means the market saw new information; re-research)

Cache is JSON on the same volume as positions.json. Atomic writes via tmpfile + replace.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from typing import Any

import config
from logger_setup import get_logger

log = get_logger(__name__)

_CACHE_FILE = config.DATA_DIR / "research_cache.json"
TTL_SECONDS = 4 * 3600          # 4 hours
PRICE_TOLERANCE = 0.05          # 5 cents on YES price


def _load() -> dict[str, Any]:
    if not _CACHE_FILE.exists():
        return {}
    try:
        with _CACHE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("research_cache unreadable (%s); starting fresh", exc)
        return {}


def _save(data: dict[str, Any]) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=".rcache.", suffix=".json", dir=str(_CACHE_FILE.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, _CACHE_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def get(condition_id: str, current_yes_price: float) -> dict | None:
    """Return cached verdict dict if fresh enough, else None."""
    cache = _load()
    entry = cache.get(condition_id)
    if not entry:
        return None
    age = time.time() - entry.get("ts", 0)
    if age > TTL_SECONDS:
        return None
    if abs(current_yes_price - entry.get("yes_price", 0)) > PRICE_TOLERANCE:
        return None
    return entry.get("verdict")


def put(condition_id: str, yes_price: float, verdict: dict) -> None:
    """Store a verdict; prune expired entries to keep the file small."""
    cache = _load()
    cache[condition_id] = {
        "ts": time.time(),
        "yes_price": yes_price,
        "verdict": verdict,
    }
    now = time.time()
    cache = {k: v for k, v in cache.items() if now - v.get("ts", 0) <= TTL_SECONDS}
    _save(cache)


def stats() -> tuple[int, int]:
    """Return (total_entries, fresh_entries) for logging."""
    cache = _load()
    now = time.time()
    fresh = sum(1 for v in cache.values() if now - v.get("ts", 0) <= TTL_SECONDS)
    return len(cache), fresh
