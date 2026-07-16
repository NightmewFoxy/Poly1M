# LEADERBOARD — overnight crypto strategy hunt (2026-07-17)

**CURRENT BEST (in-scope, futures long/short): xsmom-alts — cross-sectional alt
momentum, selection-free ensemble (long top-quintile / short bottom-quintile
weekly, lookbacks 7/14/28/60 equal-weight). VIABLE: +26.1%/yr net OOS on the
survivorship-CLEAN universe, Sharpe 1.07, maxDD −19.6%, worst 30d −9.4%;
~$0.71/day @ $1k, ~$3.57/day @ $5k at 1x (2x ≈ double, with −40% DD risk).
Sign robust in every cell of both universes; fees included; weekly ~20min ops.**

Ranked, verified-only. Every entry must have a `verdicts/<slug>.md` behind it.
Owner scope (02:50 MYT): futures long/short trading only — yield/arb entries are
kept as reference baselines, not candidates.

| rank | strategy | verdict | $/day @ $1k | $/day @ $5k | worst 30d | ops burden | one-line why |
|---|---|---|---|---|---|---|---|
| 1 | xsmom-alts (L/S alt momentum ensemble) | VIABLE | $0.71 | $3.57 | −9.4% (maxDD −19.6%) | ~20 min/week | +26.1%/yr net OOS survivorship-clean, Sharpe 1.07, selection-free, sign-robust everywhere; full-universe upper bound +87%/yr. |
| 2 | tsmom-daily (long-flat trend, majors) | MARGINAL | $0.33 | $1.66 | −24.6% (maxDD −38.5%) | ~10 min/day | +12.1%/yr net OOS but fragile params, huge DD, long-short variants negative; a diversifier, not a money-maker. |
| ref | funding-harvest (DESCOPED: yield) | MARGINAL | $0.29 | $1.45 | −2.4% | ~15 min/day | Real but small: +10.6%/yr net OOS (2025→now), slow+selective only; the bar for in-scope strategies. |

## Rejected (verified DEAD)
| strategy | kill factor |
|---|---|
| rsi-meanrev (RSI dip-buy/top-sell, 1H/4H majors) | Fee bleed × trade frequency; gross edge ≈0 — ALL 24 configs negative OOS (best-IS pick −26.4%/yr). External "survived fees" claim = 10-day noise. |
