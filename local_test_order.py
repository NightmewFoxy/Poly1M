"""Local order-signing test. Run from your home machine (no proxy needed, no Claude credits used).

What it does:
  1. Pull current esports markets from Gamma
  2. Pick the first tradeable one
  3. Ask CLOB for its canonical neg_risk + tick_size
  4. Build and sign a real $1 BUY order on the cheaper side
  5. Print the signed payload (so we can inspect it)
  6. Ask before posting -- you must type 'yes' for it to actually trade
  7. If posted, prints the full response or the error

If posting fails, the error message is what we need to fix the bot. Paste the full
traceback back into chat.

Run:
    python local_test_order.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import traceback

from py_clob_client_v2.clob_types import OrderArgs, OrderType, PartialCreateOrderOptions
from py_clob_client_v2.order_builder.constants import BUY

import config
from polymarket_client import (
    _tick_size_str,
    clob,
    discover_markets,
    filter_esports_tradeable,
    get_best_ask,
    get_market_meta,
)


def fmt(obj) -> str:
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return repr(obj)


async def main() -> None:
    print("Poly1M local order-signing test\n")

    markets = await discover_markets()
    tradeable = filter_esports_tradeable(markets)
    if not tradeable:
        print("No tradeable esports markets right now. Try again later.")
        return

    # Pick the highest-volume one for liquidity
    tradeable.sort(key=lambda m: -m.volume_usd)
    m = tradeable[0]

    print(f"Market:  {m.question}")
    print(f"Gamma:   neg_risk={m.neg_risk}  tick_size={m.tick_size}  vol=${m.volume_usd:,.0f}")

    meta = await get_market_meta(m.condition_id)
    if meta is None:
        print("CLOB get_market failed; aborting.")
        return
    print(f"CLOB:    {fmt(meta)}\n")

    # Trade the cheaper side, $1 stake
    if m.yes_price <= m.no_price:
        side = "YES"
        token = m.yes_token_id
        cheap = m.yes_price
    else:
        side = "NO"
        token = m.no_token_id
        cheap = m.no_price

    live = await get_best_ask(token)
    if live is None:
        print("No live ask; aborting.")
        return

    tick = meta["tick_size"]
    limit_raw = min(live + 0.02, 0.99)
    limit = round(round(limit_raw / tick) * tick, 6)
    size = max(1.0, round(1.00 / limit, 2))  # ~$1 worth, minimum 1 share

    print(f"Plan:    BUY {side} on {m.condition_id[:10]}... at ${limit:.4f}, "
          f"size={size}, ~${limit * size:.2f} stake")

    args = OrderArgs(token_id=token, price=limit, size=size, side=BUY)
    options = PartialCreateOrderOptions(
        neg_risk=meta["neg_risk"],
        tick_size=_tick_size_str(tick),
    )
    print(f"Options: neg_risk={meta['neg_risk']}, tick_size={_tick_size_str(tick)}\n")

    # Step 1: sign locally
    print("Signing order...")
    try:
        signed = clob().create_order(args, options=options)
    except Exception as exc:
        print(f"\nSIGN FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return
    print("Signed OK.")
    try:
        print(f"Signed payload: {fmt(signed.dict() if hasattr(signed, 'dict') else signed)}")
    except Exception:
        print(f"Signed payload (repr): {signed!r}")

    # Step 2: confirm before posting
    print(f"\nAbout to POST this $1 order. Type 'yes' to proceed (anything else aborts):")
    answer = input().strip().lower()
    if answer != "yes":
        print("Aborted; no order posted.")
        return

    # Step 3: post
    print("\nPosting order...")
    try:
        resp = clob().post_order(signed, OrderType.FOK)
    except Exception as exc:
        print(f"\nPOST FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        sys.exit(2)
    print(f"POST OK. Response: {fmt(resp)}")


if __name__ == "__main__":
    asyncio.run(main())
