"""Binance trade WebSocket feed + rolling price buffer.

Subscribes to BTC trade events and keeps the last ~120s of (ts, price) tuples
in memory. Exposes `latest_price()` and `move_pct_over(seconds)` for the
signal layer. Auto-reconnects on disconnect with exponential backoff.
"""
from __future__ import annotations

import asyncio
import json
from collections import deque
from typing import Awaitable, Callable, Optional

import websockets

import sniper_config as scfg
from logger_setup import get_logger

log = get_logger("sniper.binance")


_BUFFER_MAX = 20000  # plenty of headroom: ~3 minutes at 100 trades/sec


class BinanceFeed:
    def __init__(self, symbol: Optional[str] = None) -> None:
        self.symbol = (symbol or scfg.SNIPER_BINANCE_SYMBOL).lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        # Each entry: (trade_timestamp_seconds, price). Binance gives ms.
        self.buffer: deque[tuple[float, float]] = deque(maxlen=_BUFFER_MAX)
        self._stop = asyncio.Event()
        self._on_tick: Optional[Callable[[], Awaitable[None]]] = None

    def set_on_tick(self, cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async callback fired after each tick is buffered."""
        self._on_tick = cb

    def stop(self) -> None:
        self._stop.set()

    def latest_price(self) -> Optional[float]:
        return self.buffer[-1][1] if self.buffer else None

    def buffer_span_seconds(self) -> float:
        if len(self.buffer) < 2:
            return 0.0
        return self.buffer[-1][0] - self.buffer[0][0]

    def move_pct_over(self, seconds: float) -> Optional[float]:
        """Percent move (signed) from `seconds` ago to now. None if the buffer
        doesn't span that far back yet.
        """
        if len(self.buffer) < 2:
            return None
        latest_ts, latest_price = self.buffer[-1]
        if latest_price <= 0:
            return None
        # Refuse a stale reading: if the buffer doesn't reach back `seconds`,
        # we don't have enough data to make the call.
        if (latest_ts - self.buffer[0][0]) < seconds:
            return None
        cutoff = latest_ts - seconds
        old_price: Optional[float] = None
        for ts, p in reversed(self.buffer):
            if ts <= cutoff:
                old_price = p
                break
        if old_price is None or old_price <= 0:
            return None
        return (latest_price - old_price) / old_price * 100.0

    async def run(self) -> None:
        backoff = 1
        while not self._stop.is_set():
            try:
                log.info("Connecting to Binance trade stream: %s", self.ws_url)
                # proxy=None bypasses HTTPS_PROXY/HTTP_PROXY entirely. The
                # OUTBOUND_PROXY env var is set for Polymarket geoblock
                # avoidance on Railway, but Binance's public market data
                # stream doesn't need it (and most cheap region-shifting
                # proxies 403 the Binance handshake).
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    proxy=None,
                ) as ws:
                    backoff = 1
                    log.info("Binance trade stream connected")
                    while not self._stop.is_set():
                        raw = await ws.recv()
                        try:
                            data = json.loads(raw)
                            price = float(data["p"])
                            ts = float(data["T"]) / 1000.0
                        except (KeyError, ValueError, TypeError):
                            continue
                        self.buffer.append((ts, price))
                        if self._on_tick is not None:
                            try:
                                await self._on_tick()
                            except Exception:
                                log.exception("on_tick callback raised")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if self._stop.is_set():
                    break
                log.warning(
                    "Binance WS error: %s; reconnecting in %ds",
                    exc, backoff,
                )
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=backoff)
                except asyncio.TimeoutError:
                    pass
                backoff = min(60, backoff * 2)
        log.info("Binance feed stopped")
