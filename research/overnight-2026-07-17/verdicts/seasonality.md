# seasonality — time-of-day / day-of-week windows on BTC/ETH/SOL

**Verdict: DEAD net of fees. The one real anomaly found — a US-evening
(20:00–23:00 UTC) long drift of +5–7bp/day gross (t≈2–3, survives OOS) — is fully
consumed by the 14bp round-trip taker cost of harvesting a 2–3h window daily.
Day-of-week effects are noise. This also explains why external seasonality claims
are always quoted gross.**

## What was tested
- Pre-registered external windows on BTC (no fitting): H1 QuantPedia long
  21:00→23:00 UTC daily; H2 "Monday Asia open" (Sun 21:00→Mon 08:00 UTC);
  H3 weekend bias (readable from the day-of-week table).
- Disciplined discovery: hour-of-day grid pooled BTC/ETH/SOL, IS 2022-2024 →
  top-3 contiguous windows → OOS 2025→now. Day-of-week: IS-best long / IS-worst
  short → OOS. Fees 0.14% per daily round trip.
- Data: cached OKX 1H candles (42k bars/symbol), script `data/backtest_seasonality.py`.

## Results
| test | gross | net (taker) |
|---|---|---|
| H1 21→23 UTC [full 2022→now, n=1657] | +5.2bp/d (t=2.77) REAL | **−8.8bp/d** |
| H1 [OOS 2025→, n=561] | +6.0bp/d (t=2.25) | −8.0bp/d |
| H2 Monday-Asia [full, n=474] | −0.2bp (t=−0.03) dead even gross | −14.2bp |
| discovered 20→23 UTC [OOS] | +7.4bp/d (t=1.68) | −6.6bp/d |
| discovered 03→07, 09→12 UTC [OOS] | ≈0 gross (didn't hold) | −13 to −15bp/d |
| dow: long Mon [OOS n=80] | +28.8bp (t=1.11) | +14.8bp (t=0.57) noise |
| dow: short Thu [OOS n=81] | +54.7bp (t=1.88) | +40.7bp (t=1.40) — cherry-picked from 7 cells, not significant |

- Maker-both-sides execution (~4bp) would leave the 20–23 UTC window ~+2-3bp/day
  ≈ 8-11%/yr before slippage/fill-risk — below the xsmom leader with worse
  fill-uncertainty; not worth building.

## Bottom line
No tradeable seasonality at retail taker costs. The 20–23 UTC gross drift is real
and worth REMEMBERING as an execution-timing tailwind for OTHER strategies (e.g.
schedule xsmom's weekly rebalance near 20:00 UTC and lean entries long-side into
that window), but it is not a standalone strategy. Family closed.
