# fx-institutional — carry / xs-momentum / tsmom on the 7 USD majors (post-hunt addendum #3)

**Verdict: DEAD-to-TINY. The three documented institutional FX families,
tested with fixed classic specs (no grids, no selection), on G7 majors
2006→now: xs-momentum NEGATIVE in both decades (−3.0%/yr 2010-2019, −1.8%/yr
2020→now); tsmom ≈0 then −1.6%/yr; carry the lone survivor at +1.0%/yr
(Sh 0.19) and +1.8%/yr (Sh 0.43) — real (the accrual leg is all of it; spot
leg alone is negative, the classic carry signature) but economically
irrelevant at retail: ~$3.60/yr on $200, and retail swap spreads (not
modeled) plausibly eat most of it.**

Owner: "why don't u test more strategies" (2026-07-17). These were the three
named-but-untested FX families from `ta-rr-fx.md`. Script
`data/backtest_fx_inst.py` (reuses the cached Yahoo daily closes + FRED
fredgraph CSVs, cached `fx_rates.json`).

## Specs (fixed a priori — the xsmom lesson: selection-free, report all periods)
- Currencies as FC/USD (USDJPY/CAD/CHF inverted). Fees 0.006%/side on turnover.
- fx-xsmom: rank by trailing return, ensemble {21,63,126,252}d, long top-2 /
  short bottom-2 (±25%), rebalance every 21 trading days.
- fx-tsmom: per currency, mean sign of {63,126,252}d returns, 1/7 scale each.
- fx-carry: rank by FRED short-rate differential vs USD, long top-2 / short
  bottom-2, monthly rates forward-filled; carry accrual = rate diff/252/day.

## Results (ann / Sharpe / maxDD)
| strategy | 2010-2019 | 2020→now | last wk $200 |
|---|---|---|---|
| fx-xsmom (spot) | −3.0% / −0.56 / −20.4% | −1.8% / −0.39 / −16.0% | −$0.91 |
| fx-tsmom (spot) | +0.0% / 0.03 / −10.1% | −1.6% / −0.25 / −16.2% | −$0.88 |
| fx-carry (spot+carry) | +1.0% / 0.19 / −9.1% | +1.8% / 0.43 / −5.9% | +$1.46 |
| fx-carry (spot only) | −1.0% / −0.13 / −12.3% | −0.2% / −0.03 / −7.0% | +$1.38 |

## Caveats
- CHF rate series ends 2024-03, NZD 2024-12 (OECD MEI discontinuations),
  forward-filled — recent carry rankings mildly distorted.
- Retail swap spreads: brokers pay/charge rollover at rate-diff ± ~0.5-1%/yr
  markup each way; on a ±1x book that is the same order as the whole edge.
- G10-only universe. The carry literature's better numbers live in EM pairs
  (BRL, MXN, TRY, ZAR...) with fatter differentials AND fatter spreads/
  crash risk; not tested (no free reliable EM intraday/daily OHLC located).

## Bottom line
Consistent with the post-GFC literature: G10 FX carry/momentum Sharpes
collapsed after 2008 and never came back at retail-accessible scale. Every
tested strategy family on FX majors is now dead or sub-T-bill at 1x:
retail-TA wrapper (ta-rr-fx), xs-momentum, tsmom, carry. FX at $200-$5k is
not where the owner's edge is; crypto xsmom remains the only verified
in-scope live candidate. Untested residue: EM carry baskets and PPP/value
(data-gated), both institutional-scale ideas with documented crash tails.
