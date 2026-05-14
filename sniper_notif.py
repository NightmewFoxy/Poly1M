"""Telegram messages specific to the sniper bot.

Short, consistent formats so the user can grep their chat by prefix
(SNIPER: ..., SNIPER RESOLVED: ...).
"""
from __future__ import annotations

import sniper_config as scfg
from logger_setup import get_logger
from telegram_notif import _send

log = get_logger("sniper.notif")


async def _safe(text: str) -> None:
    try:
        await _send(text)
    except Exception as exc:
        log.warning("Telegram send failed (%s): %s", exc, text[:80])


async def notify_startup() -> None:
    mode = "DRY-RUN" if scfg.SNIPER_DRY_RUN else "LIVE"
    await _safe(
        f"SNIPER started [{mode}] | stake=${scfg.SNIPER_STAKE_USD:.2f} | "
        f"threshold={scfg.SNIPER_MOVE_THRESHOLD_PCT:.2f}% in {scfg.SNIPER_LOOKBACK_SECONDS}s | "
        f"cooldown={scfg.SNIPER_COOLDOWN_SECONDS}s | "
        f"daily_limit=-${scfg.SNIPER_DAILY_LOSS_LIMIT_USD:.0f}"
    )


async def notify_fire(
    side: str,
    target_price: float,
    expected_fair: float,
    edge_cents: float,
    move_pct: float,
    lookback_seconds: int,
    stake_usd: float,
    fill_price: float | None = None,
    dry_run: bool = False,
) -> None:
    if dry_run:
        prefix = "SNIPER WOULD-HAVE-FIRED"
        price_part = f"@ {target_price:.3f}"
    else:
        prefix = "SNIPER FIRED"
        price_part = (
            f"@ {fill_price:.3f}" if fill_price is not None else f"@ ~{target_price:.3f}"
        )
    await _safe(
        f"{prefix}: BUY {side} {price_part} on BTC-5m | "
        f"move={move_pct:+.3f}% in {lookback_seconds}s | "
        f"fair~{expected_fair:.3f} | edge={edge_cents:.1f}c | "
        f"stake=${stake_usd:.2f}"
    )


async def notify_resolution(
    side: str,
    won: bool,
    pnl: float,
    today_pnl: float,
) -> None:
    status = "WON" if won else "LOST"
    await _safe(
        f"SNIPER RESOLVED: {side} {status}. "
        f"PnL={pnl:+.2f} | day total: {today_pnl:+.2f} / "
        f"-${scfg.SNIPER_DAILY_LOSS_LIMIT_USD:.0f} limit"
    )


async def notify_daily_limit_hit(today_pnl: float) -> None:
    await _safe(
        f"SNIPER DAILY LIMIT HIT: day total {today_pnl:+.2f} <= "
        f"-${scfg.SNIPER_DAILY_LOSS_LIMIT_USD:.0f}. Pausing trades until UTC midnight."
    )


async def notify_error(where: str, err: str) -> None:
    text = f"SNIPER ERROR in {where}: {err}"
    if len(text) > 3500:
        text = text[:3500] + "..."
    await _safe(text)
