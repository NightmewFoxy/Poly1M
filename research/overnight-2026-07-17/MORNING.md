# MORNING BRIEF — overnight crypto strategy hunt, 2026-07-17

## The pick: cross-sectional altcoin momentum, long/short perps ("xsmom")

Rank a ~15-perp universe by trailing return every week; **LONG the top quintile,
SHORT the bottom quintile**, equal weight, using an ensemble of four lookbacks
(7/14/28/60 days) simultaneously so there is no parameter to pick. It was the
ONLY strategy out of 12 families verified tonight that survived every honesty
control (out-of-sample split, survivorship-clean universe, funding drag, fees,
rebalance-phase robustness).

**Verified numbers (all NET of 0.07%/side fees, out-of-sample 2024-01→2026-07):**
| cut | ann. return | Sharpe | maxDD |
|---|---|---|---|
| clean-11 universe (strictest) | +26.1%/yr | 1.07 | −19.6% |
| mid-15 universe (fair) | +38.0%/yr | 1.31 | −15.9% |
| per-year: 2024 / 2025 / 2026H1 (mid-15) | +71% / +20% / +20% | — | ≤−16% |
| all 7 weekly rebalance phases | +16.5%…+38% (mean +24%) | all positive | — |

**Forward expectation (honest): ~+20–30%/yr net at 1x gross.**
- $1,000 ⇒ ~$0.55–0.80/day · $5,000 ⇒ ~$2.70–4.10/day
- 2x leverage ≈ double the P&L and the drawdown (maxDD ~−35%); do not exceed 2x
  (momentum-crash weeks + liquidation risk).
- The SHORT leg loses money standalone (−28%/yr) but is what turns −67% long-only
  drawdowns into −16%: it is the seatbelt, not the engine. Trade it as designed.

**Deployment playbook (when you say go):**
1. Venue: Bybit or OKX USDT perps (both fine from Malaysia; you need a funded
   account — this does NOT use Polymarket).
2. Universe: top ~15-20 liquid USDT perps that are ≥6 months old (tonight's spec:
   AAVE ADA BCH BNB BTC DOGE ETH LINK NEAR PEPE SOL SUI UNI WLD XRP).
3. Every 7 days at ~20:00 UTC (a real +5-7bp/day gross drift window we measured —
   free execution tailwind): compute 7/14/28/60d returns, average the four rank
   signals, long top-3 / short bottom-3, equal weight, 1x gross total.
4. Costs: ~1.04× book turnover/week ⇒ ~3.8%/yr taker drag (halve it with limit
   orders). ~20 min/week of ops, or a small script.
5. Kill rule suggestion: stop and reassess if rolling 60d P&L < −15%.

## The honest reality check vs the RM200/day goal
RM200/day ≈ $42/day needs ~$50–75k deployed at these verified rates. At $5k the
best real, verified expectation is **$3–4/day** — crypto futures at retail scale
has no verified path to RM200/day without either capital or taking blow-up risk.
Same conclusion as every prior project phase, now confirmed across 12 more
strategy families with real data.

## Everything else tested tonight (all real-data, fee-aware, OOS)
| strategy | verdict | one line |
|---|---|---|
| tsmom trend (majors, daily) | MARGINAL | +12.1%/yr OOS, Sharpe 0.49, −38.5% maxDD, fragile params |
| liq-wick dump-buying (5m) | MARGINAL-weak | 2024 t=4 effect decayed 85%; OOS +15-29%/yr but t<2; 24/7 bot needed |
| funding harvest (descoped: yield) | MARGINAL | +10.6%/yr — the baseline everything had to beat |
| RSI/Bollinger mean reversion | DEAD | all 24 configs negative; fee bleed × frequency |
| seasonality windows | DEAD net | real 20-23 UTC gross drift exists but fees eat it |
| funding-rate FADE | DEAD | anti-alpha everywhere (−36…−55%/yr) |
| funding-rate FOLLOW | DEAD | survivorship artifact — clean universe kills it |
| pairs stat-arb | DEAD | IS Sharpe 2.35 → OOS −17.6%/yr; relationships broke |
| pre-FOMC drift | DEAD | t≈1.1 noise; sign reversed 2024+ |
| BTC→alts lead-lag (hourly) | DEAD | no retail-latency lag; it's an HFT game |
| intraday first-hours momentum | DEAD | negative both periods |
| open-interest extremes | UNVERIFIABLE | Bybit rate-blocked us; OKX keeps 180d only |
| stablecoin depeg | NOT-A-STRATEGY | ~1 event/2-3yr playbook, kept as a rule |

**Meta-finding of the night: 2024-2026 crypto is a MOMENTUM regime.** Everything
mean-reverting is dead or dying; relative momentum is the one edge that survived
every control. That's also the warning: when the regime turns, xsmom's +20-30%
becomes 2022-23's +10% (it stayed positive, but plan for the downshift).

## Open threads (not blockers)
- Gap-sweep agent (novel mechanisms: on-chain flows, ETF flows, vol-regime
  switching, sector rotation) — pending when this was written; leaderboard
  reflects the final state.
- oi-extreme: retest when Bybit unblocks this IP (hours).
- Overnight samplers recorded cross-exchange spreads + funding all night under
  data/ for any follow-up.
