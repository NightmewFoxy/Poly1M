"""Railway entry: runs the esports bot AND the BTC 5m sniper in one process.

Railway services run a single startCommand, so we drive both `main.main_async`
(esports research/trade loop) and `sniper_main.main_async` (BTC 5m sniper)
as sibling asyncio tasks. Each bot already manages its own `_shutdown` event
and its own state file (positions.json vs. sniper_positions.json), so they
don't share anything except the proxy and Polymarket credentials.

If one bot crashes, the other keeps running. SIGTERM (Railway redeploy)
shuts both down cleanly.
"""
from __future__ import annotations

import asyncio
import signal
import traceback
from typing import Any

import main as esports
import sniper_main as sniper
from logger_setup import get_logger

log = get_logger("railway_main")


def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    def _stop(*_: Any) -> None:
        log.info("Shutdown signal received; stopping esports + sniper")
        esports._shutdown.set()
        sniper._shutdown.set()

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


async def _supervise(name: str, coro_factory) -> None:
    """Run one bot's main_async. If it crashes, log + keep the other alive."""
    try:
        await coro_factory()
    except asyncio.CancelledError:
        raise
    except Exception:
        log.error(
            "%s crashed — the other bot continues. Traceback:\n%s",
            name, traceback.format_exc(limit=8),
        )


async def main_async() -> None:
    log.info("railway_main: starting esports + BTC sniper in one process")
    await asyncio.gather(
        _supervise("esports", esports.main_async),
        _supervise("sniper", sniper.main_async),
    )
    log.info("railway_main: both bots stopped")


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
