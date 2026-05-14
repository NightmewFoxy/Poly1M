"""Test ordering against an arbitrary market (bypasses the buggy esports filter).

Usage:
    python local_test_arbitrary.py <condition_id> [yes|no]

Picks the cheapest side by default. Auto-posts $1 order (no confirm prompt).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import traceback

from py_clob_client.clob_types import OrderArgs, OrderType, PartialCreateOrderOptions
from py_clob_client.order_builder.constants import BUY

# Make sure we go DIRECT, not through IPRoyal, for local testing
os.environ.pop("OUTBOUND_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("HTTP_PROXY", None)

import config
from polymarket_client import (
    _tick_size_str,
    clob,
    get_best_ask,
    get_market_meta,
    _gamma_get,
)


def fmt(obj) -> str:
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return repr(obj)


async def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python local_test_arbitrary.py <condition_id> [yes|no]")
        sys.exit(1)
    cid = sys.argv[1]
    side_hint = sys.argv[2].upper() if len(sys.argv) >= 3 else None

    print(f"Looking up market {cid[:20]}...")
    rows = await _gamma_get("/markets", {"condition_ids": cid})
    if not rows:
        print("Gamma returned no market for that condition_id")
        sys.exit(1)
    m = rows[0]
    print(f"Q: {m.get('question')}")
    print(f"   negRisk={m.get('negRisk')}  tick={m.get('orderPriceMinTickSize')}  fee={m.get('makerBaseFee')}")

    token_ids = json.loads(m["clobTokenIds"]) if isinstance(m["clobTokenIds"], str) else m["clobTokenIds"]
    prices = json.loads(m["outcomePrices"]) if isinstance(m["outcomePrices"], str) else m["outcomePrices"]
    yes_token, no_token = token_ids
    yes_price, no_price = float(prices[0]), float(prices[1])

    if side_hint == "YES":
        side, token, cheap = "YES", yes_token, yes_price
    elif side_hint == "NO":
        side, token, cheap = "NO", no_token, no_price
    elif yes_price <= no_price:
        side, token, cheap = "YES", yes_token, yes_price
    else:
        side, token, cheap = "NO", no_token, no_price

    meta = await get_market_meta(cid)
    print(f"CLOB meta: {fmt(meta)}")

    live = await get_best_ask(token)
    print(f"Live best ask for {side}: {live}")
    if live is None:
        print("No live ask; aborting")
        sys.exit(1)

    tick = meta["tick_size"]
    limit_raw = min(live + 0.02, 1.0 - tick)
    limit = round(round(limit_raw / tick) * tick, 6)
    size = max(5.0, round(1.00 / limit, 2))  # respect orderMinSize=5

    print(f"Plan: BUY {side} at ${limit:.4f} size={size} ~${limit*size:.2f}")

    args = OrderArgs(token_id=token, price=limit, size=size, side=BUY)
    options = PartialCreateOrderOptions(
        neg_risk=meta["neg_risk"],
        tick_size=_tick_size_str(tick),
    )

    print("Signing...")
    try:
        signed = clob().create_order(args, options=options)
    except Exception as exc:
        print(f"SIGN FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        sys.exit(2)
    print(f"Signed: {fmt(signed.dict() if hasattr(signed,'dict') else signed)}")

    print("Posting...")
    try:
        resp = clob().post_order(signed, OrderType.FOK)
    except Exception as exc:
        print(f"POST FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        sys.exit(2)
    print(f"POST OK: {fmt(resp)}")


if __name__ == "__main__":
    asyncio.run(main())
