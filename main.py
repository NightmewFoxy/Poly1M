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
    get_usdc_balance,
    place_market_buy,
)
from research import TradeIdea, potential_profit_net, research_and_score

try:
    import redeem
except Exception as _redeem_import_exc:
    # Don't crash the whole bot if web3/eth_account aren't importable — log
    # and disable auto-redeem. The trading path doesn't depend on it.
    redeem = None  # type: ignore[assignment]
    _REDEEM_IMPORT_ERROR: str | None = str(_redeem_import_exc)
else:
    _REDEEM_IMPORT_ERROR = None

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

    # 1b. Auto-redeem any winning positions so the USDC lands in the wallet
    # before this same cycle decides how many new positions it can afford.
    # Includes backfill for resolved wins persisted before this feature shipped
    # (records with no redeem_status field — get_pending_redemptions treats
    # them as pending).
    try:
        await _process_redemptions()
    except Exception as exc:
        log.exception("Redeem processing failed")
        await _safe_notify("redeem", exc)

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


async def _process_redemptions() -> None:
    """Submit on-chain redeem txs for resolved-won positions; wait briefly
    for confirmation so the freed USDC can be used by the same cycle.

    Two passes:
      1. Receipts for txs already submitted in prior cycles (or earlier in
         this cycle). On confirm: persist 'redeemed', Telegram, log payout.
      2. Pending wins (won + no tx yet). Submit one tx each, wait up to
         REDEEM_CONFIRMATION_WAIT_SECONDS for receipts, notify the ones
         that confirmed. Anything still pending stays as 'submitted' and
         the NEXT cycle's pass 1 will pick it up — no Telegram noise on
         interim states.
    """
    if not config.AUTO_REDEEM_ENABLED:
        return
    if redeem is None:
        log.warning(
            "redeem module unavailable (import failed: %s); skipping auto-redeem",
            _REDEEM_IMPORT_ERROR,
        )
        return

    # Pass 1: poll receipts for previously-submitted txs.
    for record in positions.get_submitted_redemptions():
        tx_hash = record.get("redeem_tx_hash")
        if not tx_hash:
            continue
        try:
            status = await redeem.get_receipt_status(tx_hash)
        except Exception as exc:
            log.warning("receipt poll failed for %s: %s", tx_hash[:10], exc)
            continue
        if status is None:
            continue  # not mined yet
        await _finalise_redeem_receipt(record, tx_hash, status)

    # Pass 2: submit txs for resolved-won records with no tx yet.
    pending = positions.get_pending_redemptions()
    just_submitted: list[tuple[dict, str]] = []
    for record in pending:
        cond_id = record.get("condition_id", "")
        token_id = record.get("token_id", "")
        side = record.get("side", "")
        shares = float(record.get("shares", 0))
        # Default neg_risk=True for legacy records that pre-date the field —
        # most Polymarket binary markets are neg-risk, and an AlreadyRedeemed
        # revert on the wrong contract is recoverable (we mark it externally
        # redeemed and stop trying).
        neg_risk = bool(record.get("neg_risk", True))
        attempts = int(record.get("redeem_attempts", 0))
        if attempts >= config.REDEEM_MAX_ATTEMPTS:
            positions.set_redeem_status(cond_id, token_id, "failed")
            log.warning(
                "Redeem max attempts reached for cond=%s side=%s; marking failed",
                cond_id[:10], side,
            )
            continue
        if shares <= 0 or not cond_id:
            positions.set_redeem_status(cond_id, token_id, "skipped")
            continue
        try:
            tx_hash = await redeem.redeem_position(
                condition_id=cond_id,
                neg_risk=neg_risk,
                side=side,
                shares=shares,
            )
        except redeem.AlreadyRedeemedError:
            positions.set_redeem_status(cond_id, token_id, "redeemed-external")
            log.info(
                "Skipping redeem (already redeemed externally): cond=%s side=%s",
                cond_id[:10], side,
            )
            continue
        except Exception as exc:
            positions.set_redeem_status(
                cond_id, token_id, "pending", increment_attempts=True,
            )
            log.warning(
                "Redeem submit failed (cond=%s attempt=%d): %s",
                cond_id[:10], attempts + 1, exc,
            )
            continue
        positions.set_redeem_status(
            cond_id, token_id, "submitted",
            tx_hash=tx_hash, increment_attempts=True,
        )
        just_submitted.append((record, tx_hash))

    # Wait briefly so newly-submitted txs can confirm within this cycle.
    # Polygon block time is ~2s; legitimate redeems usually confirm in 5-15s.
    if just_submitted:
        deadline = asyncio.get_event_loop().time() + config.REDEEM_CONFIRMATION_WAIT_SECONDS
        still_waiting = list(just_submitted)
        while still_waiting and asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(3)
            next_round: list[tuple[dict, str]] = []
            for record, tx_hash in still_waiting:
                try:
                    status = await redeem.get_receipt_status(tx_hash)
                except Exception as exc:
                    log.warning("receipt poll failed for %s: %s", tx_hash[:10], exc)
                    next_round.append((record, tx_hash))
                    continue
                if status is None:
                    next_round.append((record, tx_hash))
                    continue
                await _finalise_redeem_receipt(record, tx_hash, status)
            still_waiting = next_round
        if still_waiting:
            log.info(
                "%d redeem tx(s) still unconfirmed after %ds; will pick up "
                "the receipt(s) next cycle",
                len(still_waiting), config.REDEEM_CONFIRMATION_WAIT_SECONDS,
            )


async def _finalise_redeem_receipt(record: dict, tx_hash: str, success: bool) -> None:
    cond_id = record.get("condition_id", "")
    token_id = record.get("token_id", "")
    side = record.get("side", "?")
    shares = float(record.get("shares", 0))
    if success:
        positions.set_redeem_status(cond_id, token_id, "redeemed", tx_hash=tx_hash)
        # Gross payout = shares of the winning side (each pays $1).
        log.info(
            "Redeem confirmed: cond=%s side=%s payout=~$%.2f tx=%s",
            cond_id[:10], side, shares, tx_hash,
        )
        try:
            await tg.notify_redeem(record, payout_usd=shares, tx_hash=tx_hash)
        except Exception as exc:
            log.warning("Telegram redeem notify failed: %s", exc)
    else:
        attempts = int(record.get("redeem_attempts", 0))
        if attempts < config.REDEEM_MAX_ATTEMPTS:
            # Re-flag as pending so the next pass tries again with a fresh nonce.
            positions.set_redeem_status(cond_id, token_id, "pending", tx_hash=None)
            log.warning(
                "Redeem tx reverted (cond=%s tx=%s); will retry "
                "(attempts=%d/%d)",
                cond_id[:10], tx_hash, attempts, config.REDEEM_MAX_ATTEMPTS,
            )
        else:
            positions.set_redeem_status(cond_id, token_id, "failed", tx_hash=tx_hash)
            log.error(
                "Redeem permanently failed after %d attempts: cond=%s tx=%s",
                attempts, cond_id[:10], tx_hash,
            )


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

    try:
        await tg.notify_startup(open_now)
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
