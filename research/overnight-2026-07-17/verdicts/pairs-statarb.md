# pairs-statarb — rolling z-score pairs mean reversion on old-guard perps

**Verdict: DEAD. Textbook regime decay: IS 2022-23 top-5 portfolio Sharpe 2.35
(+44.8%/yr) → OOS 2024→now with frozen pairs: EVERY pair negative, portfolio
−17.6%/yr (Sharpe −0.90, maxDD −48%). The co-movement structure that made crypto
pairs cointegrate in 2022-23 broke in 2024-26. Pre-registered ETH/BTC: ≈0 both
periods (−6.8% IS / +3.6% OOS, Sharpe 0.33).**

## Mechanism tested
Rolling 90d OLS beta on log prices; z = spread vs rolling mean/std; enter |z|>1.5
(long cheap leg / short rich leg 0.5/0.5), exit |z|<0.5 or 30d timeout. Fees
0.07%/side (0.28% per round trip). Universe: 11 survivorship-clean old-guard
perps → all 55 pairs; top-5 by IS Sharpe frozen for OOS. No lookahead anywhere
(fully rolling estimation).

## Verification
Data: cached OKX daily closes 2021-10→2026-07 (`data/xsmom_candles.json`),
script `data/backtest_pairs.py`.

## Results
| period | top-5 portfolio | ETH/BTC (pre-registered) |
|---|---|---|
| IS 2022-2023 | Sharpe 2.35, +44.8%/yr | −6.8%/yr |
| OOS 2024→now | **−17.6%/yr, Sharpe −0.90** | +3.6%/yr (noise) |

Individual OOS: BCH/XRP −26.6%, AAVE/ADA −33.3%, AAVE/NEAR −10.4%, AAVE/DOGE
−11.0%, AAVE/LINK −16.8% — uniform failure, not one bad pair.

## Bottom line
Daily-frequency crypto pairs mean reversion is an ex-edge. Consistent with the
external warning that published Sharpes (1.5-2.5) come from 2015-2018 samples.
Also coherent with tonight's bigger pattern: 2024-2026 crypto is a MOMENTUM
regime (xsmom works, everything mean-reverting loses). Family closed.
