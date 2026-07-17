# ta-rr-fx — the same retail-TA template on forex majors (post-hunt addendum #2)

**Verdict: DEAD on forex too — and structurally worse than crypto, because FX
majors barely move. Intraday (1H/4H, 16 configs): every 1H config negative even
IN-sample at 0.6bp/side costs; frozen IS pick (ema20/50 4H k=1.5, +1.5%/yr IS)
does −1.9%/yr OOS. Daily (10-year IS 2010-2019): ALL 8 configs flat-to-negative
in-sample (best −0.0%/yr); the frozen pick's OOS 2020→now is +3.4%/yr Sharpe
0.87 — positive, but at 1x that is BELOW T-bills, and swap/rollover (not
modeled) plus the flat IS decade say regime luck (2020-2026 trend years), not
edge. Win rates 28–45%, clustered on the ~33% no-edge 2:1 break-even.
Last week on $200: every one of 24 configs between −$0.92 and +$0.36.**

Owner request 2026-07-17: after the crypto template died
(`ta-rr-template.md`), try it on forex. Same engine (imports
`backtest_tarr.py`), same entries (EMA 9/21, 20/50 cross; Donchian 20/55) ×
ATR stop k∈{1.5,2.0} × 2:1 take-profit, long/short, stop-first-if-both
(pessimistic). Script `data/backtest_tarr_fx.py`.

## Setup
- Universe: 7 USD majors (EURUSD GBPUSD USDJPY AUDUSD USDCAD USDCHF NZDUSD),
  equal-weight portfolio, 1x notional.
- Costs: 0.006%/side (~1.3 pips round-trip EURUSD) — fair retail spread.
  NOT modeled: swap/rollover on multi-day holds (drags further), Yahoo quotes
  are indicative (gotcha found mid-run: Yahoo `range=max` silently returns
  MONTHLY bars for FX `1d` — first daily pass was invalid; refetched with
  explicit period1/period2 and a dataGranularity assert).
- Splits: intraday IS 2023-10→2024-12 / OOS 2025→now (Yahoo keeps only ~33mo
  of 1H); daily IS 2010-2019 / OOS 2020→now.

## Results
- Intraday IS: 1H all negative (−2.5% to −8.7%/yr; churn × spread). 4H at most
  +1.7%/yr. OOS top-5: −4.9% to +2.5%/yr, sign-flipping neighbors.
- Daily IS (10 years, 250-580 trades/config): best +0.0%/yr — a full decade of
  the template earning exactly nothing gross of luck. OOS: EMA crosses +2.3 to
  +3.4%/yr (the 2020-2026 dollar-trend regime), Donchians negative.
- Scale reality: FX majors run ~7-10%/yr vol vs crypto's 60-100%. At 1x even a
  genuinely working config pays a few %/yr — hence retail FX is sold at
  10-50x leverage, which multiplies a ≈0 edge into spread bleed and
  margin-call risk, not into income. $200 at 1x ⇒ cents per week (observed:
  −$0.92…+$0.36 across all 24 configs last week).

## Bottom line
The indicator + 2:1 RR + stop-loss wrapper has ≈0 edge on FX majors, same as
crypto majors — confirmed on a 10-year in-sample window this time. The one
mildly positive OOS cell earns less than risk-free at 1x and needs leverage to
matter, which is exactly the retail-forex trap. Family closed for FX as well.
If FX is ever revisited, the only families worth testing are the documented
institutional ones (carry, cross-sectional FX momentum, value/PPP baskets) —
the same "momentum content, not TA wrapper" lesson as xsmom.
