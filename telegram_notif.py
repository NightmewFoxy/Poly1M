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


def _market_url(slug: str | None) -> str:
    return f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com/portfolio"


async def notify_trade(idea, fill: dict, potential_profit: float) -> None:
    side = idea.side
    price = fill["limit_price"]
    stake = fill["stake_usd"]
    shares = fill["size_shares"]
    true_pct = idea.true_prob_side * 100
    implied_pct = idea.price * 100
    url = _market_url(getattr(idea.market, "slug", "") or "")
    msg = (
        "🟢 TRADE EXECUTED\n"
        "\n"
        "📊 Market\n"
        f"{idea.market.question}\n"
        f"🔗 {url}\n"
        "\n"
        "💰 Position\n"
        f"{side} at ${price:.2f}\n"
        f"Stake: ${stake:.2f} → {shares:.2f} shares\n"
        f"Potential profit: +${potential_profit:.2f} after fees\n"
        "\n"
        "📈 Edge\n"
        f"True probability: {true_pct:.0f}% (bot's estimate)\n"
        f"Market implied: {implied_pct:.0f}%\n"
        f"EV: +{idea.ev_cents:.1f}¢ per dollar staked\n"
        "\n"
        "🧠 Why\n"
        f"{idea.summary}"
    )
    await _send(msg)


async def notify_resolution(position: dict, won: bool, pnl: float) -> None:
    header = "✅ POSITION WON" if won else "❌ POSITION LOST"
    url = _market_url(position.get("slug"))
    msg = (
        f"{header}\n"
        "\n"
        "📊 Market\n"
        f"{position['question']}\n"
        f"🔗 {url}\n"
        "\n"
        "💰 Result\n"
        f"{position['side']} @ ${position['price']:.2f}\n"
        f"Stake: ${position['stake_usd']:.2f}\n"
        f"PnL: {'+' if pnl >= 0 else ''}${pnl:.2f}"
    )
    await _send(msg)


async def notify_redeem_needed(position: dict, payout_usd: float) -> None:
    """Pings the user that a winning position is ready to redeem in the UI.
    Sent once per win (the record is marked 'notified' after this fires).
    Each winning share pays $1, so payout = shares."""
    url = _market_url(position.get("slug"))
    msg = (
        "💎 REDEEM READY\n"
        "\n"
        "📊 Market\n"
        f"{position.get('question', '?')}\n"
        "\n"
        "💰 Payout\n"
        f"{position.get('side', '?')}: {position.get('shares', 0):.2f} shares → ${payout_usd:.2f}\n"
        "\n"
        "👉 Redeem in UI\n"
        f"{url}\n"
        "Bot picks up freed USDC on the next cycle."
    )
    await _send(msg)


async def notify_history(
    resolved: list[dict],
    local_buys: int | None = None,
    onchain_buys: int | None = None,
) -> None:
    """Boot-time summary of every resolved trade.

    local_buys: count of BUY trades the bot has recorded in positions.json (open + resolved).
    onchain_buys: count of BUY trades on data-api for this proxy address.
    A gap means earlier trades aren't in positions.json (volume unmounted, fresh deploy, etc.).
    """
    if not resolved:
        msg = "📜 TRADE HISTORY\n\nNo resolved trades yet."
        if onchain_buys is not None and onchain_buys >= 0:
            msg += f"\n\nOn-chain BUYs ever made: {onchain_buys}."
            if local_buys is not None and onchain_buys > local_buys:
                msg += (
                    f"\n⚠️ Bot only knows about {local_buys} of them — "
                    "positions.json was probably wiped or volume unmounted at some point."
                )
        await _send(msg)
        return

    with_pnl = [r for r in resolved if r.get("pnl") is not None]
    without_pnl = [r for r in resolved if r.get("pnl") is None]

    lines = ["📜 TRADE HISTORY", ""]

    # --- Lifetime trade audit (positions.json vs on-chain reality)
    if onchain_buys is not None and onchain_buys >= 0:
        lines.append("🔎 Lifetime audit")
        lines.append(f"On-chain BUYs ever: {onchain_buys}")
        if local_buys is not None:
            lines.append(f"In positions.json: {local_buys}")
            if onchain_buys > local_buys:
                missing = onchain_buys - local_buys
                lines.append(
                    f"⚠️ {missing} earlier trades NOT in positions.json (volume drift / fresh deploys)."
                )
        lines.append("")

    # --- Summary stats — make small-sample warnings very loud
    if with_pnl:
        wins = [r for r in with_pnl if (r.get("won") is True or float(r.get("pnl") or 0) > 0)]
        total_pnl = sum(float(r.get("pnl") or 0) for r in with_pnl)
        total_stake = sum(float(r.get("stake_usd") or 0) for r in with_pnl)
        win_rate = len(wins) / len(with_pnl) * 100
        avg_true = sum(float(r.get("true_prob") or 0) for r in with_pnl) / len(with_pnl) * 100
        avg_gap = sum(
            (float(r.get("true_prob") or 0) - float(r.get("price") or 0))
            for r in with_pnl
        ) / len(with_pnl) * 100
        roi = (total_pnl / total_stake * 100) if total_stake > 0 else 0
        coverage = len(with_pnl) / len(resolved) * 100 if resolved else 0
        lines += [
            f"📊 Summary (over {len(with_pnl)} of {len(resolved)} closed positions = {coverage:.0f}% coverage)",
            f"Trades: {len(with_pnl)} · Profitable: {len(wins)} · Losing: {len(with_pnl) - len(wins)}",
            f"Net PnL: {'+' if total_pnl >= 0 else ''}${total_pnl:.2f} on ${total_stake:.2f} staked ({roi:+.1f}% ROI)",
            f"Win rate: {win_rate:.0f}% (model expected ~{avg_true:.0f}%)",
            f"Average edge per trade: +{avg_gap:.1f}pp (percentage points = true_prob − market_price)",
        ]
        if len(with_pnl) < 30:
            lines.append(
                f"⚠️ Sample size is only {len(with_pnl)} — not statistically meaningful. "
                "Need ~30+ trades before these numbers reflect real performance."
            )
        lines.append("")
    if without_pnl:
        lines.append(
            f"⚠️  {len(without_pnl)} trades still have no PnL (no matching CLOB sell, "
            "Gamma resolution missing, or token_id mismatch)"
        )
        lines.append("")

    # --- Per-trade list
    ordered = sorted(resolved, key=lambda r: r.get("resolved_at") or "", reverse=True)
    shown = ordered[:30]
    if shown:
        lines.append("📋 Per-trade (newest first)")
    for r in shown:
        pnl_val = r.get("pnl")
        if pnl_val is None:
            icon = "❓"
            pnl_str = "PnL ?"
        else:
            pnl = float(pnl_val)
            icon = "✅" if pnl > 0 else ("❌" if pnl < 0 else "➖")
            pnl_str = f"{'+' if pnl >= 0 else ''}${pnl:.2f}"
        q = (r.get("question") or "?")[:60]
        side = r.get("side") or "?"
        price = float(r.get("price") or 0)
        true_p = float(r.get("true_prob") or 0)
        gap_pp = (true_p - price) * 100
        lines.append(
            f"{icon} {pnl_str}  {q}\n"
            f"   {side} @ ${price:.2f} · true {true_p * 100:.0f}% (gap {gap_pp:+.1f}pp)"
        )

    if len(ordered) > len(shown):
        lines.append("")
        lines.append(f"… {len(ordered) - len(shown)} older trades not shown")

    text = "\n".join(lines)
    if len(text) > 3900:
        text = text[:3900] + "\n… (truncated)"
    await _send(text)


async def notify_no_ev_cycle(scanned: int) -> None:
    await _send(f"😴 Cycle done — no +EV markets (scanned {scanned} candidates)")


async def notify_error(where: str, err: str) -> None:
    text = (
        "⚠️ BOT ERROR\n"
        "\n"
        f"📍 Where: {where}\n"
        f"💥 {err}"
    )
    if len(text) > 3500:
        text = text[:3500] + "..."
    await _send(text)


async def notify_startup(open_positions: list[dict] | int) -> None:
    """Accepts either the list of open position dicts (preferred — emits names
    and URLs so you can tell which market is held) or a plain count for
    backwards compatibility."""
    if isinstance(open_positions, int):
        await _send(f"🚀 Bot started\n\n📂 Open positions: {open_positions}")
        return
    count = len(open_positions)
    lines = [f"🚀 Bot started", "", f"📂 Open positions: {count}"]
    for p in open_positions:
        url = _market_url(p.get("slug"))
        q = (p.get("question") or "?")[:120]
        side = p.get("side") or "?"
        shares = p.get("shares") or 0
        price = p.get("price")
        price_str = f" @ ${price:.2f}" if isinstance(price, (int, float)) else ""
        lines.append("")
        lines.append(f"• {q}")
        lines.append(f"  {side}{price_str} · {shares:.2f} shares")
        lines.append(f"  🔗 {url}")
    await _send("\n".join(lines))
