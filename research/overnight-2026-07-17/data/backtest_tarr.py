"""Retail-TA template backtest: indicator entry + ATR stop + 2:1 take-profit.

The "traditional trading" template the owner asked about (2026-07-17, post-hunt
addendum): enter on a classic chart signal, place a stop loss at k*ATR(14),
take profit at 2x the stop distance (2:1 reward:risk), stay flat otherwise.
Long AND short, BTC/ETH/SOL perps, fees 0.07%/side.

Entries (signal at bar close, filled at next bar OPEN):
  ema9/21, ema20/50 : EMA fast/slow cross (golden cross long, death cross short)
  don20, don55      : Donchian breakout (close beyond prior N-bar high/low)
Exits: intrabar stop/target; if BOTH could hit in one bar, assume the STOP
(pessimistic). No other exits - pure stop-or-target, the retail spec.

Grid: entry{4} x timeframe{1H,4H} x ATR-mult k{1.5,2.0} = 16 configs.
Discipline: IS 2022-01-01..2024-12-31 pick by Sharpe (min 100 trades), frozen,
OOS 2025-01-01..now reported. Plus: LAST-7-DAYS P&L on $200 for every config.
Data: OKX 1H OHLC (cached tarr_candles_1h.json). ASCII output only. Read-only.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CACHE = HERE / "tarr_candles_1h.json"
SYMS = ("BTC-USDT", "ETH-USDT", "SOL-USDT")
FETCH_FROM = "2021-12-01"
FEE = 0.0007
IS_START, IS_END = "2022-01-01", "2025-01-01"
MIN_TRADES_IS = 100
RR = 2.0  # take-profit distance = RR * stop distance


def fetch_1h_ohlc(client: httpx.Client, inst: str, start: str) -> list[list]:
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
                seen[int(k[0])] = [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])]
        oldest = min(int(k[0]) for k in rows)
        if oldest <= t0:
            break
        after = oldest
        time.sleep(0.11)
    # the recent endpoint fills the newest ~300 bars history-candles may lag on
    try:
        r = client.get("https://www.okx.com/api/v5/market/candles",
                       params={"instId": inst, "bar": "1H", "limit": "300"})
        for k in (r.json().get("data") or []):
            if k[-1] == "1":
                seen[int(k[0])] = [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])]
    except Exception:
        pass
    return [seen[ts] for ts in sorted(seen) if ts >= t0]


def load() -> dict[str, list[list]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data = {}
    with httpx.Client(timeout=20, trust_env=False) as client:
        for s in SYMS:
            data[s] = fetch_1h_ohlc(client, s, FETCH_FROM)
            print(f"{s}: {len(data[s])} hourly bars")
    CACHE.write_text(json.dumps(data))
    return data


def resample_4h(bars: list[list]) -> list[list]:
    out = []
    block = None
    for ts, o, h, l, c in bars:
        b = ts // (4 * 3600000)
        if block is None or b != block[0]:
            if block is not None:
                out.append(block[1])
            block = (b, [b * 4 * 3600000, o, h, l, c])
        else:
            row = block[1]
            row[2] = max(row[2], h)
            row[3] = min(row[3], l)
            row[4] = c
    if block is not None:
        out.append(block[1])
    return out[:-1]  # drop possibly-partial final block


def ema_series(closes: list[float], n: int) -> list[float]:
    out = [closes[0]] * len(closes)
    a = 2.0 / (n + 1)
    for i in range(1, len(closes)):
        out[i] = a * closes[i] + (1 - a) * out[i - 1]
    return out


def atr_series(bars: list[list], n: int = 14) -> list[float]:
    out = [0.0] * len(bars)
    prev_c = bars[0][4]
    atr = bars[0][2] - bars[0][3]
    for i, (_, o, h, l, c) in enumerate(bars):
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        atr = tr if i == 0 else (atr * (n - 1) + tr) / n
        out[i] = atr
        prev_c = c
    return out


def signal_series(bars: list[list], entry: str) -> list[int]:
    """+1 long / -1 short / 0 none, evaluated at each bar close."""
    closes = [b[4] for b in bars]
    sig = [0] * len(bars)
    if entry.startswith("ema"):
        nf, ns = (9, 21) if entry == "ema9/21" else (20, 50)
        ef, es = ema_series(closes, nf), ema_series(closes, ns)
        for i in range(1, len(bars)):
            if ef[i - 1] <= es[i - 1] and ef[i] > es[i]:
                sig[i] = 1
            elif ef[i - 1] >= es[i - 1] and ef[i] < es[i]:
                sig[i] = -1
    else:
        n = int(entry[3:])
        for i in range(n + 1, len(bars)):
            hh = max(b[2] for b in bars[i - n:i])
            ll = min(b[3] for b in bars[i - n:i])
            if closes[i] > hh:
                sig[i] = 1
            elif closes[i] < ll:
                sig[i] = -1
    return sig


def simulate(bars: list[list], entry: str, k: float,
             d_from: str, d_to: str) -> tuple[list[tuple[str, float]], int, int]:
    """Per-bar mark-to-market returns in [d_from, d_to). Returns (series, trades, wins)."""
    sig = signal_series(bars, entry)
    atr = atr_series(bars)
    dates = [datetime.fromtimestamp(b[0] / 1000, timezone.utc).strftime("%Y-%m-%d") for b in bars]
    pos = 0
    stop = target = entry_px = 0.0
    pending = 0  # signal fired at prior close, fill at this bar's open
    trades = wins = 0
    out = []
    warm = 60
    for i in range(1, len(bars)):
        ts, o, h, l, c = bars[i]
        prev_c = bars[i - 1][4]
        r = 0.0
        in_window = d_from <= dates[i] < d_to
        if pending != 0 and pos == 0:
            pos = pending
            entry_px = o
            dist = k * atr[i - 1]
            stop = entry_px - pos * dist
            target = entry_px + pos * RR * dist
            r -= FEE
            if in_window:
                trades += 1
            # intrabar exit possible on the entry bar itself
            exit_px = None
            if (pos == 1 and l <= stop) or (pos == -1 and h >= stop):
                exit_px = stop
            elif (pos == 1 and h >= target) or (pos == -1 and l <= target):
                exit_px = target
                if in_window:
                    wins += 1
            if exit_px is not None:
                r += pos * (exit_px / entry_px - 1) - FEE
                pos = 0
            else:
                r += pos * (c / entry_px - 1)
        elif pos != 0:
            exit_px = None
            if (pos == 1 and l <= stop) or (pos == -1 and h >= stop):
                exit_px = stop  # pessimistic: stop before target
            elif (pos == 1 and h >= target) or (pos == -1 and l <= target):
                exit_px = target
                if in_window:
                    wins += 1
            if exit_px is not None:
                r = pos * (exit_px / prev_c - 1) - FEE
                pos = 0
            else:
                r = pos * (c / prev_c - 1)
        pending = sig[i] if (pos == 0 and i > warm) else 0
        if d_from <= dates[i] < d_to:
            out.append((dates[i], r))
    return out, trades, wins


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
        return {"n": n, "ann": 0.0, "sharpe": 0.0, "maxdd": 0.0}
    total, peak, maxdd = 1.0, 1.0, 0.0
    for r in rs:
        total *= 1 + r
        peak = max(peak, total)
        maxdd = min(maxdd, total / peak - 1)
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1))
    return {"n": n, "ann": total ** (365 / n) - 1, "sharpe": (m / sd * math.sqrt(365)) if sd else 0.0,
            "maxdd": maxdd}


def run_cfg(frames: dict, entry: str, tf: str, k: float,
            d_from: str, d_to: str) -> tuple[dict, int, int, list[tuple[str, float]]]:
    per, tr, wn = [], 0, 0
    for s in SYMS:
        series, t, w = simulate(frames[tf][s], entry, k, d_from, d_to)
        per.append(series)
        tr += t
        wn += w
    port = portfolio(per)
    return stats(port), tr, wn, port


def main() -> None:
    data1h = load()
    frames = {"1H": data1h, "4H": {s: resample_4h(b) for s, b in data1h.items()}}
    last_date = max(datetime.fromtimestamp(b[0] / 1000, timezone.utc).strftime("%Y-%m-%d")
                    for b in data1h["BTC-USDT"])
    print(f"data through {last_date}\n")

    grid = [(e, tf, k) for e in ("ema9/21", "ema20/50", "don20", "don55")
            for tf in ("1H", "4H") for k in (1.5, 2.0)]

    print("-- IN-SAMPLE 2022-2024 (net, portfolio BTC/ETH/SOL, 2:1 RR, ATR stop) --")
    results = []
    for e, tf, k in grid:
        st, tr, wn, _ = run_cfg(frames, e, tf, k, IS_START, IS_END)
        wr = wn / tr * 100 if tr else 0.0
        results.append((st["sharpe"] if tr >= MIN_TRADES_IS else -9, e, tf, k, st, tr, wr))
        print(f"{e:9s} {tf} k={k:.1f}  Sharpe={st['sharpe']:5.2f} ann={st['ann']*100:6.1f}% "
              f"maxDD={st['maxdd']*100:6.1f}% trades={tr:5d} win%={wr:4.1f}")
    results.sort(reverse=True, key=lambda z: z[0])
    _, e, tf, k, _, _, _ = results[0]
    print(f"\nIS pick: {e} {tf} k={k}")

    print("\n-- OUT-OF-SAMPLE 2025-01-01..now (frozen pick) --")
    st, tr, wn, _ = run_cfg(frames, e, tf, k, IS_END, "2027-01-01")
    wr = wn / tr * 100 if tr else 0.0
    print(f"{e} {tf} k={k}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
          f"maxDD={st['maxdd']*100:6.1f}% trades={tr} win%={wr:4.1f} ({st['n']}d)")
    for cap in (200, 1000, 5000):
        print(f"  ${cap}: ~${cap*st['ann']/365:+.2f}/day net")

    print("\n-- OOS sensitivity (top 8 IS configs) --")
    for _, e2, tf2, k2, _, _, _ in results[:8]:
        st2, tr2, wn2, _ = run_cfg(frames, e2, tf2, k2, IS_END, "2027-01-01")
        wr2 = wn2 / tr2 * 100 if tr2 else 0.0
        print(f"{e2:9s} {tf2} k={k2:.1f}  ann={st2['ann']*100:6.1f}% Sharpe={st2['sharpe']:5.2f} "
              f"maxDD={st2['maxdd']*100:6.1f}% trades={tr2:4d} win%={wr2:4.1f}")

    print("\n-- LAST 7 DAYS, every config, $200 capital (net of fees) --")
    week_from = sorted({d for d, _ in
                        [(datetime.fromtimestamp(b[0]/1000, timezone.utc).strftime('%Y-%m-%d'), 0)
                         for b in data1h['BTC-USDT']]})[-7]
    for e3, tf3, k3 in grid:
        _, tr3, _, port3 = run_cfg(frames, e3, tf3, k3, week_from, "2027-01-01")
        wk = [r for _, r in port3]
        pnl = 200.0 * (math.prod(1 + r for r in wk) - 1)
        mark = " <== IS pick" if (e3, tf3, k3) == (e, tf, k) else ""
        print(f"{e3:9s} {tf3} k={k3:.1f}  week P&L on $200: ${pnl:+6.2f}{mark}")
    print(f"(week = {week_from}..{last_date}; positions entered before the week not carried in)")


if __name__ == "__main__":
    main()
