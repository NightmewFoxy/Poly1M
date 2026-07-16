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
| 2 | funding-fade | Funding-rate as DIRECTIONAL signal: fade crowded positioning (short extreme+funding pumps / long extreme−funding dumps), unhedged | P2 | **DEAD (both dir)** | DOWNGRADED by directional sweep: one study finds near-zero single-asset predictive power, and the fade was short-biased through 2024's rally. Test the CROSS-SECTIONAL version (rank by funding, fade extremes vs peers) with tempered expectations. Data cached (funding_hist_bybit.json) + candles. |
| 3 | xsmom-alts | Cross-sectional momentum: long top-quintile / short bottom-quintile alt perps, weekly rotate | P1 | **VIABLE** | VERIFIED iter 4 → NEW LEADER: ensemble +26.1%/yr net OOS clean-universe, Sharpe 1.07, maxDD −19.6%. verdicts/xsmom-alts.md |
| 4 | liq-wick-reversion | Buy violent liquidation dumps / sell squeezes intraday on majors (mean reversion after forced flow) | P2 | **MARGINAL (weak)** | Iter 12: dump-buy IS t=4 → OOS +15-29%/yr but t<2; pump-short anti-alpha. 5m data cached. verdicts/liq-wick-reversion.md |
| 5 | seasonality | Hour-of-day / day-of-week / session effects on BTC/ETH perps (long/short by clock) | P2 | **DEAD (net)** | Hourly candles 2021→now. Strict multiple-hypothesis discipline: discover IS ≤2024, confirm OOS 2025→now. Practitioner sweep: "Monday Asia open" momentum claim 28%/yr, 60% win/103 trades, single-sourced vendor-adjacent — test that specific hypothesis too. |
| 6 | pairs-statarb | Long/short pairs on perps (ETHBTC ratio MR; cointegrated alt pairs) | P2 | **DEAD** | In scope (it IS long-short futures). Cointegration IS 2022-2024, OOS 2025→now, fees both legs. Practitioner sweep: low-tier paper claims Sharpe 1.58-2.45 on BTC-ETH pair — replicate, expect decay. |
| 7 | btc-leads-alts | Lead-lag: BTC big move → alts follow (long/short alts on BTC impulse) | P2 | **DEAD** | Iter 10: every follow cell negative IS (t to −6); no retail-latency lag on majors. verdicts/leadlag-intraday.md |
| 8 | oi-extreme | Open-interest spikes / long-short-ratio extremes as reversal or continuation signal | P3 | **UNVERIFIABLE-DATA** | Iter 13: Bybit blocked, OKX Rubik = 180d only, Binance 30d. Settle later via Bybit OI history. Prior LOW (correlates w/ funding+momentum, both tested). |
| 9 | event-drift | Pre-FOMC drift on BTC: long ~24h before FOMC statement, flat at announcement | P2 | **DEAD** | UPGRADED by directional sweep: BTC +0.96% avg day-before-FOMC claim, echoes Lucca-Moench equity drift. FOMC ONLY (CPI debunked — no consistent effect). ~20 events/yr: small-sample honesty required. Data: hourly candles + FOMC dates 2022-2026. |
| 10 | stablecoin-depeg | Depeg mean-reversion (buy panic, sell repeg) — event TRADING | P3 | **NOT-A-STRATEGY** | Iter 13 desk note: ~1 event/2-3yr, n too small, fatal tail if wrong peg. Kept as opportunistic playbook rule in verdicts/oi-and-depeg.md |
| 12 | intraday-tsmom | Intraday TSMOM: first-30min return predicts last-30min return on HIGH-VOL days only (Shen/Urquhart/Wang, Financial Review) | P3 | **DEAD** | Iter 10 (hourly adaptation): all cells negative both periods. verdicts/leadlag-intraday.md |
| 11 | rsi-meanrev | Short-timeframe RSI/Bollinger mean reversion on liquid perps (5m-4h bars) | P2 | **DEAD** | Academic sweep: StratProof forward test on REAL Binance fees — 6/22 strategies survived, ALL were RSI mean-reversion; every trend variant lost. 10-day sample too short → backtest 2023→now, IS/OOS, taker fees. |

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
- **Iter 5 — 19:47–20:05 UTC (03:47 MYT):** rsi-meanrev VERIFIED → **DEAD** (all
  24 configs negative OOS; fee bleed × trade count; the external "survived real
  fees" claim was 10-day noise). OKX 1H candles for majors now CACHED
  (rsimr_candles_1h.json, 42k bars/sym) — makes seasonality nearly free. NEXT:
  iter 6 = **seasonality** on cached 1H data; pre-registered windows first
  (QuantPedia BTC 21:00→23:00 UTC long; "Monday Asia open"; Sunday-23:00-UTC
  US-reentry), then honest hour/day discovery IS ≤2024 → confirm OOS 2025→now,
  fees included. Also check samplers alive (last verified 18:44 UTC).
- **Iter 6 — 20:08–20:20 UTC (04:08 MYT):** seasonality VERIFIED → **DEAD net of
  fees**. Real finding preserved: 20:00–23:00 UTC long drift +5–7bp/day gross
  (t 2–3, holds OOS) — fees eat it; keep as execution-timing tailwind (do xsmom
  rebalances ~20:00 UTC). Day-of-week = noise. Samplers alive (489/675 rows @
  20:05). NEXT: iter 7 = **funding-fade** cross-sectional: Bybit funding history
  (cached, 30 syms) ∩ OKX candles (cached, 36 syms) — rank by trailing 3d
  funding, SHORT top quintile / LONG bottom quintile, daily+weekly variants,
  IS 2024 / OOS 2025→now (funding data starts 2024-01). If overlap too thin,
  re-probe Bybit for candles (block may have aged out).
- **Iter 7 — 20:22–20:40 UTC (04:22 MYT):** funding-fade VERIFIED → **DEAD both
  directions**. FADE anti-alpha everywhere (−36..−55%/yr OOS). FOLLOW looked
  spectacular on the contaminated universe (+51%/yr OOS incl. funding drag) but
  the old-guard control killed it (−35%/yr) — survivorship artifact, textbook.
  Funding P&L term added to the engine (FOLLOW pays funding both legs; cut
  headline 77.6→51.1 before the control finished it). xsmom remains the only
  clean-control survivor. NEXT: iter 8 = **event-drift (pre-FOMC)**: cached BTC
  1H + FOMC statement dates 2022→2026 (verify dates via WebSearch first),
  long 24h pre-statement → flat at 18:00/19:00 UTC announcement; also post-drift
  check. Cheap and pre-registered. Then: pairs-statarb (cached dailies),
  btc-leads-alts (cached 1H), intraday-tsmom hourly adaptation. liq-wick needs
  1m data (probe data.binance.vision); oi-extreme needs Bybit (blocked).
- **Iter 10 — 19:52–20:02 UTC (03:52 MYT):** btc-leads-alts + intraday-tsmom
  BOTH VERIFIED DEAD (no retail-latency lag on majors, t to −6; intraday
  continuation negative everywhere). NEXT: iter 11 = **xsmom deepening** to
  sharpen the morning recommendation: (a) mid-guard universe (symbols with
  full data before OOS start: +BNB/SUI/PEPE/WLD ≈15 syms, quintile 3/side) as
  a mid-bound between clean-11 (+26%) and full-36 (+87%); (b) long-only vs L/S
  split (how much comes from shorts?); (c) rebalance-day-of-week sensitivity;
  (d) turnover + practical playbook notes (venue, sizing at $1-5k, 20:00 UTC
  execution window per seasonality finding). Then iter 12 = liq-wick (probe
  data.binance.vision 1m zips); iter 13 = oi-extreme re-probe Bybit +
  stablecoin-depeg desk note.
- **Iter 11 — 20:05–20:20 UTC (04:05 MYT):** xsmom DEEP-DIVE done (verdict file
  updated): mid-15 universe +38.0%/yr Sh 1.31 maxDD −15.9%; all 7 phases
  positive (mean +23.7%); per-year +71/+20/+20%; long-only = −67% maxDD trap,
  short-only loses (shorts are the hedge); turnover 1.04x/wk (fee drag 3.8%/yr).
  Forward expectation quoted: +20–30%/yr at 1x. LEADERBOARD refreshed. NEXT:
  iter 12 = **liq-wick-reversion**: probe data.binance.vision for 1m kline zips
  (BTC/ETH/SOL 2024→now); if blocked, OKX 1m too slow → UNVERIFIABLE-DATA.
  Then iter 13 = oi-extreme (re-probe Bybit) + stablecoin-depeg desk note.
- **Iter 12 — 20:22–20:40 UTC (04:22 MYT):** liq-wick-reversion VERIFIED →
  **MARGINAL (weak)**: dump-buy real in 2024 (t=4) but decayed ~85% OOS
  (+15-29%/yr point estimates, t<2 everywhere); pump-short anti-alpha;
  volume filter useless. data.binance.vision reachable — 5m futures klines
  2024→2026-06 cached for majors. NEXT: iter 13 = cleanup pass: re-probe Bybit
  (if alive → quick **oi-extreme** check via OI history endpoint), write
  **stablecoin-depeg** desk-note verdict (episodic, small-n, likely
  UNVERIFIABLE tonight), then queue is empty → sweep round 2 (novel directional
  ideas only) or throttle to heartbeats if nothing new.
- **Iter 13 — 20:56–21:05 UTC (04:56 MYT):** cleanup pass done: oi-extreme →
  UNVERIFIABLE-DATA (Bybit still blocked; OKX Rubik 180d; Binance 30d);
  stablecoin-depeg → NOT-A-STRATEGY (desk note + playbook rule). Queue now
  fully resolved. Final gap-sweep sonnet agent spawned (novel directional
  mechanisms only, told what's already dead). NEXT: iter 14 = triage gap-sweep
  when it lands; if nothing new testable → write **MORNING.md** consolidated
  brief (the answer to "which strategy do we proceed with"), final push, then
  throttle heartbeats (~1800s) with sampler checks until owner wakes.
- **Iter 14 — 21:07–21:15 UTC (05:07 MYT):** MORNING.md brief written + pushed
  (the consolidated answer). Vol-targeting addendum to tsmom verdict: halves DD
  but Sharpe stays 0.5-0.8 — external "1.42" claim does not reproduce; xsmom
  unchallenged. Gap-sweep agent still running. NEXT: triage gap-sweep on its
  notification (test anything credible); otherwise heartbeats, keep MORNING.md
  + LEADERBOARD current.
- **Iter 15 — 21:20–21:35 UTC (05:20 MYT):** gap-sweep triaged: candidate 1
  (Coinbase premium / ETF flows) TESTED → **DEAD** (2024 launch-regime artifact,
  IS Sharpe 2.4 → OOS 0.47 sign-flipping); candidate 2 (1h stablecoin flows)
  UNVERIFIABLE-DATA + low prior; its rule-outs matched our verdicts. Search
  space is now genuinely exhausted for the night. MORNING.md updated. NEXT:
  compute TODAY'S live xsmom basket (what we'd hold right now) as a concrete
  morning deliverable, then throttle to 1800s heartbeats (samplers check only).
- **Iter 16 — 21:40 UTC (05:40 MYT):** today's live xsmom basket computed and
  added to MORNING.md (LONG UNI/AAVE/ETH, SHORT BCH/XRP/DOGE). All work items
  complete: 14 families verified, MORNING.md final. Loop enters THROTTLE mode
  (1800s heartbeats: sampler check, refresh basket if stale >6h, otherwise
  idle) until the owner interrupts.
- **Iter 8 — 19:33–19:45 UTC (03:33 MYT):** event-drift (pre-FOMC) VERIFIED →
  **DEAD** (t≈1.1 noise over 36 events; sign reversed 2024→now; ≤+2.5%/yr best
  case). 2026 FOMC dates verified vs Fed calendar. NEXT: iter 9 =
  **pairs-statarb** from cached OKX dailies: ETHBTC ratio z-score MR + top
  cointegrated old-guard pairs; IS 2022-2023 fit (lookback, entry/exit z),
  OOS 2024→now, fees both legs. Expect decay per academic sweep; verify.
- **Iter 9 — 19:37–19:50 UTC (03:37 MYT):** pairs-statarb VERIFIED → **DEAD**
  (IS Sharpe 2.35 → OOS −17.6%/yr, all 5 frozen pairs negative; ETHBTC ≈0).
  Emerging meta-finding: 2024-2026 = MOMENTUM regime; every mean-reversion
  family fails, momentum families survive. NEXT: iter 10 = **btc-leads-alts**
  (cached 1H: BTC 4h/24h impulse → ETH/SOL next-hours follow; IS 2022-2024 /
  OOS 2025→now) + **intraday-tsmom hourly adaptation** (first-hour → rest-of-day,
  vol-conditional) in the same iteration if fast. Then: liq-wick (probe
  data.binance.vision for 1m zips), xsmom deepening (rebalance timing 20:00 UTC,
  long-only variant, mid-guard universe), stablecoin-depeg desk check,
  oi-extreme (re-probe Bybit).
