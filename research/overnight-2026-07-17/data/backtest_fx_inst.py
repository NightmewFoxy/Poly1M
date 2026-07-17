"""Institutional FX families on the 7 USD majors: carry, xs-momentum, tsmom.

Post-hunt addendum #3 (owner: "test more strategies", 2026-07-17). The three
families the academic/practitioner literature actually documents for FX,
tested with FIXED classic specs — no grids, no parameter picking, so both
periods are honest (the xsmom lesson: selection-free specs, report everything):

  fx-xsmom : rank the 7 currencies (vs USD) by trailing return, ensemble of
             {21,63,126,252}d lookbacks, LONG top-2 / SHORT bottom-2, equal
             weight (1x gross), rebalance every 21 trading days.
  fx-tsmom : per currency, position = mean sign of {63,126,252}d trailing
             return, scaled 1/7 each, rebalance every 21 trading days.
  fx-carry : rank by short-rate differential vs USD (FRED monthly policy /
             call-money rates), LONG top-2 / SHORT bottom-2, monthly. Carry
             accrual (rate diff / 252 per day) is included for THIS strategy
             and reported separately from the spot leg.

Currencies quoted as FC/USD (USDJPY/USDCHF/USDCAD inverted) so "long" always
means long the foreign currency against USD. Costs 0.006%/side on turnover;
swap spreads beyond mid-carry not modeled. Data: cached tarr_fx_candles.json
daily closes (Yahoo, 2006→now) + FRED fredgraph CSVs (cached fx_rates.json).
Periods reported: 2010-2019, 2020→now, and last-7-days P&L on $200. Read-only.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import httpx

import backtest_tarr as bt

HERE = Path(__file__).resolve().parent
PX_CACHE = HERE / "tarr_fx_candles.json"
RATE_CACHE = HERE / "fx_rates.json"
PAIRS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")
CCY = {"EURUSD": "EUR", "GBPUSD": "GBP", "USDJPY": "JPY", "AUDUSD": "AUD",
       "USDCAD": "CAD", "USDCHF": "CHF", "NZDUSD": "NZD"}
INVERT = {"USDJPY", "USDCAD", "USDCHF"}
FRED = {"USD": "FEDFUNDS", "EUR": "IRSTCI01EZM156N", "GBP": "IRSTCI01GBM156N",
        "JPY": "IRSTCI01JPM156N", "AUD": "IRSTCI01AUM156N", "CAD": "IRSTCI01CAM156N",
        "CHF": "IRSTCI01CHM156N", "NZD": "IRSTCI01NZM156N"}
FEE = 0.00006
REB = 21  # trading days
P1, P2 = ("2010-01-01", "2020-01-01"), ("2020-01-01", "2027-01-01")
CAP = 200.0


def load_prices() -> tuple[list[str], dict[str, list[float]]]:
    """Aligned daily FC/USD closes per currency, common dates."""
    raw = json.loads(PX_CACHE.read_text())["1D"]
    series = {}
    for p in PAIRS:
        m = {}
        for ts, o, h, l, c in raw[p]:
            d = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d")
            m[d] = 1.0 / c if p in INVERT else c
        series[CCY[p]] = m
    common = sorted(set.intersection(*(set(m) for m in series.values())))
    return common, {c: [series[c][d] for d in common] for c in series}


def load_rates() -> dict[str, dict[str, float]]:
    """ccy -> {YYYY-MM: rate %}. FRED fredgraph CSV, no key needed."""
    if RATE_CACHE.exists():
        return json.loads(RATE_CACHE.read_text())
    out = {}
    with httpx.Client(timeout=25, trust_env=False, follow_redirects=True) as c:
        for ccy, sid in FRED.items():
            r = c.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": sid})
            rows = r.text.strip().splitlines()[1:]
            m = {}
            for line in rows:
                d, v = line.split(",")[:2]
                if v not in (".", ""):
                    m[d[:7]] = float(v)
            out[ccy] = m
            last = max(m) if m else "NONE"
            print(f"rates {ccy} ({sid}): {len(m)} months, through {last}")
    RATE_CACHE.write_text(json.dumps(out))
    return out


def stats_from(dates: list[str], rets: list[float], d_from: str, d_to: str) -> dict:
    return bt.stats([(d, r) for d, r in zip(dates, rets) if d_from <= d < d_to])


def run_weights(dates: list[str], px: dict[str, list[float]],
                weight_fn, accrual_fn=None) -> list[float]:
    """Daily portfolio returns; weight_fn(i) -> {ccy: w} on rebalance days."""
    ccys = list(px)
    n = len(dates)
    rets = [0.0] * n
    w = {c: 0.0 for c in ccys}
    for i in range(1, n):
        r = 0.0
        for c in ccys:
            r += w[c] * (px[c][i] / px[c][i - 1] - 1)
        if accrual_fn is not None:
            r += accrual_fn(w, dates[i])
        if (i - 253) % REB == 0 and i >= 253:  # rebalance at close -> costs hit today
            new_w = weight_fn(i)
            r -= FEE * sum(abs(new_w[c] - w[c]) for c in ccys)
            w = new_w
        rets[i] = r
    return rets


def main() -> None:
    dates, px = load_prices()
    ccys = list(px)
    print(f"prices: {len(dates)} common days {dates[0]}..{dates[-1]}\n")
    rates = load_rates()
    print()

    def xs_weights(i: int) -> dict[str, float]:
        score = {c: sum(sorted(ccys, key=lambda x: px[x][i] / px[x][i - lb]).index(c)
                        for lb in (21, 63, 126, 252)) for c in ccys}
        order = sorted(ccys, key=lambda c: score[c], reverse=True)  # high score = winner
        w = {c: 0.0 for c in ccys}
        for c in order[:2]:
            w[c] = 0.25
        for c in order[-2:]:
            w[c] = -0.25
        return w

    def ts_weights(i: int) -> dict[str, float]:
        w = {}
        for c in ccys:
            s = sum(1 if px[c][i] > px[c][i - lb] else -1 for lb in (63, 126, 252))
            w[c] = (s / 3) / len(ccys)
        return w

    def rate_diff(c: str, d: str) -> float | None:
        mon = d[:7]
        rc = rates.get(c, {})
        ru = rates.get("USD", {})
        mc = max((m for m in rc if m <= mon), default=None)
        mu = max((m for m in ru if m <= mon), default=None)
        if mc is None or mu is None or mc < "2005" or mu < "2005":
            return None
        return rc[mc] - ru[mu]

    def carry_weights(i: int) -> dict[str, float]:
        diffs = {c: rate_diff(c, dates[i]) for c in ccys}
        if any(v is None for v in diffs.values()):
            return {c: 0.0 for c in ccys}
        order = sorted(ccys, key=lambda c: diffs[c], reverse=True)
        w = {c: 0.0 for c in ccys}
        for c in order[:2]:
            w[c] = 0.25
        for c in order[-2:]:
            w[c] = -0.25
        return w

    def carry_accrual(w: dict[str, float], d: str) -> float:
        a = 0.0
        for c, wc in w.items():
            if wc:
                diff = rate_diff(c, d)
                if diff is not None:
                    a += wc * (diff / 100.0) / 252.0
        return a

    strategies = [
        ("fx-xsmom (spot)", xs_weights, None),
        ("fx-tsmom (spot)", ts_weights, None),
        ("fx-carry (spot+carry)", carry_weights, carry_accrual),
        ("fx-carry (spot only)", carry_weights, None),
    ]
    week_from = dates[-6]
    print(f"{'strategy':24s} {'2010-2019':>28s} {'2020-now':>28s} {'wk $200':>8s}")
    for name, wf, af in strategies:
        rets = run_weights(dates, px, wf, af)
        cells = []
        for d_from, d_to in (P1, P2):
            st = stats_from(dates, rets, d_from, d_to)
            cells.append(f"ann={st['ann']*100:+5.1f}% Sh={st['sharpe']:5.2f} DD={st['maxdd']*100:5.1f}%")
        wk = [r for d, r in zip(dates, rets) if d >= week_from]
        pnl = CAP * (math.prod(1 + r for r in wk) - 1)
        print(f"{name:24s} {cells[0]:>28s} {cells[1]:>28s} {pnl:+8.2f}")
    print(f"\n(week = {week_from}..{dates[-1]}; fees {FEE*1e4:.1f}bp/side on turnover; "
          f"carry rates monthly FRED, forward-filled)")

    # rate coverage honesty
    print("\nrate series coverage (carry validity):")
    for c in FRED:
        m = rates.get(c, {})
        print(f"  {c}: {min(m) if m else '-'}..{max(m) if m else '-'}")


if __name__ == "__main__":
    main()
