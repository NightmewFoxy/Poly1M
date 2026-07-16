"""Seasonality tests on BTC/ETH/SOL hourly closes (long/short perps; mechanical).

A) PRE-REGISTERED external hypotheses (tested exactly, no fitting):
   H1: long BTC daily 21:00->23:00 UTC (QuantPedia time-of-day).
   H2: long BTC Sunday 21:00 UTC -> Monday 08:00 UTC ("Monday Asia open").
   H3: long BTC weekends: Saturday 00:00 -> Monday 00:00 UTC.
B) DISCOVERY with discipline: per-hour mean returns IS 2022-2024 -> pick top-2
   contiguous 2-6h windows by |t| -> confirm OOS 2025->now. Same for day-of-week
   (long best / short worst).

Fees: 0.07% per side => 0.14% per round trip (per traded day for daily windows;
per week for dow strategy). Reports gross AND net with t-stats. Data: cached
rsimr_candles_1h.json (OKX 1H). ASCII output only.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "rsimr_candles_1h.json"
FEE_RT = 0.0014
IS_START, IS_END = "2022-01-01", "2025-01-01"


def load() -> dict[str, list[tuple[str, int, int, float]]]:
    """{sym: [(date, hour_utc, dow, hourly_return)]}; hour = hour the bar ENDS."""
    raw = json.loads(CACHE.read_text())
    out = {}
    for sym, bars in raw.items():
        rows = []
        for i in range(1, len(bars)):
            ts, c = bars[i]
            _, cp = bars[i - 1]
            dt = datetime.fromtimestamp(ts / 1000, timezone.utc)
            end = dt  # bar open time; return accrues open->open of next... use open ts convention
            rows.append((dt.strftime("%Y-%m-%d"), dt.hour, dt.weekday(), c / cp - 1))
        out[sym] = rows
    return out


def tstat(vals: list[float]) -> float:
    n = len(vals)
    if n < 10:
        return 0.0
    m = sum(vals) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def window_daily(rows, h_from: int, h_to: int, d_from: str, d_to: str,
                 dows: set[int] | None = None) -> list[float]:
    """Per-traded-day gross returns for holding hours [h_from, h_to) UTC each day.
    Hours are the bar-open hours whose returns we collect (h_from <= h < h_to,
    wrapping if needed)."""
    hours = set()
    h = h_from
    while h != h_to:
        hours.add(h)
        h = (h + 1) % 24
    byd: dict[str, float] = {}
    for d, hh, dow, r in rows:
        if d_from <= d < d_to and hh in hours and (dows is None or dow in dows):
            byd[d] = byd.get(d, 0.0) + r  # sum of hourly rets ~ window ret
    return [v for _, v in sorted(byd.items())]


def simple_report(label: str, vals: list[float], fee: float, years: float) -> None:
    n = len(vals)
    if n < 10:
        print(f"{label:44s}: n={n} (too few events)")
        return
    g = sum(vals) / n
    nm = g - fee
    ann_net = nm * (n / years)
    print(f"{label:44s}: n={n:4d} gross={g*10000:6.1f}bp (t={tstat(vals):5.2f}) "
          f"net={nm*10000:6.1f}bp (t={tstat([v - fee for v in vals]):5.2f}) ann-net={ann_net*100:6.1f}%")


def years_between(d0: str, d1: str) -> float:
    a = datetime.strptime(d0, "%Y-%m-%d")
    b = datetime.strptime(d1, "%Y-%m-%d")
    return (b - a).days / 365.25


def main() -> None:
    data = load()
    btc = data["BTC-USDT"]
    last_date = max(d for d, _, _, _ in btc)
    oos_years = years_between("2025-01-01", last_date)
    is_years = years_between("2022-01-01", "2025-01-01")
    full_years = years_between("2022-01-01", last_date)
    print(f"data through {last_date}\n")

    print("== A) PRE-REGISTERED (BTC, full 2022->now, then 2025->now) ==")
    for (lbl, hf, ht, dows) in [
        ("H1 long 21:00->23:00 UTC daily", 21, 23, None),
        ("H2 long Sun 21:00 -> Mon 08:00 UTC", 21, 8, None),  # dows filter applied below
        ("H3 long weekend Sat00 -> Mon00 UTC", 0, 0, {5, 6}),
    ]:
        if lbl.startswith("H2"):
            # hours 21-23 on Sunday (dow 6) + 0-7 on Monday (dow 0)
            vals_full, vals_oos = [], []
            for span, sink in ((("2022-01-01", "2027-01-01"), vals_full), (("2025-01-01", "2027-01-01"), vals_oos)):
                byd: dict[str, float] = {}
                for d, hh, dow, r in btc:
                    if span[0] <= d < span[1] and ((dow == 6 and hh >= 21) or (dow == 0 and hh < 8)):
                        key = d  # groups Sun evening with its own date; fine for event stats
                        byd[key] = byd.get(key, 0.0) + r
                sink.extend(v for _, v in sorted(byd.items()))
            simple_report(lbl + " [full]", vals_full, FEE_RT, full_years)
            simple_report(lbl + " [2025->]", vals_oos, FEE_RT, oos_years)
            continue
        if lbl.startswith("H3"):
            vals_full = window_daily(btc, 0, 0, "2022-01-01", "2027-01-01", dows={5, 6})
            vals_oos = window_daily(btc, 0, 0, "2025-01-01", "2027-01-01", dows={5, 6})
            # weekend = 2 daily events but 1 round trip / weekend => halve fee per event
            simple_report(lbl + " [full]", vals_full, FEE_RT / 2, full_years)
            simple_report(lbl + " [2025->]", vals_oos, FEE_RT / 2, oos_years)
            continue
        vals_full = window_daily(btc, hf, ht, "2022-01-01", "2027-01-01")
        vals_oos = window_daily(btc, hf, ht, "2025-01-01", "2027-01-01")
        simple_report(lbl + " [full]", vals_full, FEE_RT, full_years)
        simple_report(lbl + " [2025->]", vals_oos, FEE_RT, oos_years)

    print("\n== B) DISCOVERY: hour-of-day (pooled BTC+ETH+SOL, IS 2022-2024) ==")
    pooled = [(d, hh, dow, r) for sym in data.values() for (d, hh, dow, r) in sym]
    by_h: dict[int, list[float]] = {}
    for d, hh, dow, r in pooled:
        if IS_START <= d < IS_END:
            by_h.setdefault(hh, []).append(r)
    hour_stats = {h: (sum(v) / len(v), tstat(v)) for h, v in by_h.items()}
    for h in range(24):
        m, t = hour_stats[h]
        bar = "#" * min(20, int(abs(t) * 4)) if t else ""
        print(f"  h{h:02d}: {m*10000:6.2f}bp t={t:5.2f} {'+' if m>0 else '-'}{bar}")

    # top contiguous windows 2-6h by |sum of means| * sign consistency, ranked by |t| of window sums
    best = []
    for L in (2, 3, 4, 6):
        for h0 in range(24):
            hrs = [(h0 + k) % 24 for k in range(L)]
            vals = window_daily_pooled(pooled, hrs, IS_START, IS_END)
            best.append((abs(tstat(vals)), h0, L, sum(vals) / len(vals), tstat(vals)))
    best.sort(reverse=True)
    print("\n  top-3 IS windows (pooled):")
    picks = []
    used = set()
    for absT, h0, L, m, t in best:
        span = {(h0 + k) % 24 for k in range(L)}
        if span & used:
            continue
        picks.append((h0, L, m, t))
        used |= span
        print(f"    {h0:02d}:00->{(h0+L)%24:02d}:00 UTC  {m*10000:6.1f}bp/day t={t:5.2f}")
        if len(picks) == 3:
            break

    print("\n  OOS 2025->now for those windows (sign from IS, fees included):")
    for h0, L, m, t in picks:
        hrs = [(h0 + k) % 24 for k in range(L)]
        vals = window_daily_pooled(pooled, hrs, "2025-01-01", "2027-01-01")
        sign = 1 if m > 0 else -1
        simple_report(f"    {'long' if sign>0 else 'short'} {h0:02d}->{(h0+L)%24:02d} UTC",
                      [sign * v for v in vals], FEE_RT, oos_years)

    print("\n== C) DISCOVERY: day-of-week (BTC daily, IS 2022-2024 -> OOS) ==")
    dnames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    by_dow_is: dict[int, list[float]] = {}
    by_dow_oos: dict[int, list[float]] = {}
    byd: dict[str, tuple[int, float]] = {}
    for d, hh, dow, r in btc:
        cur = byd.get(d, (dow, 0.0))
        byd[d] = (dow, cur[1] + r)
    for d, (dow, r) in byd.items():
        if IS_START <= d < IS_END:
            by_dow_is.setdefault(dow, []).append(r)
        elif d >= "2025-01-01":
            by_dow_oos.setdefault(dow, []).append(r)
    for dow in range(7):
        v = by_dow_is.get(dow, [])
        m, t = (sum(v) / len(v), tstat(v)) if v else (0, 0)
        vo = by_dow_oos.get(dow, [])
        mo, to = (sum(vo) / len(vo), tstat(vo)) if vo else (0, 0)
        print(f"  {dnames[dow]}: IS {m*10000:6.1f}bp (t={t:5.2f})   OOS {mo*10000:6.1f}bp (t={to:5.2f})")
    bd = max(by_dow_is, key=lambda k: sum(by_dow_is[k]) / len(by_dow_is[k]))
    wd = min(by_dow_is, key=lambda k: sum(by_dow_is[k]) / len(by_dow_is[k]))
    lv = [x for x in by_dow_oos.get(bd, [])]
    sv = [-x for x in by_dow_oos.get(wd, [])]
    simple_report(f"  OOS long {dnames[bd]} (IS-best)", lv, FEE_RT, oos_years)
    simple_report(f"  OOS short {dnames[wd]} (IS-worst)", sv, FEE_RT, oos_years)


def window_daily_pooled(pooled, hrs, d_from, d_to) -> list[float]:
    hs = set(hrs)
    byd: dict[str, float] = {}
    for d, hh, dow, r in pooled:
        if d_from <= d < d_to and hh in hs:
            byd[d] = byd.get(d, 0.0) + r / 3.0  # pooled across 3 symbols
    return [v for _, v in sorted(byd.items())]


if __name__ == "__main__":
    main()
