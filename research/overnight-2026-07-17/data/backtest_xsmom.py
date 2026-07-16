"""Cross-sectional momentum/reversal on OKX USDT perps (long/short; mechanical).

Universe: top-N USDT swaps by current 24h USD volume (survivorship caveat noted in
verdict — delisted perps are absent; symbols enter the backtest when their data
starts). Weekly rebalance at close: rank by trailing R-day return; LONG top
quintile, SHORT bottom quintile, equal weight, gross 1x (0.5 long / 0.5 short).
Variants: momentum (long winners) and reversal (long losers); lookbacks include a
28d-skip-7 variant. Fees 0.07% per side on turnover. No lookahead: weights chosen
at close t apply to day t+1 returns.

IS = 2022-01-01..2023-12-31 (grid, pick by Sharpe); OOS = 2024-01-01..now (frozen).
Data: OKX history-candles 1Dutc from 2021-10-01, cached xsmom_candles.json.
ASCII output only.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CACHE = HERE / "xsmom_candles.json"
TOP_N = 40
FEE = 0.0007
FETCH_FROM = "2021-10-01"
IS_START, IS_END = "2022-01-01", "2024-01-01"
REB_EVERY = 7
QUANTILE = 5


def now_ms() -> int:
    return int(time.time() * 1000)


def fetch_universe(client: httpx.Client) -> list[str]:
    r = client.get("https://www.okx.com/api/v5/market/tickers", params={"instType": "SWAP"})
    rows = [t for t in r.json()["data"] if t["instId"].endswith("-USDT-SWAP")]
    def usd_vol(t):
        try:
            return float(t["volCcy24h"]) * float(t["last"])
        except Exception:
            return 0.0
    rows.sort(key=usd_vol, reverse=True)
    return [t["instId"] for t in rows[:TOP_N]]


def fetch_daily(client: httpx.Client, inst: str, start: str) -> dict[str, float]:
    """{date: close} via history-candles, backward pagination."""
    t0 = int(datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    closes: dict[str, float] = {}
    after = None
    while True:
        params = {"instId": inst, "bar": "1Dutc", "limit": "100"}
        if after is not None:
            params["after"] = str(after)
        try:
            r = client.get("https://www.okx.com/api/v5/market/history-candles", params=params)
            rows = r.json().get("data") or []
        except Exception:
            time.sleep(1.0)
            continue
        if not rows:
            break
        for k in rows:
            if k[-1] != "1":
                continue
            d = datetime.fromtimestamp(int(k[0]) / 1000, timezone.utc).strftime("%Y-%m-%d")
            closes[d] = float(k[4])
        oldest = min(int(k[0]) for k in rows)
        if oldest <= t0:
            break
        after = oldest
        time.sleep(0.12)
    return closes


def load() -> dict[str, dict[str, float]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data: dict[str, dict[str, float]] = {}
    with httpx.Client(timeout=20, trust_env=False) as client:
        universe = fetch_universe(client)
        print(f"universe ({len(universe)}): {','.join(u.replace('-USDT-SWAP','') for u in universe[:12])}...")
        for i, inst in enumerate(universe):
            closes = fetch_daily(client, inst, FETCH_FROM)
            if len(closes) >= 60:
                data[inst] = closes
            print(f"  [{i+1}/{len(universe)}] {inst}: {len(closes)}d")
    CACHE.write_text(json.dumps(data))
    return data


def daily_rets(closes: dict[str, float], dates: list[str]) -> dict[str, float]:
    out = {}
    prev = None
    for d in dates:
        c = closes.get(d)
        if c is not None and prev is not None:
            out[d] = c / prev - 1
        if c is not None:
            prev = c
    return out


def trailing_ret(closes: dict[str, float], dates: list[str], i: int, lb: int, skip: int = 0) -> float | None:
    d_now, d_then = dates[i - skip], dates[i - lb]
    a, b = closes.get(d_now), closes.get(d_then)
    if a is None or b is None or b == 0:
        return None
    return a / b - 1


def simulate(data: dict[str, dict[str, float]], dates: list[str], lb: int, skip: int,
             reverse: bool, d_from: str, d_to: str) -> list[tuple[str, float]]:
    rets = {inst: daily_rets(cl, dates) for inst, cl in data.items()}
    weights: dict[str, float] = {}
    out = []
    for i, d in enumerate(dates[:-1]):
        nxt = dates[i + 1]
        if i >= lb and (i % REB_EVERY == 0):
            scores = {}
            for inst, cl in data.items():
                # need the symbol to have today's close and enough history
                tr = trailing_ret(cl, dates, i, lb, skip)
                if tr is not None and cl.get(d) is not None:
                    scores[inst] = tr
            if len(scores) >= QUANTILE * 2:
                ranked = sorted(scores, key=scores.get, reverse=not reverse)
                q = max(2, len(ranked) // QUANTILE)
                longs, shorts = ranked[:q], ranked[-q:]
                new_w = {s: 0.5 / q for s in longs}
                new_w.update({s: -0.5 / q for s in shorts})
                cost = sum(abs(new_w.get(s, 0) - weights.get(s, 0))
                           for s in set(new_w) | set(weights)) * FEE
                weights = new_w
            else:
                cost = 0.0
        else:
            cost = 0.0
        r = sum(w * rets[inst].get(nxt, 0.0) for inst, w in weights.items()) - cost
        if d_from <= nxt < d_to:
            out.append((nxt, r))
    return out


def stats(series: list[tuple[str, float]]) -> dict:
    rs = [r for _, r in series]
    n = len(rs)
    if n < 30:
        return {"n": n, "ann": 0.0, "sharpe": 0.0, "maxdd": 0.0, "worst30": 0.0, "total": 0.0}
    total, peak, maxdd = 1.0, 1.0, 0.0
    for r in rs:
        total *= 1 + r
        peak = max(peak, total)
        maxdd = min(maxdd, total / peak - 1)
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1))
    return {"n": n, "ann": total ** (365 / n) - 1, "sharpe": (m / sd * math.sqrt(365)) if sd else 0,
            "maxdd": maxdd, "worst30": min((sum(rs[j:j + 30]) for j in range(max(1, n - 30))), default=0),
            "total": total - 1}


def main() -> None:
    import sys
    data = load()
    if "--oldguard" in sys.argv:
        # survivorship control: only perps with full history since ~2021
        data = {k: v for k, v in data.items() if len(v) >= 1700}
        print(f"OLD-GUARD universe: {','.join(k.replace('-USDT-SWAP','') for k in data)}")
    dates = sorted({d for cl in data.values() for d in cl})
    print(f"{len(data)} symbols, {dates[0]}..{dates[-1]}\n")

    grid = []
    for lb, skip in ((7, 0), (14, 0), (28, 0), (60, 0), (28, 7)):
        for reverse in (False, True):
            grid.append((lb, skip, reverse))

    print("-- IN-SAMPLE 2022-2023 (net, weekly rebalance, quintile L/S gross 1x) --")
    results = []
    for lb, skip, rev in grid:
        st = stats(simulate(data, dates, lb, skip, rev, IS_START, IS_END))
        results.append((st["sharpe"], lb, skip, rev, st))
        print(f"lb={lb:3d} skip={skip} {'REV' if rev else 'MOM'}  Sharpe={st['sharpe']:5.2f} "
              f"ann={st['ann']*100:7.1f}% maxDD={st['maxdd']*100:6.1f}% worst30={st['worst30']*100:6.1f}% ({st['n']}d)")
    results.sort(reverse=True, key=lambda x: x[0])
    _, lb, skip, rev, _ = results[0]
    print(f"\nIS pick: lb={lb} skip={skip} {'REV' if rev else 'MOM'}")

    print("\n-- OUT-OF-SAMPLE 2024-01-01..now (frozen) --")
    st = stats(simulate(data, dates, lb, skip, rev, IS_END, "2027-01-01"))
    print(f"IS-pick: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} maxDD={st['maxdd']*100:6.1f}% "
          f"worst30={st['worst30']*100:6.1f}% total={st['total']*100:6.1f}% ({st['n']}d)")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*st['ann']/365:.2f}/day net")

    print("\n-- OOS all combos (sensitivity/decay map) --")
    for lb2, skip2, rev2 in grid:
        st2 = stats(simulate(data, dates, lb2, skip2, rev2, IS_END, "2027-01-01"))
        print(f"lb={lb2:3d} skip={skip2} {'REV' if rev2 else 'MOM'}  ann={st2['ann']*100:7.1f}% "
              f"Sharpe={st2['sharpe']:5.2f} maxDD={st2['maxdd']*100:6.1f}%")

    # selection-free ensemble: equal capital across the four no-skip MOM lookbacks
    print("\n-- OOS selection-free MOM ensemble (lb 7/14/28/60, no-skip, equal wt) --")
    series = [dict(simulate(data, dates, lb3, 0, False, IS_END, "2027-01-01"))
              for lb3 in (7, 14, 28, 60)]
    common = sorted(set(series[0]) & set(series[1]) & set(series[2]) & set(series[3]))
    ens = [(d, sum(s[d] for s in series) / 4) for d in common]
    st3 = stats(ens)
    print(f"ensemble: ann={st3['ann']*100:6.1f}% Sharpe={st3['sharpe']:5.2f} "
          f"maxDD={st3['maxdd']*100:6.1f}% worst30={st3['worst30']*100:6.1f}% ({st3['n']}d)")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*st3['ann']/365:.2f}/day net")
    # and its in-sample counterpart for the record
    series_is = [dict(simulate(data, dates, lb3, 0, False, IS_START, IS_END))
                 for lb3 in (7, 14, 28, 60)]
    common_is = sorted(set(series_is[0]) & set(series_is[1]) & set(series_is[2]) & set(series_is[3]))
    st4 = stats([(d, sum(s[d] for s in series_is) / 4) for d in common_is])
    print(f"(IS 2022-23 ensemble: ann={st4['ann']*100:6.1f}% Sharpe={st4['sharpe']:5.2f} maxDD={st4['maxdd']*100:6.1f}%)")


if __name__ == "__main__":
    main()
