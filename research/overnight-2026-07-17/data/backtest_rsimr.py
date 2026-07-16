"""RSI mean-reversion backtest on BTC/ETH/SOL, 1H + 4H bars (long/short perps).

Spec: RSI(n) Wilder-smoothed on bar closes. LONG when RSI < X, SHORT when
RSI > 100-X (both sides always enabled); exit when RSI crosses 50 or after
MAX_HOLD bars. Optional trend filter: longs only if close > SMA200, shorts only
if close < SMA200 (Connors style). No lookahead: signal at close t earns from
bar t+1. Fees 0.07% per side of turnover. Portfolio = equal-weight average of
the three symbols' per-bar strategy returns.

Grid: timeframe x n{2,14} x X{10,20,30} x filter{none,sma200} — searched
IN-SAMPLE 2022-01-01..2024-12-31, picked by Sharpe (min 100 trades), frozen,
reported OUT-OF-SAMPLE 2025-01-01..now. 4H bars are resampled locally from the
fetched 1H data. Data: OKX history-candles 1H (cached rsimr_candles_1h.json).
ASCII output only.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CACHE = HERE / "rsimr_candles_1h.json"
SYMS = ("BTC-USDT", "ETH-USDT", "SOL-USDT")
FETCH_FROM = "2021-10-01"
FEE = 0.0007
IS_START, IS_END = "2022-01-01", "2025-01-01"
MAX_HOLD = 48  # bars
MIN_TRADES_IS = 100


def fetch_1h(client: httpx.Client, inst: str, start: str) -> list[list]:
    t0 = int(datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    seen: dict[int, list] = {}
    after = None
    while True:
        params = {"instId": inst, "bar": "1H", "limit": "100"}
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
            if k[-1] == "1":
                seen[int(k[0])] = [int(k[0]), float(k[4])]  # ts, close
        oldest = min(int(k[0]) for k in rows)
        if oldest <= t0:
            break
        after = oldest
        time.sleep(0.11)
    return [seen[ts] for ts in sorted(seen) if ts >= t0]


def load() -> dict[str, list[list]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data = {}
    with httpx.Client(timeout=20, trust_env=False) as client:
        for s in SYMS:
            data[s] = fetch_1h(client, s, FETCH_FROM)
            print(f"{s}: {len(data[s])} hourly bars")
    CACHE.write_text(json.dumps(data))
    return data


def resample_4h(bars: list[list]) -> list[list]:
    out = []
    for ts, c in bars:
        if (ts // 3600000) % 4 == 3:  # close of the 4h block (00-03,04-07,... UTC)
            out.append([ts, c])
    return out


def rsi_series(closes: list[float], n: int) -> list[float]:
    rsis = [50.0] * len(closes)
    up = dn = 0.0
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        u, d = max(ch, 0.0), max(-ch, 0.0)
        if i <= n:
            up += u / n
            dn += d / n
            rsis[i] = 50.0
        else:
            up = (up * (n - 1) + u) / n
            dn = (dn * (n - 1) + d) / n
            rsis[i] = 100.0 if dn == 0 else 100.0 - 100.0 / (1.0 + up / dn)
    return rsis


def sma_series(closes: list[float], n: int) -> list[float]:
    out = [0.0] * len(closes)
    s = 0.0
    for i, c in enumerate(closes):
        s += c
        if i >= n:
            s -= closes[i - n]
        out[i] = s / n if i >= n - 1 else float("nan")
    return out


def simulate(bars: list[list], n: int, x: float, use_filter: bool,
             d_from: str, d_to: str) -> tuple[list[tuple[str, float]], int]:
    closes = [b[1] for b in bars]
    dates = [datetime.fromtimestamp(b[0] / 1000, timezone.utc).strftime("%Y-%m-%d") for b in bars]
    rsis = rsi_series(closes, n)
    sma = sma_series(closes, 200)
    pos = 0
    hold = 0
    trades = 0
    out = []
    for i in range(1, len(bars)):
        # return earned this bar from position decided at bar i-1
        prev_pos = pos if False else None  # placeholder (clarity)
        r = pos * (closes[i] / closes[i - 1] - 1)
        # decide new position at close i (affects bar i+1)
        new_pos = pos
        if pos == 0:
            long_ok = (not use_filter) or (not math.isnan(sma[i]) and closes[i] > sma[i])
            short_ok = (not use_filter) or (not math.isnan(sma[i]) and closes[i] < sma[i])
            if rsis[i] < x and long_ok and i > 200:
                new_pos = 1
            elif rsis[i] > 100 - x and short_ok and i > 200:
                new_pos = -1
        else:
            hold += 1
            if (pos == 1 and rsis[i] > 50) or (pos == -1 and rsis[i] < 50) or hold >= MAX_HOLD:
                new_pos = 0
        if new_pos != pos:
            r -= FEE * abs(new_pos - pos)
            if new_pos != 0:
                trades += 1
            hold = 0
        pos = new_pos
        if d_from <= dates[i] < d_to:
            out.append((dates[i], r))
    return out, trades


def daily_agg(series: list[tuple[str, float]]) -> list[tuple[str, float]]:
    byd: dict[str, float] = {}
    for d, r in series:
        byd[d] = byd.get(d, 0.0) + r
    return sorted(byd.items())


def portfolio(per_sym: list[list[tuple[str, float]]]) -> list[tuple[str, float]]:
    byd: dict[str, list[float]] = {}
    for s in per_sym:
        for d, r in daily_agg(s):
            byd.setdefault(d, []).append(r)
    return sorted((d, sum(v) / len(v)) for d, v in byd.items())


def stats(series: list[tuple[str, float]]) -> dict:
    rs = [r for _, r in series]
    n = len(rs)
    if n < 30:
        return {"n": n, "ann": 0.0, "sharpe": 0.0, "maxdd": 0.0, "worst30": 0.0}
    total, peak, maxdd = 1.0, 1.0, 0.0
    for r in rs:
        total *= 1 + r
        peak = max(peak, total)
        maxdd = min(maxdd, total / peak - 1)
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1))
    return {"n": n, "ann": total ** (365 / n) - 1, "sharpe": (m / sd * math.sqrt(365)) if sd else 0.0,
            "maxdd": maxdd, "worst30": min((sum(rs[j:j + 30]) for j in range(max(1, n - 30))), default=0.0)}


def main() -> None:
    data1h = load()
    frames = {"1H": data1h, "4H": {s: resample_4h(b) for s, b in data1h.items()}}
    print()

    grid = [(tf, n, x, f) for tf in ("1H", "4H") for n in (2, 14)
            for x in (10.0, 20.0, 30.0) for f in (False, True)]

    print("-- IN-SAMPLE 2022-2024 (net, portfolio of BTC/ETH/SOL) --")
    results = []
    for tf, n, x, f in grid:
        per, tr = [], 0
        for s in SYMS:
            series, t = simulate(frames[tf][s], n, x, f, IS_START, IS_END)
            per.append(series)
            tr += t
        st = stats(portfolio(per))
        results.append((st["sharpe"] if tr >= MIN_TRADES_IS else -9, tf, n, x, f, st, tr))
        print(f"{tf} RSI{n:2d} X={int(x):2d} {'flt' if f else '   '}  Sharpe={st['sharpe']:5.2f} "
              f"ann={st['ann']*100:6.1f}% maxDD={st['maxdd']*100:6.1f}% trades={tr}")
    results.sort(reverse=True, key=lambda z: z[0])
    _, tf, n, x, f, _, _ = results[0]
    print(f"\nIS pick: {tf} RSI{n} X={int(x)} filter={f}")

    print("\n-- OUT-OF-SAMPLE 2025-01-01..now (frozen) --")
    per, tr = [], 0
    for s in SYMS:
        series, t = simulate(frames[tf][s], n, x, f, IS_END, "2027-01-01")
        per.append(series)
        tr += t
    st = stats(portfolio(per))
    print(f"IS-pick: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} maxDD={st['maxdd']*100:6.1f}% "
          f"worst30={st['worst30']*100:6.1f}% trades={tr} ({st['n']}d)")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*st['ann']/365:.2f}/day net")

    print("\n-- OOS sensitivity (top 8 IS configs) --")
    for _, tf2, n2, x2, f2, _, _ in results[:8]:
        per2 = []
        tr2 = 0
        for s in SYMS:
            series, t = simulate(frames[tf2][s], n2, x2, f2, IS_END, "2027-01-01")
            per2.append(series)
            tr2 += t
        st2 = stats(portfolio(per2))
        print(f"{tf2} RSI{n2:2d} X={int(x2):2d} {'flt' if f2 else '   '}  ann={st2['ann']*100:6.1f}% "
              f"Sharpe={st2['sharpe']:5.2f} maxDD={st2['maxdd']*100:6.1f}% trades={tr2}")


if __name__ == "__main__":
    main()
