"""Backtest of "The Moving Average / Arty" RSI *regular*-divergence strategy
(YouTube K7vFNn7fZ7Y, transcript-extracted 2026-08-24) on Binance BTC 15m.

Strategy as taught in the video (bearish; longs mirrored):
  - 15m chart, RSI(14) with the 50 line as bull/bear divider (not 70/30).
  - Smoothed MAs (RMA) 21 / 150 / 200.
  - Regular bearish divergence: price higher high, RSI lower high.
  - DO NOT enter on the divergence alone ("too early = fighting momentum").
    Wait for confluences:
      * RSI below 50
      * break of market structure (price closes below the swing low between
        the two divergence highs)
      * price below the 21 SMMA (he adds "with a retest")
      * optional entry trigger: three-line strike (3 candles one way then an
        engulfing candle the other way)
  - SL beyond the divergence extreme, ride it down (he targets the 200 SMMA);
    we test fixed 1.5R / 2R and a 200-SMMA target.

Tiers tested:
  A  naive: enter on divergence confirmation alone (what he says NOT to do)
  B  confluences: divergence + RSI<50 + BOS + below SMMA21 (entry when all met)
  C  B + engulfing / three-line-strike trigger
Each with TP at 1.5R and 2R, plus tier B with 200-SMMA target.

No lookahead: pivots act PIVOT_LR bars after forming; entries at bar close.
Data: data-api.binance.vision.
"""

from __future__ import annotations

import json
import time
import urllib.request

BASE = "https://data-api.binance.vision/api/v3/klines"
RSI_LEN = 14
PIVOT_LR = 3
MAX_PIVOT_GAP = 60     # max bars between the two divergence pivots
CONF_WINDOW = 40       # bars after divergence to wait for confluences
FEE = 0.00075          # taker per side


def fetch_klines(symbol, interval, start_ms, end_ms):
    out = []
    cur = start_ms
    while cur < end_ms:
        url = f"{BASE}?symbol={symbol}&interval={interval}&startTime={cur}&endTime={end_ms}&limit=1000"
        with urllib.request.urlopen(url, timeout=30) as r:
            batch = json.loads(r.read())
        if not batch:
            break
        out.extend(batch)
        cur = batch[-1][6] + 1
        time.sleep(0.12)
    return out


def rsi(closes, n=RSI_LEN):
    vals = [None] * len(closes)
    g = l = 0.0
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        up, dn = max(d, 0), max(-d, 0)
        if i <= n:
            g += up; l += dn
            if i == n:
                ag, al = g / n, l / n
                vals[i] = 100 - 100 / (1 + (ag / al if al else 1e9))
        else:
            ag = (ag * (n - 1) + up) / n
            al = (al * (n - 1) + dn) / n
            vals[i] = 100 - 100 / (1 + (ag / al if al else 1e9))
    return vals


def smma(closes, n):
    vals = [None] * len(closes)
    s = sum(closes[:n]) / n
    vals[n - 1] = s
    for i in range(n, len(closes)):
        s = (s * (n - 1) + closes[i]) / n
        vals[i] = s
    return vals


def pivots(highs, lows, lr=PIVOT_LR):
    ph, pl = [], []
    for i in range(lr, len(highs) - lr):
        if highs[i] == max(highs[i - lr:i + lr + 1]):
            ph.append(i)
        if lows[i] == min(lows[i - lr:i + lr + 1]):
            pl.append(i)
    return ph, pl


def run(kl, tier, tp_r, target_ma=None):
    o = [float(k[1]) for k in kl]
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    r = rsi(c)
    ma21 = smma(c, 21)
    ma200 = smma(c, 200)
    ph, pl = pivots(h, l)
    phs, pls = set(ph), set(pl)

    trades = []
    in_pos = 0  # 0 flat, +1 long, -1 short
    entry = sl = tp = 0.0
    # pending divergence signals awaiting confluences: (dir, sig_bar, extreme, bos_level)
    pending = []
    last_ph = []  # recent pivot high indices
    last_pl = []

    for i in range(250, len(kl)):
        # manage position
        if in_pos:
            if in_pos < 0:
                hit_sl = h[i] >= sl
                hit_tp = (l[i] <= tp) if target_ma is None else (l[i] <= ma200[i])
            else:
                hit_sl = l[i] <= sl
                hit_tp = (h[i] >= tp) if target_ma is None else (h[i] >= ma200[i])
            if hit_sl:
                px = sl
                trades.append(in_pos * (px - entry) / entry - 2 * FEE)
                in_pos = 0
            elif hit_tp:
                px = tp if target_ma is None else ma200[i]
                trades.append(in_pos * (px - entry) / entry - 2 * FEE)
                in_pos = 0
            if in_pos:
                continue

        # pivot confirmed lr bars ago
        j = i - PIVOT_LR
        if j in phs:
            prev = [p for p in last_ph if j - p <= MAX_PIVOT_GAP]
            for p in prev:
                if h[j] > h[p] and r[j] is not None and r[p] is not None and r[j] < r[p]:
                    bos = min(l[p:j + 1])
                    pending.append((-1, i, max(h[j], h[p]), bos))
                    break
            last_ph.append(j)
        if j in pls:
            prev = [p for p in last_pl if j - p <= MAX_PIVOT_GAP]
            for p in prev:
                if l[j] < l[p] and r[j] is not None and r[p] is not None and r[j] > r[p]:
                    bos = max(h[p:j + 1])
                    pending.append((1, i, min(l[j], l[p]), bos))
                    break
            last_pl.append(j)
        last_ph = last_ph[-8:]
        last_pl = last_pl[-8:]

        # check pending signals
        keep = []
        fired = None
        for (d, sb, ext, bos) in pending:
            if i - sb > CONF_WINDOW:
                continue
            if tier == "A":
                fired = (d, ext); continue  # fire immediately at sb==i
            ok = True
            if d < 0:
                ok = r[i] is not None and r[i] < 50 and c[i] < bos and c[i] < ma21[i]
            else:
                ok = r[i] is not None and r[i] > 50 and c[i] > bos and c[i] > ma21[i]
            if ok and tier == "C":
                # three-line strike / engulfing trigger
                if d < 0:
                    ok = (all(c[k] > o[k] for k in (i - 3, i - 2, i - 1))
                          and c[i] < o[i] and c[i] < o[i - 1])
                else:
                    ok = (all(c[k] < o[k] for k in (i - 3, i - 2, i - 1))
                          and c[i] > o[i] and c[i] > o[i - 1])
            if ok:
                fired = (d, ext)
            else:
                keep.append((d, sb, ext, bos))
        pending = keep if tier != "A" else []

        if fired and not in_pos:
            d, ext = fired
            entry = c[i]
            risk = abs(ext - entry)
            if risk / entry < 0.0008:   # degenerate: stop too close
                continue
            in_pos = d
            sl = ext
            tp = entry + d * tp_r * risk
            pending = []

    n = len(trades)
    if not n:
        return "no trades"
    wins = sum(1 for t in trades if t > 0)
    tot = sum(trades)
    return (f"n={n:4d}  win={wins/n:5.1%}  avg={tot/n*100:+.3f}%  "
            f"total={tot*100:+7.1f}%")


def main():
    end = int(time.time() * 1000)
    start = end - 2 * 365 * 24 * 3600 * 1000
    print("fetching BTCUSDT 15m, 2y ...")
    kl = fetch_klines("BTCUSDT", "15m", start, end)
    print(f"{len(kl)} bars  {time.strftime('%Y-%m-%d', time.gmtime(kl[0][0]/1000))}"
          f" -> {time.strftime('%Y-%m-%d', time.gmtime(kl[-1][0]/1000))}\n")
    for tier in ("A", "B", "C"):
        for tp_r in (1.5, 2.0):
            print(f"tier {tier}  TP {tp_r}R : {run(kl, tier, tp_r)}")
    print(f"tier B  TP=200SMMA: {run(kl, 'B', 2.0, target_ma=True)}")


if __name__ == "__main__":
    main()
