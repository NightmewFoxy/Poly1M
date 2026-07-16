"""Delta-neutral funding-harvest backtest (mechanical; public Bybit data only).

Strategy: long spot + short USDT-perp on the symbols with the highest trailing
funding; collect funding while hedged. Daily rebalance at 00:00 UTC into the top-K
symbols whose trailing annualized funding exceeds a threshold; slots with no
qualifier sit in cash. No lookahead: the day-D basket is chosen on funding data
strictly before D and earns day-D's realized funding.

Costs (pessimistic, taker everywhere): entering or exiting a slot trades spot+perp:
spot taker 0.10% + perp taker 0.055% + slippage/spread 0.05% per side
=> ~0.36% of slot notional per full rotation (0.18% per change-direction, charged
per basket change). Funding accrues on perp notional = 50% of slot capital
(1x margin, no leverage — conservative retail sizing).

Phase 1 fetches Bybit funding history since 2024-01-01 for today's top-N turnover
linear perps and caches to funding_hist_bybit.json. Phase 2 grid-searches
(K, lookback, threshold) IN-SAMPLE on 2024 and reports the frozen pick's
OUT-OF-SAMPLE result on 2025-01-01 -> today. Prints ASCII only.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CACHE = HERE / "funding_hist_bybit.json"
START_MS = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
TOP_N = 30
FEE_PER_ROTATION = 0.0036       # fraction of slot notional, full enter+exit
NOTIONAL_FRac = 0.5             # funding earned on this fraction of slot capital
IS_END = "2025-01-01"           # in-sample: 2024; OOS: 2025-01-01 onward


def fetch_universe(client: httpx.Client) -> list[str]:
    r = client.get("https://api.bybit.com/v5/market/tickers", params={"category": "linear"})
    ticks = [t for t in r.json()["result"]["list"] if t["symbol"].endswith("USDT")]
    ticks.sort(key=lambda t: float(t.get("turnover24h") or 0), reverse=True)
    return [t["symbol"] for t in ticks[:TOP_N]]


def fetch_funding(client: httpx.Client, sym: str) -> list[tuple[int, float]]:
    """All (ts_ms, rate) events for sym since START_MS, ascending."""
    out: list[tuple[int, float]] = []
    end = int(time.time() * 1000)
    while True:
        r = client.get("https://api.bybit.com/v5/market/funding/history",
                       params={"category": "linear", "symbol": sym,
                               "startTime": START_MS, "endTime": end, "limit": 200})
        rows = r.json()["result"]["list"]
        if not rows:
            break
        for t in rows:
            out.append((int(t["fundingRateTimestamp"]), float(t["fundingRate"])))
        oldest = min(int(t["fundingRateTimestamp"]) for t in rows)
        if oldest <= START_MS or len(rows) < 200:
            break
        end = oldest - 1
        time.sleep(0.06)
    out = sorted(set(out))
    return out


def load_data() -> dict[str, dict[str, float]]:
    """{sym: {date: daily funding sum}}; fetch+cache if needed."""
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data: dict[str, dict[str, float]] = {}
    with httpx.Client(timeout=20, trust_env=False) as client:
        universe = fetch_universe(client)
        print(f"universe ({len(universe)}): {','.join(universe[:10])}...")
        for i, sym in enumerate(universe):
            try:
                events = fetch_funding(client, sym)
            except Exception as e:
                print(f"  {sym}: FETCH FAIL {e}")
                continue
            daily: dict[str, float] = {}
            for ts, rate in events:
                d = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d")
                daily[d] = daily.get(d, 0.0) + rate
            data[sym] = daily
            print(f"  [{i+1}/{len(universe)}] {sym}: {len(events)} events")
    CACHE.write_text(json.dumps(data))
    return data


def simulate(data: dict[str, dict[str, float]], dates: list[str],
             k: int, lookback: int, thresh_apr: float) -> tuple[float, float, int]:
    """Returns (total net return fraction on capital, worst 30d net, n_rotations)."""
    idx = {d: i for i, d in enumerate(dates)}
    daily_ret: list[float] = []
    prev_basket: set[str] = set()
    rotations = 0
    for i, d in enumerate(dates):
        # signal: trailing funding over [i-lookback, i)
        if i < lookback:
            daily_ret.append(0.0)
            continue
        window = dates[i - lookback:i]
        scores = {}
        for sym, daily in data.items():
            vals = [daily.get(w) for w in window]
            vals = [v for v in vals if v is not None]
            if len(vals) < lookback // 2 + 1:
                continue
            apr = (sum(vals) / len(vals)) * 365
            if apr > thresh_apr:
                scores[sym] = apr
        basket = set(sorted(scores, key=scores.get, reverse=True)[:k])
        changes = len(basket - prev_basket) + len(prev_basket - basket)
        rotations += changes
        # realized funding today on basket (equal slots, NOTIONAL_FRac of slot)
        gross = 0.0
        for sym in basket:
            gross += data[sym].get(d, 0.0) * NOTIONAL_FRac / k
        cost = changes * (FEE_PER_ROTATION / 2) / k  # half rotation per change
        daily_ret.append(gross - cost)
        prev_basket = basket
    # aggregate
    total = 1.0
    for r in daily_ret:
        total *= (1 + r)
    worst30 = min(
        (sum(daily_ret[j:j + 30]) for j in range(0, max(1, len(daily_ret) - 30))),
        default=0.0)
    return total - 1.0, worst30, rotations


def main() -> None:
    data = load_data()
    all_dates = sorted({d for daily in data.values() for d in daily})
    is_dates = [d for d in all_dates if d < IS_END]
    oos_dates = [d for d in all_dates if d >= IS_END]
    print(f"\ndates: {all_dates[0]}..{all_dates[-1]}  IS={len(is_dates)}d OOS={len(oos_dates)}d")
    print(f"symbols cached: {len(data)}")

    grid = [(k, lb, th) for k in (1, 3, 5) for lb in (3, 7, 14) for th in (0.0, 0.05, 0.10)]
    print("\n-- IN-SAMPLE 2024 grid (net return on capital) --")
    best, best_ret = None, -9e9
    for k, lb, th in grid:
        ret, w30, rot = simulate(data, is_dates, k, lb, th)
        apr = ret / max(len(is_dates), 1) * 365
        print(f"K={k} lb={lb:2d}d th={int(th*100):3d}%  net={ret*100:6.2f}%  (~{apr*100:5.1f}%/yr)  worst30d={w30*100:5.2f}%  rot={rot}")
        if ret > best_ret:
            best, best_ret = (k, lb, th), ret
    k, lb, th = best
    print(f"\nIS pick: K={k} lb={lb}d th={int(th*100)}%")

    ret, w30, rot = simulate(data, oos_dates, k, lb, th)
    days = len(oos_dates)
    apr = ret / max(days, 1) * 365
    print("\n-- OUT-OF-SAMPLE 2025-01-01 .. today (frozen params) --")
    print(f"net={ret*100:.2f}% over {days}d  => {apr*100:.2f}%/yr net")
    print(f"worst 30d: {w30*100:.2f}%   rotations: {rot}")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*apr/365:.2f}/day net")
    # also show OOS for a couple of robust alternates to see param sensitivity
    print("\n-- OOS param sensitivity (top alternates) --")
    for kk, lbb, thh in [(3, 7, 0.05), (3, 14, 0.10), (5, 7, 0.05), (1, 7, 0.10)]:
        r2, w2, ro2 = simulate(data, oos_dates, kk, lbb, thh)
        print(f"K={kk} lb={lbb:2d}d th={int(thh*100):3d}%  OOSnet={r2*100:6.2f}% (~{r2/max(days,1)*365*100:5.1f}%/yr) worst30d={w2*100:5.2f}%")


if __name__ == "__main__":
    main()
