"""Trend/momentum backtest on BTC/ETH/SOL daily (long/short perps; mechanical).

Signal families:
  tsmomN  : sign of trailing N-day return
  smaN    : +1 above SMA(N), -1 below
  donN    : Donchian stop-and-reverse — long on N-day-high breakout, short on
            N-day-low breakdown, hold otherwise
  don-ens : mean of don20+don55+don100 signals (pre-registered from SSRN 5209907
            style multi-horizon ensemble — reported OOS regardless of IS rank)
Variants: LS (long/short) and LF (long/flat); sizing fixed-1x or vol-target
(30% ann / realized 30d vol, capped at 1x).

No lookahead: position decided at close t earns close-to-close return t+1.
Fees: 0.07% of turnover (taker 0.055% + slippage on majors), charged on
|pos_t - pos_{t-1}|. IS = ..2023-12-31 (grid, pick by Sharpe); OOS = 2024-01-01..
(frozen). Data: Binance spot daily klines (proxy for perp prices on majors),
cached to daily_candles.json. ASCII output only.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CACHE = HERE / "daily_candles.json"
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
START = {"BTCUSDT": "2019-01-01", "ETHUSDT": "2019-01-01", "SOLUSDT": "2020-08-15"}
FEE = 0.0007
IS_END = "2024-01-01"
VOL_TARGET = 0.30


OKX_MAP = {"BTCUSDT": "BTC-USDT", "ETHUSDT": "ETH-USDT", "SOLUSDT": "SOL-USDT"}


def fetch_daily(client: httpx.Client, sym: str, start: str) -> list[dict]:
    """OKX spot daily candles, paginated backwards (Bybit temp rate-blocked us)."""
    inst = OKX_MAP[sym]
    t0 = int(datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    seen: dict[int, dict] = {}
    after = None
    while True:
        params = {"instId": inst, "bar": "1Dutc", "limit": "100"}
        if after is not None:
            params["after"] = str(after)
        r = client.get("https://www.okx.com/api/v5/market/history-candles", params=params)
        rows = r.json().get("data") or []
        if not rows:
            break
        for k in rows:
            ts = int(k[0])
            if k[-1] != "1":  # unconfirmed (partial) candle
                continue
            seen[ts] = {"d": datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d"),
                        "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
        oldest = min(int(k[0]) for k in rows)
        if oldest <= t0:
            break
        after = oldest
        time.sleep(0.15)
    return [seen[ts] for ts in sorted(seen) if ts >= t0]


def load() -> dict[str, list[dict]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data = {}
    with httpx.Client(timeout=20, trust_env=False) as client:
        for sym in SYMS:
            data[sym] = fetch_daily(client, sym, START[sym])
            print(f"{sym}: {len(data[sym])} days {data[sym][0]['d']}..{data[sym][-1]['d']}")
    CACHE.write_text(json.dumps(data))
    return data


def signal_series(candles: list[dict], kind: str, n: int) -> list[float]:
    """Raw signal in [-1,1] decided at each day's close."""
    c = [x["c"] for x in candles]
    h = [x["h"] for x in candles]
    lo = [x["l"] for x in candles]
    sig = [0.0] * len(c)
    if kind == "tsmom":
        for i in range(len(c)):
            if i >= n:
                sig[i] = 1.0 if c[i] > c[i - n] else -1.0
    elif kind == "sma":
        s = 0.0
        for i in range(len(c)):
            s += c[i]
            if i >= n:
                s -= c[i - n]
            if i >= n - 1:
                sig[i] = 1.0 if c[i] > s / n else -1.0
    elif kind == "don":
        cur = 0.0
        for i in range(len(c)):
            if i >= n:
                hh = max(h[i - n:i])
                ll = min(lo[i - n:i])
                if c[i] >= hh:
                    cur = 1.0
                elif c[i] <= ll:
                    cur = -1.0
            sig[i] = cur
    elif kind == "donens":
        parts = [signal_series(candles, "don", k) for k in (20, 55, 100)]
        sig = [sum(p[i] for p in parts) / 3 for i in range(len(c))]
    return sig


def vol_scale(candles: list[dict]) -> list[float]:
    c = [x["c"] for x in candles]
    rets = [0.0] + [c[i] / c[i - 1] - 1 for i in range(1, len(c))]
    scale = [1.0] * len(c)
    for i in range(len(c)):
        if i >= 30:
            window = rets[i - 29:i + 1]
            m = sum(window) / 30
            var = sum((x - m) ** 2 for x in window) / 29
            av = math.sqrt(var) * math.sqrt(365)
            scale[i] = min(1.0, VOL_TARGET / av) if av > 0 else 1.0
    return scale


def run(candles: list[dict], kind: str, n: int, ls: bool, vt: bool,
        d_from: str, d_to: str) -> list[tuple[str, float]]:
    """Daily net strategy returns within [d_from, d_to)."""
    sig = signal_series(candles, kind, n)
    if not ls:
        sig = [max(0.0, s) for s in sig]
    if vt:
        vs = vol_scale(candles)
        sig = [s * v for s, v in zip(sig, vs)]
    c = [x["c"] for x in candles]
    out = []
    prev_pos = 0.0
    for i in range(1, len(c)):
        d = candles[i]["d"]
        pos = sig[i - 1]
        ret = pos * (c[i] / c[i - 1] - 1) - FEE * abs(pos - prev_pos)
        prev_pos = pos
        if d_from <= d < d_to:
            out.append((d, ret))
    return out


def combine(per_sym: list[list[tuple[str, float]]]) -> list[tuple[str, float]]:
    byd: dict[str, list[float]] = {}
    for series in per_sym:
        for d, r in series:
            byd.setdefault(d, []).append(r)
    return sorted((d, sum(v) / len(v)) for d, v in byd.items())


def stats(series: list[tuple[str, float]]) -> dict:
    rs = [r for _, r in series]
    n = len(rs)
    if n < 30:
        return {"n": n, "ann": 0, "sharpe": 0, "maxdd": 0, "worst30": 0}
    total = 1.0
    peak = 1.0
    maxdd = 0.0
    for r in rs:
        total *= 1 + r
        peak = max(peak, total)
        maxdd = min(maxdd, total / peak - 1)
    m = sum(rs) / n
    var = sum((x - m) ** 2 for x in rs) / (n - 1)
    sd = math.sqrt(var)
    sharpe = (m / sd * math.sqrt(365)) if sd > 0 else 0
    ann = (total) ** (365 / n) - 1
    worst30 = min((sum(rs[j:j + 30]) for j in range(max(1, n - 30))), default=0)
    return {"n": n, "ann": ann, "sharpe": sharpe, "maxdd": maxdd, "worst30": worst30, "total": total - 1}


def main() -> None:
    data = load()
    last = min(data[s][-1]["d"] for s in SYMS)
    print(f"data through {last}\n")

    combos = []
    for n in (10, 20, 30, 60, 90, 120):
        combos.append(("tsmom", n))
    for n in (20, 50, 100, 200):
        combos.append(("sma", n))
    for n in (20, 55, 100):
        combos.append(("don", n))
    combos.append(("donens", 0))

    results = []
    for kind, n in combos:
        for ls in (True, False):
            for vt in (True, False):
                per = [run(data[s], kind, n, ls, vt, "2019-01-01", IS_END) for s in SYMS]
                st = stats(combine(per))
                results.append((st["sharpe"], kind, n, ls, vt, st))
    results.sort(reverse=True, key=lambda x: x[0])

    print("-- IN-SAMPLE ..2023 top 10 by Sharpe (net, portfolio BTC+ETH+SOL) --")
    for sh, kind, n, ls, vt, st in results[:10]:
        print(f"{kind}{n:>3} {'LS' if ls else 'LF'} {'vt' if vt else '1x'}  "
              f"Sharpe={sh:5.2f} ann={st['ann']*100:7.1f}% maxDD={st['maxdd']*100:6.1f}% worst30={st['worst30']*100:6.1f}%")

    best = results[0]
    _, kind, n, ls, vt, _ = best
    print(f"\nIS pick: {kind}{n} {'LS' if ls else 'LF'} {'vt' if vt else '1x'}")

    def oos_report(kind, n, ls, vt, label):
        per = [run(data[s], kind, n, ls, vt, IS_END, "2027-01-01") for s in SYMS]
        st = stats(combine(per))
        print(f"{label}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}% worst30={st['worst30']*100:6.1f}% total={st['total']*100:6.1f}% ({st['n']}d)")
        return st

    print("\n-- OUT-OF-SAMPLE 2024-01-01..now (frozen) --")
    st = oos_report(kind, n, ls, vt, "IS-pick   ")
    st_ens = oos_report("donens", 0, True, True, "don-ens vt")
    oos_report("donens", 0, True, False, "don-ens 1x")
    # buy & hold benchmark
    per_bh = []
    for s in SYMS:
        cs = data[s]
        rows = [(cs[i]["d"], cs[i]["c"] / cs[i - 1]["c"] - 1) for i in range(1, len(cs))
                if IS_END <= cs[i]["d"] < "2027-01-01"]
        per_bh.append(rows)
    st_bh = stats(combine(per_bh))
    print(f"buy&hold  : ann={st_bh['ann']*100:6.1f}% Sharpe={st_bh['sharpe']:5.2f} "
          f"maxDD={st_bh['maxdd']*100:6.1f}% worst30={st_bh['worst30']*100:6.1f}%")

    for cap in (1000, 5000):
        print(f"IS-pick ${cap}: ~${cap*st['ann']/365:.2f}/day  | don-ens vt ${cap}: ~${cap*st_ens['ann']/365:.2f}/day")

    print("\n-- OOS param sensitivity (LS 1x across horizons) --")
    for kind2, n2 in [("tsmom", 20), ("tsmom", 30), ("tsmom", 60), ("tsmom", 90),
                      ("sma", 50), ("sma", 100), ("sma", 200), ("don", 20), ("don", 55), ("don", 100)]:
        per = [run(data[s], kind2, n2, True, False, IS_END, "2027-01-01") for s in SYMS]
        st2 = stats(combine(per))
        print(f"{kind2}{n2:>3} LS 1x: ann={st2['ann']*100:6.1f}% Sharpe={st2['sharpe']:5.2f} maxDD={st2['maxdd']*100:6.1f}%")


if __name__ == "__main__":
    main()
