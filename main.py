"""Entry point: continuous loop, every LOOP_INTERVAL_SECONDS.

Each cycle:
  1. Reconcile: check resolutions on open positions, notify, persist.
  2. Discover: fetch markets from Gamma, filter to tradeable esports.
  3. Research: run Claude+web-search on each survivor, collect +EV ideas.
  4. Rank: sort by EV cents desc, then volume desc, then earliest end date.
  5. Trade: open up to MAX_OPEN_POSITIONS, skip events already held, $10 each.
  6. Notify: Telegram on each fill, or one summary if nothing traded.

Signal handlers ensure positions.json is fully flushed before SIGTERM exits
(Railway sends SIGTERM on redeploy).
"""
from __future__ import annotations

import asyncio
import signal
import traceback
from typing import Any

import config
import positions
import telegram_notif as tg
from logger_setup import get_logger
from polymarket_client import (
    GeoblockedError,
    MarketCandidate,
    discover_markets,
    filter_esports_tradeable,
    get_best_ask,
    place_market_buy,
)
from research import TradeIdea, potential_profit_net, research_and_score

log = get_logger(__name__)

_shutdown = asyncio.Event()
# Tracks whether the previous cycle hit a geoblock, so we only Telegram on transitions
# (entering blocked state, or recovering from it) instead of once per 30-min cycle.
_geoblocked = False


def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    def _stop(*_: Any) -> None:
        log.info("Shutdown signal received")
        _shutdown.set()

    # SIGTERM/SIGINT on Linux (Railway); SIGBREAK on Windows
    for sig_name in ("SIGTERM", "SIGINT", "SIGBREAK"):
        sig = getattr(signal, sig_name, None)
        if sig is None:
            continue
        try:
            loop.add_signal_handler(sig, _stop)
        except (NotImplementedError, RuntimeError):
            # Windows asyncio can't add_signal_handler; fall back to signal.signal
            try:
                signal.signal(sig, _stop)
            except (ValueError, OSError):
                pass


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def rank_ideas(ideas: list[TradeIdea]) -> list[TradeIdea]:
    """Highest EV first; tie-break by volume desc, then nearest end date."""
    def end_seconds(i: TradeIdea) -> float:
        try:
            return i.market.hours_to_resolution()
        except Exception:
            return float("inf")

    return sorted(
        ideas,
        key=lambda i: (-i.ev_cents, -i.market.volume_usd, end_seconds(i)),
    )


# ---------------------------------------------------------------------------
# Cycle
# ---------------------------------------------------------------------------


async def run_cycle() -> None:
    log.info("=== Cycle start ===")

    # 1. Resolutions
    try:
        settled = await positions.check_resolutions()
        for pos, won, pnl in settled:
            try:
                await tg.notify_resolution(pos, won, pnl)
            except Exception as exc:
                log.warning("Telegram resolution notify failed: %s", exc)
        if settled:
            log.info("Settled %d positions", len(settled))
    except Exception as exc:
        log.exception("Resolution check failed")
        await _safe_notify("resolution_check", exc)

    open_now = positions.open_count()
    slots = max(0, config.MAX_OPEN_POSITIONS - open_now)
    log.info("Open=%d slots_available=%d", open_now, slots)
    if slots == 0:
        log.info("At capacity, skipping discovery this cycle")
        return

    held_events = positions.open_event_keys()

    # 2. Discovery
    try:
        all_markets = await discover_markets()
    except Exception as exc:
        log.exception("Market discovery failed")
        await _safe_notify("market_discovery", exc)
        return
    candidates = filter_esports_tradeable(all_markets)
    candidates = [c for c in candidates if c.question_id not in held_events]
    if not candidates:
        log.info("No tradeable esports markets after filters")
        try:
            await tg.notify_no_ev_cycle(0)
        except Exception:
            pass
        return

    # Cap research to a sane number to avoid burning API budget on a giant cycle.
    RESEARCH_CAP = 25
    if len(candidates) > RESEARCH_CAP:
        candidates = sorted(candidates, key=lambda c: -c.volume_usd)[:RESEARCH_CAP]
        log.info("Capped research universe to top %d by volume", RESEARCH_CAP)

    # 3. Research (concurrent but bounded; Claude calls are slow but tool-loops, so 4 at a time)
    sem = asyncio.Semaphore(4)

    async def _one(m: MarketCandidate) -> TradeIdea | None:
        async with sem:
            try:
                return await asyncio.to_thread(research_and_score, m)
            except Exception as exc:
                log.warning("Research failed for '%s': %s", m.question[:80], exc)
                return None

    ideas_raw = await asyncio.gather(*[_one(m) for m in candidates])
    ideas = [i for i in ideas_raw if i is not None]
    log.info("Research produced %d +EV ideas", len(ideas))

    if not ideas:
        try:
            await tg.notify_no_ev_cycle(len(candidates))
        except Exception:
            pass
        return

    # 4. Rank
    ranked = rank_ideas(ideas)
    log.info(
        "Top idea: %s | %s @ %.3f | EV=%.1fc | true=%.2f",
        ranked[0].market.question[:80],
        ranked[0].side,
        ranked[0].price,
        ranked[0].ev_cents,
        ranked[0].true_prob_side,
    )

    # 5. Trade
    used_events: set[str] = set(held_events)
    filled = 0
    for idea in ranked:
        if filled >= slots:
            break
        if _shutdown.is_set():
            log.info("Shutdown requested; stopping trade loop")
            break
        qid = idea.market.question_id
        if qid in used_events:
            continue

        # Re-check the live best ask right before sending the order.
        live_ask = await get_best_ask(idea.token_id)
        if live_ask is None:
            log.info("No live ask for %s, skipping", idea.market.question[:60])
            continue
        if live_ask > config.MAX_PRICE:
            log.info("Live ask %.3f above max, skipping", live_ask)
            continue
        # If price moved against us enough to flip EV negative, skip.
        from research import ev_cents_per_dollar  # local import to avoid cycle at module load
        live_ev = ev_cents_per_dollar(idea.true_prob_side, live_ask)
        if live_ev <= 0:
            log.info("Live price %.3f killed EV (%.1fc); skipping", live_ask, live_ev)
            continue

        try:
            fill = await place_market_buy(
                token_id=idea.token_id,
                target_price=live_ask,
                stake_usd=config.STAKE_USD,
            )
        except GeoblockedError as exc:
            # No point trying the next idea this cycle — every order from this IP will 403.
            global _geoblocked
            log.error("Geoblocked by Polymarket CLOB: %s", exc)
            if not _geoblocked:
                _geoblocked = True
                await _safe_notify("place_order_geoblock", exc)
            else:
                log.info("Still geoblocked; suppressing duplicate Telegram alert")
            return
        except Exception as exc:
            log.warning("Order placement failed for %s: %s", idea.market.question[:60], exc)
            await _safe_notify("place_order", exc)
            continue

        # First fill since recovery from a geoblock — let the user know egress is healthy again.
        if _geoblocked:
            globals()["_geoblocked"] = False
            try:
                await tg.notify_error("geoblock_cleared", "CLOB egress is healthy again; trading resumed.")
            except Exception:
                pass

        # Persist + notify
        pp = potential_profit_net(fill["limit_price"], fill["stake_usd"])
        record = positions.build_position_record(idea, fill, pp)
        try:
            positions.append_open(record)
        except Exception as exc:
            log.exception("Failed to persist position; the order DID go through")
            await _safe_notify("persist_position", exc)
        used_events.add(qid)
        filled += 1
        try:
            await tg.notify_trade(idea, fill, pp)
        except Exception as exc:
            log.warning("Telegram trade notify failed: %s", exc)

    log.info("Cycle done; filled %d new positions", filled)


async def _safe_notify(where: str, exc: BaseException) -> None:
    try:
        await tg.notify_error(where, f"{type(exc).__name__}: {exc}")
    except Exception as inner:
        log.warning("Telegram error notify failed: %s", inner)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


async def main_async() -> None:
    log.info(
        "Starting bot | model=%s | stake=$%s | loop=%ss | max_positions=%d",
        config.ANTHROPIC_MODEL,
        config.STAKE_USD,
        config.LOOP_INTERVAL_SECONDS,
        config.MAX_OPEN_POSITIONS,
    )
    try:
        await tg.notify_startup(positions.open_count())
    except Exception as exc:
        log.warning("Startup Telegram notify failed: %s", exc)

    while not _shutdown.is_set():
        try:
            await run_cycle()
        except Exception:
            log.exception("Unhandled exception in cycle")
            await _safe_notify("run_cycle", Exception(traceback.format_exc(limit=4)))
        # Sleep interruptibly so SIGTERM is responsive.
        try:
            await asyncio.wait_for(_shutdown.wait(), timeout=config.LOOP_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            pass

    log.info("Bot shut down cleanly")


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _install_signal_handlers(loop)
    try:
        loop.run_until_complete(main_async())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
