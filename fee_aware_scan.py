"""Read-only: what survives BOTH the v2 re-check AND the fee filter, right now.

Runs the real scanner path (scan_binary_merge -> confirm_hits), then asks the
CLOB for each survivor's taker fee and splits them into:
  TRADEABLE  : confirmed edge AND zero taker fee  (what the fee-aware executor
               would actually take)
  FEE-WALLED : confirmed edge but nonzero taker fee (phantom profit — the v2
               report counted these)
No orders, no wallet. Fees fetched straight from the CLOB REST endpoint.
"""
import json

import httpx

import arb_scanner

CLOB = "https://clob.polymarket.com"
H = httpx.Client(trust_env=False, timeout=30)


def taker_fee(cond: str):
    try:
        r = H.get(f"{CLOB}/markets/{cond}")
        if r.status_code != 200:
            return None
        return r.json().get("taker_base_fee")
    except Exception:
        return None


def main() -> None:
    raw = arb_scanner.scan_binary_merge()
    hits = arb_scanner.confirm_hits(raw)
    print(f"{len(raw)} raw binary-merge hits -> {len(hits)} confirmed (v2 re-check)\n")
    tradeable, walled = [], []
    for h in hits:
        fee = taker_fee(h.get("condition_id") or "")
        row = (h["edge_cents"], h["depth_sets"], h["max_profit_usd"], fee, h["title"])
        (tradeable if fee == 0 else walled).append(row)

    print("== TRADEABLE (confirmed edge, zero taker fee) ==")
    if tradeable:
        for ec, d, mp, fee, t in sorted(tradeable, key=lambda r: -r[2]):
            print(f"  edge={ec:5.2f}c depth={d:8.1f} maxProfit=${mp:6.2f}  {t}")
    else:
        print("  (none right now)")

    print("\n== FEE-WALLED (confirmed edge but taker fee != 0 -> phantom) ==")
    for ec, d, mp, fee, t in sorted(walled, key=lambda r: -r[2])[:15]:
        print(f"  edge={ec:5.2f}c fee={fee} maxProfit=${mp:6.2f}  {t}")
    if len(walled) > 15:
        print(f"  ... and {len(walled) - 15} more")

    print(f"\nSUMMARY: {len(tradeable)} tradeable, {len(walled)} fee-walled "
          f"of {len(hits)} confirmed.")


if __name__ == "__main__":
    main()
