"""Sniper entry point. Runs as a separate process from main.py.

Tasks:
  - Binance trade feed (sniper_binance.BinanceFeed) — populates rolling buffer
  - Signal loop — wakes on each Binance tick, evaluates fire conditions
  - Resolution poller — every SNIPER_RESOLUTION_POLL_SECONDS, settles closed
    positions in sniper_positions.json
  - Heartbeat — every SNIPER_HEARTBEAT_SECONDS, logs liveness

Risk gates enforced before every order: SNIPER_ENABLED, SNIPER_DRY_RUN,
daily loss limit, already-open position, cooldown, time-to-resolution.
"""
from __future__ import annotations

import asyncio
import signal
import time
import traceback
from typing import Any

import sniper_config as scfg
import sniper_notif as snotif
import sniper_signal
from logger_setup import get_logger
from polymarket_client import GeoblockedError, place_market_buy
from sniper_binance import BinanceFeed
from sniper_market import BtcMarketCache, get_btc_market_resolution
from sniper_state import SniperState, build_position_record

log = get_logger("sniper.main")

_shutdown = asyncio.Event()


# ---------------------------------------------------------------------------
# Signal handlers — Railway sends SIGTERM on redeploy.
# ---------------------------------------------------------------------------


def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    def _stop(*_: Any) -> None:
        log.info("Shutdown signal received")
        _shutdown.set()

    for sig_name in ("SIGTERM", "SIGINT", "SIGBREAK"):
        sig = getattr(signal, sig_name, None)
        if sig is None:
            continue
        try:
            loop.add_signal_handler(sig, _stop)
        except (NotImplementedError, RuntimeError):
            try:
                signal.signal(sig, _stop)
            except (ValueError, OSError):
                pass


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


class Sniper:
    def __init__(self) -> None:
        self.state = SniperState()
        self.market_cache = BtcMarketCache()
        self.feed = BinanceFeed()
        self.last_fire_monotonic: float | None = None
        self.signal_event = asyncio.Event()
        self.eval_lock = asyncio.Lock()
        self.alerted_daily_limit = False

    # ----- hot path -------------------------------------------------------

    async def _on_tick(self) -> None:
        # Cheap: just wake the signal loop. The loop coalesces bursts of
        # ticks into single evaluations so we never queue work behind a slow
        # HTTP call.
        self.signal_event.set()

    async def _signal_loop(self) -> None:
        while not _shutdown.is_set():
            try:
                await asyncio.wait_for(
                    self.signal_event.wait(), timeout=5.0
                )
            except asyncio.TimeoutError:
                continue
            self.signal_event.clear()
            if self.eval_lock.locked():
                # Another evaluation is already in flight; the event will
                # be re-set by the next tick anyway.
                continue
            async with self.eval_lock:
                try:
                    await self._evaluate_and_maybe_fire()
                except Exception:
                    log.exception("signal evaluation crashed")

    async def _evaluate_and_maybe_fire(self) -> None:
        # Risk gates first — cheap and they short-circuit most ticks.
        if not scfg.SNIPER_ENABLED:
            return

        if self.state.is_at_daily_limit():
            if not self.alerted_daily_limit:
                self.alerted_daily_limit = True
                await snotif.notify_daily_limit_hit(self.state.today_pnl())
            return
        # Reset the alerted flag if a new UTC day rolls in.
        if self.alerted_daily_limit and not self.state.is_at_daily_limit():
            self.alerted_daily_limit = False

        if self.state.has_open_position():
            return

        market = await self.market_cache.get()
        if market is None:
            return

        decision = await sniper_signal.evaluate(
            self.feed, market, self.last_fire_monotonic
        )
        if not decision.fire:
            return

        await self._fire(market, decision)

    async def _fire(self, market, decision) -> None:
        self.last_fire_monotonic = time.monotonic()
        log.info(
            "FIRE %s @ ~%.4f | move=%+.3f%% | fair=%.3f | edge=%.2fc | "
            "stake=$%.2f | dry_run=%s",
            decision.side, decision.live_ask, decision.move_pct,
            decision.expected_fair, decision.edge_cents,
            scfg.SNIPER_STAKE_USD, scfg.SNIPER_DRY_RUN,
        )

        if scfg.SNIPER_DRY_RUN:
            await snotif.notify_fire(
                side=decision.side,
                target_price=decision.live_ask,
                expected_fair=decision.expected_fair,
                edge_cents=decision.edge_cents,
                move_pct=decision.move_pct,
                lookback_seconds=scfg.SNIPER_LOOKBACK_SECONDS,
                stake_usd=scfg.SNIPER_STAKE_USD,
                dry_run=True,
            )
            return

        try:
            fill = await place_market_buy(
                token_id=decision.token_id,
                target_price=decision.live_ask,
                stake_usd=scfg.SNIPER_STAKE_USD,
                neg_risk=market.neg_risk,
                tick_size=market.tick_size,
            )
        except GeoblockedError as exc:
            log.error("Geoblocked: %s", exc)
            await snotif.notify_error("place_order_geoblock", str(exc))
            return
        except Exception as exc:
            log.warning("Order placement failed: %s", exc)
            await snotif.notify_error("place_order", f"{type(exc).__name__}: {exc}")
            return

        record = build_position_record(
            market_question=market.question,
            condition_id=market.condition_id,
            side=decision.side,
            token_id=decision.token_id,
            fill=fill,
            move_pct=decision.move_pct,
            edge_cents=decision.edge_cents,
            expected_fair=decision.expected_fair,
        )
        try:
            self.state.record_open(record)
        except Exception as exc:
            log.exception("Failed to persist sniper position; the order DID go through")
            await snotif.notify_error("persist_position", f"{type(exc).__name__}: {exc}")
        await snotif.notify_fire(
            side=decision.side,
            target_price=decision.live_ask,
            expected_fair=decision.expected_fair,
            edge_cents=decision.edge_cents,
            move_pct=decision.move_pct,
            lookback_seconds=scfg.SNIPER_LOOKBACK_SECONDS,
            stake_usd=fill["stake_usd"],
            fill_price=fill["limit_price"],
            dry_run=False,
        )

    # ----- background tasks ----------------------------------------------

    async def _resolution_loop(self) -> None:
        while not _shutdown.is_set():
            try:
                await self._check_resolutions_once()
            except Exception:
                log.exception("resolution check crashed")
            try:
                await asyncio.wait_for(
                    _shutdown.wait(),
                    timeout=scfg.SNIPER_RESOLUTION_POLL_SECONDS,
                )
            except asyncio.TimeoutError:
                pass

    async def _check_resolutions_once(self) -> None:
        for pos in self.state.get_open_positions():
            cid = pos.get("condition_id") or ""
            up_token = pos.get("token_id") if pos.get("side") == "UP" else None
            # We need the UP token id either way; recover it from cache if
            # this position was DOWN. The cache is keyed by current-active
            # market though, so as a fallback we fetch the market record
            # fresh via _gamma_get inside get_btc_market_resolution and
            # pass the UP token from the *position* if it matches.
            if up_token is None:
                # Position is DOWN: we don't have UP token cached on the
                # position record. The simplest recovery is to re-fetch the
                # market and let get_btc_market_resolution flip the index;
                # but get_btc_market_resolution wants up_token as an arg.
                # We work around by asking the resolver in "winner unknown"
                # mode: pass the DOWN token as up_token, then invert.
                info = await get_btc_market_resolution(cid, pos["token_id"])
                if info is not None and info.get("winner") is not None:
                    inverted = "DOWN" if info["winner"] == "UP" else "UP"
                    info = {**info, "winner": inverted}
            else:
                info = await get_btc_market_resolution(cid, up_token)

            if info is None or not info.get("closed"):
                continue

            resolved = self.state.record_resolution(
                cid, info.get("winner"), info.get("resolved_at")
            )
            if resolved is None:
                continue
            _record, won, pnl = resolved
            await snotif.notify_resolution(
                side=pos.get("side", "?"),
                won=won,
                pnl=pnl,
                today_pnl=self.state.today_pnl(),
            )

    async def _heartbeat_loop(self) -> None:
        while not _shutdown.is_set():
            try:
                await asyncio.wait_for(
                    _shutdown.wait(),
                    timeout=scfg.SNIPER_HEARTBEAT_SECONDS,
                )
            except asyncio.TimeoutError:
                pass
            if _shutdown.is_set():
                break
            latest = self.feed.latest_price()
            span = self.feed.buffer_span_seconds()
            open_n = len(self.state.get_open_positions())
            today = self.state.today_pnl()
            log.info(
                "heartbeat: btc=%s buffer_span=%.1fs open=%d today_pnl=%+.2f",
                f"{latest:.2f}" if latest is not None else "none",
                span, open_n, today,
            )

    # ----- lifecycle ------------------------------------------------------

    async def run(self) -> None:
        if not scfg.SNIPER_ENABLED:
            log.info("SNIPER_ENABLED=false; exiting")
            return

        log.info(
            "Sniper starting | dry_run=%s | stake=$%s | threshold=%s%% in %ss | "
            "cooldown=%ss | daily_limit=-$%s | min_edge=%sc",
            scfg.SNIPER_DRY_RUN, scfg.SNIPER_STAKE_USD,
            scfg.SNIPER_MOVE_THRESHOLD_PCT, scfg.SNIPER_LOOKBACK_SECONDS,
            scfg.SNIPER_COOLDOWN_SECONDS, scfg.SNIPER_DAILY_LOSS_LIMIT_USD,
            scfg.SNIPER_MIN_EDGE_CENTS,
        )

        try:
            await snotif.notify_startup()
        except Exception as exc:
            log.warning("Startup notify failed: %s", exc)

        self.feed.set_on_tick(self._on_tick)
        feed_task = asyncio.create_task(self.feed.run(), name="binance_feed")
        signal_task = asyncio.create_task(self._signal_loop(), name="signal_loop")
        resolution_task = asyncio.create_task(
            self._resolution_loop(), name="resolution_loop"
        )
        heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(), name="heartbeat"
        )

        try:
            await _shutdown.wait()
        finally:
            log.info("Shutting down sniper")
            self.feed.stop()
            for t in (feed_task, signal_task, resolution_task, heartbeat_task):
                t.cancel()
            for t in (feed_task, signal_task, resolution_task, heartbeat_task):
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass
        log.info("Sniper shut down cleanly")


async def main_async() -> None:
    sniper = Sniper()
    try:
        await sniper.run()
    except Exception:
        log.exception("Unhandled exception in sniper")
        try:
            await snotif.notify_error(
                "run", Exception(traceback.format_exc(limit=4)).__str__()
            )
        except Exception:
            pass
        raise


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
