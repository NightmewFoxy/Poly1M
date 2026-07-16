"""Perp funding-rate snapshot sampler (read-only, public endpoints, no keys).

Every INTERVAL seconds appends funding snapshots to funding_snaps.jsonl next to this
file: Bybit all linear USDT perps (top by 24h turnover), OKX majors, Binance fapi if
reachable. Feeds the funding-harvest strategy verification with live breadth. Purely
mechanical. Run with --once for a single probe cycle.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent / "funding_snaps.jsonl"
INTERVAL = 300
TOP_N = 150
OKX_MAJORS = ("BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "XRP-USDT-SWAP", "DOGE-USDT-SWAP")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sample(client: httpx.Client) -> list[dict]:
    ts = now()
    rows: list[dict] = []

    def err(venue: str, e: Exception) -> None:
        rows.append({"ts": ts, "venue": venue, "err": f"{type(e).__name__}: {e}"[:160]})

    # Bybit: one call covers every linear perp incl. funding + next funding time
    try:
        r = client.get("https://api.bybit.com/v5/market/tickers", params={"category": "linear"})
        ticks = [t for t in r.json()["result"]["list"]
                 if t["symbol"].endswith("USDT") and t.get("fundingRate")]
        ticks.sort(key=lambda t: float(t.get("turnover24h") or 0), reverse=True)
        for t in ticks[:TOP_N]:
            rows.append({"ts": ts, "venue": "bybit", "sym": t["symbol"],
                         "funding": float(t["fundingRate"]),
                         "next_ft": t.get("nextFundingTime"),
                         "mark": float(t["markPrice"]) if t.get("markPrice") else None,
                         "turnover24h": float(t.get("turnover24h") or 0)})
    except Exception as e:
        err("bybit", e)

    # OKX majors (per-instrument endpoint)
    for inst in OKX_MAJORS:
        try:
            r = client.get("https://www.okx.com/api/v5/public/funding-rate", params={"instId": inst})
            d = r.json()["data"][0]
            rows.append({"ts": ts, "venue": "okx", "sym": inst,
                         "funding": float(d["fundingRate"]),
                         "next_funding": d.get("nextFundingRate") or None})
        except Exception as e:
            err("okx", e)
            break

    # Binance futures (reachability unknown from here; one call covers all)
    try:
        r = client.get("https://fapi.binance.com/fapi/v1/premiumIndex")
        data = r.json()
        data.sort(key=lambda t: t["symbol"])
        for t in data:
            if t["symbol"] in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"):
                rows.append({"ts": ts, "venue": "binance", "sym": t["symbol"],
                             "funding": float(t["lastFundingRate"]),
                             "mark": float(t["markPrice"])})
    except Exception as e:
        err("binance", e)

    return rows


def main() -> None:
    once = "--once" in sys.argv
    cycles = 0
    while True:
        try:
            with httpx.Client(timeout=15, trust_env=False) as client:
                rows = sample(client)
            with OUT.open("a", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row) + "\n")
            cycles += 1
            oks = sum(1 for r in rows if "err" not in r)
            errs = [r["venue"] for r in rows if "err" in r]
            if once or cycles % 6 == 1:
                print(f"[{now()}] cycle {cycles}: {oks} rows, errors={errs or 'none'}", flush=True)
        except Exception as e:  # never die
            print(f"[{now()}] cycle error: {e}", flush=True)
        if once:
            break
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
