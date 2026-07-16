"""Cross-sectional funding-rate fade/follow on perps (long/short; mechanical).

Signal: trailing L-day funding sum per symbol (Bybit funding history, cached).
FADE = SHORT the most-positive-funding quintile (crowded longs) and LONG the most-
negative (crowded shorts). FOLLOW = the reverse. Rebalance every R days at close;
equal weight, gross 1x (0.5/0.5); fees 0.07%/side on turnover. Prices: OKX daily
perp candles (cached xsmom_candles.json), joined to Bybit symbols by base coin.
Funding P&L of holding the positions is NOT included in returns (conservative for
FADE, which would additionally COLLECT funding on its shorts and pay less on its
longs — noted in verdict).

Grid: L in {1,3,7} x R in {1,7} x {fade,follow} — IS 2024 (funding history starts
2024-01), frozen pick -> OOS 2025-01-01..now + full sensitivity map. No lookahead:
weights chosen at close t earn day t+1. ASCII output only.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FUND = HERE / "funding_hist_bybit.json"
CANDLES = HERE / "xsmom_candles.json"
FEE = 0.0007
IS_START, IS_END = "2024-01-01", "2025-01-01"
QUANTILE = 4  # quartiles here: overlap universe is smaller than xsmom's


def base_of_bybit(sym: str) -> str:
    s = sym[:-4] if sym.endswith("USDT") else sym  # strip USDT
    if s.startswith("1000"):
        s = s[4:]
    return s


def base_of_okx(inst: str) -> str:
    return inst.split("-")[0]


def load() -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    fund_raw = json.loads(FUND.read_text())          # bybit sym -> {date: funding sum}
    px_raw = json.loads(CANDLES.read_text())         # okx inst -> {date: close}
    px_by_base = {base_of_okx(i): cl for i, cl in px_raw.items()}
    fund, px = {}, {}
    for bsym, f in fund_raw.items():
        b = base_of_bybit(bsym)
        if b in px_by_base:
            fund[b] = f
            px[b] = px_by_base[b]
    return fund, px


def daily_rets(closes: dict[str, float], dates: list[str]) -> dict[str, float]:
    out, prev = {}, None
    for d in dates:
        c = closes.get(d)
        if c is not None and prev is not None:
            out[d] = c / prev - 1
        if c is not None:
            prev = c
    return out


def simulate(fund: dict, px: dict, dates: list[str], lb: int, reb: int, fade: bool,
             d_from: str, d_to: str) -> list[tuple[str, float]]:
    rets = {b: daily_rets(cl, dates) for b, cl in px.items()}
    weights: dict[str, float] = {}
    out = []
    for i, d in enumerate(dates[:-1]):
        nxt = dates[i + 1]
        if i >= lb and i % reb == 0:
            scores = {}
            for b in fund:
                window = dates[i - lb + 1:i + 1]
                vals = [fund[b].get(w) for w in window]
                if any(v is None for v in vals):
                    continue
                if px[b].get(d) is None:
                    continue
                scores[b] = sum(vals)
            if len(scores) >= QUANTILE * 2:
                # fade: short highest funding, long lowest
                ranked = sorted(scores, key=scores.get, reverse=True)
                q = max(2, len(ranked) // QUANTILE)
                hi, lo = ranked[:q], ranked[-q:]
                shorts, longs = (hi, lo) if fade else (lo, hi)
                new_w = {b: 0.5 / len(longs) for b in longs}
                new_w.update({b: -0.5 / len(shorts) for b in shorts})
                cost = sum(abs(new_w.get(b, 0) - weights.get(b, 0))
                           for b in set(new_w) | set(weights)) * FEE
                weights = new_w
            else:
                cost = 0.0
        else:
            cost = 0.0
        r = sum(w * rets[b].get(nxt, 0.0) for b, w in weights.items()) - cost
        # funding P&L: longs pay positive funding, shorts receive it (and pay when
        # negative) => per-day funding P&L = -w * funding_sum. FOLLOW pays on BOTH
        # legs; FADE collects on both. This term is mandatory for honesty.
        r += sum(-w * fund[b].get(nxt, 0.0) for b, w in weights.items())
        if d_from <= nxt < d_to:
            out.append((nxt, r))
    return out


def stats(series):
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
    import sys
    fund, px = load()
    if "--oldguard" in sys.argv:
        keep = {b for b, cl in px.items() if len(cl) >= 1700}
        fund = {b: f for b, f in fund.items() if b in keep}
        px = {b: cl for b, cl in px.items() if b in keep}
        print("OLD-GUARD control (survivorship-clean)")
    print(f"joined universe ({len(fund)}): {','.join(sorted(fund))}")
    dates = sorted({d for cl in px.values() for d in cl if d >= "2023-12-01"})

    grid = [(lb, reb, fade) for lb in (1, 3, 7) for reb in (1, 7) for fade in (True, False)]
    print("\n-- IN-SAMPLE 2024 (net, quartile L/S gross 1x) --")
    results = []
    for lb, reb, fade in grid:
        st = stats(simulate(fund, px, dates, lb, reb, fade, IS_START, IS_END))
        results.append((st["sharpe"], lb, reb, fade, st))
        print(f"L={lb} R={reb} {'FADE  ' if fade else 'FOLLOW'}  Sharpe={st['sharpe']:5.2f} "
              f"ann={st['ann']*100:7.1f}% maxDD={st['maxdd']*100:6.1f}%")
    results.sort(reverse=True, key=lambda z: z[0])
    _, lb, reb, fade, _ = results[0]
    print(f"\nIS pick: L={lb} R={reb} {'FADE' if fade else 'FOLLOW'}")

    print("\n-- OUT-OF-SAMPLE 2025-01-01..now (frozen) --")
    st = stats(simulate(fund, px, dates, lb, reb, fade, IS_END, "2027-01-01"))
    print(f"IS-pick: ann={st['ann']*100:6.1f}% Sharpe={st['sharpe']:5.2f} maxDD={st['maxdd']*100:6.1f}% "
          f"worst30={st['worst30']*100:6.1f}% ({st['n']}d)")
    for cap in (1000, 5000):
        print(f"  ${cap}: ~${cap*st['ann']/365:.2f}/day net")

    print("\n-- OOS all combos --")
    for lb2, reb2, fade2 in grid:
        st2 = stats(simulate(fund, px, dates, lb2, reb2, fade2, IS_END, "2027-01-01"))
        print(f"L={lb2} R={reb2} {'FADE  ' if fade2 else 'FOLLOW'}  ann={st2['ann']*100:7.1f}% "
              f"Sharpe={st2['sharpe']:5.2f} maxDD={st2['maxdd']*100:6.1f}%")


if __name__ == "__main__":
    main()
