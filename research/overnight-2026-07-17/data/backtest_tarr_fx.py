"""Retail-TA template on FOREX majors: indicator entry + ATR stop + 2:1 take-profit.

Same template as backtest_tarr.py (whose simulate/indicator engine this imports),
owner request 2026-07-17: does the classic indicator + 2:1 RR + stop-loss recipe
work on forex where it failed on crypto? Universe: 7 USD majors. Costs: 0.006%
per side (~1.3 pips round-trip on EURUSD) - a fair-to-pessimistic retail spread
on majors; swap/rollover on multi-day holds NOT modeled (see verdict caveat).

Two timeframe groups, each with its own IS/OOS split (Yahoo gives ~33 months of
1H bars but decades of daily):
  intraday 1H/4H : IS 2023-10..2024-12-31, OOS 2025-01-01..now
  daily 1D       : IS 2010-01-01..2019-12-31, OOS 2020-01-01..now
Grid per group: entries {ema9/21, ema20/50, don20, don55} x k {1.5, 2.0}.
Plus LAST-7-DAYS P&L on $200 for every config. Data: Yahoo v8 chart API
(indicative quotes - caveat), cached tarr_fx_candles.json. Read-only.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import httpx

import backtest_tarr as bt

HERE = Path(__file__).resolve().parent
CACHE = HERE / "tarr_fx_candles.json"
PAIRS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")
FEE_SIDE = 0.00006  # 0.006%/side ~= 1.3 pip round trip on EURUSD
MIN_TRADES = {"intraday": 100, "daily": 50}
SPLITS = {"intraday": ("2023-10-01", "2025-01-01"), "daily": ("2010-01-01", "2020-01-01")}
CAP = 200.0


def fetch(client: httpx.Client, pair: str, interval: str, rng: str) -> list[list]:
    # range=max silently downgrades 1d to monthly bars for FX; use explicit
    # period1/period2 timestamps for daily instead.
    if interval == "1d":
        params = {"interval": "1d", "period1": "1136073600",  # 2006-01-01
                  "period2": str(int(datetime.now(timezone.utc).timestamp()))}
    else:
        params = {"interval": interval, "range": rng}
    r = client.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}=X",
                   params=params, headers={"User-Agent": "Mozilla/5.0"})
    res = r.json()["chart"]["result"][0]
    gran = res.get("meta", {}).get("dataGranularity")
    if gran and gran != interval:
        raise RuntimeError(f"{pair}: asked {interval}, got {gran}")
    q = res["indicators"]["quote"][0]
    bars = []
    for ts, o, h, l, c in zip(res["timestamp"], q["open"], q["high"], q["low"], q["close"]):
        if None in (o, h, l, c) or min(o, h, l, c) <= 0:
            continue
        bars.append([ts * 1000, o, max(o, h, l, c), min(o, h, l, c), c])
    return bars


def load() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data = {"1H": {}, "1D": {}}
    with httpx.Client(timeout=25, trust_env=False) as client:
        for p in PAIRS:
            data["1H"][p] = fetch(client, p, "1h", "730d")
            data["1D"][p] = fetch(client, p, "1d", "max")
            print(f"{p}: {len(data['1H'][p])} 1H bars, {len(data['1D'][p])} daily bars "
                  f"(daily from {datetime.fromtimestamp(data['1D'][p][0][0]/1000, timezone.utc):%Y-%m-%d})")
    CACHE.write_text(json.dumps(data))
    return data


def run_cfg(frames: dict, entry: str, tf: str, k: float,
            d_from: str, d_to: str) -> tuple[dict, int, int, list]:
    per, tr, wn = [], 0, 0
    for p in PAIRS:
        series, t, w = bt.simulate(frames[tf][p], entry, k, d_from, d_to)
        per.append(series)
        tr += t
        wn += w
    port = bt.portfolio(per)
    return bt.stats(port), tr, wn, port


def main() -> None:
    bt.FEE = FEE_SIDE
    data = load()
    frames = {"1H": data["1H"],
              "4H": {p: bt.resample_4h(b) for p, b in data["1H"].items()},
              "1D": data["1D"]}
    last_date = max(datetime.fromtimestamp(b[0] / 1000, timezone.utc).strftime("%Y-%m-%d")
                    for b in data["1H"]["EURUSD"])
    print(f"data through {last_date}, fee {FEE_SIDE*1e4:.1f}bp/side\n")

    groups = {"intraday": [(e, tf, k) for e in ("ema9/21", "ema20/50", "don20", "don55")
                           for tf in ("1H", "4H") for k in (1.5, 2.0)],
              "daily": [(e, "1D", k) for e in ("ema9/21", "ema20/50", "don20", "don55")
                        for k in (1.5, 2.0)]}
    picks = {}
    for g, grid in groups.items():
        is_from, is_to = SPLITS[g]
        print(f"-- {g.upper()} IN-SAMPLE {is_from}..{is_to} (net, 7-pair portfolio) --")
        results = []
        for e, tf, k in grid:
            st, tr, wn, _ = run_cfg(frames, e, tf, k, is_from, is_to)
            wr = wn / tr * 100 if tr else 0.0
            results.append((st["sharpe"] if tr >= MIN_TRADES[g] else -9, e, tf, k, st, tr, wr))
            print(f"{e:9s} {tf} k={k:.1f}  Sharpe={st['sharpe']:5.2f} ann={st['ann']*100:6.1f}% "
                  f"maxDD={st['maxdd']*100:6.1f}% trades={tr:5d} win%={wr:4.1f}")
        results.sort(reverse=True, key=lambda z: z[0])
        _, e, tf, k, _, _, _ = results[0]
        picks[g] = (e, tf, k)
        print(f"\n{g} IS pick: {e} {tf} k={k}")

        print(f"\n-- {g.upper()} OUT-OF-SAMPLE {is_to}..now (frozen pick) --")
        st, tr, wn, _ = run_cfg(frames, e, tf, k, is_to, "2027-01-01")
        wr = wn / tr * 100 if tr else 0.0
        print(f"{e} {tf} k={k}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}% trades={tr} win%={wr:4.1f} ({st['n']}d)")
        print(f"  $200: ~${CAP*st['ann']/365:+.3f}/day net")

        print(f"\n-- {g.upper()} OOS sensitivity (top 5 IS configs) --")
        for _, e2, tf2, k2, _, _, _ in results[:5]:
            st2, tr2, wn2, _ = run_cfg(frames, e2, tf2, k2, is_to, "2027-01-01")
            wr2 = wn2 / tr2 * 100 if tr2 else 0.0
            print(f"{e2:9s} {tf2} k={k2:.1f}  ann={st2['ann']*100:6.1f}% Sharpe={st2['sharpe']:5.2f} "
                  f"maxDD={st2['maxdd']*100:6.1f}% trades={tr2:4d} win%={wr2:4.1f}")
        print()

    print("-- LAST 7 DAYS, every config, $200 capital (net of spread) --")
    week_from = sorted({datetime.fromtimestamp(b[0] / 1000, timezone.utc).strftime("%Y-%m-%d")
                        for b in data["1H"]["EURUSD"]})[-7]
    for g, grid in groups.items():
        for e3, tf3, k3 in grid:
            _, _, _, port3 = run_cfg(frames, e3, tf3, k3, week_from, "2027-01-01")
            pnl = CAP * (math.prod(1 + r for _, r in port3) - 1)
            mark = f" <== {g} IS pick" if (e3, tf3, k3) == picks[g] else ""
            print(f"{e3:9s} {tf3} k={k3:.1f}  week P&L on $200: ${pnl:+6.2f}{mark}")
    print(f"(week = {week_from}..{last_date}; positions entered before the week not carried in)")


if __name__ == "__main__":
    main()
