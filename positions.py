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


def list_open() -> list[dict[str, Any]]:
    return list(load()["open"])


def list_resolved() -> list[dict[str, Any]]:
    return list(load()["resolved"])


def mark_details_sent(token_id: str) -> bool:
    """Flag an open position as having had its OPEN POSITION review message
    emitted, so the boot-time resend doesn't spam it on every restart.
    Returns True if a record was found and updated."""
    data = load()
    changed = False
    for p in data["open"]:
        if str(p.get("token_id") or "") == str(token_id):
            p["details_sent"] = True
            changed = True
            break
    if changed:
        save(data)
    return changed


def reconcile_with_onchain(held_token_ids: set[str]) -> list[dict[str, Any]]:
    """Drop entries from `open` whose token_id is no longer held on-chain.

    Covers manual UI exits and pre-redeem-flow positions already redeemed in
    the UI. Dropped entries are appended to `resolved` with reconciled=True so
    we don't silently lose the record. Returns the list of dropped entries.
    """
    data = load()
    still_open: list[dict] = []
    dropped: list[dict] = []
    for p in data["open"]:
        token_id = str(p.get("token_id") or "")
        if token_id and token_id in held_token_ids:
            still_open.append(p)
        else:
            dropped.append({
                **p,
                "resolved_at": _now_iso(),
                "reconciled": True,
                "winner": None,
                "won": None,
                "pnl": None,
                "redeem_status": "skipped",
            })
    if not dropped:
        return []
    data["open"] = still_open
    data["resolved"].extend(dropped)
    if len(data["resolved"]) > 200:
        data["resolved"] = data["resolved"][-200:]
    save(data)
    return dropped


def open_event_keys() -> set[str]:
    """Set of question_ids already held -- used to avoid doubling up on the same match."""
    return {p["question_id"] for p in load()["open"] if p.get("question_id")}


def get_pending_redemptions() -> list[dict[str, Any]]:
    """Resolved-winning records the user hasn't been told to redeem yet.
    Legacy records with no redeem_status field are treated as pending so
    historical wins get a one-off ping after this feature deploys."""
    out: list[dict[str, Any]] = []
    for r in load()["resolved"]:
        if not r.get("won"):
            continue
        status = r.get("redeem_status")
        if status in (None, "pending"):
            out.append(r)
    return out


def set_redeem_status(
    condition_id: str,
    token_id: str,
    status: str,
) -> bool:
    """Update a resolved record's redeem state. Matches by (condition_id,
    token_id) since the same condition could appear twice (different sides
    bought on the same market across history). Returns True if a record
    was matched and updated."""
    data = load()
    for r in data["resolved"]:
        if (
            r.get("condition_id") == condition_id
            and r.get("token_id") == token_id
        ):
            r["redeem_status"] = status
            save(data)
            return True
    return False


def build_position_record(
    idea,
    fill: dict,
    potential_profit: float,
    neg_risk: bool,
) -> dict[str, Any]:
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
        # Needed at redeem time to pick the right CTF contract (NegRiskAdapter
        # vs ConditionalTokens). Captured at order time from CLOB meta — that's
        # the same value used to sign the order.
        "neg_risk": bool(neg_risk),
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
            # redeem_status: "pending" = won, user not yet told to redeem;
            # "notified" = Telegram ping sent, awaiting manual UI redeem;
            # "skipped" = losing position, nothing to redeem.
            "redeem_status": "pending" if won else "skipped",
        }
        data["resolved"].append(p_resolved)
        settled.append((p_resolved, won, pnl))
    data["open"] = still_open
    # Keep resolved log bounded
    if len(data["resolved"]) > 200:
        data["resolved"] = data["resolved"][-200:]
    save(data)
    return settled
