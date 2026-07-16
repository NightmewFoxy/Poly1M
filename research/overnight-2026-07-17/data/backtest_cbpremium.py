"""Coinbase-premium (US institutional demand proxy) -> next-day BTC drift.

Premium_t = Coinbase BTC-USD close / OKX BTC-USDT close - 1 (daily, UTC close).
Signal: rolling z-score of the premium (30d window). Rule: LONG BTC next day if
z > +Z, SHORT if z < -Z, else flat. Fees 0.07% per side of position change.
Grid: Z in {0.3, 0.5, 1.0} x signal {raw z, 3d-smoothed z} — IS 2024 (ETF era
starts 2024-01) pick by Sharpe -> frozen OOS 2025->now. Also reports the
always-in variant (sign of z). Data: Coinbase Exchange public candles + cached
OKX dailies. Caveat noted in verdict: premium includes USDT/USD basis noise.
ASCII output only.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CB_CACHE = HERE / "cb_btcusd_daily.json"
OKX_CACHE = HERE / "daily_candles.json"  # from backtest_tsmom (BTCUSDT key)
START = "2023-11-01"


def fetch_cb(client: httpx.Client) -> dict[str, float]:
    if CB_CACHE.exists():
        return json.loads(CB_CACHE.read_text())
    out = {}
    t0 = int(datetime.strptime(START, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    end = int(time.time())
    step = 300 * 86400
    t = t0
    while t < end:
        t1 = min(t + step, end)
        r = client.get("https://api.exchange.coinbase.com/products/BTC-USD/candles",
                       params={"granularity": 86400,
                               "start": datetime.fromtimestamp(t, timezone.utc).isoformat(),
                               "end": datetime.fromtimestamp(t1, timezone.utc).isoformat()},
                       headers={"User-Agent": "research/1.0"})
        rows = r.json()
        if isinstance(rows, list):
            for k in rows:  # [time, low, high, open, close, volume]
                d = datetime.fromtimestamp(k[0], timezone.utc).strftime("%Y-%m-%d")
                out[d] = float(k[4])
        t = t1
        time.sleep(0.35)
    CB_CACHE.write_text(json.dumps(out))
    return out


def zscores(vals: list[float], win: int) -> list[float]:
    out = [float("nan")] * len(vals)
    for i in range(win, len(vals)):
        w = vals[i - win:i]
        m = sum(w) / win
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / (win - 1))
        out[i] = (vals[i] - m) / sd if sd > 0 else 0.0
    return out


def stats(rs):
    n = len(rs)
    if n < 30:
        return None
    total, peak, maxdd = 1.0, 1.0, 0.0
    for r in rs:
        total *= 1 + r
        peak = max(peak, total)
        maxdd = min(maxdd, total / peak - 1)
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1))
    return {"n": n, "ann": total ** (365 / n) - 1, "sharpe": (m / sd * math.sqrt(365)) if sd else 0.0,
            "maxdd": maxdd}


def simulate(dates, prem_z, btc_ret_next, z_th, smooth, mode, d_from, d_to):
    """mode: 'band' (long/flat/short by threshold) or 'sign' (always in)."""
    sig = prem_z[:]
    if smooth:
        sig = [float("nan") if i < 2 or any(math.isnan(x) for x in prem_z[i-2:i+1])
               else sum(prem_z[i-2:i+1]) / 3 for i in range(len(prem_z))]
    rs = []
    prev_pos = 0.0
    for i, d in enumerate(dates[:-1]):
        z = sig[i]
        if math.isnan(z):
            continue
        if mode == "band":
            pos = 1.0 if z > z_th else (-1.0 if z < -z_th else 0.0)
        else:
            pos = 1.0 if z > 0 else -1.0
        r = pos * btc_ret_next[i] - 0.0007 * abs(pos - prev_pos)
        prev_pos = pos
        if d_from <= dates[i + 1] < d_to:
            rs.append(r)
    return rs


def main():
    with httpx.Client(timeout=20, trust_env=False) as client:
        cb = fetch_cb(client)
    okx = {d["d"]: d["c"] for d in json.loads(OKX_CACHE.read_text())["BTCUSDT"]}
    dates = sorted(set(cb) & set(okx))
    print(f"joined days: {len(dates)} ({dates[0]}..{dates[-1]})")
    prem = [cb[d] / okx[d] - 1 for d in dates]
    avg_prem_bp = sum(prem) / len(prem) * 10000
    print(f"avg premium: {avg_prem_bp:.1f}bp  (USDT/USD basis noise included)")
    pz = zscores(prem, 30)
    ret_next = [(okx[dates[i + 1]] / okx[dates[i]] - 1) if i + 1 < len(dates) else 0.0
                for i in range(len(dates))]

    print("\n-- IN-SAMPLE 2024 --")
    results = []
    for z_th in (0.3, 0.5, 1.0):
        for smooth in (False, True):
            rs = simulate(dates, pz, ret_next, z_th, smooth, "band", "2024-01-01", "2025-01-01")
            st = stats(rs)
            if st:
                results.append((st["sharpe"], z_th, smooth, "band", st))
                print(f"band Z={z_th} {'sm3' if smooth else 'raw'}: ann={st['ann']*100:6.1f}% "
                      f"Sharpe={st['sharpe']:5.2f} maxDD={st['maxdd']*100:6.1f}%")
    rs = simulate(dates, pz, ret_next, 0, False, "sign", "2024-01-01", "2025-01-01")
    st = stats(rs)
    if st:
        results.append((st["sharpe"], 0, False, "sign", st))
        print(f"sign (always-in)  : ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}%")

    results.sort(reverse=True, key=lambda x: x[0])
    _, z_th, smooth, mode, _ = results[0]
    print(f"\nIS pick: mode={mode} Z={z_th} smooth={smooth}")

    print("\n-- OUT-OF-SAMPLE 2025-01-01..now (frozen) --")
    rs = simulate(dates, pz, ret_next, z_th, smooth, mode, "2025-01-01", "2027-01-01")
    st = stats(rs)
    if st:
        print(f"OOS: ann={st['ann']*100:.1f}% Sharpe={st['sharpe']:.2f} maxDD={st['maxdd']*100:.1f}% ({st['n']}d)")
        for cap in (1000, 5000):
            print(f"  ${cap}: ~${cap*st['ann']/365:.2f}/day net")

    print("\n-- OOS all configs (sensitivity) --")
    for z_th2 in (0.3, 0.5, 1.0):
        for smooth2 in (False, True):
            rs2 = simulate(dates, pz, ret_next, z_th2, smooth2, "band", "2025-01-01", "2027-01-01")
            st2 = stats(rs2)
            if st2:
                print(f"band Z={z_th2} {'sm3' if smooth2 else 'raw'}: ann={st2['ann']*100:6.1f}% "
                      f"Sharpe={st2['sharpe']:5.2f} maxDD={st2['maxdd']*100:6.1f}%")
    rs2 = simulate(dates, pz, ret_next, 0, False, "sign", "2025-01-01", "2027-01-01")
    st2 = stats(rs2)
    if st2:
        print(f"sign (always-in)  : ann={st2['ann']*100:6.1f}% Sharpe={st2['sharpe']:5.2f} "
              f"maxDD={st2['maxdd']*100:6.1f}%")


if __name__ == "__main__":
    main()
