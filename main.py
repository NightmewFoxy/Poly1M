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
from datetime import datetime, timezone
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
    get_market_game_start_times,
    get_market_meta,
    get_onchain_position_tokens,
    get_token_outcome_map,
    get_usdc_balance,
    get_user_activity,
    get_user_positions_full,
    get_user_trades,
    place_market_buy,
    place_market_sell,
)
from polymarket_client import NoFillError


def _parse_ts(val: Any) -> "datetime | None":
    """Best-effort parse of unix-seconds or ISO-8601 timestamps to UTC datetime."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        try:
            return datetime.fromtimestamp(float(val), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(val, str):
        s = val.strip()
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            pass
        try:
            return datetime.fromtimestamp(float(s), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    return None
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
    if slots == 0 and not config.ROTATION_ENABLED:
        log.info("At capacity, skipping discovery this cycle (rotation disabled)")
        return
    if slots == 0:
        log.info("At capacity but rotation enabled — researching for swap candidates")

    # Cap slots by what we can actually afford. With rotation enabled we still
    # research even at $0 balance — a SELL on a held position self-funds the
    # next BUY, so we can rotate without a positive starting balance.
    balance = await get_usdc_balance()
    if balance is None:
        log.info("Balance unknown; proceeding with position-count slots only")
    else:
        affordable_slots = int(balance // config.STAKE_USD)
        log.info("USDC=$%.2f affordable_slots=%d", balance, affordable_slots)
        if affordable_slots < slots:
            slots = affordable_slots
        if slots == 0 and not config.ROTATION_ENABLED:
            log.info(
                "Balance $%.2f < stake $%.2f; skipping discovery + research (rotation disabled)",
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

    # 5b. Rotation pass — for remaining ideas the normal loop didn't take
    # (slots full, or event already used), check whether any held position
    # has a pp gap that's at least ROTATION_MIN_PP_IMPROVEMENT smaller. If
    # so, SELL the weakest held + BUY the new one. Capped per cycle so we
    # don't churn fees.
    rotations_done = 0
    if config.ROTATION_ENABLED:
        for idea in ranked:
            if rotations_done >= config.ROTATION_MAX_PER_CYCLE:
                break
            if _shutdown.is_set():
                break
            if idea.market.question_id in used_events:
                continue
            new_gap_pp = (idea.true_prob_side - idea.price) * 100
            # Find the held position with the LOWEST pp gap that's at least
            # ROTATION_MIN_PP_IMPROVEMENT below the new idea.
            held = positions.list_open_strategy()
            target = None
            target_gap = None
            for p in held:
                try:
                    h_gap = (float(p.get("true_prob") or 0) - float(p.get("price") or 0)) * 100
                except (TypeError, ValueError):
                    continue
                if new_gap_pp - h_gap < config.ROTATION_MIN_PP_IMPROVEMENT:
                    continue
                if target is None or h_gap < target_gap:
                    target = p
                    target_gap = h_gap
            if target is None:
                continue

            ok = await _execute_rotation(target, idea, used_events)
            if ok:
                rotations_done += 1

    log.info("Cycle done; filled %d new positions, rotated %d", filled, rotations_done)


async def _execute_rotation(
    old_position: dict[str, Any],
    new_idea,
    used_events: set[str],
) -> bool:
    """Sell `old_position`, then buy `new_idea`. Returns True on full success.
    On partial failure (sell ok but buy fails), the sale's USDC stays free
    for the next cycle — no rollback attempted."""
    old_token = str(old_position.get("token_id") or "")
    if not old_token:
        return False
    old_shares = float(old_position.get("shares") or 0)
    if old_shares <= 0:
        return False

    # Get current best bid for the position to set a realistic price floor
    try:
        live_bid = await get_best_ask(old_token)  # asks for OPPOSITE token = our bid
    except Exception:
        live_bid = None
    target_sell_price = (1.0 - float(live_bid)) if live_bid is not None else 0.5
    if target_sell_price <= 0 or target_sell_price >= 1:
        target_sell_price = max(0.05, min(0.95, float(old_position.get("price") or 0.5)))

    try:
        sell_result = await place_market_sell(
            token_id=old_token,
            shares=old_shares,
            target_price=target_sell_price,
            neg_risk=bool(old_position.get("neg_risk")),
        )
    except NoFillError as exc:
        log.warning("Rotation SELL got no fill on %s: %s", old_token[:12], exc)
        return False
    except Exception as exc:
        log.warning("Rotation SELL failed on %s: %s", old_token[:12], exc)
        await _safe_notify("rotation_sell", exc)
        return False

    positions.mark_rotated_out(
        token_id=old_token,
        usd_received=sell_result["usd_received"],
        sell_price=sell_result["limit_price"],
        rotated_into_question=new_idea.market.question,
    )

    # Now place the new BUY. If it fails, the freed USDC stays for next cycle.
    live_ask = await get_best_ask(new_idea.token_id)
    if live_ask is None or live_ask > config.MAX_PRICE or live_ask < config.MIN_PRICE:
        log.warning("Rotation aborted on BUY leg: live_ask=%s out of range", live_ask)
        return False
    meta = await get_market_meta(new_idea.market.condition_id)
    if meta is None:
        log.warning("Rotation aborted on BUY leg: no CLOB meta")
        return False
    try:
        fill = await place_market_buy(
            token_id=new_idea.token_id,
            target_price=live_ask,
            stake_usd=config.STAKE_USD,
            neg_risk=meta["neg_risk"],
            tick_size=meta["tick_size"],
        )
    except NoFillError as exc:
        log.warning("Rotation BUY got no fill: %s", exc)
        return False
    except Exception as exc:
        log.warning("Rotation BUY failed: %s", exc)
        await _safe_notify("rotation_buy", exc)
        return False

    pp = potential_profit_net(fill["limit_price"], fill["stake_usd"])
    record = positions.build_position_record(new_idea, fill, pp, meta["neg_risk"])
    try:
        positions.append_open(record)
    except Exception as exc:
        log.exception("Failed to persist rotation-bought position; order did go through")
        await _safe_notify("rotation_persist", exc)

    used_events.add(new_idea.market.question_id)
    try:
        await tg.notify_rotation(old_position, new_idea, fill, sell_result)
    except Exception as exc:
        log.warning("Rotation Telegram notify failed: %s", exc)
    return True


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


async def _reconstruct_account_pnl(user_address: str) -> dict[str, Any]:
    """Pull every CLOB trade for the proxy from data-api, pair buys & sells
    per token_id, and infer redemption proceeds for fully-exited positions
    via Gamma market resolution.

    Filters out three classes of bot-error trades:
      - extreme entry prices (>=$0.95 or <=$0.05) — early calibration bugs
      - entries placed AFTER the game's start time — pre-live-check trades
      - both YES and NO bet on same market — duplicate-side bug
    Also filters to ESPORTS markets only by intersecting with conditionIds
    the bot ever recorded in positions.json (bot only opens esports markets,
    so anything outside that set is a manual UI trade).

    Returns {"closed": [...], "excluded_extreme": N, "excluded_live": N, ...}.
    """
    from polymarket_client import get_market_resolution

    # Build the bot-known set: conditionIds the bot itself ever traded.
    # Manual UI trades on non-esports markets (Bitcoin minutes, Beast Games,
    # etc.) won't be in this set and get filtered out.
    bot_known_cids = {
        str(p.get("condition_id") or "")
        for p in positions.list_open() + positions.list_resolved()
        if p.get("condition_id")
    }
    bot_known_cids.discard("")

    try:
        trades = await get_user_trades(user_address)
    except Exception as exc:
        log.warning("Account PnL: trades fetch failed: %s", exc)
        return {"closed": [], "excluded_extreme": 0, "excluded_live": 0, "excluded_both_sides": 0, "excluded_non_esports": 0}

    by_token: dict[str, dict[str, Any]] = {}
    for t in trades:
        token = str(t.get("asset") or t.get("tokenId") or "")
        if not token:
            continue
        side = str(t.get("side") or "").upper()
        try:
            price = float(t.get("price") or 0)
            size = float(t.get("size") or 0)
        except (TypeError, ValueError):
            continue
        d = by_token.setdefault(token, {
            "condition_id": (t.get("conditionId") or t.get("condition_id") or ""),
            "outcome": str(t.get("outcome") or "").upper(),
            "title": (t.get("title") or t.get("eventTitle") or t.get("question") or "")[:80],
            "buy_value": 0.0, "buy_shares": 0.0,
            "sell_value": 0.0, "sell_shares": 0.0,
            "first_price": None,
            "first_buy_ts": None,
        })
        if side == "BUY":
            d["buy_value"] += price * size
            d["buy_shares"] += size
            if d["first_price"] is None and price > 0:
                d["first_price"] = price
            # first BUY timestamp; data-api varies in field name
            ts = (
                t.get("timestamp") or t.get("time") or t.get("tradeTime")
                or t.get("createdAt") or t.get("matchTime")
            )
            if d["first_buy_ts"] is None and ts is not None:
                d["first_buy_ts"] = ts
        elif side == "SELL":
            d["sell_value"] += price * size
            d["sell_shares"] += size

    # Batch-fetch gameStartTime for live-entry filtering
    cond_ids = [d["condition_id"] for d in by_token.values() if d.get("condition_id")]
    try:
        start_times_raw = await get_market_game_start_times(list(set(cond_ids)))
    except Exception as exc:
        log.warning("gameStartTime batch fetch failed: %s", exc)
        start_times_raw = {}
    start_times: dict[str, "datetime"] = {}
    for cid, raw in start_times_raw.items():
        dt = _parse_ts(raw)
        if dt is not None:
            start_times[cid] = dt

    # Detect condition_ids where the user bet both YES and NO (bot error)
    outcomes_by_cond: dict[str, set[str]] = {}
    for d in by_token.values():
        cid = d.get("condition_id") or ""
        oc = (d.get("outcome") or "").upper()
        if cid and oc:
            outcomes_by_cond.setdefault(cid, set()).add(oc)
    both_sides_conds = {cid for cid, outs in outcomes_by_cond.items() if len(outs) > 1}

    # Apply exclusion filters
    excluded_extreme = 0
    excluded_live = 0
    excluded_both_sides = 0
    excluded_non_esports = 0
    filtered: dict[str, dict[str, Any]] = {}
    for token, d in by_token.items():
        cid = d.get("condition_id") or ""
        # Esports-only filter: must be a market the bot itself traded.
        # The bot's discover_markets queries by tag_slug=esports, so any
        # conditionId outside positions.json is a non-esports manual trade.
        if bot_known_cids and cid and cid not in bot_known_cids:
            excluded_non_esports += 1
            continue
        fp = d.get("first_price")
        if fp is not None and (fp >= 0.95 or fp <= 0.05):
            excluded_extreme += 1
            continue
        buy_dt = _parse_ts(d.get("first_buy_ts"))
        gst = start_times.get(cid)
        if buy_dt is not None and gst is not None and buy_dt >= gst:
            excluded_live += 1
            continue
        if cid and cid in both_sides_conds:
            excluded_both_sides += 1
            continue
        filtered[token] = d

    try:
        held = await get_onchain_position_tokens(user_address)
    except Exception:
        held = set()

    # Authoritative token→side map from Gamma clobTokenIds. Lets us figure
    # out if our held token was the winning side without trusting data-api's
    # per-trade `outcome` field (which in practice is often empty).
    filtered_cid_set = {d.get("condition_id") or "" for d in filtered.values() if d.get("condition_id")}
    filtered_cid_set.discard("")
    filtered_cids = list(filtered_cid_set)
    try:
        side_map = await get_token_outcome_map(filtered_cids)
    except Exception as exc:
        log.warning("Token outcome map fetch failed: %s", exc)
        side_map = {}

    # Reverse index: conditionId → list of (token_id, side) for our positions
    cid_to_tokens: dict[str, list[str]] = {}
    for tk, d in filtered.items():
        cid = d.get("condition_id") or ""
        if cid:
            cid_to_tokens.setdefault(cid, []).append(tk)

    # Primary truth source: Polymarket's own /positions with sizeThreshold=0,
    # which returns CLOSED positions too with their realizedPnl. This is what
    # the Polymarket UI uses — most reliable PnL data we can get.
    pm_pnl_by_token: dict[str, dict[str, Any]] = {}
    try:
        positions_full = await get_user_positions_full(user_address)
    except Exception as exc:
        log.warning("Polymarket /positions full fetch failed: %s", exc)
        positions_full = []
    for p in positions_full:
        token = str(p.get("asset") or p.get("tokenId") or "")
        if not token:
            continue
        # Polymarket's field naming varies; try several
        rpnl_raw = (
            p.get("realizedPnl") or p.get("realized_pnl")
            or p.get("cashPnl") or p.get("cash_pnl")
        )
        try:
            rpnl = float(rpnl_raw) if rpnl_raw is not None else None
        except (TypeError, ValueError):
            rpnl = None
        size_raw = p.get("size") or 0
        try:
            cur_size = float(size_raw)
        except (TypeError, ValueError):
            cur_size = 0.0
        pm_pnl_by_token[token] = {
            "realized_pnl": rpnl,
            "size": cur_size,
            "title": str(p.get("title") or p.get("eventTitle") or "")[:80],
            "outcome": str(p.get("outcome") or "").upper(),
        }

    # Secondary: /activity for REDEEM events. Polymarket keys these by
    # conditionId (market-level), not by token_id — redemption is a single
    # action on the whole market. So we match by conditionId + figure out
    # which of our tokens it applies to via the outcomeIndex (or by knowing
    # we only ever hold one side per market after the both-sides filter).
    redemptions_by_token: dict[str, float] = {}
    redemption_shares_by_token: dict[str, float] = {}
    activity_type_counts: dict[str, int] = {}
    sample_redeem: dict[str, Any] | None = None
    try:
        activity = await get_user_activity(user_address)
    except Exception as exc:
        log.warning("User activity fetch failed: %s", exc)
        activity = []

    def _to_float(v: Any) -> "float | None":
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    for a in activity:
        atype = str(a.get("type") or "").strip()
        activity_type_counts[atype or "<empty>"] = activity_type_counts.get(atype or "<empty>", 0) + 1
        is_redeem = "redeem" in atype.lower() or atype.lower() in ("redemption", "claim", "settle")
        if not is_redeem:
            continue
        if sample_redeem is None:
            sample_redeem = dict(a)  # capture first REDEEM for diagnostic

        # Resolve which token this redemption applies to.
        # 1) Try direct asset/token field.
        token = str(a.get("asset") or a.get("tokenId") or a.get("token") or "")

        # 2) Match by conditionId + outcomeIndex via side_map.
        cid = str(a.get("conditionId") or a.get("condition_id") or a.get("market") or "")
        if not token and cid and cid in side_map:
            outcome_idx = a.get("outcomeIndex")
            if outcome_idx is None:
                outcome_idx = a.get("outcome_index") or a.get("index")
            try:
                idx_val = int(outcome_idx) if outcome_idx is not None else None
            except (TypeError, ValueError):
                idx_val = None
            sm = side_map[cid]
            if idx_val == 0:
                token = str(sm.get("yes_token") or "")
            elif idx_val == 1:
                token = str(sm.get("no_token") or "")

        # 3) Fallback: if we hold exactly one position on this conditionId
        #    (our normal case after the both-sides filter), the redemption
        #    must be for that token regardless of outcomeIndex.
        if not token and cid and cid in cid_to_tokens:
            cands = cid_to_tokens[cid]
            if len(cands) == 1:
                token = cands[0]

        if not token:
            continue

        # Extract USDC received
        cash: "float | None" = None
        for k in (
            "usdcAmount", "usdcSize", "cashAmount", "cash", "value",
            "amount", "valueUsd", "usdValue", "totalUsd", "payout",
            "payoutAmount", "payoutValue",
        ):
            cash = _to_float(a.get(k))
            if cash is not None:
                break

        # Shares redeemed
        size = 0.0
        for k in ("size", "shares", "quantity", "amountShares", "redeemSize"):
            sv = _to_float(a.get(k))
            if sv is not None:
                size = sv
                break

        # Winner detection from outcomeIndex matching our token's side:
        # if the REDEEM is for the SAME outcomeIndex as our token, it's a
        # winning redemption (payout = size × $1). Otherwise it's a losing
        # redemption (payout = $0).
        side_of_token = ""
        if cid and cid in side_map:
            if str(token) == str(side_map[cid].get("yes_token")):
                side_of_token = "YES"
            elif str(token) == str(side_map[cid].get("no_token")):
                side_of_token = "NO"
        redeemed_idx = a.get("outcomeIndex")
        try:
            redeemed_idx_int = int(redeemed_idx) if redeemed_idx is not None else None
        except (TypeError, ValueError):
            redeemed_idx_int = None
        redeemed_side = None
        if redeemed_idx_int == 0:
            redeemed_side = "YES"
        elif redeemed_idx_int == 1:
            redeemed_side = "NO"

        # If cash is missing, infer from shares × win-indicator
        if cash is None and size > 0:
            if redeemed_side and side_of_token and redeemed_side == side_of_token:
                cash = size  # winning shares pay $1 each
            elif redeemed_side and side_of_token and redeemed_side != side_of_token:
                cash = 0.0  # losing redemption pays nothing
            else:
                cash = size  # ambiguous — assume winning (Gamma fallback will correct losses)

        if cash is not None and cash > 0:
            redemptions_by_token[token] = redemptions_by_token.get(token, 0.0) + cash
        if size > 0:
            redemption_shares_by_token[token] = redemption_shares_by_token.get(token, 0.0) + size

    def _token_side(condition_id: str, token_id: str) -> str:
        """Return 'YES' or 'NO' for this token within the market, or '' if unknown."""
        m = side_map.get(condition_id)
        if not m:
            return ""
        if str(token_id) == str(m.get("yes_token")):
            return "YES"
        if str(token_id) == str(m.get("no_token")):
            return "NO"
        return ""

    closed: list[dict[str, Any]] = []
    for token, d in filtered.items():
        if token in held:
            continue
        cid = d["condition_id"] or ""
        side = _token_side(cid, token) or d.get("outcome", "")
        net_shares = d["buy_shares"] - d["sell_shares"]
        redeem_cash = redemptions_by_token.get(token, 0.0)

        # PRIMARY: Polymarket's own realizedPnl for this token (their UI's number).
        pm_info = pm_pnl_by_token.get(token, {})
        pm_realized = pm_info.get("realized_pnl")
        pm_size = pm_info.get("size", 0.0)
        if pm_realized is not None and pm_size <= 0.01:
            pnl = float(pm_realized)
            exit_kind = "redeemed_win" if pnl > 0 else ("redeemed_loss" if pnl < 0 else "flat")
            closed.append({
                "token_id": token,
                "title": (pm_info.get("title") or d["title"] or "?"),
                "outcome": side or pm_info.get("outcome", ""),
                "entry_price": d["first_price"],
                "pnl": round(pnl, 4),
                "buy_value": round(d["buy_value"], 4),
                "sell_value": round(d["sell_value"], 4),
                "redeem_value": round(redeem_cash, 4),
                "won": pnl > 0,
                "exit_kind": exit_kind,
                "source": "pm_realized",
            })
            continue

        # FALLBACK: reconstruct from /trades + /activity + Gamma resolution.
        proceeds = d["sell_value"]
        exit_kind = "ui_sell" if d["sell_value"] > 0 else "unknown"
        if redeem_cash > 0:
            proceeds += redeem_cash
            exit_kind = "redeemed_win"
        redeem_shares = redemption_shares_by_token.get(token, 0.0)
        remaining = net_shares - redeem_shares
        if remaining > 0.01 and redeem_cash == 0 and cid:
            try:
                info = await get_market_resolution(cid)
            except Exception:
                info = None
            if info and info.get("closed"):
                winner = info.get("winner")
                if winner and side:
                    if winner == side:
                        proceeds += remaining * 1.0
                        exit_kind = "redeemed_win"
                    else:
                        exit_kind = "redeemed_loss"
                else:
                    exit_kind = "resolved_unknown"

        pnl = proceeds - d["buy_value"]
        closed.append({
            "token_id": token,
            "title": d["title"] or "?",
            "outcome": side,
            "entry_price": d["first_price"],
            "pnl": round(pnl, 4),
            "buy_value": round(d["buy_value"], 4),
            "sell_value": round(d["sell_value"], 4),
            "redeem_value": round(redeem_cash, 4),
            "won": pnl > 0,
            "exit_kind": exit_kind,
            "source": "reconstructed",
        })
    # Debug: log how many came from each source so we can see if Polymarket's
    # realizedPnl actually populated, or if we fell back to reconstruction.
    by_source: dict[str, int] = {}
    for c in closed:
        s = c.get("source", "?")
        by_source[s] = by_source.get(s, 0) + 1
    log.info("Account PnL sources: %s", by_source)
    pm_with_realized = sum(
        1 for v in pm_pnl_by_token.values() if v.get("realized_pnl") is not None
    )
    log.info(
        "Polymarket /positions returned %d rows, %d with realizedPnl; /activity returned %d events",
        len(pm_pnl_by_token), pm_with_realized, len(activity),
    )
    # Sample REDEEM record keys+values so we can see Polymarket's actual schema
    sample_redeem_summary = ""
    if sample_redeem:
        items = list(sample_redeem.items())[:12]  # first 12 fields
        sample_redeem_summary = ", ".join(f"{k}={str(v)[:30]}" for k, v in items)

    return {
        "closed": closed,
        "excluded_extreme": excluded_extreme,
        "excluded_live": excluded_live,
        "excluded_both_sides": excluded_both_sides,
        "excluded_non_esports": excluded_non_esports,
        "debug_sources": by_source,
        "debug_pm_rows": len(pm_pnl_by_token),
        "debug_pm_with_pnl": pm_with_realized,
        "debug_activity_events": len(activity),
        "debug_activity_types": activity_type_counts,
        "debug_redemptions_matched": len(redemptions_by_token),
        "debug_sample_redeem": sample_redeem_summary,
    }


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

    # Stamp bot_error=True on records matching known error patterns so every
    # downstream report filters them out automatically (extreme entry price,
    # live-game entries, both-sides bets on the same condition_id).
    try:
        all_cond_ids = [
            p.get("condition_id")
            for p in positions.list_open() + positions.list_resolved()
            if p.get("condition_id")
        ]
        raw_starts = await get_market_game_start_times(list(set(all_cond_ids)))
        parsed_starts: dict[str, "datetime"] = {}
        for cid, raw in raw_starts.items():
            dt = _parse_ts(raw)
            if dt is not None:
                parsed_starts[cid] = dt
        flagged = positions.mark_bot_errors(game_start_times=parsed_starts)
        if flagged:
            log.info("Flagged %d positions as bot_error", flagged)
    except Exception as exc:
        log.warning("Bot-error flagging skipped: %s", exc)

    try:
        await tg.notify_startup(positions.list_open_strategy())
    except Exception as exc:
        log.warning("Startup Telegram notify failed: %s", exc)

    # One-shot per-position review: resend the TRADE EXECUTED format for any
    # open position that hasn't had its review message emitted yet. Lets the
    # user spot thin-edge trades currently held and manually exit them.
    for p in positions.list_open_strategy():
        if p.get("details_sent"):
            continue
        try:
            await tg.notify_open_position_details(p)
            positions.mark_details_sent(p.get("token_id") or "")
        except Exception as exc:
            log.warning("Open-position detail notify failed: %s", exc)

    try:
        resolved_records = positions.list_resolved_strategy()
        enriched = await _enrich_with_realised_pnl(
            resolved_records, config.POLYMARKET_FUNDER_ADDRESS
        )
        local_buys = len(resolved_records) + len(positions.list_open_strategy())
        onchain_buys = await _count_total_buys(config.POLYMARKET_FUNDER_ADDRESS)
        await tg.notify_history(enriched, local_buys=local_buys, onchain_buys=onchain_buys)
    except Exception as exc:
        log.warning("History Telegram report failed: %s", exc)

    # Full lifetime PnL reconstructed straight from on-chain /trades
    # (positions.json-independent). Answers "what's my real account history".
    try:
        account_data = await _reconstruct_account_pnl(config.POLYMARKET_FUNDER_ADDRESS)
        await tg.notify_account_pnl(
            account_data.get("closed", []),
            excluded_extreme=account_data.get("excluded_extreme", 0),
            excluded_live=account_data.get("excluded_live", 0),
            excluded_both_sides=account_data.get("excluded_both_sides", 0),
            excluded_non_esports=account_data.get("excluded_non_esports", 0),
            debug_sources=account_data.get("debug_sources", {}),
            debug_pm_rows=account_data.get("debug_pm_rows", 0),
            debug_pm_with_pnl=account_data.get("debug_pm_with_pnl", 0),
            debug_activity_events=account_data.get("debug_activity_events", 0),
            debug_activity_types=account_data.get("debug_activity_types", {}),
            debug_redemptions_matched=account_data.get("debug_redemptions_matched", 0),
            debug_sample_redeem=account_data.get("debug_sample_redeem", ""),
        )
    except Exception as exc:
        log.warning("Account PnL Telegram report failed: %s", exc)

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
