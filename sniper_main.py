"""Sniper entry point. Runs as a separate process from main.py.

Strategy (current): for every consecutive BTC Up-or-Down 5m market, buy
whichever side (UP or DOWN) has an ask sitting in the trigger window
[SNIPER_TRIGGER_PRICE - N*tick, SNIPER_TRIGGER_PRICE + N*tick] (where N =
SNIPER_TRIGGER_TOLERANCE_TICKS). If the book has moved past the window we
do NOT chase — we wait for the ask to settle back inside. The
open-position gate is per-market (condition_id), so a still-resolving
position on market A does not block sniping market B.

Tasks:
  - Binance trade feed — kept running (informational only; not used as the
    trigger). Cheap, gives us a live BTC tape in the logs.
  - WS orderbook stream (sniper_orderbook.OrderbookStream) — subscribes
    to the active market's UP+DOWN tokens, maintains live best ask in
    memory. Started in `_ensure_book_stream` and rotated on market rollover.
  - Signal poller — every SNIPER_POLL_INTERVAL_SECONDS, reads the WS-cached
    asks (falls back to REST asks on the cached BtcMarket if WS hasn't
    seeded yet) and evaluates the trigger.
  - Resolution poller — every SNIPER_RESOLUTION_POLL_SECONDS, settles closed
    positions in sniper_positions.json.
  - Heartbeat — every SNIPER_HEARTBEAT_SECONDS, logs liveness.

Risk gates enforced before every order: SNIPER_ENABLED, SNIPER_DRY_RUN,
daily loss limit, already-open position (per-market), cooldown (per-market).
"""
from __future__ import annotations

import asyncio
import signal
import time
import traceback
from typing import Any, Optional

import sniper_config as scfg
import sniper_notif as snotif
import sniper_signal
from logger_setup import get_logger
from polymarket_client import (
    GeoblockedError,
    NoFillError,
    get_best_ask,
    place_market_buy,
)
from sniper_binance import BinanceFeed
from sniper_market import BtcMarket, get_active_market_meta, get_btc_market_resolution
from sniper_orderbook import OrderbookStream
from sniper_state import SniperState, build_position_record

try:
    import sniper_redeem
except Exception as _redeem_import_exc:
    # Don't crash the whole sniper if web3 isn't installed yet — log and
    # disable auto-redeem. The trading path doesn't depend on it.
    sniper_redeem = None  # type: ignore[assignment]
    _REDEEM_IMPORT_ERROR: Optional[str] = str(_redeem_import_exc)
else:
    _REDEEM_IMPORT_ERROR = None

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
        # WS orderbook stream for the currently-active BTC 5m market. Lazily
        # (re)created when the active market's condition_id changes.
        self.book_stream: "OrderbookStream | None" = None

    async def _ensure_book_stream(self, market: BtcMarket) -> None:
        """Start a WS stream for `market` if we don't have one yet, or swap to
        a new one when the active market rolls over."""
        if (
            self.book_stream is not None
            and self.book_stream.condition_id == market.condition_id
        ):
            return
        if self.book_stream is not None:
            log.info(
                "WS orderbook: rolling over %s -> %s",
                self.book_stream.condition_id[:10], market.condition_id[:10],
            )
            await self.book_stream.stop()
            self.book_stream = None
        stream = OrderbookStream(
            up_token_id=market.up_token_id,
            down_token_id=market.down_token_id,
            condition_id=market.condition_id,
        )
        await stream.start()
        self.book_stream = stream

    async def _live_asks(
        self, market: BtcMarket
    ) -> tuple[float | None, float | None]:
        """Return (up_ask, down_ask) preferring the WS stream.

        WS is the primary source. The REST fallback is ONLY used when the
        WS task isn't connected at all — once `connected=True` we trust it
        to deliver the book snapshot within a handful of ms and just return
        (None, None) for the brief seed window. Hammering REST on every
        0.5s tick while waiting for WS to seed turned the loop into a
        15-30s-per-tick crawl when CLOB REST was also timing out.
        """
        s = self.book_stream
        if s is not None and s.connected:
            return s.latest_up_ask, s.latest_down_ask
        rest_up, rest_down = await asyncio.gather(
            get_best_ask(market.up_token_id),
            get_best_ask(market.down_token_id),
        )
        return rest_up, rest_down

    # ----- signal poller --------------------------------------------------

    async def _signal_poller(self) -> None:
        # Cooldown is tracked per-market (condition_id). When the active 5m
        # market rolls over we reset the cooldown so the new market can fire
        # immediately, independent of when the previous one was fired.
        last_fire_ts = 0.0
        last_fire_market: str | None = None
        tick = 0
        poll_interval = scfg.SNIPER_POLL_INTERVAL_SECONDS
        # Heartbeat-log every ~30s regardless of poll cadence.
        log_every_n = max(1, int(round(30.0 / max(poll_interval, 0.01))))
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

                # Reset daily-limit alert flag once a fresh UTC day rolls in.
                if self.alerted_daily_limit and not self.state.is_at_daily_limit():
                    self.alerted_daily_limit = False

                if blocked_reason is not None:
                    if tick % log_every_n == 0:
                        log.info("signal_poller blocked: %s", blocked_reason)
                    await asyncio.sleep(poll_interval)
                    continue

                # Metadata-only fetch (cached). Asks come from WS via _live_asks.
                market = await get_active_market_meta()
                if market is None:
                    if tick % log_every_n == 0:
                        log.info("signal_poller: no active BTC 5m market found")
                    await asyncio.sleep(poll_interval)
                    continue

                # Drop cooldown the moment the active market rolls over —
                # otherwise a fire late in market A would block the start of
                # market B.
                if last_fire_market is not None and last_fire_market != market.condition_id:
                    last_fire_ts = 0.0
                    last_fire_market = None

                # Start (or swap) the WS orderbook stream for this market.
                await self._ensure_book_stream(market)

                # Per-market open-position gate: skip THIS market only if we
                # already have a position on it. Open positions on previous
                # (still-resolving) markets must NOT block sniping the next one.
                if self.state.has_open_position_on(market.condition_id):
                    if tick % log_every_n == 0:
                        log.info(
                            "signal_poller: already filled on %s — waiting for resolution",
                            market.slug or market.condition_id[:10],
                        )
                    await asyncio.sleep(poll_interval)
                    continue

                # Prefer the WS-derived asks (real-time). REST is only hit
                # per-side when WS hasn't seeded that token's book yet.
                up_ask, down_ask = await self._live_asks(market)
                market.up_ask = up_ask
                market.down_ask = down_ask
                if up_ask is None or down_ask is None:
                    if tick % log_every_n == 0:
                        log.info(
                            "signal_poller: missing ask (up=%s down=%s); skipping tick",
                            up_ask, down_ask,
                        )
                    await asyncio.sleep(poll_interval)
                    continue

                decision = sniper_signal.evaluate(market, last_fire_ts)
                if tick % log_every_n == 0:
                    cooldown_remaining = max(
                        0,
                        scfg.SNIPER_COOLDOWN_SECONDS - (time.time() - last_fire_ts),
                    )
                    ws_status = (
                        "ws" if (self.book_stream is not None and self.book_stream.connected)
                        else "rest"
                    )
                    log.info(
                        "signal_poller tick=%d market=%s src=%s up=%s down=%s "
                        "trigger=%.2f cooldown=%.0fs decision=%s",
                        tick, market.slug or market.condition_id[:10], ws_status,
                        f"{up_ask:.3f}" if up_ask is not None else "none",
                        f"{down_ask:.3f}" if down_ask is not None else "none",
                        scfg.SNIPER_TRIGGER_PRICE, cooldown_remaining,
                        decision.side if decision else "none",
                    )

                if decision is not None:
                    fired = await self._maybe_fire(market, decision)
                    if fired:
                        last_fire_ts = time.time()
                        last_fire_market = market.condition_id
            except Exception:
                log.exception("signal_poller error")
            await asyncio.sleep(poll_interval)

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
        except NoFillError as exc:
            # FAK returned zero fill — book moved past our cap, or had nothing
            # at <=cap. Not a system error; just record the cooldown so we
            # don't spam retries on the same spike, and move on quietly.
            log.info("Sniper missed fill on %s: %s", decision.side, exc)
            return True
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
        # Persist neg_risk on the position so the redeemer knows which
        # contract (CTF vs NegRiskAdapter) to call after resolution.
        record["neg_risk"] = bool(market.neg_risk)
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

    # ----- on-chain redemption -------------------------------------------

    async def _redeem_loop(self) -> None:
        """Periodically submit redeem txs for resolved-won positions and
        check receipts on already-submitted ones. Disabled if
        SNIPER_AUTO_REDEEM=false or the redeem module failed to import.
        """
        if not scfg.SNIPER_AUTO_REDEEM:
            log.info("SNIPER_AUTO_REDEEM=false; skipping redeem loop")
            return
        if sniper_redeem is None:
            log.warning(
                "sniper_redeem unavailable (import failed: %s); skipping",
                _REDEEM_IMPORT_ERROR,
            )
            return

        while not _shutdown.is_set():
            try:
                await self._process_redemptions_once()
            except Exception:
                log.exception("redeem loop iteration crashed")
            try:
                await asyncio.wait_for(
                    _shutdown.wait(),
                    timeout=scfg.SNIPER_REDEEM_POLL_SECONDS,
                )
            except asyncio.TimeoutError:
                pass

    async def _process_redemptions_once(self) -> None:
        # Step 1: any in-flight (submitted but unconfirmed) txs — poll receipts.
        data = self.state._load()  # noqa: SLF001 (intentional internal access)
        for record in data.get("resolved", []):
            if record.get("redeem_status") != "submitted":
                continue
            tx_hash = record.get("redeem_tx_hash")
            if not tx_hash:
                continue
            try:
                status = await sniper_redeem.get_receipt_status(tx_hash)
            except Exception as exc:
                log.warning(
                    "receipt poll failed for %s: %s", tx_hash[:10], exc
                )
                continue
            if status is None:
                continue  # not mined yet
            cond_id = record.get("condition_id", "")
            token_id = record.get("token_id", "")
            side = record.get("side", "?")
            shares = float(record.get("shares", 0))
            if status:
                self.state.set_redeem_status(
                    cond_id, token_id, "redeemed", tx_hash=tx_hash,
                )
                try:
                    await snotif.notify_redeem_confirmed(
                        side=side, payout_usd=shares, tx_hash=tx_hash,
                    )
                except Exception:
                    log.exception("redeem_confirmed notify failed")
                log.info(
                    "Redeem confirmed: cond=%s side=%s payout=~$%.2f tx=%s",
                    cond_id[:10], side, shares, tx_hash,
                )
            else:
                attempts = int(record.get("redeem_attempts", 0))
                # Receipt status 0 = reverted on-chain. Re-flag as pending so
                # the submit-side of this loop can retry (until max attempts).
                if attempts < scfg.SNIPER_REDEEM_MAX_ATTEMPTS:
                    self.state.set_redeem_status(
                        cond_id, token_id, "pending", tx_hash=None,
                    )
                    log.warning(
                        "Redeem tx reverted (cond=%s tx=%s); will retry "
                        "(attempts=%d/%d)",
                        cond_id[:10], tx_hash, attempts,
                        scfg.SNIPER_REDEEM_MAX_ATTEMPTS,
                    )
                else:
                    self.state.set_redeem_status(
                        cond_id, token_id, "failed", tx_hash=tx_hash,
                    )
                    try:
                        await snotif.notify_redeem_failed(
                            side=side, attempts=attempts,
                            reason=f"tx {tx_hash[:10]} reverted",
                        )
                    except Exception:
                        log.exception("redeem_failed notify failed")

        # Step 2: pending positions (no tx submitted yet) — fire one tx each.
        for record in list(self.state.get_pending_redemptions()):
            cond_id = record.get("condition_id", "")
            token_id = record.get("token_id", "")
            side = record.get("side", "")
            shares = float(record.get("shares", 0))
            neg_risk = bool(record.get("neg_risk", True))  # default True (BTC 5m is neg-risk)
            attempts = int(record.get("redeem_attempts", 0))
            if attempts >= scfg.SNIPER_REDEEM_MAX_ATTEMPTS:
                self.state.set_redeem_status(
                    cond_id, token_id, "failed",
                )
                try:
                    await snotif.notify_redeem_failed(
                        side=side, attempts=attempts,
                        reason="max attempts exceeded before send",
                    )
                except Exception:
                    log.exception("redeem_failed notify failed")
                continue
            if shares <= 0 or not cond_id:
                self.state.set_redeem_status(cond_id, token_id, "skipped")
                continue
            try:
                tx_hash = await sniper_redeem.redeem_position(
                    condition_id=cond_id,
                    neg_risk=neg_risk,
                    side=side,
                    shares=shares,
                )
            except Exception as exc:
                self.state.set_redeem_status(
                    cond_id, token_id, "pending", increment_attempts=True,
                )
                log.warning(
                    "Redeem submit failed (cond=%s attempt=%d): %s",
                    cond_id[:10], attempts + 1, exc,
                )
                # Only Telegram on final failure to avoid noise.
                if attempts + 1 >= scfg.SNIPER_REDEEM_MAX_ATTEMPTS:
                    try:
                        await snotif.notify_redeem_failed(
                            side=side, attempts=attempts + 1, reason=str(exc),
                        )
                    except Exception:
                        log.exception("redeem_failed notify failed")
                continue
            self.state.set_redeem_status(
                cond_id, token_id, "submitted",
                tx_hash=tx_hash, increment_attempts=True,
            )
            try:
                await snotif.notify_redeem_submitted(
                    side=side, payout_usd=shares, tx_hash=tx_hash,
                )
            except Exception:
                log.exception("redeem_submitted notify failed")

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
        redeem_task = asyncio.create_task(
            self._redeem_loop(), name="redeem_loop"
        )

        try:
            await _shutdown.wait()
        finally:
            log.info("Shutting down sniper")
            self.feed.stop()
            if self.book_stream is not None:
                try:
                    await self.book_stream.stop()
                except Exception:
                    log.exception("book_stream stop failed")
                self.book_stream = None
            tasks = (
                feed_task, poller_task, resolution_task,
                heartbeat_task, redeem_task,
            )
            for t in tasks:
                t.cancel()
            for t in tasks:
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
