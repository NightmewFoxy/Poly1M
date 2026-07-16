"""Cross-exchange top-of-book sampler (read-only, public endpoints, no keys).

Every INTERVAL seconds, snapshots bid/ask for BTC/ETH/SOL across venues and appends
JSONL rows to xex_spreads.jsonl next to this file. Errors are logged as rows too —
an unreachable venue is itself a finding. Purely mechanical; part of the overnight
strategy research 2026-07-17. Run with --once for a single probe cycle.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent / "xex_spreads.jsonl"
INTERVAL = 60
SYMS = ("BTC", "ETH", "SOL")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sample(client: httpx.Client) -> list[dict]:
    ts = now()
    rows: list[dict] = []

    def err(venue: str, e: Exception) -> None:
        rows.append({"ts": ts, "venue": venue, "err": f"{type(e).__name__}: {e}"[:160]})

    # Bybit spot + linear perps
    for cat in ("spot", "linear"):
        try:
            r = client.get("https://api.bybit.com/v5/market/tickers", params={"category": cat})
            for t in r.json()["result"]["list"]:
                if t["symbol"] in {s + "USDT" for s in SYMS}:
                    rows.append({"ts": ts, "venue": f"bybit_{cat}", "sym": t["symbol"],
                                 "bid": float(t["bid1Price"]), "ask": float(t["ask1Price"]),
                                 **({"funding": float(t["fundingRate"])} if cat == "linear" and t.get("fundingRate") else {})})
        except Exception as e:
            err(f"bybit_{cat}", e)

    # OKX spot + swap
    for inst in ("SPOT", "SWAP"):
        try:
            want = {f"{s}-USDT" if inst == "SPOT" else f"{s}-USDT-SWAP" for s in SYMS}
            r = client.get("https://www.okx.com/api/v5/market/tickers", params={"instType": inst})
            for t in r.json()["data"]:
                if t["instId"] in want and t.get("bidPx") and t.get("askPx"):
                    rows.append({"ts": ts, "venue": f"okx_{inst.lower()}", "sym": t["instId"],
                                 "bid": float(t["bidPx"]), "ask": float(t["askPx"])})
        except Exception as e:
            err(f"okx_{inst.lower()}", e)

    # Kraken spot
    try:
        r = client.get("https://api.kraken.com/0/public/Ticker", params={"pair": "XBTUSDT,ETHUSDT,SOLUSDT"})
        for k, t in r.json()["result"].items():
            rows.append({"ts": ts, "venue": "kraken_spot", "sym": k,
                         "bid": float(t["b"][0]), "ask": float(t["a"][0])})
    except Exception as e:
        err("kraken_spot", e)

    # KuCoin spot
    for s in SYMS:
        try:
            r = client.get("https://api.kucoin.com/api/v1/market/orderbook/level1",
                           params={"symbol": f"{s}-USDT"})
            d = r.json()["data"]
            rows.append({"ts": ts, "venue": "kucoin_spot", "sym": f"{s}-USDT",
                         "bid": float(d["bestBid"]), "ask": float(d["bestAsk"])})
        except Exception as e:
            err("kucoin_spot", e)
            break  # one failure means the venue is down; don't spam 3 errors

    # Binance spot (reachability unknown from here — result either way is data)
    try:
        r = client.get("https://api.binance.com/api/v3/ticker/bookTicker",
                       params={"symbols": json.dumps([s + "USDT" for s in SYMS], separators=(",", ":"))})
        for t in r.json():
            rows.append({"ts": ts, "venue": "binance_spot", "sym": t["symbol"],
                         "bid": float(t["bidPrice"]), "ask": float(t["askPrice"])})
    except Exception as e:
        err("binance_spot", e)

    return rows


def main() -> None:
    once = "--once" in sys.argv
    cycles = 0
    while True:
        try:
            with httpx.Client(timeout=10, trust_env=False) as client:
                rows = sample(client)
            with OUT.open("a", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row) + "\n")
            cycles += 1
            oks = sum(1 for r in rows if "err" not in r)
            errs = [r["venue"] for r in rows if "err" in r]
            if once or cycles % 10 == 1:
                print(f"[{now()}] cycle {cycles}: {oks} quotes, errors={errs or 'none'}", flush=True)
        except Exception as e:  # never die
            print(f"[{now()}] cycle error: {e}", flush=True)
        if once:
            break
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
