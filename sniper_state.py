"""Sniper state: separate sniper_positions.json with daily PnL tracking.

Schema:
{
  "open":     [SniperPosition, ...],
  "resolved": [ResolvedSniperPosition, ...],   // capped to last 200
  "daily":    {"YYYY-MM-DD": pnl_usd, ...}     // rolling, capped to last 30 days
}

Daily counters key off UTC dates so the rollover happens at 00:00 UTC.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Optional

import sniper_config as scfg
from logger_setup import get_logger

log = get_logger("sniper.state")


_EMPTY: dict[str, Any] = {"open": [], "resolved": [], "daily": {}}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class SniperState:
    def __init__(self) -> None:
        self.path = scfg.SNIPER_STATE_FILE

    # ----- low-level IO ----------------------------------------------------

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"open": [], "resolved": [], "daily": {}}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            log.error("sniper_positions.json unreadable (%s); starting fresh", exc)
            return {"open": [], "resolved": [], "daily": {}}
        data.setdefault("open", [])
        data.setdefault("resolved", [])
        data.setdefault("daily", {})
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            prefix=".sniper.", suffix=".json", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ----- public ---------------------------------------------------------

    def today_pnl(self) -> float:
        data = self._load()
        return float(data["daily"].get(_today_utc_key(), 0.0))

    def is_at_daily_limit(self) -> bool:
        return self.today_pnl() <= -float(scfg.SNIPER_DAILY_LOSS_LIMIT_USD)

    def has_open_position(self) -> bool:
        return len(self._load()["open"]) > 0

    def has_open_position_on(self, condition_id: str) -> bool:
        return any(
            p.get("condition_id") == condition_id for p in self._load()["open"]
        )

    def get_open_positions(self) -> list[dict[str, Any]]:
        return list(self._load()["open"])

    def get_pending_redemptions(self) -> list[dict[str, Any]]:
        """Resolved-winning positions that still need an on-chain redeem.

        A record qualifies if it won AND either has `redeem_status='pending'`
        (the post-feature path) OR has no `redeem_status` field at all
        (historical records from before auto-redeem shipped — backfilled
        on first scan).
        """
        return [
            r for r in self._load()["resolved"]
            if r.get("won")
            and r.get("redeem_status") in (None, "pending")
        ]

    def set_redeem_status(
        self,
        condition_id: str,
        token_id: str,
        status: str,
        tx_hash: Optional[str] = None,
        increment_attempts: bool = False,
    ) -> bool:
        """Mark a resolved record's redeem state. Matches by condition_id +
        token_id since the same condition_id could theoretically appear twice
        (different sides bought on the same market). Returns True on success.
        """
        data = self._load()
        for r in data["resolved"]:
            if (
                r.get("condition_id") == condition_id
                and r.get("token_id") == token_id
            ):
                r["redeem_status"] = status
                if tx_hash is not None:
                    r["redeem_tx_hash"] = tx_hash
                if increment_attempts:
                    r["redeem_attempts"] = int(r.get("redeem_attempts", 0)) + 1
                self._save(data)
                return True
        return False

    def record_open(self, position: dict[str, Any]) -> None:
        data = self._load()
        data["open"].append(position)
        self._save(data)

    def record_resolution(
        self,
        condition_id: str,
        winner: Optional[str],
        resolved_at: Optional[str],
    ) -> Optional[tuple[dict[str, Any], bool, float]]:
        """Move an open position to resolved, update daily PnL. Returns
        (position, won, pnl) or None if no matching open position."""
        data = self._load()
        idx = None
        for i, p in enumerate(data["open"]):
            if p.get("condition_id") == condition_id:
                idx = i
                break
        if idx is None:
            return None
        pos = data["open"].pop(idx)

        # PnL math mirrors positions.py: fee on net winnings only.
        side = pos.get("side")
        stake = float(pos.get("stake_usd", 0.0))
        shares = float(pos.get("shares", 0.0))
        if winner is None:
            # invalid resolution → refund assumption
            won = False
            pnl = 0.0
        else:
            won = winner == side
            if won:
                gross = shares - stake
                # Reuse main config's POLYMARKET_FEE so the math stays consistent.
                import config as _shared
                pnl = (1.0 - _shared.POLYMARKET_FEE) * gross
            else:
                pnl = -stake

        # redeem_status: "pending" if won + payout claim still on-chain,
        # "skipped" if losing position (no USDC to claim, save gas),
        # "redeemed" after a successful on-chain redemption,
        # "submitted" if a tx is in flight, "failed" if a redeem attempt errored.
        resolved_record = {
            **pos,
            "resolved_at": resolved_at or _now_iso(),
            "winner": winner,
            "won": won,
            "pnl": round(pnl, 4),
            "redeem_status": "pending" if won else "skipped",
            "redeem_tx_hash": None,
            "redeem_attempts": 0,
        }
        data["resolved"].append(resolved_record)
        if len(data["resolved"]) > 200:
            data["resolved"] = data["resolved"][-200:]

        # Daily PnL counter (UTC).
        today = _today_utc_key()
        data["daily"][today] = round(
            float(data["daily"].get(today, 0.0)) + pnl, 4
        )
        # Trim daily history to last 30 days for tidiness.
        if len(data["daily"]) > 30:
            for k in sorted(data["daily"].keys())[:-30]:
                data["daily"].pop(k, None)

        self._save(data)
        return resolved_record, won, pnl


def build_position_record(
    market_question: str,
    condition_id: str,
    side: str,
    token_id: str,
    fill: dict[str, Any],
    move_pct: float,
    edge_cents: float,
    expected_fair: Optional[float],
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "question": market_question,
        "side": side,
        "token_id": token_id,
        "price": fill["limit_price"],
        "shares": fill["size_shares"],
        "stake_usd": fill["stake_usd"],
        "move_pct": round(move_pct, 4),
        "edge_cents": round(edge_cents, 3),
        "expected_fair": round(expected_fair, 4) if expected_fair is not None else None,
        "opened_at": _now_iso(),
    }
