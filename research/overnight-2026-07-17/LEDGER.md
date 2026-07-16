# LEDGER — overnight crypto strategy hunt (2026-07-17)

Single source of truth. Re-read FIRST every iteration. Conversation context is NOT
trusted memory.

## Strategy queue

Priorities: P1 = high prior AND verifiable tonight with free data. P2 = worth it.
P3 = long shot / probably UNVERIFIABLE tonight. Statuses: queued / verifying /
VIABLE / MARGINAL / DEAD / UNVERIFIABLE-DATA.

**SCOPE (owner, 02:50 MYT): futures LONG/SHORT trading only. Yield/arb/passive
descoped — see PROTOCOL amendment.**

| # | slug | strategy | prior | status | notes |
|---|---|---|---|---|---|
| 1 | tsmom-daily | Time-series momentum / trend on BTC+ETH+SOL perps (daily, long-short) | P1 | **MARGINAL** | VERIFIED iter 3: +12.1%/yr net OOS, Sharpe 0.49, maxDD −38.5%, params fragile, LS variants negative. verdicts/tsmom-daily.md. Data: daily candles 2019→now (Bybit/OKX/data.binance.vision). Grid IS ≤2023, OOS 2024→now. Include fees 0.06%+slip per side. Also test vol-scaled sizing + Donchian breakout variant in same harness. Academic sweep: SSRN 5209907 (Concretum) claims Donchian multi-horizon ensemble on top-20 coins, Sharpe>1.5 NET, +10.8%/yr alpha — strongest in-scope external evidence so far; extend to top-20 rotation via xsmom row if majors verify. |
| 2 | funding-fade | Funding-rate as DIRECTIONAL signal: fade crowded positioning (short extreme+funding pumps / long extreme−funding dumps), unhedged | P2 | queued | DOWNGRADED by directional sweep: one study finds near-zero single-asset predictive power, and the fade was short-biased through 2024's rally. Test the CROSS-SECTIONAL version (rank by funding, fade extremes vs peers) with tempered expectations. Data cached (funding_hist_bybit.json) + candles. |
| 3 | xsmom-alts | Cross-sectional momentum: long top-quintile / short bottom-quintile alt perps, weekly rotate | P1 | **VIABLE** | VERIFIED iter 4 → NEW LEADER: ensemble +26.1%/yr net OOS clean-universe, Sharpe 1.07, maxDD −19.6%. verdicts/xsmom-alts.md |
| 4 | liq-wick-reversion | Buy violent liquidation dumps / sell squeezes intraday on majors (mean reversion after forced flow) | P2 | queued | Data: 1m klines from data.binance.vision bulk zips (BTC/ETH/SOL 2024→now). Define wick/velocity trigger IS, OOS test. Fees hurt at this frequency — taker both ways. |
| 5 | seasonality | Hour-of-day / day-of-week / session effects on BTC/ETH perps (long/short by clock) | P2 | queued | Hourly candles 2021→now. Strict multiple-hypothesis discipline: discover IS ≤2024, confirm OOS 2025→now. Practitioner sweep: "Monday Asia open" momentum claim 28%/yr, 60% win/103 trades, single-sourced vendor-adjacent — test that specific hypothesis too. |
| 6 | pairs-statarb | Long/short pairs on perps (ETHBTC ratio MR; cointegrated alt pairs) | P2 | queued | In scope (it IS long-short futures). Cointegration IS 2022-2024, OOS 2025→now, fees both legs. Practitioner sweep: low-tier paper claims Sharpe 1.58-2.45 on BTC-ETH pair — replicate, expect decay. |
| 7 | btc-leads-alts | Lead-lag: BTC big move → alts follow (long/short alts on BTC impulse) | P2 | queued | Hourly/15m candles BTC + top alts. Test signal lag structure IS, OOS confirm. Retail latency OK if effect persists hours. |
| 8 | oi-extreme | Open-interest spikes / long-short-ratio extremes as reversal or continuation signal | P3 | queued | Bybit has OI history endpoint (verify depth); combine with price. Mark UNVERIFIABLE-DATA if history too shallow. |
| 9 | event-drift | Pre-FOMC drift on BTC: long ~24h before FOMC statement, flat at announcement | P2 | queued | UPGRADED by directional sweep: BTC +0.96% avg day-before-FOMC claim, echoes Lucca-Moench equity drift. FOMC ONLY (CPI debunked — no consistent effect). ~20 events/yr: small-sample honesty required. Data: hourly candles + FOMC dates 2022-2026. |
| 10 | stablecoin-depeg | Depeg mean-reversion (buy panic, sell repeg) — event TRADING | P3 | queued | Episodic; verify known events + frequency. Tail-risk honest (USTC went to 0). |
| 12 | intraday-tsmom | Intraday TSMOM: first-30min return predicts last-30min return on HIGH-VOL days only (Shen/Urquhart/Wang, Financial Review) | P3 | queued | Peer-reviewed but figures unverified (paywalled); needs 30m candles; 2 taker fees/day is a high bar. Re-verify on 2024-2026. |
| 11 | rsi-meanrev | Short-timeframe RSI/Bollinger mean reversion on liquid perps (5m-4h bars) | P2 | queued | Academic sweep: StratProof forward test on REAL Binance fees — 6/22 strategies survived, ALL were RSI mean-reversion; every trend variant lost. 10-day sample too short → backtest 2023→now, IS/OOS, taker fees. |

Non-queued notes from academic sweep: hourly ML (XGBoost) forecasting = DEAD by
its own rigorous paper (arXiv 2606.00060: naive −64% net; cost-aware ≈ buy-and-hold);
dynamic grid (arXiv 2506.11921) descoped (passive); Binance listing-drift = decayed/
front-run; funding-carry decay confirmed externally (matches our baseline verdict).
Seasonality row: prioritize the QuantPedia-specific BTC 21:00→23:00 UTC window
(gross claims only — expect the 0.11%/day taker round-trip to kill it; test anyway).
Pairs row: academic says BTC-ETH cointegration edge is from 2015-2018 samples,
likely decayed — conflicting with practitioner sweep's Sharpe claim; verify, expect decay.
| — | funding-harvest | Delta-neutral funding harvest | — | **MARGINAL (baseline)** | VERIFIED iter 2: +10.6%/yr net OOS, $1.45/day @ $5k. DESCOPED (yield) — the bar to beat. verdicts/funding-harvest.md |
| — | poly-deribit-prob | Polymarket vs Deribit implied prob | — | descoped | Owner scope: futures L/S only. |
| — | carry-basis | Cash-and-carry quarterly basis | — | descoped | Yield-like. |
| — | xex-spot-arb | Cross-exchange spot arb | — | descoped | Not directional trading; sampler keeps recording anyway (free data). |
| — | grid-mm | Grid / passive MM | — | descoped | Passive/short-vol, not directional. |
| — | perpdex-incentives | Perp-DEX incentive farming | — | descoped | Farming, not trading. |

## Data-source notes (what works from this machine)
- 19:10 UTC: **Bybit API rate-blocked this IP** (connect timeouts; OKX/Kraken/
  google fine) after the 400-call funding fetch. Future Bybit bulk fetches:
  sleep ≥0.25s/call. Samplers keep logging Bybit errors as rows until it ages out.
  OKX is the healthy fallback for candles (spot history to 2019, `1Dutc` bars).
- 19:00 UTC: nowcast sweep agent DIED (API connection error). Not relaunched —
  its scope (basis/IV/pegs/incentives/Polymarket) is mostly descoped post owner
  directive; live funding breadth already covered by our own sampler.
- Probe 18:42 UTC: ALL venues reachable, zero errors — Bybit spot+linear, OKX
  spot+swap, Kraken, KuCoin, **Binance spot AND fapi both work** (WARP egress via
  Singapore). data.binance.vision therefore presumed fine for bulk history.
- Samplers RUNNING since 18:44 UTC (background tasks): xex_spreads.jsonl (60s),
  funding_snaps.jsonl (300s, top-150 Bybit linear + OKX majors + Binance majors).

## Push log
- 18:45 UTC: initial push (setup commit).

## Iteration log
- **Iter 1 — 18:40–18:50 UTC (02:40 MYT):** Setup. Protocol/ledger/leaderboard
  created. Venue probe all-green. Both samplers launched. 3 sonnet sweep agents
  spawned (academic / practitioner / live-nowcast) → will land in sweeps/.
  NEXT: iter 2 = verify **funding-harvest** (pull Bybit funding history + Binance
  fundingRate dumps 2024→now, backtest delta-neutral rotation net of 4 taker legs).
- **Iter 2 — 18:52–19:05 UTC (02:52 MYT):** funding-harvest VERIFIED → MARGINAL:
  +10.6%/yr net OOS (562d, frozen IS-2024 params K=1/lb14/th10), $0.29/day @$1k,
  $1.45/day @$5k, worst 30d −2.44%. Fast variants NEGATIVE (rotation costs).
  **OWNER SCOPE CHANGE mid-iter (02:50 MYT): futures LONG/SHORT only** — protocol
  amended, queue rebuilt (tsmom/funding-fade/xsmom = new P1s; yield & arb rows
  descoped; funding-harvest kept as the baseline to beat). 4th sweep agent spawned
  (directional-futures-focused). NEXT: iter 3 = verify **tsmom-daily** (candles
  2019→now, IS ≤2023 grid, OOS 2024→now, incl. Donchian + vol-sizing variants).
- **Iter 3 — 19:05–19:20 UTC (03:05 MYT):** tsmom-daily VERIFIED → MARGINAL
  (+12.1%/yr net OOS, Sharpe 0.49, maxDD −38.5%; IS Sharpe 2.1 was bull-era
  mirage; LS variants negative OOS; SSRN ensemble claim does not reproduce on
  majors). Now CURRENT BEST in-scope by default — weak. Bybit rate-blocked mid-
  iter; pivoted candles to OKX (cached 2019→now majors). Academic+practitioner
  sweeps triaged earlier this iter (rsi-meanrev added as #11). NEXT: iter 4 =
  verify **xsmom-alts** via OKX swap universe (top ~40 by volume, daily candles,
  weekly long-top/short-bottom quintile rotation, IS 2022-2023 / OOS 2024→now)
  — this is also the honest test of the SSRN top-20 rotation claim. After that:
  funding-fade (needs Bybit block to age out; funding history already cached).
- **Iter 4 — 19:25–19:45 UTC (03:25 MYT):** xsmom-alts VERIFIED → **VIABLE, NEW
  LEADER**: selection-free MOM ensemble (lb 7/14/28/60, weekly quintile L/S)
  +26.1%/yr net OOS Sharpe 1.07 maxDD −19.6% on the survivorship-CLEAN 11-symbol
  universe (full universe +87%/yr = inflated upper bound; frozen single-param
  picks only ~+12% — the ensemble is the defensible spec). Reversal negative
  everywhere = momentum sign robust. Directional sweep triaged mid-iter:
  funding-fade DOWNGRADED to P2 (near-zero single-asset predictive power),
  event-drift UPGRADED to P2 (pre-FOMC-only), intraday-tsmom added P3 (#12),
  CME-gap-fill dead (24/7 CME since 2026-05-29). NEXT: iter 5 = **rsi-meanrev**
  (OKX 1H/4H candles majors, RSI-extreme entries, IS ≤2024 / OOS 2025→now) —
  highest remaining prior (survived a real-fee forward test externally).
