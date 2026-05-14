"""Position store: read/write positions.json atomically, check resolutions.

Schema:
{
  "open": [Position, ...],
  "resolved": [ResolvedPosition, ...]   // capped to last 200
}

Position fields written on entry; resolution adds won/pnl/resolved_at.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any

import config
from logger_setup import get_logger
from polymarket_client import get_market_resolution

log = get_logger(__name__)


_EMPTY: dict[str, list] = {"open": [], "resolved": []}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> dict[str, list]:
    if not config.POSITIONS_FILE.exists():
        return {"open": [], "resolved": []}
    try:
        with config.POSITIONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("open", [])
        data.setdefault("resolved", [])
        return data
    except (json.JSONDecodeError, OSError) as exc:
        log.error("positions.json unreadable (%s); starting fresh", exc)
        return {"open": [], "resolved": []}


def save(data: dict[str, list]) -> None:
    """Atomic write: tmp file + replace, so a crash mid-write can't corrupt state."""
    config.POSITIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=".positions.", suffix=".json", dir=str(config.POSITIONS_FILE.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp_path, config.POSITIONS_FILE)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def append_open(position: dict[str, Any]) -> None:
    data = load()
    data["open"].append(position)
    save(data)


def open_count() -> int:
    return len(load()["open"])


def open_event_keys() -> set[str]:
    """Set of question_ids already held -- used to avoid doubling up on the same match."""
    return {p["question_id"] for p in load()["open"] if p.get("question_id")}


def build_position_record(idea, fill: dict, potential_profit: float) -> dict[str, Any]:
    return {
        "condition_id": idea.market.condition_id,
        "question_id": idea.market.question_id,
        "question": idea.market.question,
        "slug": idea.market.slug,
        "side": idea.side,
        "token_id": idea.token_id,
        "price": fill["limit_price"],
        "shares": fill["size_shares"],
        "stake_usd": fill["stake_usd"],
        "true_prob": idea.true_prob_side,
        "ev_cents": idea.ev_cents,
        "confidence": idea.confidence,
        "summary": idea.summary,
        "potential_profit_net": potential_profit,
        "opened_at": _now_iso(),
        "ends_at": idea.market.end_date_iso,
    }


async def check_resolutions() -> list[tuple[dict, bool, float]]:
    """For each open position, ask Gamma if the market has closed; move resolved
    ones to the `resolved` bucket. Returns list of (position, won, pnl)."""
    data = load()
    still_open: list[dict] = []
    settled: list[tuple[dict, bool, float]] = []
    for p in data["open"]:
        info = None
        try:
            info = await get_market_resolution(p["condition_id"])
        except Exception as exc:
            log.warning("resolution lookup failed for %s: %s", p["condition_id"], exc)
        if not info or not info.get("closed"):
            still_open.append(p)
            continue
        winner = info.get("winner")  # "YES" / "NO" / None
        if winner is None:
            # Closed but unresolved (e.g. invalid market); refund assumption: PnL = 0
            won = False
            pnl = 0.0
        else:
            won = winner == p["side"]
            if won:
                gross_profit = p["shares"] - p["stake_usd"]
                pnl = (1 - config.POLYMARKET_FEE) * gross_profit
            else:
                pnl = -p["stake_usd"]
        p_resolved = {
            **p,
            "resolved_at": info.get("resolved_at") or _now_iso(),
            "winner": winner,
            "won": won,
            "pnl": round(pnl, 4),
        }
        data["resolved"].append(p_resolved)
        settled.append((p_resolved, won, pnl))
    data["open"] = still_open
    # Keep resolved log bounded
    if len(data["resolved"]) > 200:
        data["resolved"] = data["resolved"][-200:]
    save(data)
    return settled
