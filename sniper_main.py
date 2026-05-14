"""Sniper entry point. Runs as a separate process from main.py.

Strategy (current): buy whichever side (UP or DOWN) of the active BTC 5m
Polymarket market first reaches an ask of SNIPER_TRIGGER_PRICE. Polymarket-
only trigger — no Binance dependency, no edge math.

Tasks:
  - Binance trade feed — kept running (informational only; not used as the
    trigger). Cheap, gives us a live BTC tape in the logs.
  - Signal poller — every 2 seconds, evaluates the price trigger via
    get_active_market() + sniper_signal.evaluate().
  - Resolution poller — every SNIPER_RESOLUTION_POLL_SECONDS, settles closed
    positions in sniper_positions.json.
  - Heartbeat — every SNIPER_HEARTBEAT_SECONDS, logs liveness.

Risk gates enforced before every order: SNIPER_ENABLED, SNIPER_DRY_RUN,
daily loss limit, already-open position, cooldown.
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
from sniper_market import BtcMarket, get_active_market, get_btc_market_resolution
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
        self.feed = BinanceFeed()
        self.alerted_daily_limit = False

    # ----- signal poller --------------------------------------------------

    async def _signal_poller(self) -> None:
        last_fire_ts = 0.0
        tick = 0
        while not _shutdown.is_set():
            tick += 1
            try:
                # Risk gates first — cheap, so they short-circuit before the
                # orderbook HTTP fetch in get_active_market().
                blocked_reason: str | None = None
                if not scfg.SNIPER_ENABLED:
                    blocked_reason = "SNIPER_ENABLED=false"
                elif self.state.is_at_daily_limit():
                    blocked_reason = (
                        f"daily_limit_hit pnl={self.state.today_pnl():+.2f}"
                    )
                    if not self.alerted_daily_limit:
                        self.alerted_daily_limit = True
                        try:
                            await snotif.notify_daily_limit_hit(
                                self.state.today_pnl()
                            )
                        except Exception:
                            log.exception("daily_limit notify failed")
                elif self.state.has_open_position():
                    blocked_reason = "open_position"

                # Reset daily-limit alert flag once a fresh UTC day rolls in.
                if self.alerted_daily_limit and not self.state.is_at_daily_limit():
                    self.alerted_daily_limit = False

                if blocked_reason is not None:
                    if tick % 15 == 0:
                        log.info("signal_poller blocked: %s", blocked_reason)
                    await asyncio.sleep(2)
                    continue

                market = await get_active_market()
                if market is None:
                    if tick % 15 == 0:
                        log.info("signal_poller: no active BTC 5m market found")
                    await asyncio.sleep(2)
                    continue

                decision = sniper_signal.evaluate(market, last_fire_ts)
                if tick % 15 == 0:
                    cooldown_remaining = max(
                        0,
                        scfg.SNIPER_COOLDOWN_SECONDS - (time.time() - last_fire_ts),
                    )
                    log.info(
                        "signal_poller tick=%d up=%.3f down=%.3f trigger=%.2f "
                        "cooldown=%.0fs decision=%s",
                        tick, market.up_ask, market.down_ask,
                        scfg.SNIPER_TRIGGER_PRICE, cooldown_remaining,
                        decision.side if decision else "none",
                    )

                if decision is not None:
                    fired = await self._maybe_fire(market, decision)
                    if fired:
                        last_fire_ts = time.time()
            except Exception:
                log.exception("signal_poller error")
            await asyncio.sleep(2)

    # ----- order placement ------------------------------------------------

    async def _maybe_fire(self, market: BtcMarket, decision) -> bool:
        """Place the order (or log dry-run). Returns True if a fire happened
        so the caller updates last_fire_ts (starts the cooldown window).
        """
        log.info(
            "FIRE %s @ %.4f | trigger=%.2f | stake=$%.2f | dry_run=%s",
            decision.side, decision.price, scfg.SNIPER_TRIGGER_PRICE,
            scfg.SNIPER_STAKE_USD, scfg.SNIPER_DRY_RUN,
        )

        if scfg.SNIPER_DRY_RUN:
            try:
                await snotif.notify_would_fire(
                    side=decision.side,
                    price=decision.price,
                    trigger=scfg.SNIPER_TRIGGER_PRICE,
                    stake_usd=scfg.SNIPER_STAKE_USD,
                )
            except Exception:
                log.exception("dry-run notify failed")
            return True

        try:
            fill = await place_market_buy(
                token_id=decision.token_id,
                target_price=decision.price,
                stake_usd=scfg.SNIPER_STAKE_USD,
                neg_risk=market.neg_risk,
                tick_size=market.tick_size,
                max_slippage_ticks=scfg.SNIPER_MAX_SLIPPAGE_TICKS,
            )
        except GeoblockedError as exc:
            log.error("Geoblocked: %s", exc)
            try:
                await snotif.notify_error("place_order_geoblock", str(exc))
            except Exception:
                log.exception("geoblock notify failed")
            return False
        except Exception as exc:
            log.warning("Order placement failed: %s", exc)
            try:
                await snotif.notify_error(
                    "place_order", f"{type(exc).__name__}: {exc}"
                )
            except Exception:
                log.exception("error notify failed")
            return False

        record = build_position_record(
            market_question=market.question,
            condition_id=market.condition_id,
            side=decision.side,
            token_id=decision.token_id,
            fill=fill,
            move_pct=0.0,
            edge_cents=0.0,
            expected_fair=None,
        )
        try:
            self.state.record_open(record)
        except Exception as exc:
            log.exception("Failed to persist sniper position; the order DID go through")
            try:
                await snotif.notify_error(
                    "persist_position", f"{type(exc).__name__}: {exc}"
                )
            except Exception:
                log.exception("persist error notify failed")

        try:
            await snotif.notify_fire(
                side=decision.side,
                price=fill["limit_price"],
                trigger=scfg.SNIPER_TRIGGER_PRICE,
                stake_usd=fill["stake_usd"],
            )
        except Exception:
            log.exception("fire notify failed")
        return True

    # ----- resolution polling --------------------------------------------

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
            if up_token is None:
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
            try:
                await snotif.notify_resolution(
                    side=pos.get("side", "?"),
                    won=won,
                    pnl=pnl,
                    today_pnl=self.state.today_pnl(),
                )
            except Exception:
                log.exception("resolution notify failed")

    # ----- heartbeat -----------------------------------------------------

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
            "Sniper starting | dry_run=%s | stake=$%s | trigger=$%.2f | "
            "cooldown=%ss | daily_limit=-$%s",
            scfg.SNIPER_DRY_RUN, scfg.SNIPER_STAKE_USD,
            scfg.SNIPER_TRIGGER_PRICE, scfg.SNIPER_COOLDOWN_SECONDS,
            scfg.SNIPER_DAILY_LOSS_LIMIT_USD,
        )

        try:
            await snotif.notify_startup()
        except Exception as exc:
            log.warning("Startup notify failed: %s", exc)

        # Binance feed is kept running for the live BTC tape (heartbeat
        # surfaces it). The signal layer no longer consumes its events.
        feed_task = asyncio.create_task(self.feed.run(), name="binance_feed")
        poller_task = asyncio.create_task(
            self._signal_poller(), name="signal_poller"
        )
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
            for t in (feed_task, poller_task, resolution_task, heartbeat_task):
                t.cancel()
            for t in (feed_task, poller_task, resolution_task, heartbeat_task):
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
