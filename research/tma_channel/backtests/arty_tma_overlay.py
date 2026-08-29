"""Backtest of Arty's TMA Overlay strategy (video 6mr-XMcYU5c, "Best Scalping
Indicator **FREE**") on Bitcoin.

Rules as stated in the video, with signal formulas taken verbatim from the
open-source Pine of the TMA Overlay indicator (tradingview.com/script/zX3fvduH):

  - SMMAs 21/50/200 on close (100 optional, Arty turns it off).
  - Trend: close above 200 SMMA -> longs only; below -> shorts only.
  - MAs "lined up in order": 21>50>200 for longs, 21<50<200 for shorts.
  - Pullback to the 21 SMMA and rejection off it.
  - Entry candle: engulfing ("Big A$$ Candle") or 3-line strike, exact Pine:
      bullishEngulfing = open<=close[1] and open<open[1] and close>open[1]
      bullSig(3LS)     = 3 consecutive red closes then close>open[1]
  - Stop loss: double the length of the entry candle. TP: 2:1 R/R.
  - Entry modeled at the signal bar close (taker), MEXC futures
    taker fee 0.02% per side. SL/TP same bar -> SL (pessimistic).

No lookahead: everything is computed on closed bars; entry is at signal close.
"""
from __future__ import annotations
import json, math, os, sys, time, urllib.request, datetime

BASE = "https://data-api.binance.vision/api/v3/klines"
TAKER = 0.0002  # MEXC futures taker 0.02% per side (owner request)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def fetch(symbol, interval, start_ms, end_ms):
    cache = f"{DATA_DIR}/{symbol}_{interval}.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    out, cur = [], start_ms
    while cur < end_ms:
        url = f"{BASE}?symbol={symbol}&interval={interval}&startTime={cur}&endTime={end_ms}&limit=1000"
        with urllib.request.urlopen(url, timeout=30) as r:
            batch = json.loads(r.read())
        if not batch:
            break
        out.extend(batch)
        cur = batch[-1][6] + 1
        time.sleep(0.1)
    json.dump(out, open(cache, "w"))
    return out


def smma(x, n):
    vals = [None] * len(x)
    s = sum(x[:n]) / n
    vals[n - 1] = s
    for i in range(n, len(x)):
        s = (s * (n - 1) + x[i]) / n
        vals[i] = s
    return vals


def backtest(kl, require_stack=True, require_pullback=True, signals="both",
             pullback_lookback=3, sl_mult=2.0, rr=2.0):
    t = [k[0] for k in kl]
    o = [float(k[1]) for k in kl]
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    n = len(c)
    m21, m50, m200 = smma(c, 21), smma(c, 50), smma(c, 200)

    trades = []
    busy_until = -1
    for i in range(203, n - 1):
        if i <= busy_until:
            continue
        if m200[i] is None:
            continue
        # signal formulas (verbatim from Pine)
        bullE = o[i] <= c[i-1] and o[i] < o[i-1] and c[i] > o[i-1]
        bearE = o[i] >= c[i-1] and o[i] > o[i-1] and c[i] < o[i-1]
        bull3 = c[i-3] < o[i-3] and c[i-2] < o[i-2] and c[i-1] < o[i-1] and c[i] > o[i-1]
        bear3 = c[i-3] > o[i-3] and c[i-2] > o[i-2] and c[i-1] > o[i-1] and c[i] < o[i-1]
        if signals == "engulf":
            long_sig, short_sig = bullE, bearE
        elif signals == "3ls":
            long_sig, short_sig = bull3, bear3
        else:
            long_sig, short_sig = (bullE or bull3), (bearE or bear3)

        dr = 0
        if long_sig and c[i] > m200[i]:
            if (not require_stack) or (m21[i] > m50[i] > m200[i]):
                if (not require_pullback) or any(
                        l[j] <= m21[j] for j in range(i - pullback_lookback, i + 1)):
                    dr = 1
        if dr == 0 and short_sig and c[i] < m200[i]:
            if (not require_stack) or (m21[i] < m50[i] < m200[i]):
                if (not require_pullback) or any(
                        h[j] >= m21[j] for j in range(i - pullback_lookback, i + 1)):
                    dr = -1
        if dr == 0:
            continue

        entry = c[i]
        candle = h[i] - l[i]
        if candle <= 0:
            continue
        risk = sl_mult * candle
        sl = entry - dr * risk
        tp = entry + dr * rr * risk
        exit_px = exit_bar = None
        for j in range(i + 1, n):
            hit_sl = l[j] <= sl if dr > 0 else h[j] >= sl
            hit_tp = h[j] >= tp if dr > 0 else l[j] <= tp
            if hit_sl:
                exit_px, exit_bar = sl, j
                break
            if hit_tp:
                exit_px, exit_bar = tp, j
                break
        if exit_px is None:
            exit_px, exit_bar = c[-1], n - 1
        gross = dr * (exit_px - entry) / entry
        net = gross - 2 * TAKER
        trades.append({"t": t[i], "dir": dr, "gross": gross, "net": net,
                       "win": exit_px == tp})
        busy_until = exit_bar
    return trades


def report(label, trades):
    n = len(trades)
    if n == 0:
        print(f"{label:52s} n=0")
        return
    wins = sum(1 for tr in trades if tr["win"])
    nets = [tr["net"] for tr in trades]
    tot, avg = sum(nets), sum(nets) / n
    var = sum((x - avg) ** 2 for x in nets) / max(n - 1, 1)
    tstat = avg / (math.sqrt(var) / math.sqrt(n)) if var > 0 else 0.0
    gr = sum(tr["gross"] for tr in trades) / n
    print(f"{label:52s} n={n:5d} win={wins/n:5.1%} avg_gross={gr*100:+.3f}% "
          f"avg_net={avg*100:+.3f}% total_net={tot*100:+9.1f}% t={tstat:+.2f}")


def main():
    end = int(time.time() * 1000)
    start = end - 2 * 365 * 86400000
    for iv in ["5m", "15m", "1h"]:
        print(f"\n=== BTCUSDT {iv} (2y, MEXC taker 0.02%/side, SL=2x candle, TP=2R) ===")
        kl = fetch("BTCUSDT", iv, start, end)
        d0 = datetime.datetime.utcfromtimestamp(kl[0][0]/1000).date()
        d1 = datetime.datetime.utcfromtimestamp(kl[-1][0]/1000).date()
        print(f"bars={len(kl)} {d0} -> {d1}")
        full = backtest(kl)
        report("FULL strategy (stack+pullback, engulf|3LS)", full)
        # year split
        ts = [tr["t"] for tr in full]
        if ts:
            mid = min(ts) + (max(ts) - min(ts)) / 2
            report("  first half", [tr for tr in full if tr["t"] < mid])
            report("  second half", [tr for tr in full if tr["t"] >= mid])
            report("  longs only", [tr for tr in full if tr["dir"] > 0])
            report("  shorts only", [tr for tr in full if tr["dir"] < 0])
        report("variant: 3LS signals only", backtest(kl, signals="3ls"))
        report("variant: engulfing only", backtest(kl, signals="engulf"))
        report("variant: no MA-stack requirement", backtest(kl, require_stack=False))
        report("variant: no pullback requirement", backtest(kl, require_pullback=False))
        report("variant: trend filter only (no stack/pullback)",
               backtest(kl, require_stack=False, require_pullback=False))


if __name__ == "__main__":
    main()
