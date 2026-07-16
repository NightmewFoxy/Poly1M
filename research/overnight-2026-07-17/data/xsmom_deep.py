"""xsmom deep-dive: robustness of the cross-sectional momentum ensemble.

Everything on cached OKX daily closes (xsmom_candles.json). The traded spec is
the selection-free ensemble: equal capital across lookbacks {7,14,28,60}, weekly
quintile long/short, gross 1x, fees 0.07%/side of turnover, no lookahead.

Cuts examined (all OOS 2024-01-01..now unless stated):
  1. Universe bounds: clean-11 (full history), mid-15 (listed >=6mo before OOS),
     full-36 (today's list, survivorship-inflated upper bound).
  2. Mode: long/short vs long-only vs short-only (where does the P&L come from?).
  3. Rebalance phase: weekly offset 0..6 (robustness to arbitrary day choice).
  4. Per-year OOS breakdown (2024 / 2025 / 2026H1) for mid-15 LS.
  5. Average weekly turnover and annual fee drag for mid-15 LS.
ASCII output only.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDLES = HERE / "xsmom_candles.json"
FEE = 0.0007
REB = 7
LOOKBACKS = (7, 14, 28, 60)
OOS = "2024-01-01"


def load_universes():
    raw = json.loads(CANDLES.read_text())
    data = {inst.split("-")[0]: cl for inst, cl in raw.items()}
    u_clean = {b: cl for b, cl in data.items() if len(cl) >= 1700}
    u_mid = {b: cl for b, cl in data.items() if len(cl) >= 1050}
    return data, u_clean, u_mid


def daily_rets(closes, dates):
    out, prev = {}, None
    for d in dates:
        c = closes.get(d)
        if c is not None and prev is not None:
            out[d] = c / prev - 1
        if c is not None:
            prev = c
    return out


def simulate(data, dates, lb, mode, phase, d_from, d_to, track_turnover=False):
    rets = {b: daily_rets(cl, dates) for b, cl in data.items()}
    weights = {}
    out = []
    turn = []
    for i, d in enumerate(dates[:-1]):
        nxt = dates[i + 1]
        cost = 0.0
        if i >= lb and i % REB == phase % REB:
            scores = {}
            for b, cl in data.items():
                a, z = cl.get(d), cl.get(dates[i - lb])
                if a and z and z != 0:
                    scores[b] = a / z - 1
            if len(scores) >= 10:
                ranked = sorted(scores, key=scores.get, reverse=True)
                q = max(2, len(ranked) // 5)
                new_w = {}
                if mode in ("ls", "lo"):
                    gross_long = 0.5 if mode == "ls" else 1.0
                    new_w.update({b: gross_long / q for b in ranked[:q]})
                if mode in ("ls", "so"):
                    gross_short = 0.5 if mode == "ls" else 1.0
                    new_w.update({b: -gross_short / q for b in ranked[-q:]})
                dturn = sum(abs(new_w.get(b, 0) - weights.get(b, 0))
                            for b in set(new_w) | set(weights))
                cost = dturn * FEE
                if track_turnover and d_from <= nxt < d_to:
                    turn.append(dturn)
                weights = new_w
        r = sum(w * rets[b].get(nxt, 0.0) for b, w in weights.items()) - cost
        if d_from <= nxt < d_to:
            out.append((nxt, r))
    return (out, turn) if track_turnover else out


def ensemble(data, dates, mode, phase, d_from, d_to):
    series = [dict(simulate(data, dates, lb, mode, phase, d_from, d_to)) for lb in LOOKBACKS]
    common = sorted(set.intersection(*(set(s) for s in series)))
    return [(d, sum(s[d] for s in series) / len(series)) for d in common]


def stats(series):
    rs = [r for _, r in series]
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


def rep(label, st):
    if st is None:
        print(f"{label:36s}: too few days")
        return
    print(f"{label:36s}: ann={st['ann']*100:7.1f}% Sharpe={st['sharpe']:5.2f} "
          f"maxDD={st['maxdd']*100:6.1f}% ({st['n']}d)")


def main():
    data, u_clean, u_mid = load_universes()
    dates = sorted({d for cl in data.values() for d in cl})
    print(f"universes: clean-11={len(u_clean)} mid-15={len(u_mid)} full={len(data)}")
    print(f"mid-15 = {','.join(sorted(u_mid))}\n")

    print("-- 1) universe bounds (ensemble LS, phase 0, OOS 2024->now) --")
    for label, uni in (("clean-11", u_clean), ("mid-15", u_mid), ("full-36 (inflated)", data)):
        rep(label, stats(ensemble(uni, dates, "ls", 0, OOS, "2027-01-01")))

    print("\n-- 2) mode decomposition (mid-15, OOS) --")
    for mode, label in (("ls", "long/short 0.5/0.5"), ("lo", "long-only 1x"), ("so", "short-only 1x")):
        rep(label, stats(ensemble(u_mid, dates, mode, 0, OOS, "2027-01-01")))

    print("\n-- 3) rebalance phase 0..6 (mid-15 LS, OOS) --")
    anns = []
    for p in range(7):
        st = stats(ensemble(u_mid, dates, "ls", p, OOS, "2027-01-01"))
        anns.append(st["ann"])
        rep(f"phase {p}", st)
    print(f"phase spread: min={min(anns)*100:.1f}% max={max(anns)*100:.1f}% "
          f"mean={sum(anns)/7*100:.1f}%")

    print("\n-- 4) per-year OOS breakdown (mid-15 LS, phase 0) --")
    for d0, d1 in (("2024-01-01", "2025-01-01"), ("2025-01-01", "2026-01-01"),
                   ("2026-01-01", "2027-01-01")):
        rep(f"{d0[:4]}", stats(ensemble(u_mid, dates, "ls", 0, d0, d1)))

    print("\n-- 5) turnover & fee drag (mid-15, lb=14 rep, LS, OOS) --")
    _, turn = simulate(u_mid, dates, 14, "ls", 0, OOS, "2027-01-01", track_turnover=True)
    if turn:
        avg_t = sum(turn) / len(turn)
        print(f"avg weekly turnover: {avg_t:.2f}x of book; fee drag ~{avg_t*FEE*52*100:.1f}%/yr "
              f"(of the {FEE*10000:.0f}bp/side assumption)")
    # clean-11 per-year too, for the morning table
    print("\n-- clean-11 LS per-year (reference) --")
    for d0, d1 in (("2024-01-01", "2025-01-01"), ("2025-01-01", "2026-01-01"),
                   ("2026-01-01", "2027-01-01")):
        rep(f"{d0[:4]}", stats(ensemble(u_clean, dates, "ls", 0, d0, d1)))


if __name__ == "__main__":
    main()
