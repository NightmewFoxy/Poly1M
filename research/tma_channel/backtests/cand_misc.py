"""Remaining TMA-channel candidate families, mechanical translations.

All entries taker-at-close of the signal bar (his style: "enter at candle
close"), SL structural, TP 2R unless the video says otherwise. The maker
variant is only re-tested for anything that survives gross.
Families:
  3LS        three-line strike: 3 same-colour candles then opposite engulfing
             (engulfs last body). Variants: raw, with-trend (SMMA200), at
             21-SMMA pullback (price within 0.2*ATR of SMMA21).
  HANW       Heikin-Ashi no-wick entry after pullback in trend: c>SMMA200,
             price pulled back to/below SMMA21, first HA candle with no
             bottom wick (tolerance 5% of range) -> long. SL last swing low
             (fractal), TP 2R.
  ST         SuperTrend(10, 2.5) flip entry, exit on opposite flip (trail),
             and fixed-2R variant with SL at the ST line.
  SRSI       StochRSI(14,14,3,3) K crosses D upward while K<20 and c>SMMA200
             -> long (mirrored). SL swing low, TP 2R.
  RSIREJ     RSI(14) re-enters the band: RSI was >70, crosses below 70 ->
             short (mirror 30). Variants raw / with-trend. SL swing, TP 2R.
  MA200RT    200-SMMA retest-reject: bar touches SMMA200 and closes back on
             the trend side (trend = side of the last 50 closes majority).
             SL beyond the wick extreme, TP 2R.
  SESSBRK    session opening-range breakout (DR): range of first hour after
             session open (London 07 UTC / NY 13 UTC), first candle CLOSE
             beyond range within next 6h -> enter, SL range midpoint, TP 2R.
"""
import sys
from engine import *


def taker_signals_run(d, sigs, tp_r=2.0, label="", trail=None):
    """sigs: list of (bar, dir, sl). Entry at close of bar (taker)."""
    h, l, c, t = d["h"], d["l"], d["c"], d["t"]
    trades = []
    busy = -1
    for (i, dr, sl) in sigs:
        if i <= busy:
            continue
        entry = c[i]
        risk = abs(entry - sl)
        if risk / entry < 0.0008 or (dr > 0) != (entry > sl):
            continue
        tp = entry + dr * tp_r * risk
        exit_px = exit_fee = exit_bar = None
        for jj in range(i + 1, len(c)):
            hit_sl = l[jj] <= sl if dr > 0 else h[jj] >= sl
            hit_tp = h[jj] >= tp if dr > 0 else l[jj] <= tp
            if hit_sl:
                exit_px, exit_fee, exit_bar = sl, TAKER, jj
                break
            if hit_tp:
                exit_px, exit_fee, exit_bar = tp, MAKER, jj
                break
            if trail is not None and trail(jj, dr):
                exit_px, exit_fee, exit_bar = c[jj], TAKER, jj
                break
        if exit_px is None:
            exit_px, exit_fee, exit_bar = c[-1], TAKER, len(c) - 1
        gross = dr * (exit_px - entry) / entry
        trades.append({"i": i, "dir": dr, "gross": gross,
                       "net": gross - TAKER - exit_fee, "t": t[i],
                       "exit_bar": exit_bar})
        busy = exit_bar
    return trades


def show(tr, name):
    print(report(tr, name))
    y1, y2 = split_years(tr)
    print("   " + report(y1, " yr1"))
    print("   " + report(y2, " yr2"))


def sig_3ls(d, mode="raw"):
    o, h, l, c = d["o"], d["h"], d["l"], d["c"]
    ma200 = smma(c, 200)
    ma21 = smma(c, 21)
    a = atr(h, l, c, 14)
    out = []
    for i in range(210, len(c)):
        # bullish strike: 3 red then green engulfing last body
        bull = (all(c[k] < o[k] for k in (i - 3, i - 2, i - 1))
                and c[i] > o[i] and c[i] > o[i - 1])
        bear = (all(c[k] > o[k] for k in (i - 3, i - 2, i - 1))
                and c[i] < o[i] and c[i] < o[i - 1])
        if not (bull or bear):
            continue
        dr = 1 if bull else -1
        if mode == "trend":
            if dr > 0 and c[i] < ma200[i]:
                continue
            if dr < 0 and c[i] > ma200[i]:
                continue
        if mode == "ma21":
            if a[i] is None:
                continue
            lo_ext = min(l[i - 3:i + 1]) if dr > 0 else max(h[i - 3:i + 1])
            if abs(lo_ext - ma21[i]) > 0.5 * a[i]:
                continue
            if dr > 0 and c[i] < ma200[i]:
                continue
            if dr < 0 and c[i] > ma200[i]:
                continue
        sl = min(l[i - 3:i + 1]) if dr > 0 else max(h[i - 3:i + 1])
        out.append((i, dr, sl))
    return out


def heikin(o, h, l, c):
    ha_c = [(o[i] + h[i] + l[i] + c[i]) / 4 for i in range(len(c))]
    ha_o = [o[0]]
    for i in range(1, len(c)):
        ha_o.append((ha_o[-1] + ha_c[i - 1]) / 2)
    ha_h = [max(h[i], ha_o[i], ha_c[i]) for i in range(len(c))]
    ha_l = [min(l[i], ha_o[i], ha_c[i]) for i in range(len(c))]
    return ha_o, ha_h, ha_l, ha_c


def sig_hanw(d):
    o, h, l, c = d["o"], d["h"], d["l"], d["c"]
    ma200 = smma(c, 200)
    ma21 = smma(c, 21)
    ph, pl = pivots(h, l, 3)
    plset = sorted(pl)
    phset = sorted(ph)
    ha_o, ha_h, ha_l, ha_c = heikin(o, h, l, c)
    out = []
    pulled_long = pulled_short = False
    import bisect
    for i in range(210, len(c)):
        up = c[i] > ma200[i]
        dn = c[i] < ma200[i]
        if up and l[i] <= ma21[i]:
            pulled_long = True
        if dn and h[i] >= ma21[i]:
            pulled_short = True
        if not up:
            pulled_long = False
        if not dn:
            pulled_short = False
        rng = ha_h[i] - ha_l[i]
        if rng <= 0:
            continue
        no_bot = (min(ha_o[i], ha_c[i]) - ha_l[i]) <= 0.05 * rng and ha_c[i] > ha_o[i]
        no_top = (ha_h[i] - max(ha_o[i], ha_c[i])) <= 0.05 * rng and ha_c[i] < ha_o[i]
        if up and pulled_long and no_bot:
            k = bisect.bisect_left(plset, i - 3)
            if k > 0:
                sl = l[plset[k - 1]]
                out.append((i, 1, sl))
                pulled_long = False
        if dn and pulled_short and no_top:
            k = bisect.bisect_left(phset, i - 3)
            if k > 0:
                sl = h[phset[k - 1]]
                out.append((i, -1, sl))
                pulled_short = False
    return out


def supertrend(d, n=10, mult=2.5):
    h, l, c = d["h"], d["l"], d["c"]
    a = atr(h, l, c, n)
    ub = [None] * len(c)
    lb = [None] * len(c)
    trend = [None] * len(c)
    st = [None] * len(c)
    for i in range(len(c)):
        if a[i] is None:
            continue
        mid = (h[i] + l[i]) / 2
        bu = mid + mult * a[i]
        bl = mid - mult * a[i]
        if ub[i - 1] is not None:
            bu = bu if (bu < ub[i - 1] or c[i - 1] > ub[i - 1]) else ub[i - 1]
            bl = bl if (bl > lb[i - 1] or c[i - 1] < lb[i - 1]) else lb[i - 1]
        ub[i], lb[i] = bu, bl
        if trend[i - 1] is None:
            trend[i] = 1 if c[i] > bu else -1
        elif trend[i - 1] == 1:
            trend[i] = 1 if c[i] > lb[i] else -1
        else:
            trend[i] = -1 if c[i] < ub[i] else 1
        st[i] = lb[i] if trend[i] == 1 else ub[i]
    return trend, st


def sig_st(d):
    trend, st = supertrend(d)
    out = []
    for i in range(220, len(d["c"])):
        if trend[i] is None or trend[i - 1] is None:
            continue
        if trend[i] == 1 and trend[i - 1] == -1:
            out.append((i, 1, st[i]))
        if trend[i] == -1 and trend[i - 1] == 1:
            out.append((i, -1, st[i]))
    return out, trend


def sig_srsi(d):
    c = d["c"]
    h, l = d["h"], d["l"]
    k, dd = stoch_rsi(c)
    ma200 = smma(c, 200)
    ph, pl = pivots(h, l, 3)
    import bisect
    pls, phs = sorted(pl), sorted(ph)
    out = []
    for i in range(230, len(c)):
        if None in (k[i], k[i - 1], dd[i], dd[i - 1]):
            continue
        if k[i - 1] <= dd[i - 1] and k[i] > dd[i] and k[i - 1] < 20 and c[i] > ma200[i]:
            j = bisect.bisect_left(pls, i - 3)
            if j > 0:
                out.append((i, 1, l[pls[j - 1]]))
        if k[i - 1] >= dd[i - 1] and k[i] < dd[i] and k[i - 1] > 80 and c[i] < ma200[i]:
            j = bisect.bisect_left(phs, i - 3)
            if j > 0:
                out.append((i, -1, h[phs[j - 1]]))
    return out


def sig_rsirej(d, trend_filter=False):
    c, h, l = d["c"], d["h"], d["l"]
    r = rsi(c)
    ma200 = smma(c, 200)
    ph, pl = pivots(h, l, 3)
    import bisect
    pls, phs = sorted(pl), sorted(ph)
    out = []
    for i in range(230, len(c)):
        if r[i] is None or r[i - 1] is None:
            continue
        if r[i - 1] > 70 and r[i] < 70:
            if trend_filter and c[i] > ma200[i]:
                continue
            j = bisect.bisect_left(phs, i - 3)
            if j > 0:
                out.append((i, -1, h[phs[j - 1]]))
        if r[i - 1] < 30 and r[i] > 30:
            if trend_filter and c[i] < ma200[i]:
                continue
            j = bisect.bisect_left(pls, i - 3)
            if j > 0:
                out.append((i, 1, l[pls[j - 1]]))
    return out


def sig_ma200rt(d):
    c, h, l, o = d["c"], d["h"], d["l"], d["o"]
    ma200 = smma(c, 200)
    out = []
    for i in range(260, len(c)):
        if ma200[i] is None:
            continue
        above = sum(1 for k in range(i - 50, i) if c[k] > ma200[k])
        if above >= 40 and l[i] <= ma200[i] and c[i] > ma200[i]:
            out.append((i, 1, l[i]))
        elif above <= 10 and h[i] >= ma200[i] and c[i] < ma200[i]:
            out.append((i, -1, h[i]))
    return out


def sig_sessbrk(d, open_hour=7, range_bars_h=1):
    c, h, l, t = d["c"], d["h"], d["l"], d["t"]
    bar_ms = t[1] - t[0]
    per_h = int(3600000 // bar_ms)
    out = []
    i = 0
    n = len(c)
    while i < n:
        hour = (t[i] // 3600000) % 24
        minute = (t[i] % 3600000) // 60000
        if hour == open_hour and minute == 0:
            rb = range_bars_h * per_h
            if i + rb >= n:
                break
            rh = max(h[i:i + rb])
            rl = min(l[i:i + rb])
            mid = (rh + rl) / 2
            # look for first close beyond range in next 6h
            for j in range(i + rb, min(i + rb + 6 * per_h, n)):
                if c[j] > rh:
                    out.append((j, 1, mid))
                    break
                if c[j] < rl:
                    out.append((j, -1, mid))
                    break
            i += rb
        else:
            i += 1
    return out


def main():
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    for iv in ("15m", "30m", "1h"):
        d = load(sym, iv)
        print(f"=== {sym} {iv} ===")
        for mode in ("raw", "trend", "ma21"):
            show(taker_signals_run(d, sig_3ls(d, mode)), f"3LS {mode} 2R")
        show(taker_signals_run(d, sig_hanw(d)), "HA no-wick pullback 2R")
        st_sigs, st_trend = sig_st(d)
        show(taker_signals_run(d, st_sigs,
                               trail=lambda jj, dr: st_trend[jj] == -dr),
             "SuperTrend flip trail")
        show(taker_signals_run(d, st_sigs), "SuperTrend 2R")
        show(taker_signals_run(d, sig_srsi(d)), "StochRSI cross+200 2R")
        show(taker_signals_run(d, sig_rsirej(d)), "RSI band-rejoin 2R")
        show(taker_signals_run(d, sig_rsirej(d, True)), "RSI band-rejoin ctr-trend 2R")
        show(taker_signals_run(d, sig_ma200rt(d)), "SMMA200 retest-reject 2R")
        for oh in (7, 13):
            show(taker_signals_run(d, sig_sessbrk(d, oh)), f"Sess ORB {oh:02d}UTC 2R")


if __name__ == "__main__":
    main()
