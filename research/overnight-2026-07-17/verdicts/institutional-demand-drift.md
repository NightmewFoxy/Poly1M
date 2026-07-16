# institutional-demand-drift — Coinbase premium / ETF-flow → next-day BTC

**Verdict: DEAD as a standalone (2024-launch-regime artifact). IS 2024 looked
spectacular (Sharpe 2.2–2.4, +100–172%/yr — the spot-ETF launch year, when US
demand flow genuinely led price). OOS 2025→now: frozen pick +11.3%/yr, Sharpe
0.47, maxDD −42.8%, and the config map flips sign (−13%…+19%/yr) — no stable
edge remains. The academic Granger-causality results (SSRN 6592830, FalconX)
captured a regime, not a durable mechanism.**

## Mechanism tested
Daily Coinbase premium = Coinbase BTC-USD close ÷ OKX BTC-USDT close − 1
(free, real-time computable US-demand proxy; the gap-sweep's #1 novel candidate).
Rolling 30d z-score → long BTC next day if z > +Z, short if z < −Z (Z ∈
{0.3,0.5,1.0}, raw + 3d-smoothed) + always-in sign variant. Fees 0.07%/side of
turnover. IS 2024 → frozen → OOS 2025→2026-07. 988 joined days.

## Verification
Data: Coinbase Exchange public candles (cached `data/cb_btcusd_daily.json`) ×
cached OKX dailies; script `data/backtest_cbpremium.py`. Caveat: premium
includes USDT/USD basis noise (avg −0.9bp — small).

## Companion (gap-sweep candidate #2): stablecoin 1h exchange-flow forecasting
**UNVERIFIABLE-DATA + low prior.** Free 1h exchange-flow data is gated
(CryptoQuant/Glassnode paid tiers); and tonight's repeated finding is that 1h
signals die at 14bp round-trip costs (RSI, lead-lag, intraday tsmom all dead).
Not worth paid data.

## Bottom line
The last untested mechanism family is closed. Leaderboard unchanged: xsmom
stands alone as the verified pick.
