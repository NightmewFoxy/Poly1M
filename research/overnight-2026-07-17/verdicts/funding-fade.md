# funding-fade / funding-follow — funding rate as a directional cross-sectional signal

**Verdict: DEAD in both directions.**
- **FADE (short crowded longs / long crowded shorts): anti-alpha everywhere** —
  −36% to −55%/yr net OOS in every cell of both universes. The retail folk wisdom
  "fade extreme funding" is precisely backwards during trends and pays fees on top.
- **FOLLOW (long high-funding / short negative-funding): a survivorship artifact.**
  Full (today's-top-volume) universe: IS Sharpe 2.21 → OOS +51.1%/yr net incl.
  funding drag — looks spectacular. Survivorship-CLEAN control (9 majors with full
  history): **negative nearly everywhere, frozen pick −35.1%/yr OOS.** The entire
  "edge" came from being retroactively long HYPE/PEPE/SUI-type recent listings
  that are only in the universe because they pumped into today's top-volume list.

## Mechanism tested
Rank perps by trailing L-day funding sum (Bybit funding history); short top
quartile / long bottom quartile (FADE) or the reverse (FOLLOW). L ∈ {1,3,7} ×
rebalance {1d,7d} × direction. Gross 1x (0.5/0.5), fees 0.07%/side on turnover,
**funding P&L included** (mandatory: FOLLOW pays funding on BOTH legs — adding it
cut the full-universe headline from +77.6% to +51.1%/yr before the control killed
the rest). IS 2024 → frozen → OOS 2025-01→2026-07.

## Verification
- Data: Bybit funding history (30 syms, cached) ⋈ OKX daily perp candles (cached)
  → 20-symbol joined universe; old-guard control = the 9 with full history
  (AAVE ADA BTC DOGE ETH LINK NEAR SOL XRP). Script `data/backtest_fundfade.py`.

## Why this matters for the leader (xsmom)
Same control, opposite outcome: xsmom's momentum ensemble KEPT +26.1%/yr on the
clean universe; funding-follow collapsed to negative. Cross-sectional PRICE
momentum is real among majors; cross-sectional FUNDING ranking carries no
information there — funding just proxies "recently-listed hot coin" in
contaminated universes.

## Bottom line
Do not trade funding-fade; do not trust funding-follow backtests built on today's
top-volume universes. A point-in-time-universe retest could revisit FOLLOW someday,
but tonight's clean-universe evidence says the signal is not real. Family closed.
