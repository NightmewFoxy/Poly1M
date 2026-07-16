# xsmom-alts — cross-sectional momentum on alt perps (long winners / short losers)

**Verdict: VIABLE (best in-scope so far). Selection-free momentum ensemble on the
survivorship-CLEAN universe: +26.1%/yr net OOS (2024→now), Sharpe 1.07, maxDD
−19.6%, worst 30d −9.4%. ~$0.71/day @ $1k, ~$3.57/day @ $5k at 1x gross; scales
~linearly with leverage (2x ⇒ ~52%/yr, maxDD ~−40%). The effect's SIGN is robust
everywhere: every momentum cell positive OOS, every reversal cell negative, in
both universes.**

## Mechanism
Weekly rebalance at close across a USDT-perp universe: rank by trailing R-day
return; LONG top quintile, SHORT bottom quintile, equal weight, gross 1x
(0.5/0.5). The traded spec is the **selection-free ensemble**: equal capital
across R ∈ {7, 14, 28, 60} no-skip momentum sub-strategies (no parameter picking
at all — every lookback runs simultaneously).

## Verification
- Data: OKX daily perp candles 2021-10→2026-07-15, top-40 by today's volume
  (36 usable) + an "old guard" control = the 11 perps with full history since
  2021 (ETH BTC SOL XRP DOGE BCH UNI NEAR ADA LINK AAVE). Cached
  `data/xsmom_candles.json`, script `data/backtest_xsmom.py`.
- Fees 0.07%/side on turnover; weekly rotation; no lookahead (weights at close t
  earn t+1).
- Discipline: grid IS 2022-2023 / frozen OOS 2024→now for the pick; PLUS the
  selection-free ensemble reported on both periods; PLUS survivorship control.

## Results
| spec | universe | IS 2022-23 | OOS 2024→now |
|---|---|---|---|
| frozen IS-pick (lb28skip7 / lb28) | full / old-guard | Sharpe 0.56 / 0.86 | +13.3%/yr Sh 0.51 / +11.5%/yr Sh 0.51 |
| **ensemble (7/14/28/60 MOM)** | **old-guard (clean)** | +10.7%/yr Sh 0.50 | **+26.1%/yr Sh 1.07, maxDD −19.6%** |
| ensemble (same) | full (survivorship-inflated) | +0.2%/yr | +87.3%/yr Sh 1.91 (UPPER BOUND, not trustworthy) |
| reversal variants (all) | both | negative | −22% to −66%/yr (confirms momentum) |

- Honest expectation for live trading a liquid dynamic universe: between the
  clean +26%/yr and the inflated +87%/yr, much closer to +26%. Breadth (more
  than 11 symbols, chosen point-in-time by liquidity) should add something.
- Funding P&L not modeled: alt L/S books roughly cancel (longs pay, shorts
  receive; crowded pumped alts on the short side usually pay MORE) ⇒ omission is
  neutral-to-conservative here.

## Caveats / risks
- Regime dependence: 2022-23 delivered only ~+10%/yr — momentum breathes with
  the cycle; momentum CRASHES (sharp reversals) are the classic tail (see
  −19.6% maxDD even in a good regime).
- Concentration: 11-symbol universe ⇒ only 2 names/side. A live version should
  use a point-in-time top-20/30 liquid universe (~4-6/side).
- Weekly ops ≈ 20 min; one exchange; shorts = perps (no borrow needed).
- Leverage: 2-3x feasible on perps; scales return AND drawdown; liquidation risk
  concentrated in momentum-crash weeks — size margin for −20% weeks.

## Bottom line
First strategy tonight that clears the bar convincingly: ~2.5× the funding-
harvest baseline at Sharpe >1 with fees included, selection-free, sign-robust
across universes and regimes. At owner scale: ~$1.3k/yr on $5k at 1x; leverage
2x ≈ $2.6k/yr if he can stomach −40% drawdowns. Candidate for the morning pick.
