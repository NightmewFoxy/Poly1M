# liq-wick-reversion — buying liquidation dumps on 5m bars (BTC/ETH/SOL)

**Verdict: MARGINAL (weak). Dump-buying had a real, strong 2024 in-sample effect
(+59…+166bp/event, t up to 4.0) that decayed ~85% out-of-sample: frozen pick
+15.5bp/event, t=0.64, ≈+17%/yr net. All dump-buy cells stayed positive OOS
(+11–29%/yr) but none clear t=2. Fading pumps (shorting squeezes) is anti-alpha
in both periods. Ranked below xsmom: weaker statistics, fatter tails (knife-
catching), and it requires 24/7 automation to trade 5-minute triggers.**

## Mechanism tested
Single 5m bar move ≥ thr {1.5%, 2.5%, 4%} → enter at bar close (dump→LONG,
pump→SHORT), exit after H {6,12,36} bars (30m/1h/3h); optional forced-flow
filter (bar volume >5× trailing 1h avg); one position at a time; fees 0.14%
per event.

## Verification
- Data: data.binance.vision monthly 5m futures klines, 262,656 bars/symbol
  (2024-01→2026-06), cached; script `data/backtest_liqwick.py`.
- IS 2024 grid (pick by t-stat, n≥30) → frozen OOS 2025→2026-06.

## Results
| cell (dump-buy) | IS 2024 | OOS 2025→ |
|---|---|---|
| thr1.5% H36 (pick) | +118bp/ev, t=4.0 | +15.5bp/ev, t=0.64, +16.9%/yr |
| thr1.5% H6 | +59bp, t=3.2 | +21.3bp, t=1.41, +29.0%/yr |
| thr2.5% H6 | +103bp, t=2.1 | +116bp, t=1.79, +28.6%/yr (n=37) |
| pump-short (all) | −45…−212bp/ev | negative/noise |

- $5k at the OOS point estimates ≈ $2.3–4/day — comparable to xsmom's range but
  with t<2 everywhere OOS (could be zero), high event-level variance, and real
  tail risk (a cascade that keeps cascading).
- The volume filter did not help (cuts n without raising the mean).

## Bottom line
The only mean-reversion-family survivor tonight, because it reverts FORCED flow
rather than prices generally. Too statistically fragile and ops-heavy to be the
pick; worth revisiting only as a future add-on module once xsmom is running,
ideally with maker-limit resting bids instead of taker entries.
