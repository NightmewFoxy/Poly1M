"""Pairs stat-arb on old-guard perps (long/short; mechanical; cached data only).

Spread: log(A) - beta*log(B), beta + mean + std estimated on a ROLLING 90d window
(no lookahead; tradeable as-is). Enter when |z| > Z_ENTRY (long cheap leg / short
rich leg, 0.5/0.5 notional), exit |z| < 0.5 or 30d timeout. Fees 0.07% per side
=> 0.28% per full round trip (4 legs). Universe: the 11 survivorship-clean
old-guard perps -> all 55 pairs; SELECTION DISCIPLINE: rank pairs by IS 2022-2023
Sharpe, freeze the top-5, report their OOS 2024->now as a portfolio. ETH/BTC also
reported alone (pre-registered classic). Z_ENTRY in {1.5, 2.0} chosen on IS.
Data: xsmom_candles.json (OKX daily closes). ASCII output only.
"""
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDLES = HERE / "xsmom_candles.json"
FEE = 0.0007
WIN = 90
Z_EXIT = 0.5
TIMEOUT = 30
IS_START, IS_END = "2022-01-01", "2024-01-01"


def load() -> dict[str, dict[str, float]]:
    raw = json.loads(CANDLES.read_text())
    data = {}
    for inst, cl in raw.items():
        if len(cl) >= 1700:
            data[inst.split("-")[0]] = cl
    return data


def simulate_pair(pxa: dict, pxb: dict, dates: list[str], z_entry: float,
                  d_from: str, d_to: str) -> tuple[list[tuple[str, float]], int]:
    la, lb = [], []
    ds = []
    for d in dates:
        a, b = pxa.get(d), pxb.get(d)
        if a and b:
            ds.append(d)
            la.append(math.log(a))
            lb.append(math.log(b))
    rets_a = {ds[i]: math.exp(la[i] - la[i - 1]) - 1 for i in range(1, len(ds))}
    rets_b = {ds[i]: math.exp(lb[i] - lb[i - 1]) - 1 for i in range(1, len(ds))}
    pos = 0  # +1 = long A/short B, -1 = reverse
    hold = 0
    trades = 0
    out = []
    for i in range(WIN, len(ds) - 1):
        # rolling beta/mean/std on window [i-WIN, i)
        xa = la[i - WIN:i]
        xb = lb[i - WIN:i]
        mb = sum(xb) / WIN
        ma = sum(xa) / WIN
        cov = sum((xb[k] - mb) * (xa[k] - ma) for k in range(WIN))
        var = sum((xb[k] - mb) ** 2 for k in range(WIN))
        beta = cov / var if var > 0 else 1.0
        spreads = [xa[k] - beta * xb[k] for k in range(WIN)]
        ms = sum(spreads) / WIN
        sd = math.sqrt(sum((s - ms) ** 2 for s in spreads) / (WIN - 1))
        if sd == 0:
            continue
        z = (la[i] - beta * lb[i] - ms) / sd
        new_pos = pos
        if pos == 0:
            if z > z_entry:
                new_pos = -1  # A rich: short A, long B
            elif z < -z_entry:
                new_pos = 1
        else:
            hold += 1
            if abs(z) < Z_EXIT or hold >= TIMEOUT:
                new_pos = 0
        d_next = ds[i + 1]
        r = 0.0
        if pos != 0:
            r = 0.5 * pos * rets_a.get(d_next, 0.0) - 0.5 * pos * rets_b.get(d_next, 0.0)
        if new_pos != pos:
            r -= FEE * 2 * 0.5 * abs(new_pos - pos)  # 2 legs x 0.5 notional per unit change
            if new_pos != 0:
                trades += 1
            hold = 0
        pos = new_pos
        if d_from <= d_next < d_to:
            out.append((d_next, r))
    return out, trades


def stats(series):
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


def portfolio(series_list):
    byd = {}
    for s in series_list:
        for d, r in s:
            byd.setdefault(d, []).append(r)
    return sorted((d, sum(v) / len(v)) for d, v in byd.items())


def main() -> None:
    data = load()
    names = sorted(data)
    print(f"old-guard universe: {','.join(names)}")
    dates = sorted({d for cl in data.values() for d in cl})

    best_z = None
    results_by_z = {}
    for z_entry in (1.5, 2.0):
        rows = []
        for a, b in itertools.combinations(names, 2):
            series, tr = simulate_pair(data[a], data[b], dates, z_entry, IS_START, IS_END)
            st = stats(series)
            if tr >= 5:
                rows.append((st["sharpe"], a, b, st, tr))
        rows.sort(reverse=True, key=lambda r: r[0])
        results_by_z[z_entry] = rows
        top5 = rows[:5]
        port_is = portfolio([simulate_pair(data[a], data[b], dates, z_entry, IS_START, IS_END)[0]
                             for _, a, b, _, _ in top5])
        stp = stats(port_is)
        print(f"\nIS 2022-23, Z={z_entry}: top-5 pairs portfolio Sharpe={stp['sharpe']:.2f} "
              f"ann={stp['ann']*100:.1f}%")
        for sh, a, b, st, tr in top5:
            print(f"  {a}/{b}: IS Sharpe={sh:5.2f} ann={st['ann']*100:6.1f}% trades={tr}")
        if best_z is None or stp["sharpe"] > best_z[1]:
            best_z = (z_entry, stp["sharpe"])

    z_entry = best_z[0]
    top5 = results_by_z[z_entry][:5]
    print(f"\nFROZEN: Z={z_entry}, pairs={[f'{a}/{b}' for _, a, b, _, _ in top5]}")

    print("\n-- OUT-OF-SAMPLE 2024-01-01..now --")
    oos_series = []
    for _, a, b, _, _ in top5:
        s, tr = simulate_pair(data[a], data[b], dates, z_entry, IS_END, "2027-01-01")
        st = stats(s)
        oos_series.append(s)
        print(f"  {a}/{b}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}% trades={tr}")
    stp = stats(portfolio(oos_series))
    print(f"  PORTFOLIO: ann={stp['ann']*100:.1f}% Sharpe={stp['sharpe']:.2f} maxDD={stp['maxdd']*100:.1f}%")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*stp['ann']/365:.2f}/day net")

    print("\n-- pre-registered ETH/BTC pair --")
    for period, d0, d1 in (("IS 2022-23", IS_START, IS_END), ("OOS 2024->", IS_END, "2027-01-01")):
        s, tr = simulate_pair(data["ETH"], data["BTC"], dates, 2.0, d0, d1)
        st = stats(s)
        print(f"  {period}: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} "
              f"maxDD={st['maxdd']*100:6.1f}% trades={tr}")


if __name__ == "__main__":
    main()
