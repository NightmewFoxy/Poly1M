# ta-rr-template — classic indicator entry + ATR stop + 2:1 take-profit (post-hunt addendum)

**Verdict: DEAD. The retail-TA template (chart-signal entry, k×ATR stop loss,
2:1 reward:risk take-profit, long/short BTC/ETH/SOL) does not survive the
IS→OOS split. Best in-sample config (Donchian-55 breakout, 4H, k=2.0:
+36.1%/yr, Sharpe 0.92 IS) does −9.4%/yr, Sharpe −0.11 OOS. Top-8 IS configs
OOS: 6 of 8 negative (−34.5% to +15.5%/yr, no stable pattern). Win rates sit
at 33–41% everywhere — almost exactly the ~33% a 2:1 RR earns on a no-edge
entry, i.e. the exit scheme is reshaping noise, not harvesting signal.**

Owner asked 2026-07-17 morning why the hunt skipped "traditional" strategies
(indicators + 2:1 risk-reward + stop loss). This tests exactly that template
under the same honesty controls as the overnight hunt.

## Mechanism tested
Signal at bar close, fill next bar open, flat otherwise. Entries: EMA cross
(9/21, 20/50) and Donchian breakout (20, 55 bars), both directions. Exit ONLY
by intrabar stop (entry ∓ k×ATR14) or take-profit at 2× the stop distance;
both-in-one-bar resolves to the STOP (pessimistic). Grid: 4 entries × {1H,4H}
× k∈{1.5,2.0} = 16 configs, portfolio BTC/ETH/SOL equal weight, fees
0.07%/side. Script `data/backtest_tarr.py`, data OKX 1H OHLC 2021-12→2026-07-17
(cached `data/tarr_candles_1h.json`, gitignored).

## Results
- IS 2022-2024: every 1H config negative (−6% to −43%/yr — fee bleed at
  frequency, same kill factor as rsi-meanrev). 4H configs mixed; best
  don55/4H/k2.0 +36.1%/yr Sharpe 0.92 (428 trades, win 41.4%).
- OOS 2025→now (frozen pick): **−9.4%/yr, Sharpe −0.11, maxDD −33.5%**
  (238 trades, win 36.6%). ≈ −$0.26/day at $1k.
- OOS sensitivity, top-8 IS: don20 −6.4%, ema9/21 −14.5%, don55k1.5 +8.0%,
  don20k1.5 −20.1%, ema20/50-1H −34.5%, ema20/50-4H-k1.5 +15.5% (Sharpe 0.85 —
  a lottery survivor you could only have picked with hindsight; it ranked 7th
  IS), ema9/21k1.5 −26.3%. No parameter neighborhood is robust.
- Last-7-days check (2026-07-11→17, $200): configs ranged **−$4.17 to +$5.14**,
  IS pick −$2.48. Sign flips across near-identical configs in the same week —
  single-week results are noise, as expected.

## Why the 2:1 RR doesn't rescue it
Expectancy = win%×2R − loss%×1R. Observed win rates 33–41% bracket the 33.3%
no-edge break-even almost exactly; the small residual edge in trending IS years
was regime luck (2023-24 trends), and 0.14% round-trip × hundreds of trades/yr
eats what's left. Money management reshapes the P&L distribution; only the
entry's predictive power sets its mean, and that mean is ≈0 on majors.

## Bottom line
Confirms the overnight meta-finding from the other side: the profitable part
of "traditional" trading in 2024-2026 crypto is the momentum CONTENT (which
xsmom/tsmom capture systematically), not the indicator/RR/stop-loss WRAPPER.
Family closed alongside rsi-meanrev.
