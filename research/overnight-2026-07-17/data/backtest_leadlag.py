"""(A) BTC->alts lead-lag and (B) intraday time-series momentum, hourly data.

A: when BTC's trailing k-hour return exceeds a threshold, take a position in
   ETH+SOL (follow or fade) for the next h hours; one position at a time per alt;
   fees 0.07%/side (0.14% per event). Grid: k{4,24} x thr x h{4,12,24} x dir,
   IS 2022-2024 pick by Sharpe (>=30 events), frozen -> OOS 2025->now.
   LIMITATION (noted in verdict): majors-only universe (cached data); true
   lead-lag plays are usually vs small alts.

B: sign of BTC's first F hours of the UTC day -> hold same sign for the rest of
   the day; variants F{1,2} x {all days, high-vol days only (trailing 24h realized
   vol > trailing 30d median)}. Fees 0.14%/traded day. Same IS/OOS split.

Data: cached OKX 1H candles (rsimr_candles_1h.json). ASCII output only.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "rsimr_candles_1h.json"
FEE_RT = 0.0014
IS_START, IS_END = "2022-01-01", "2025-01-01"


def load():
    raw = json.loads(CACHE.read_text())
    out = {}
    for sym, bars in raw.items():
        ts = [b[0] for b in bars]
        cl = [b[1] for b in bars]
        out[sym] = (ts, cl)
    return out


def tstat(vals):
    n = len(vals)
    if n < 5:
        return 0.0
    m = sum(vals) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def stats_events(vals, years):
    n = len(vals)
    if n < 20:
        return None
    m = sum(vals) / n
    return {"n": n, "mean_bp": m * 10000, "t": tstat(vals), "ann": m * n / years}


def date_of(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def lead_lag_events(data, k, thr, h, follow, d_from, d_to):
    """Event returns (net) on ETH+SOL when BTC |k-hour ret| > thr."""
    ts_b, cl_b = data["BTC-USDT"]
    idx_b = {t: i for i, t in enumerate(ts_b)}
    events = []
    for alt in ("ETH-USDT", "SOL-USDT"):
        ts_a, cl_a = data[alt]
        idx_a = {t: i for i, t in enumerate(ts_a)}
        i = k
        while i < len(ts_b) - h - 1:
            t = ts_b[i]
            d = date_of(t)
            if not (d_from <= d < d_to):
                i += 1
                continue
            btc_ret = cl_b[i] / cl_b[i - k] - 1
            if abs(btc_ret) >= thr:
                j = idx_a.get(t)
                if j is not None and j + h < len(cl_a):
                    alt_ret = cl_a[j + h] / cl_a[j] - 1
                    sign = 1 if btc_ret > 0 else -1
                    if not follow:
                        sign = -sign
                    events.append(sign * alt_ret - FEE_RT)
                i += h  # one position at a time
            else:
                i += 1
    return events


def intraday_events(data, first_h, vol_filter, d_from, d_to):
    ts_b, cl_b = data["BTC-USDT"]
    # group indices by UTC date
    by_day: dict[str, list[int]] = {}
    for i, t in enumerate(ts_b):
        by_day.setdefault(date_of(t), []).append(i)
    days = sorted(by_day)
    # trailing realized vol (24h of hourly rets) per day boundary
    rets = [0.0] + [cl_b[i] / cl_b[i - 1] - 1 for i in range(1, len(cl_b))]
    events = []
    vol_hist = []
    for d in days:
        idxs = by_day[d]
        if len(idxs) < 24:
            continue
        i0 = idxs[0]
        if i0 < 24 * 30:
            continue
        # day's realized vol yesterday (for filter) from the 24 hourly rets before i0
        w = rets[i0 - 24:i0]
        m = sum(w) / 24
        vol = math.sqrt(sum((x - m) ** 2 for x in w) / 23)
        vol_hist.append(vol)
        med = sorted(vol_hist[-30:])[len(vol_hist[-30:]) // 2]
        if not (d_from <= d < d_to):
            continue
        first_ret = cl_b[i0 + first_h - 1] / cl_b[i0 - 1] - 1 if i0 > 0 else 0
        rest_ret = cl_b[idxs[-1]] / cl_b[i0 + first_h - 1] - 1
        if vol_filter and vol <= med:
            continue
        sign = 1 if first_ret > 0 else -1
        events.append(sign * rest_ret - FEE_RT)
    return events


def main():
    data = load()
    is_years, oos_years = 3.0, 1.55

    print("== A) BTC -> ETH/SOL lead-lag ==")
    grid = []
    for k, thrs in ((4, (0.01, 0.02)), (24, (0.02, 0.04))):
        for thr in thrs:
            for h in (4, 12, 24):
                for follow in (True, False):
                    grid.append((k, thr, h, follow))
    results = []
    print(f"{'cfg':28s}  {'IS mean_bp':>10s} {'t':>6s} {'n':>5s} {'ann':>7s}")
    for k, thr, h, follow in grid:
        ev = lead_lag_events(data, k, thr, h, follow, IS_START, IS_END)
        st = stats_events(ev, is_years)
        if st:
            results.append((st["t"], k, thr, h, follow, st))
            print(f"k={k:2d} thr={thr*100:3.0f}% h={h:2d} {'FOLLOW' if follow else 'FADE  '}"
                  f"  {st['mean_bp']:10.1f} {st['t']:6.2f} {st['n']:5d} {st['ann']*100:6.1f}%")
    if results:
        results.sort(reverse=True, key=lambda r: r[0])
        _, k, thr, h, follow, _ = results[0]
        print(f"\nIS pick: k={k} thr={thr*100:.0f}% h={h} {'FOLLOW' if follow else 'FADE'}")
        ev = lead_lag_events(data, k, thr, h, follow, IS_END, "2027-01-01")
        st = stats_events(ev, oos_years)
        if st:
            print(f"OOS: mean={st['mean_bp']:.1f}bp t={st['t']:.2f} n={st['n']} ann-net={st['ann']*100:.1f}%")
        else:
            print("OOS: too few events")

    print("\n== B) intraday tsmom (BTC, first hours -> rest of day) ==")
    for first_h in (1, 2):
        for vf in (False, True):
            lbl = f"F={first_h} {'high-vol only' if vf else 'all days     '}"
            is_ev = intraday_events(data, first_h, vf, IS_START, IS_END)
            oos_ev = intraday_events(data, first_h, vf, IS_END, "2027-01-01")
            st_is = stats_events(is_ev, is_years)
            st_oos = stats_events(oos_ev, oos_years)
            if st_is and st_oos:
                print(f"{lbl}: IS mean={st_is['mean_bp']:6.1f}bp t={st_is['t']:5.2f} n={st_is['n']:4d} "
                      f"ann={st_is['ann']*100:6.1f}% | OOS mean={st_oos['mean_bp']:6.1f}bp "
                      f"t={st_oos['t']:5.2f} n={st_oos['n']:4d} ann={st_oos['ann']*100:6.1f}%")


if __name__ == "__main__":
    main()
