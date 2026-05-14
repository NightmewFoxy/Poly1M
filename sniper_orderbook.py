"""Polymarket CLOB WebSocket orderbook stream for the sniper.

REST polling caps reaction time at the poll interval. On a fast 5-min market
the ask can step through the trigger between two polls and the bot never
observes it. This module subscribes to the CLOB `market` channel for the
active BTC 5m market's UP and DOWN tokens and maintains the current best ask
in memory; the signal poller reads from this cache.

Endpoint: wss://ws-subscriptions-clob.polymarket.com/ws/market
Subscribe: {"type":"Market","assets_ids":["<up>","<down>"]}
Event types we care about:
  book          full snapshot for one asset_id
  price_change  list of price-level deltas for one asset_id

Connection routing: bypasses HTTPS_PROXY (iproyal) with `proxy=None`. The
Polymarket geoblock applies to the *trading* CLOB REST API; the public
market-data WS endpoint accepts handshakes from any IP, including Railway.
We saw iproyal start returning HTTP 504 on the WS upgrade intermittently,
so going direct removes that single point of failure from the live-asks
path. REST trading still goes via iproyal (geoblock-protected).
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

import websockets

from logger_setup import get_logger

log = get_logger("sniper.orderbook")

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


class OrderbookStream:
    """Live best-ask cache for one BTC 5m market (UP + DOWN tokens)."""

    def __init__(
        self,
        up_token_id: str,
        down_token_id: str,
        condition_id: str,
    ) -> None:
        self.up_token_id = up_token_id
        self.down_token_id = down_token_id
        self.condition_id = condition_id
        # price (float) -> size (float). Best ask = min(keys).
        self._up_asks: dict[float, float] = {}
        self._down_asks: dict[float, float] = {}
        self._stop = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        self._connected = False
        self._last_event_ts: float = 0.0
        # Track first-book diagnostic so we can confirm data is flowing.
        self._frames_seen = 0
        self._seeded_up = False
        self._seeded_down = False

    # -------- accessors --------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_event_age(self) -> float:
        """Seconds since last message; inf if no message yet."""
        if self._last_event_ts == 0.0:
            return float("inf")
        return time.monotonic() - self._last_event_ts

    @property
    def latest_up_ask(self) -> Optional[float]:
        d = self._up_asks
        return min(d) if d else None

    @property
    def latest_down_ask(self) -> Optional[float]:
        d = self._down_asks
        return min(d) if d else None

    # -------- lifecycle --------------------------------------------------

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(
                self._run(), name=f"ws_orderbook_{self.condition_id[:8]}"
            )

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None
        self._connected = False

    # -------- internals --------------------------------------------------

    async def _run(self) -> None:
        backoff = 1
        while not self._stop.is_set():
            try:
                # proxy=None: bypass iproyal. Market-data WS is not geoblocked
                # and iproyal has been returning 504 on the WS upgrade.
                async with websockets.connect(
                    WS_URL,
                    ping_interval=20,
                    ping_timeout=10,
                    open_timeout=15,
                    proxy=None,
                ) as ws:
                    sub = {
                        "type": "Market",
                        "assets_ids": [self.up_token_id, self.down_token_id],
                    }
                    await ws.send(json.dumps(sub))
                    self._connected = True
                    backoff = 1
                    log.info(
                        "WS orderbook connected (market=%s up=%s down=%s)",
                        self.condition_id[:10],
                        self.up_token_id[:8], self.down_token_id[:8],
                    )
                    while not self._stop.is_set():
                        raw = await ws.recv()
                        self._handle_frame(raw)
                        self._last_event_ts = time.monotonic()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if self._stop.is_set():
                    break
                self._connected = False
                log.warning(
                    "WS orderbook error (%s): %s; reconnecting in %ds",
                    self.condition_id[:10], exc, backoff,
                )
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=backoff)
                except asyncio.TimeoutError:
                    pass
                backoff = min(60, backoff * 2)
        self._connected = False

    def _handle_frame(self, raw) -> None:
        self._frames_seen += 1
        # On the very first frame, log the raw payload (truncated) so we can
        # see what Polymarket is actually sending if seeding stalls.
        if self._frames_seen == 1:
            preview = raw if isinstance(raw, (str, bytes)) else repr(raw)
            if isinstance(preview, bytes):
                preview = preview.decode("utf-8", "replace")
            log.info(
                "WS first frame (market=%s): %s",
                self.condition_id[:10], preview[:300],
            )
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            return
        # Polymarket can send a bare object OR a JSON array of objects per frame.
        msgs = payload if isinstance(payload, list) else [payload]
        for m in msgs:
            if not isinstance(m, dict):
                continue
            self._apply(m)

    def _apply(self, m: dict) -> None:
        event_type = str(m.get("event_type") or m.get("type") or "").lower()
        asset_id = str(m.get("asset_id") or m.get("assetId") or "")
        if not asset_id or event_type in ("", "pong"):
            return
        if asset_id == self.up_token_id:
            target_name = "up"
        elif asset_id == self.down_token_id:
            target_name = "down"
        else:
            return

        if event_type == "book":
            # Full snapshot — rebuild atomically (swap dict, never empty mid-read).
            new_asks: dict[float, float] = {}
            for entry in m.get("asks", []) or []:
                try:
                    p = float(entry["price"])
                    s = float(entry["size"])
                except (KeyError, ValueError, TypeError):
                    continue
                if s > 0:
                    new_asks[p] = s
            if target_name == "up":
                self._up_asks = new_asks
                if not self._seeded_up:
                    self._seeded_up = True
                    log.info(
                        "WS UP book seeded (market=%s best_ask=%s levels=%d)",
                        self.condition_id[:10],
                        f"{min(new_asks):.3f}" if new_asks else "none",
                        len(new_asks),
                    )
            else:
                self._down_asks = new_asks
                if not self._seeded_down:
                    self._seeded_down = True
                    log.info(
                        "WS DOWN book seeded (market=%s best_ask=%s levels=%d)",
                        self.condition_id[:10],
                        f"{min(new_asks):.3f}" if new_asks else "none",
                        len(new_asks),
                    )
            return

        if event_type in ("price_change", "pricechange"):
            target = self._up_asks if target_name == "up" else self._down_asks
            for change in m.get("changes", []) or []:
                if str(change.get("side", "")).lower() != "sell":
                    continue
                try:
                    p = float(change["price"])
                    s = float(change["size"])
                except (KeyError, ValueError, TypeError):
                    continue
                if s == 0:
                    target.pop(p, None)
                else:
                    target[p] = s
            return

        # Other event_types (last_trade_price, tick_size_change) — ignore.
