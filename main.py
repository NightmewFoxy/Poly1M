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
    fetch_market_trade_safety,
    filter_esports_tradeable,
    get_best_ask,
    get_market_meta,
    get_onchain_position_tokens,
    get_usdc_balance,
    get_user_trades,
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
    """Highest EV first; tie-break by nearest end date, then volume desc."""
    def end_seconds(i: TradeIdea) -> float:
        try:
            return i.market.hours_to_resolution()
        except Exception:
            return float("inf")

    return sorted(
        ideas,
        key=lambda i: (-i.ev_cents, end_seconds(i), -i.market.volume_usd),
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

    # 1b. Notify the user about any winning positions that haven't been
    # redeemed yet (UI redeem is gasless; bot-side redeem isn't, so we punt
    # the click to the user). Once they redeem, the wallet refills and the
    # balance check below sees the new USDC on a future cycle — no
    # feedback loop needed.
    try:
        await _notify_pending_redemptions()
    except Exception as exc:
        log.exception("Pending-redeem notify failed")
        await _safe_notify("redeem_notify", exc)

    open_now = positions.open_count()
    slots = max(0, config.MAX_OPEN_POSITIONS - open_now)
    log.info("Open=%d slots_available=%d", open_now, slots)
    if slots == 0:
        log.info("At capacity, skipping discovery this cycle")
        return

    # Cap slots by what we can actually afford. Otherwise we'd burn Claude tokens
    # researching markets we don't have cash to enter — and just fail at order time.
    # When older positions resolve in a future cycle, the wallet refills (for wins)
    # and affordable_slots grows again, so trading resumes naturally.
    balance = await get_usdc_balance()
    if balance is None:
        log.info("Balance unknown; proceeding with position-count slots only")
    else:
        affordable_slots = int(balance // config.STAKE_USD)
        log.info("USDC=$%.2f affordable_slots=%d", balance, affordable_slots)
        if affordable_slots < slots:
            slots = affordable_slots
        if slots == 0:
            log.info(
                "Balance $%.2f < stake $%.2f; skipping discovery + research to avoid wasting API tokens",
                balance, config.STAKE_USD,
            )
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
    RESEARCH_CAP = 10
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

        # Re-check live status. The discovery filter ran minutes ago; a match
        # can cross its start time during research/ranking inside this same
        # cycle. is_live() compares the cached game_start_time to *now*, so
        # calling it again here catches games that flipped to live mid-cycle.
        # Claude's pre-match research is blind to in-game state — never trade
        # into a live match.
        if idea.market.is_live():
            log.info(
                "Match '%s' has gone live since discovery; skipping",
                idea.market.question[:60],
            )
            continue

        # Belt-and-suspenders: the cached event.live flag may be stale (set
        # at discovery), and game_start_time can be missing entirely. Hit
        # Gamma right now for fresh live/closed/archived flags. If Gamma
        # can't be reached after retries, refuse to trade — safer than
        # guessing on any of these.
        safety = await fetch_market_trade_safety(idea.market.condition_id)
        if safety is None:
            log.info(
                "Couldn't verify trade safety from Gamma for '%s'; "
                "skipping to avoid trading into a possibly-live or "
                "possibly-resolved market",
                idea.market.question[:60],
            )
            continue
        if safety["live"]:
            log.info(
                "Fresh Gamma check: '%s' is currently live; skipping",
                idea.market.question[:60],
            )
            continue
        if safety["closed"] or safety["archived"] or not safety["active"]:
            log.info(
                "Fresh Gamma check: '%s' has been closed/archived since "
                "discovery (closed=%s archived=%s active=%s); skipping",
                idea.market.question[:60],
                safety["closed"], safety["archived"], safety["active"],
            )
            continue

        # Re-check the live best ask right before sending the order.
        live_ask = await get_best_ask(idea.token_id)
        if live_ask is None:
            log.info("No live ask for %s, skipping", idea.market.question[:60])
            continue
        if live_ask > config.MAX_PRICE:
            log.info("Live ask %.3f above max, skipping", live_ask)
            continue
        if live_ask < config.MIN_PRICE:
            log.info("Live ask %.4f below MIN_PRICE; likely resolved market; skipping",
                     live_ask)
            continue
        # If price moved against us enough to flip EV negative, skip.
        from research import ev_cents_per_dollar  # local import to avoid cycle at module load
        live_ev = ev_cents_per_dollar(idea.true_prob_side, live_ask)
        if live_ev <= 0:
            log.info("Live price %.3f killed EV (%.1fc); skipping", live_ask, live_ev)
            continue
        if live_ev > config.MAX_EV_CENTS_PER_DOLLAR:
            log.info("EV %.1fc implausibly high (%.4f price, %.2f true prob); "
                     "market probably resolved or glitched; skipping",
                     live_ev, live_ask, idea.true_prob_side)
            continue

        # Use CLOB as the authoritative source for neg_risk + tick_size.
        # Gamma's negRisk is occasionally wrong or missing — signing with a
        # wrong neg_risk targets the wrong exchange contract and either
        # fails or, worse, fills against the wrong contract. If CLOB
        # doesn't answer, refuse to trade rather than fall back to Gamma's
        # potentially-stale values.
        meta = await get_market_meta(idea.market.condition_id)
        if meta is None:
            log.info(
                "CLOB get_market(%s) returned no meta; refusing to fall "
                "back to Gamma neg_risk/tick — skipping",
                idea.market.condition_id,
            )
            continue
        order_neg_risk = meta["neg_risk"]
        order_tick = meta["tick_size"]
        if not meta.get("accepting_orders", True) or not meta.get("enable_order_book", True):
            log.info("Market not accepting orders right now; skipping")
            continue

        if not config.TRADING_ENABLED:
            log.info(
                "TRADING_ENABLED=false; WOULD HAVE TRADED %s %s @ %.3f stake=$%s "
                "neg_risk=%s tick=%s ev=%.1fc",
                idea.market.question[:60], idea.side, live_ask,
                config.STAKE_USD, order_neg_risk, order_tick, idea.ev_cents,
            )
            used_events.add(qid)
            continue

        try:
            fill = await place_market_buy(
                token_id=idea.token_id,
                target_price=live_ask,
                stake_usd=config.STAKE_USD,
                neg_risk=order_neg_risk,
                tick_size=order_tick,
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
        record = positions.build_position_record(idea, fill, pp, order_neg_risk)
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


async def _notify_pending_redemptions() -> None:
    """Telegram the user once for each resolved-winning position that hasn't
    been claimed yet. Marks the record as 'notified' so we don't ping the
    same win every 30 minutes. Bot-side redeem is deliberately not
    automated — UI redeem is gasless, so the user clicks it themselves and
    the next cycle's USDC balance check picks up the freed cash.

    Includes backfill: legacy resolved-won records persisted before this
    feature shipped have no redeem_status field; get_pending_redemptions
    treats those as pending too, so historical wins get pinged once.
    """
    for record in positions.get_pending_redemptions():
        cond_id = record.get("condition_id", "")
        token_id = record.get("token_id", "")
        side = record.get("side", "?")
        shares = float(record.get("shares", 0))
        try:
            await tg.notify_redeem_needed(record, payout_usd=shares)
        except Exception as exc:
            log.warning("Telegram redeem-needed notify failed: %s", exc)
            # Don't mark notified — try again next cycle.
            continue
        positions.set_redeem_status(cond_id, token_id, "notified")
        log.info(
            "Notified user to redeem cond=%s side=%s payout=~$%.2f",
            cond_id[:10], side, shares,
        )


async def _safe_notify(where: str, exc: BaseException) -> None:
    try:
        await tg.notify_error(where, f"{type(exc).__name__}: {exc}")
    except Exception as inner:
        log.warning("Telegram error notify failed: %s", inner)


async def _enrich_with_realised_pnl(
    records: list[dict[str, Any]], user_address: str
) -> list[dict[str, Any]]:
    """For records missing pnl/won (manual UI exits), compute realised PnL by
    matching against on-chain SELL trades on the same token_id. Best-effort —
    on any failure we return the records untouched.
    """
    needs_pnl = [r for r in records if r.get("pnl") is None and r.get("token_id")]
    if not needs_pnl:
        return records
    try:
        trades = await get_user_trades(user_address)
    except Exception as exc:
        log.warning("data-api trades fetch failed; skipping PnL enrichment: %s", exc)
        return records

    # Bucket SELL trades by token_id
    sells_by_token: dict[str, list[dict]] = {}
    for t in trades:
        side = str(t.get("side") or "").upper()
        if side != "SELL":
            continue
        token_id = str(t.get("asset") or t.get("tokenId") or "")
        if not token_id:
            continue
        sells_by_token.setdefault(token_id, []).append(t)

    enriched = list(records)
    for i, r in enumerate(enriched):
        if r.get("pnl") is not None:
            continue
        token_id = str(r.get("token_id") or "")
        sells = sells_by_token.get(token_id, [])
        if not sells:
            continue
        proceeds = 0.0
        for t in sells:
            try:
                proceeds += float(t.get("price") or 0) * float(t.get("size") or 0)
            except (TypeError, ValueError):
                continue
        stake = float(r.get("stake_usd") or 0)
        pnl = proceeds - stake
        enriched[i] = {**r, "pnl": round(pnl, 4), "won": pnl > 0, "exit_kind": "ui_sell"}

    # Step 2: for records still without PnL, ask Gamma if the market resolved.
    # If yes, the position was likely redeemed (not sold) — compute PnL from
    # won/lost. Covers the common case where you redeemed in the UI.
    from polymarket_client import get_market_resolution
    for i, r in enumerate(enriched):
        if r.get("pnl") is not None:
            continue
        cond_id = r.get("condition_id")
        if not cond_id:
            continue
        try:
            info = await get_market_resolution(cond_id)
        except Exception:
            continue
        if not info or not info.get("closed"):
            continue
        winner = info.get("winner")
        shares = float(r.get("shares") or 0)
        stake = float(r.get("stake_usd") or 0)
        if winner is None:
            # Resolved invalid — assume full loss
            enriched[i] = {**r, "pnl": round(-stake, 4), "won": False, "exit_kind": "invalid"}
            continue
        won = winner == r.get("side")
        if won:
            pnl = (1 - config.POLYMARKET_FEE) * (shares - stake)
        else:
            pnl = -stake
        enriched[i] = {**r, "pnl": round(pnl, 4), "won": won, "exit_kind": "redeemed"}
    return enriched


async def _count_total_buys(user_address: str) -> int:
    """How many BUY trades has this proxy ever made on-chain? Tells the user
    whether positions.json has captured everything or whether the volume was
    unmounted at some point and earlier trades were lost from local state."""
    try:
        trades = await get_user_trades(user_address)
    except Exception:
        return -1
    return sum(1 for t in trades if str(t.get("side") or "").upper() == "BUY")


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
    # Audit position persistence at boot. If positions.json doesn't exist on
    # Railway after the first run, the volume isn't mounted (or DATA_DIR is
    # wrong) and the bot will happily re-buy the other side of an already-held
    # market on the next deploy. Make that visible immediately.
    open_now = positions.open_count()
    log.info("Loaded %d open positions from %s", open_now, config.POSITIONS_FILE)
    if not config.POSITIONS_FILE.exists():
        log.warning(
            "positions.json MISSING at %s — first run OR Railway volume not "
            "mounted. Check DATA_DIR env (should be /data on Railway) and that "
            "a volume is attached at that mount path.",
            config.POSITIONS_FILE,
        )

    # Reconcile against on-chain holdings: prune entries the bot recorded but
    # the user has since sold/redeemed via the UI. Best-effort — if data-api
    # is down we keep the local list as-is rather than wrongly nuking it.
    try:
        held = await get_onchain_position_tokens(config.POLYMARKET_FUNDER_ADDRESS)
        dropped = positions.reconcile_with_onchain(held)
        if dropped:
            log.info("Reconciled out %d stale open positions (no on-chain shares)", len(dropped))
            for d in dropped:
                log.info("  dropped: %s side=%s", (d.get("question") or "?")[:80], d.get("side"))
    except Exception as exc:
        log.warning("On-chain reconcile skipped: %s", exc)

    try:
        await tg.notify_startup(positions.list_open())
    except Exception as exc:
        log.warning("Startup Telegram notify failed: %s", exc)

    try:
        resolved_records = positions.list_resolved()
        enriched = await _enrich_with_realised_pnl(
            resolved_records, config.POLYMARKET_FUNDER_ADDRESS
        )
        local_buys = len(resolved_records) + positions.open_count()
        onchain_buys = await _count_total_buys(config.POLYMARKET_FUNDER_ADDRESS)
        await tg.notify_history(enriched, local_buys=local_buys, onchain_buys=onchain_buys)
    except Exception as exc:
        log.warning("History Telegram report failed: %s", exc)

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
