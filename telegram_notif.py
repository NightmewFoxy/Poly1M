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
    slug = getattr(idea.market, "slug", "") or ""
    url = f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com/portfolio"
    msg = (
        "TRADE EXECUTED\n"
        f"Market: {idea.market.question}\n"
        f"Link: {url}\n"
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


async def notify_redeem_needed(position: dict, payout_usd: float) -> None:
    """Pings the user that a winning position is ready to redeem in the UI.
    Sent once per win (the record is marked 'notified' after this fires).
    Each winning share pays $1, so payout = shares."""
    slug = position.get("slug") or ""
    market_url = f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com/portfolio"
    msg = (
        "REDEEM READY (click in UI)\n"
        f"Market: {position.get('question', '?')}\n"
        f"Side: {position.get('side', '?')} ({position.get('shares', 0):.2f} shares)\n"
        f"Payout: ${payout_usd:.2f}\n"
        f"Go redeem: {market_url}\n"
        "Bot will pick up the freed USDC on its next cycle."
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


async def notify_startup(open_positions: list[dict] | int) -> None:
    """Accepts either the list of open position dicts (preferred — emits names
    and URLs so you can tell which market is held) or a plain count for
    backwards compatibility."""
    if isinstance(open_positions, int):
        await _send(f"Bot started. Open positions: {open_positions}.")
        return
    count = len(open_positions)
    lines = [f"Bot started. Open positions: {count}."]
    for p in open_positions:
        slug = p.get("slug") or ""
        url = f"https://polymarket.com/event/{slug}" if slug else ""
        q = (p.get("question") or "?")[:120]
        side = p.get("side") or "?"
        shares = p.get("shares") or 0
        line = f"- {q} | {side} ({shares:.2f} shares)"
        if url:
            line += f"\n  {url}"
        lines.append(line)
    await _send("\n".join(lines))
