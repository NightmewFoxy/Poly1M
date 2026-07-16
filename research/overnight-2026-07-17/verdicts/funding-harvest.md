# funding-harvest — delta-neutral perp funding harvesting

**Verdict: MARGINAL (as yield) — and DESCOPED by owner directive 02:50 MYT
("futures long/short trading only; no staking/investing-like yield"). Kept as the
verified baseline that passive carry ≈ 10%/yr, i.e. the number an in-scope trading
strategy must beat.**

## Mechanism
Long spot + short USDT-perp on the symbols with the highest trailing funding;
collect funding every 8h while price-neutral. Daily rebalance into top-K by
trailing annualized funding above a threshold; cash when nothing qualifies.

## Verification (real data, reproduced tonight)
- Data: Bybit v5 funding history, 2024-01-01 → 2026-07-16, today's top-30 turnover
  linear perps (~2,700–4,300 funding events each), fetched + cached
  (`data/funding_hist_bybit.json`, script `data/backtest_funding.py`).
- Costs: taker both legs + slippage = 0.36% of slot notional per full rotation;
  funding earned on 50% of slot capital (1x perp margin, no leverage).
- Discipline: 27-combo grid searched IN-SAMPLE on 2024 only (best: K=1, 14d
  lookback, >10% APR threshold, +12.1%/yr IS); params frozen, then OOS 2025-01-01
  → 2026-07-16 (562 days).

## Results (OOS, net of costs)
- **+16.25% over 562d ⇒ ~10.6%/yr net.** Worst 30d: −2.44%. 71 rotations.
- **$1k ⇒ ~$0.29/day. $5k ⇒ ~$1.45/day.** (2–3x perp margin scales this ~1.5–2x
  with liquidation-watch ops.)
- Param sensitivity OOS: K=1/lb=7d/th=10% ⇒ +8.3%/yr; K=3/lb=14d/th=10% ⇒ +6.2%/yr;
  fast/no-threshold variants go NEGATIVE (rotation costs eat the carry). The edge
  is real but small and parameter-sensitive; slow + selective is the only regime
  that survives costs.

## Caveats / risks
- Universe = today's top-30 by turnover ⇒ survivorship + several tokenized-equity/
  metal perps (XAUUSDT, SOXL, SNDK, SKHYNIX) rode into the basket. Directionally
  this FLATTERS the result.
- Basis P&L on entry/exit not modeled (spot-perp basis moves can add ±0.1–0.3%
  per rotation, both directions).
- Blow-up mode: perp short liquidation on a violent pump if margin is thin
  (mitigated at 1x, the sized assumption).
- Ops: ~15 min/day (rotation check), one exchange, no custody complexity.

## Bottom line
Real, reproducible, boring: ~10%/yr net at retail scale ⇒ **$0.29–$1.45/day at
$1–5k — two orders of magnitude short of the RM200/day goal, and now out of scope
(yield-like).** Baseline for the directional hunt: beat 10%/yr net OOS or it's
not worth trading.
