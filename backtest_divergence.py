"""Backtest of the "Moving Average / Arty" RSI hidden-divergence strategy
(YouTube trx_M2Bss-c, watched frame-by-frame 2026-08-21) on Binance 1h data.

Strategy as taught in the video:
  - 1h chart, standard RSI(14), 70/30 band.
  - Trade HIDDEN divergences only (with-trend continuation):
      hidden bullish: uptrend, price higher low + RSI lower low  -> LONG
      hidden bearish: downtrend, price lower high + RSI higher high -> SHORT
  - "Secret sauce" filters:
      * price must have broken previous market structure (BOS) in trade direction
      * Gann box (levels 0/0.5/1) over the BOS impulse leg: entry pullback must
        sit in the discount half (long) / premium half (short) of that leg
  - Entry on divergence confirmation, SL beyond the divergence pivot,
    TP at 1:1.5 R (video's "safe" option) or 1:2; optional BE-move at 1.5R.

Pivots are fractal (PIVOT_LR bars each side); a divergence is only acted on
PIVOT_LR bars after the pivot forms (no lookahead). Entry at that bar's close.

Data: data-api.binance.vision (api.binance.com is ISP-blocked here).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request

BASE = "https://data-api.binance.vision/api/v3/klines"
RSI_LEN = 14
PIVOT_LR = 3          # fractal pivot strength (bars each side)
MAX_PIVOT_GAP = 60    # max bars between the two divergence pivots
FEE = 0.00075         # taker fee per side (Binance w/ BNB discount)


_CACHE: dict = {}


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int):
    key = (symbol, interval, start_ms, end_ms)
    if key in _CACHE:
        return _CACHE[key]
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
        time.sleep(0.15)
    _CACHE[key] = out
    return out


def rsi(closes, n=RSI_LEN):
    vals = [None] * len(closes)
    gain = loss = 0.0
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        g, l = max(d, 0.0), max(-d, 0.0)
        if i <= n:
            gain += g
            loss += l
            if i == n:
                ag, al = gain / n, loss / n
                vals[i] = 100 - 100 / (1 + (ag / al if al else float("inf")))
        else:
            ag = (ag * (n - 1) + g) / n
            al = (al * (n - 1) + l) / n
            vals[i] = 100 - 100 / (1 + (ag / al if al else float("inf")))
    return vals


def pivots(series, lr, kind):
    """Return indices i that are fractal highs/lows (strict vs neighbours)."""
    idx = []
    for i in range(lr, len(series) - lr):
        w = series[i - lr : i + lr + 1]
        v = series[i]
        if kind == "high" and v == max(w) and w.count(v) == 1:
            idx.append(i)
        elif kind == "low" and v == min(w) and w.count(v) == 1:
            idx.append(i)
    return idx


def backtest(symbol, interval, start_ms, end_ms, rr=1.5, use_pd=True,
             use_bos=True, be_move=False, kind_filter="hidden"):
    kl = fetch_klines(symbol, interval, start_ms, end_ms)
    o = [float(k[1]) for k in kl]
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    t = [k[0] for k in kl]
    r = rsi(c)

    ph = set(pivots(h, PIVOT_LR, "high"))
    pl = set(pivots(l, PIVOT_LR, "low"))
    ph_list, pl_list = [], []   # confirmed pivots in time order

    trades = []
    pos = None  # dict(side, entry, sl, tp, ei)

    # market-structure state: last confirmed swing high/low, BOS direction
    last_sh = None  # (idx, price)
    last_sl_ = None
    bos_dir = 0     # +1 up, -1 down
    leg_lo = leg_hi = None  # impulse leg for the current BOS

    for i in range(RSI_LEN + PIVOT_LR + 1, len(c)):
        # confirm pivots that completed at bar i (pivot at i-PIVOT_LR)
        j = i - PIVOT_LR
        if j in ph:
            ph_list.append(j)
        if j in pl:
            pl_list.append(j)

        # ---- manage open position on bar i (intrabar: SL first, conservative)
        if pos:
            side, entry, sl, tp = pos["side"], pos["entry"], pos["sl"], pos["tp"]
            risk = abs(entry - sl)
            hit_sl = l[i] <= sl if side == 1 else h[i] >= sl
            hit_tp = h[i] >= tp if side == 1 else l[i] <= tp
            if be_move and not pos.get("be"):
                be_lvl = entry + side * risk * 1.5
                if (side == 1 and h[i] >= be_lvl) or (side == -1 and l[i] <= be_lvl):
                    # BE armed; only counts from next bar to stay conservative
                    pos["sl"] = entry
                    pos["be"] = True
                    sl = entry
                    hit_sl = False  # same-bar: assume TP path checked below
            if hit_sl and hit_tp:
                res = -1.0  # ambiguous bar -> assume loss
            elif hit_sl:
                res = 0.0 if pos.get("be") and abs(sl - entry) < 1e-12 else -1.0
            elif hit_tp:
                res = rr
            else:
                res = None
            if res is not None:
                trades.append({"side": side, "r": res, "t": t[i]})
                pos = None

        # ---- update market structure on close of bar i
        if ph_list and c[i] > h[ph_list[-1]] and (last_sh is None or ph_list[-1] != last_sh[0]):
            # BOS up through the most recent confirmed swing high
            last_sh = (ph_list[-1], h[ph_list[-1]])
            bos_dir = 1
            # impulse leg: from the last confirmed swing low before that high to current high
            lows_before = [p for p in pl_list if p < ph_list[-1]]
            leg_lo = l[lows_before[-1]] if lows_before else min(l[max(0, i - 40): i + 1])
            leg_hi = h[i]
        elif pl_list and c[i] < l[pl_list[-1]] and (last_sl_ is None or pl_list[-1] != last_sl_[0]):
            last_sl_ = (pl_list[-1], l[pl_list[-1]])
            bos_dir = -1
            highs_before = [p for p in ph_list if p > 0 and p < pl_list[-1]]
            leg_hi = h[highs_before[-1]] if highs_before else max(h[max(0, i - 40): i + 1])
            leg_lo = l[i]
        # extend the leg while trend runs
        if bos_dir == 1 and leg_hi is not None:
            leg_hi = max(leg_hi, h[i])
        if bos_dir == -1 and leg_lo is not None:
            leg_lo = min(leg_lo, l[i])

        if pos:
            continue

        # ---- signals: divergence between the two most recent confirmed pivots
        def try_long():
            if len(pl_list) < 2:
                return None
            b, a = pl_list[-1], pl_list[-2]
            if b != j or b - a > MAX_PIVOT_GAP:
                return None
            if r[a] is None or r[b] is None:
                return None
            if kind_filter == "hidden":
                ok = l[b] > l[a] and r[b] < r[a]          # hidden bullish
            else:
                ok = l[b] < l[a] and r[b] > r[a]          # regular bullish
            if not ok:
                return None
            if use_bos and bos_dir != 1:
                return None
            if use_pd and leg_hi is not None and leg_lo is not None:
                mid = (leg_hi + leg_lo) / 2
                if l[b] > mid:                            # must be in discount
                    return None
            entry = c[i]
            sl = l[b] * (1 - 0.0005)
            if entry <= sl:
                return None
            return {"side": 1, "entry": entry, "sl": sl,
                    "tp": entry + rr * (entry - sl), "ei": i}

        def try_short():
            if len(ph_list) < 2:
                return None
            b, a = ph_list[-1], ph_list[-2]
            if b != j or b - a > MAX_PIVOT_GAP:
                return None
            if r[a] is None or r[b] is None:
                return None
            if kind_filter == "hidden":
                ok = h[b] < h[a] and r[b] > r[a]          # hidden bearish
            else:
                ok = h[b] > h[a] and r[b] < r[a]          # regular bearish
            if not ok:
                return None
            if use_bos and bos_dir != -1:
                return None
            if use_pd and leg_hi is not None and leg_lo is not None:
                mid = (leg_hi + leg_lo) / 2
                if h[b] < mid:                            # must be in premium
                    return None
            entry = c[i]
            sl = h[b] * (1 + 0.0005)
            if entry >= sl:
                return None
            return {"side": -1, "entry": entry, "sl": sl,
                    "tp": entry - rr * (sl - entry), "ei": i}

        pos = try_long() or try_short()

    return trades, len(c)


def summarize(name, trades, rr):
    n = len(trades)
    if not n:
        print(f"{name:58s}  no trades")
        return
    wins = sum(1 for x in trades if x["r"] > 0)
    bes = sum(1 for x in trades if x["r"] == 0)
    losses = n - wins - bes
    # net R after fees: fee cost per trade ~ 2*FEE / risk% — approximate in R
    gross_r = sum(x["r"] for x in trades)
    wr = wins / n * 100
    wr_ex_be = wins / (wins + losses) * 100 if wins + losses else 0
    exp = gross_r / n
    print(f"{name:58s}  n={n:4d}  win={wr:5.1f}%  (ex-BE {wr_ex_be:5.1f}%)  "
          f"BE={bes:3d}  netR={gross_r:+8.1f}  exp/trade={exp:+.3f}R")


if __name__ == "__main__":
    import datetime as dt
    end = int(dt.datetime(2026, 8, 20).timestamp() * 1000)
    start = int(dt.datetime(2023, 8, 20).timestamp() * 1000)  # 3 years
    symbols = sys.argv[1:] or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    for sym in symbols:
        print(f"\n=== {sym} 1h  2023-08-20 .. 2026-08-20 ===")
        for rr in (1.5, 2.0):
            for use_pd, use_bos, label in (
                (True, True, "full strategy (BOS+PD)"),
                (False, True, "BOS only"),
                (False, False, "hidden div only"),
            ):
                tr, nb = backtest(sym, "1h", start, end, rr=rr,
                                  use_pd=use_pd, use_bos=use_bos)
                summarize(f"  RR 1:{rr}  {label}", tr, rr)
            tr, _ = backtest(sym, "1h", start, end, rr=rr,
                             use_pd=True, use_bos=True, be_move=True)
            summarize(f"  RR 1:{rr}  full + BE@1.5R", tr, rr)
