# rsi-meanrev — RSI-extreme mean reversion on BTC/ETH/SOL (1H/4H, long/short)

**Verdict: DEAD. Every configuration with a meaningful trade count loses money in
BOTH periods. IS-pick (4H RSI-2 X=30 + SMA200 filter): −26.4%/yr net OOS
(3,459 trades). Kill factor: fee bleed at mean-reversion trade frequency — the
gross hourly mean-reversion edge on majors is ≈0, and 0.14% round-trip × thousands
of trades turns that into deep negative.**

## Mechanism tested
RSI(n) Wilder, long when RSI<X / short when RSI>100−X, exit at RSI 50-cross or
48-bar timeout; optional SMA200 trend-alignment filter (Connors style). Grid:
{1H,4H} × RSI{2,14} × X{10,20,30} × filter{on,off} = 24 configs, portfolio of
BTC/ETH/SOL equal weight, fees 0.07%/side.

## Verification
- Data: OKX 1H candles 2021-10→now (41,995 bars/symbol; 4H resampled locally),
  cached `data/rsimr_candles_1h.json`, script `data/backtest_rsimr.py`.
- IS 2022-2024 grid → best (only near-flat) config frozen → OOS 2025→now.

## Results
- IS: ALL high-frequency cells deeply negative (1H RSI-2 variants: −61% to −92%/yr,
  13k–26k trades). Only cells with 0–23 trades show positive noise.
- OOS frozen pick: **−26.4%/yr, Sharpe −0.80, maxDD −39.6%.**
- OOS sensitivity: top-8 IS configs ALL negative OOS (−0.7% to −46%/yr).

## Notes
- This kills the StratProof/Quantocracy claim ("RSI mean reversion survived real
  Binance fees") for majors on 2022–2026 data — their 10-day forward sample was
  noise. Maker-only execution could remove ~half the fee drag, but the gross edge
  is ≈0, so there is nothing left to collect.
- Consistent with the academic sweep's cost-aware ML paper: high-frequency signals
  on majors do not clear costs at retail.

## Bottom line
Do not trade RSI dip-buying/top-selling on crypto majors. Family closed.
