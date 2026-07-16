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
| seasonality (time-of-day/day-of-week windows) | Real 20–23 UTC gross drift (+5–7bp/d, t≈2–3) but 14bp round-trip fees eat it; dow = noise. Keep only as execution-timing tailwind for other strategies. |
| funding-fade (short crowded longs) | Anti-alpha: −36 to −55%/yr OOS in every cell, both universes. Folk wisdom is backwards. |
| funding-follow (long high-funding) | Survivorship artifact: +51%/yr on contaminated universe → −35%/yr on clean 9-major control. Funding rank = "recently-listed hot coin" proxy, no real signal. |
| event-drift (pre-FOMC long) | t≈1.1 noise over 36 events; sign REVERSED 2024→now (−26bp net/event); best case +2.5%/yr. |
| pairs-statarb (rolling-z pairs MR) | Regime decay: IS Sharpe 2.35 → OOS −17.6%/yr, ALL frozen pairs negative; ETH/BTC ≈ 0. 2024-26 is a momentum regime — mean reversion loses. |
| btc-leads-alts (hourly lead-lag) | No retail-latency lag on majors: every follow cell negative (t to −6); real lag is sub-minute/HFT. |
| intraday-tsmom (first hours → rest of day) | All cells negative both periods; 30-min paper effect doesn't survive hourly granularity + daily fee drag. |
