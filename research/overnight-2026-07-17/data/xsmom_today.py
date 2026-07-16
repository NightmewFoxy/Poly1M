"""Compute TODAY's xsmom ensemble basket (indicative, read-only).

Fetches the last ~80 daily candles fresh from OKX for the mid-15 universe,
computes the four lookback returns (7/14/28/60d), averages the ranks, and
prints the long-3 / short-3 basket with per-symbol signals. ASCII only.
"""
import time
from datetime import datetime, timezone

import httpx

UNIVERSE = ("AAVE", "ADA", "BCH", "BNB", "BTC", "DOGE", "ETH", "LINK",
            "NEAR", "PEPE", "SOL", "SUI", "UNI", "WLD", "XRP")
LOOKBACKS = (7, 14, 28, 60)


def main() -> None:
    closes = {}
    with httpx.Client(timeout=20, trust_env=False) as c:
        for b in UNIVERSE:
            r = c.get("https://www.okx.com/api/v5/market/candles",
                      params={"instId": f"{b}-USDT-SWAP", "bar": "1Dutc", "limit": "80"})
            rows = r.json().get("data") or []
            rows = [k for k in rows if k[-1] == "1"]  # confirmed bars only
            rows.sort(key=lambda k: int(k[0]))
            closes[b] = [float(k[4]) for k in rows]
            time.sleep(0.12)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"as of {now} (last confirmed daily close)")

    ranks_sum = {b: 0.0 for b in UNIVERSE}
    for lb in LOOKBACKS:
        scores = {b: cl[-1] / cl[-1 - lb] - 1 for b, cl in closes.items() if len(cl) > lb}
        ranked = sorted(scores, key=scores.get, reverse=True)
        for pos, b in enumerate(ranked):
            ranks_sum[b] += pos
    avg_rank = {b: ranks_sum[b] / len(LOOKBACKS) for b in UNIVERSE if len(closes[b]) > 60}
    order = sorted(avg_rank, key=avg_rank.get)

    print("\nfull ranking (best momentum first; avg rank across 7/14/28/60d):")
    for b in order:
        rets = " ".join(f"{lb}d={closes[b][-1]/closes[b][-1-lb]-1:+.1%}" for lb in LOOKBACKS)
        print(f"  {b:5s} avg_rank={avg_rank[b]:4.1f}  {rets}")

    print(f"\nLONG  (top 3): {', '.join(order[:3])}")
    print(f"SHORT (bot 3): {', '.join(order[-3:])}")
    print("(equal weight, 1x gross total: each long +16.7%, each short -16.7% of capital)")


if __name__ == "__main__":
    main()
