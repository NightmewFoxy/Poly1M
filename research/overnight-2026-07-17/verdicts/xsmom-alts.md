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

---

## DEEP-DIVE (iteration 11, robustness — script `data/xsmom_deep.py`)

1. **Universe bounds (ensemble LS, OOS 2024→now):** clean-11 +26.1%/yr (Sh 1.07)
   → **mid-15 +38.0%/yr (Sh 1.31, maxDD −15.9%)** → full-36 +87.3% (inflated).
   Mid-15 = everything listed ≥6mo before OOS (adds BNB/SUI/PEPE/WLD); its only
   residual bias is coins that died before 2026 — modest. Honest range:
   **+26–38%/yr net at 1x, Sharpe 1.1–1.3.**
2. **Mode decomposition (mid-15):** long-only +47.6%/yr but Sharpe 0.88 and
   maxDD −67%; short-only −28.2%/yr standalone. **The short leg is a hedge, not
   a profit center** — it buys the −16% drawdown profile. Do not trade long-only
   thinking it's "the same but better".
3. **Rebalance-phase robustness:** all 7 weekly phases positive OOS
   (+16.5%…+38.0%, mean +23.7%) — expected value ≈ phase mean ~24%/yr (mid-15),
   not the best-phase 38%.
4. **Per-year OOS (mid-15):** 2024 +71.2%, 2025 +20.0%, 2026H1 +19.9% —
   positive every year; the CURRENT regime supports ~+10–20%/yr (clean-11 2026H1
   was +9.9%). Quote this, not the 3-year average, as the forward expectation.
5. **Turnover:** ~1.04× book/week ⇒ fee drag ~3.8%/yr at taker 7bp/side
   (~1.1%/yr if maker-filled — execution upside; schedule rebalances ~20:00 UTC
   per the seasonality finding).

**Refined morning numbers (1x gross, mid-15 spec, phase-mean honesty):**
~+20–30%/yr net expectation, Sharpe ~1.0–1.3, maxDD −16–20%;
$1k ⇒ ~$0.55–0.80/day; $5k ⇒ ~$2.70–4.10/day. 2x leverage doubles both P&L and
drawdown (maxDD ~−35%); beyond 2x, momentum-crash weeks threaten liquidation.
