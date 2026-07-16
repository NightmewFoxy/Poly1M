"""Pre-FOMC drift event study on BTC (long-only windows; mechanical).

Pre-registered external hypothesis (Lucca-Moench analog claimed for BTC by the
directional sweep): LONG BTC for the 24h BEFORE the FOMC statement (14:00 ET),
flat at the announcement. Windows tested:
  PRE24  : [t-24h, t)      PRE24X2: [t-24h, t-2h)  (exit before the spike)
  POST24 : [t, t+24h)      (informational)
Fees 0.14% per event round trip. FOMC statement datetimes hardcoded with correct
EST/EDT UTC hours (14:00 ET = 19:00 UTC in winter, 18:00 UTC in DST). 2026 dates
verified against the Fed calendar 2026-07-17. Data: cached OKX BTC 1H candles.
No fitting anywhere — pure event stats, full 2022->now plus 2024->now subset.
ASCII output only.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "rsimr_candles_1h.json"
FEE_RT = 0.0014

FOMC = [  # (YYYY-MM-DD statement day, UTC hour of 14:00 ET)
    ("2022-01-26", 19), ("2022-03-16", 18), ("2022-05-04", 18), ("2022-06-15", 18),
    ("2022-07-27", 18), ("2022-09-21", 18), ("2022-11-02", 18), ("2022-12-14", 19),
    ("2023-02-01", 19), ("2023-03-22", 18), ("2023-05-03", 18), ("2023-06-14", 18),
    ("2023-07-26", 18), ("2023-09-20", 18), ("2023-11-01", 18), ("2023-12-13", 19),
    ("2024-01-31", 19), ("2024-03-20", 18), ("2024-05-01", 18), ("2024-06-12", 18),
    ("2024-07-31", 18), ("2024-09-18", 18), ("2024-11-07", 19), ("2024-12-18", 19),
    ("2025-01-29", 19), ("2025-03-19", 18), ("2025-05-07", 18), ("2025-06-18", 18),
    ("2025-07-30", 18), ("2025-09-17", 18), ("2025-10-29", 18), ("2025-12-10", 19),
    ("2026-01-28", 19), ("2026-03-18", 18), ("2026-04-29", 18), ("2026-06-17", 18),
]


def tstat(vals):
    n = len(vals)
    if n < 5:
        return 0.0
    m = sum(vals) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def main() -> None:
    bars = json.loads(CACHE.read_text())["BTC-USDT"]  # [ [open_ts_ms, close], ... ]
    rets: dict[int, float] = {}  # open_ts -> hourly return
    for i in range(1, len(bars)):
        rets[bars[i][0]] = bars[i][1] / bars[i - 1][1] - 1

    def window(t_ms: int, h_from: int, h_to: int) -> float | None:
        """Sum of hourly returns for bars opening in [t+h_from*3600s, t+h_to*3600s)."""
        vals = []
        for k in range(h_from, h_to):
            r = rets.get(t_ms + k * 3600_000)
            if r is not None:
                vals.append(r)
        return sum(vals) if len(vals) >= (h_to - h_from) - 2 else None

    events = []
    for d, hh in FOMC:
        t = int(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                .replace(hour=hh).timestamp() * 1000)
        pre24 = window(t, -24, 0)
        pre24x2 = window(t, -24, -2)
        post24 = window(t, 0, 24)
        if pre24 is not None:
            events.append((d, pre24, pre24x2, post24))

    def rep(label, vals, fee, years):
        vals = [v for v in vals if v is not None]
        n = len(vals)
        g = sum(vals) / n
        net = g - fee
        print(f"{label:34s}: n={n:2d} gross={g*10000:7.1f}bp (t={tstat(vals):5.2f}) "
              f"net={net*10000:7.1f}bp (t={tstat([v-fee for v in vals]):5.2f}) "
              f"ann-net={net*(n/years)*100:6.1f}%")

    for (lbl, filt, years) in (("FULL 2022->now", lambda d: True, 4.55),
                               ("RECENT 2024->now", lambda d: d >= "2024-01-01", 2.55)):
        ev = [e for e in events if filt(e[0])]
        print(f"== {lbl} ({len(ev)} events) ==")
        rep("  PRE24  long [t-24h, t)", [e[1] for e in ev], FEE_RT, years)
        rep("  PRE24X2 long [t-24h, t-2h)", [e[2] for e in ev], FEE_RT, years)
        rep("  POST24 long [t, t+24h) info", [e[3] for e in ev], FEE_RT, years)
        print()

    print("per-event PRE24 (bp): " + " ".join(f"{e[0][2:7]}:{e[1]*10000:+.0f}" for e in events))


if __name__ == "__main__":
    main()
