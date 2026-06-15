"""Read-only probe: is there ANY fee-free binary-merge arb flow?

Loops the real scanner path (scan_binary_merge -> confirm_hits) for N minutes,
looks up each confirmed hit's CLOB taker fee, and counts only the fee-free ones
— i.e. exactly what the now-fee-aware executor would actually be allowed to
trade. Answers the question the v2 report never did: net of fees, is there
anything here, or was it all in the fee-walled markets?

No orders, no wallet. Fees come straight from the CLOB REST endpoint and are
cached per market for the run. Writes per-cycle rows to data/zero_fee_probe.jsonl
and prints a summary at the end. This file is SEPARATE from the v1/v2 arb logs
on purpose — do not mix.

Usage:
  python probe_zero_fee.py --minutes 30 --interval 60
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import httpx

import arb_scanner
import config

CLOB = "https://clob.polymarket.com"
H = httpx.Client(trust_env=False, timeout=30)
OUT = config.DATA_DIR / "zero_fee_probe.jsonl"

_fee_cache: dict[str, float | None] = {}


def taker_fee(cond: str) -> float | None:
    if not cond:
        return None
    if cond in _fee_cache:
        return _fee_cache[cond]
    fee: float | None = None
    try:
        r = H.get(f"{CLOB}/markets/{cond}")
        if r.status_code == 200:
            raw = r.json().get("taker_base_fee")
            fee = float(raw) if raw is not None else None
    except Exception:
        fee = None
    _fee_cache[cond] = fee
    return fee


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--minutes", type=float, default=30.0)
    ap.add_argument("--interval", type=float, default=60.0)
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + args.minutes * 60
    cycles = 0
    total_confirmed = 0
    total_tradeable_obs = 0   # fee-free confirmed hits, counted every cycle seen
    total_walled = 0
    total_unknown = 0
    best: dict[str, dict] = {}  # distinct fee-free markets -> best stats seen

    print(f"PROBE START: {args.minutes:.0f} min, every {args.interval:.0f}s. "
          f"Counting fee-free confirmed binary-merge arbs only.", flush=True)

    while time.time() < deadline:
        t0 = time.time()
        cycles += 1
        try:
            raw = arb_scanner.scan_binary_merge()
            hits = arb_scanner.confirm_hits(raw)
        except Exception as exc:
            print(f"  cycle {cycles} scan failed: {exc}", flush=True)
            time.sleep(max(5.0, args.interval - (time.time() - t0)))
            continue

        tradeable, walled, unknown = [], 0, 0
        for h in hits:
            fee = taker_fee(h.get("condition_id") or "")
            if fee is None:
                unknown += 1
            elif fee > 0:
                walled += 1
            else:
                tradeable.append(h)
                key = h.get("condition_id") or h["title"]
                prev = best.get(key)
                if prev is None or h["max_profit_usd"] > prev["max_profit_usd"]:
                    best[key] = {"title": h["title"], "edge_cents": h["edge_cents"],
                                 "depth_sets": h["depth_sets"],
                                 "max_profit_usd": h["max_profit_usd"]}

        total_confirmed += len(hits)
        total_tradeable_obs += len(tradeable)
        total_walled += walled
        total_unknown += unknown

        row = {"ts": int(time.time()), "cycle": cycles, "raw": len(raw),
               "confirmed": len(hits), "tradeable": len(tradeable),
               "walled": walled, "unknown": unknown,
               "tradeable_titles": [h["title"] for h in tradeable]}
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

        flag = "  <<< FEE-FREE ARB" if tradeable else ""
        print(f"  cycle {cycles:>3}: raw={len(raw):>2} confirmed={len(hits):>2} "
              f"tradeable={len(tradeable)} walled={walled} unknown={unknown}"
              f"{flag}", flush=True)

        if time.time() >= deadline:
            break
        time.sleep(max(5.0, args.interval - (time.time() - t0)))

    print("\n=== PROBE SUMMARY ===", flush=True)
    print(f"cycles: {cycles} over ~{args.minutes:.0f} min", flush=True)
    print(f"confirmed arbs (all): {total_confirmed}", flush=True)
    print(f"  fee-free observations: {total_tradeable_obs}", flush=True)
    print(f"  fee-walled observations: {total_walled}", flush=True)
    print(f"  fee-unknown observations: {total_unknown}", flush=True)
    print(f"distinct fee-free markets seen: {len(best)}", flush=True)
    for b in sorted(best.values(), key=lambda x: -x["max_profit_usd"]):
        print(f"  edge={b['edge_cents']:5.2f}c depth={b['depth_sets']:8.1f} "
              f"maxProfit=${b['max_profit_usd']:6.2f}  {b['title']}", flush=True)
    if not best:
        print("  (none -- no fee-free arb appeared in the entire window)", flush=True)
    print(f"\nlog: {OUT}", flush=True)


if __name__ == "__main__":
    main()
