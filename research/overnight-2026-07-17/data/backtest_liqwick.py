"""Liquidation-wick / cascade reversion on BTC/ETH/SOL 5m futures bars.

Trigger: a single 5m bar moves >= thr (down => LONG the close, "buy the dump";
up => SHORT the close, "fade the squeeze"). Optional forced-flow filter: bar
volume > 5x trailing 1h average. Exit after H bars. One position at a time per
symbol. Fees 0.14% per event round trip.

Grid: thr {1.5%, 2.5%, 4%} x H {6,12,36 bars} x dir {dump-buy, pump-short} x
volfilter {off,on} — IS 2024 (pick by t-stat, n>=30) -> frozen OOS 2025->now.
Data: data.binance.vision monthly 5m futures klines 2024-01..2026-06, parsed
in-memory, condensed cache liqwick_5m_<sym>.json. ASCII output only.
"""
import io
import json
import math
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
MONTHS = [f"{y}-{m:02d}" for y in (2024, 2025, 2026) for m in range(1, 13)
          if f"{y}-{m:02d}" <= "2026-06"]
FEE_RT = 0.0014
BASE = "https://data.binance.vision/data/futures/um/monthly/klines"


def load_sym(client: httpx.Client, sym: str) -> list[list]:
    cache = HERE / f"liqwick_5m_{sym}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    rows = []
    for mo in MONTHS:
        url = f"{BASE}/{sym}/5m/{sym}-5m-{mo}.zip"
        try:
            r = client.get(url)
            if r.status_code != 200:
                print(f"  {sym} {mo}: HTTP {r.status_code} (skip)")
                continue
            zf = zipfile.ZipFile(io.BytesIO(r.content))
            with zf.open(zf.namelist()[0]) as f:
                for line in io.TextIOWrapper(f, encoding="utf-8"):
                    parts = line.strip().split(",")
                    if not parts or not parts[0].isdigit():
                        continue  # header
                    ts = int(parts[0])
                    if ts > 10**14:  # some files use microseconds
                        ts //= 1000
                    rows.append([ts, float(parts[4]), float(parts[5])])  # ts, close, vol
        except Exception as e:
            print(f"  {sym} {mo}: {type(e).__name__} (skip)")
        time.sleep(0.05)
    rows.sort()
    cache.write_text(json.dumps(rows))
    print(f"{sym}: {len(rows)} 5m bars cached")
    return rows


def tstat(vals):
    n = len(vals)
    if n < 5:
        return 0.0
    m = sum(vals) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def events_for(bars, thr, hold, dump_buy, volf, d_from, d_to):
    """Net event returns."""
    out = []
    i = 13  # need trailing 12 bars for vol avg
    n = len(bars)
    while i < n - hold - 1:
        ts, c, v = bars[i]
        d = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d")
        if not (d_from <= d < d_to):
            i += 1
            continue
        pc = bars[i - 1][1]
        if pc <= 0:
            i += 1
            continue
        r = c / pc - 1
        trig = (r <= -thr) if dump_buy else (r >= thr)
        if trig and volf:
            avg_v = sum(b[2] for b in bars[i - 12:i]) / 12
            trig = v > 5 * avg_v
        if trig:
            exit_c = bars[i + hold][1]
            ev = (exit_c / c - 1) if dump_buy else -(exit_c / c - 1)
            out.append(ev - FEE_RT)
            i += hold
        else:
            i += 1
    return out


def stats_events(vals, years):
    n = len(vals)
    if n < 20:
        return None
    m = sum(vals) / n
    return {"n": n, "mean_bp": m * 10000, "t": tstat(vals), "ann": m * n / years}


def main():
    data = {}
    with httpx.Client(timeout=60, trust_env=False) as client:
        for s in SYMS:
            data[s] = load_sym(client, s)

    grid = [(thr, h, db, vf) for thr in (0.015, 0.025, 0.04) for h in (6, 12, 36)
            for db in (True, False) for vf in (False, True)]

    print("\n-- IN-SAMPLE 2024 (pooled BTC+ETH+SOL, net per event) --")
    results = []
    for thr, h, db, vf in grid:
        ev = []
        for s in SYMS:
            ev += events_for(data[s], thr, h, db, vf, "2024-01-01", "2025-01-01")
        st = stats_events(ev, 1.0)
        if st and st["n"] >= 30:
            results.append((st["t"], thr, h, db, vf, st))
            print(f"thr={thr*100:3.1f}% H={h:2d} {'DUMP-BUY ' if db else 'PUMP-SHRT'} "
                  f"{'vf' if vf else '  '}  mean={st['mean_bp']:7.1f}bp t={st['t']:5.2f} "
                  f"n={st['n']:4d} ann={st['ann']*100:7.1f}%")
    if not results:
        print("no cells with enough events")
        return
    results.sort(reverse=True, key=lambda z: z[0])
    _, thr, h, db, vf, _ = results[0]
    print(f"\nIS pick: thr={thr*100:.1f}% H={h} {'DUMP-BUY' if db else 'PUMP-SHORT'} volf={vf}")

    print("\n-- OUT-OF-SAMPLE 2025-01-01..2026-06-30 (frozen) --")
    ev = []
    for s in SYMS:
        ev += events_for(data[s], thr, h, db, vf, "2025-01-01", "2027-01-01")
    st = stats_events(ev, 1.5)
    if st:
        print(f"OOS: mean={st['mean_bp']:.1f}bp t={st['t']:.2f} n={st['n']} ann-net={st['ann']*100:.1f}%")
        for cap in (1000, 5000):
            print(f"  ${cap}: ~${cap*st['ann']/365:.2f}/day net")
    else:
        print("OOS: too few events")

    print("\n-- OOS top-6 IS cells (sensitivity) --")
    for _, thr2, h2, db2, vf2, _ in results[:6]:
        ev2 = []
        for s in SYMS:
            ev2 += events_for(data[s], thr2, h2, db2, vf2, "2025-01-01", "2027-01-01")
        st2 = stats_events(ev2, 1.5)
        if st2:
            print(f"thr={thr2*100:3.1f}% H={h2:2d} {'DUMP-BUY ' if db2 else 'PUMP-SHRT'} "
                  f"{'vf' if vf2 else '  '}  mean={st2['mean_bp']:7.1f}bp t={st2['t']:5.2f} "
                  f"n={st2['n']:4d} ann={st2['ann']*100:7.1f}%")


if __name__ == "__main__":
    main()
