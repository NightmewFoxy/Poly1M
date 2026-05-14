"""Telegram notifications. Direct Bot API via httpx (no extra deps needed)."""
from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import config
from logger_setup import get_logger

log = get_logger(__name__)


_TG_URL = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((httpx.HTTPError,)),
    reraise=False,
)
async def _send(text: str) -> None:
    async with httpx.AsyncClient(timeout=15) as ac:
        r = await ac.post(
            _TG_URL,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": text,
                "disable_web_page_preview": True,
            },
        )
        if r.status_code >= 400:
            log.warning("Telegram %s: %s", r.status_code, r.text[:200])
            r.raise_for_status()


async def notify_trade(idea, fill: dict, potential_profit: float) -> None:
    side = idea.side
    implied_pct = idea.price * 100
    true_pct = idea.true_prob_side * 100
    msg = (
        "TRADE EXECUTED\n"
        f"Market: {idea.market.question}\n"
        f"My position: {side} at {fill['limit_price'] * 100:.1f} cents\n"
        f"True probability estimate: {true_pct:.0f}%\n"
        f"Market implied probability: {implied_pct:.0f}%\n"
        f"EV: +{idea.ev_cents:.1f} cents per dollar\n"
        f"Stake: ${fill['stake_usd']:.2f}\n"
        f"Potential profit: ${potential_profit:.2f} after fees\n"
        f"Research summary: {idea.summary}"
    )
    await _send(msg)


async def notify_resolution(position: dict, won: bool, pnl: float) -> None:
    status = "WON" if won else "LOST"
    msg = (
        f"POSITION RESOLVED ({status})\n"
        f"Market: {position['question']}\n"
        f"Side: {position['side']} @ {position['price'] * 100:.1f}c\n"
        f"Stake: ${position['stake_usd']:.2f}\n"
        f"PnL: ${pnl:+.2f}"
    )
    await _send(msg)


async def notify_no_ev_cycle(scanned: int) -> None:
    await _send(
        f"Cycle complete -- no positive EV markets found (scanned {scanned} candidates)."
    )


async def notify_error(where: str, err: str) -> None:
    text = f"BOT ERROR in {where}: {err}"
    if len(text) > 3500:
        text = text[:3500] + "..."
    await _send(text)


async def notify_startup(open_positions: int) -> None:
    await _send(f"Bot started. Open positions: {open_positions}.")
