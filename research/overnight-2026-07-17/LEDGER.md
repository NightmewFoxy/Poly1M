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
| 1 | tsmom-daily | Time-series momentum / trend on BTC+ETH+SOL perps (daily, long-short) | P1 | queued | NEXT (iter 3). Data: daily candles 2019→now (Bybit/OKX/data.binance.vision). Grid IS ≤2023, OOS 2024→now. Include fees 0.06%+slip per side. Also test vol-scaled sizing + Donchian breakout variant in same harness. |
| 2 | funding-fade | Funding-rate as DIRECTIONAL signal: fade crowded positioning (short extreme+funding pumps / long extreme−funding dumps), unhedged | P1 | queued | Data already cached (funding_hist_bybit.json) + candles. Different from harvest: takes price risk. Literature: crowded-long unwinds. |
| 3 | xsmom-alts | Cross-sectional momentum: long top-quintile / short bottom-quintile alt perps, weekly rotate | P1 | queued | Data: daily candles for ~40 perps. Survivorship-aware (use symbols live at signal time). IS 2022-2023 wait — Bybit history depth varies; use 2023-2024 IS, 2025→now OOS. |
| 4 | liq-wick-reversion | Buy violent liquidation dumps / sell squeezes intraday on majors (mean reversion after forced flow) | P2 | queued | Data: 1m klines from data.binance.vision bulk zips (BTC/ETH/SOL 2024→now). Define wick/velocity trigger IS, OOS test. Fees hurt at this frequency — taker both ways. |
| 5 | seasonality | Hour-of-day / day-of-week / session effects on BTC/ETH perps (long/short by clock) | P2 | queued | Hourly candles 2021→now. Strict multiple-hypothesis discipline: discover IS ≤2024, confirm OOS 2025→now. |
| 6 | pairs-statarb | Long/short pairs on perps (ETHBTC ratio MR; cointegrated alt pairs) | P2 | queued | In scope (it IS long-short futures). Cointegration IS 2022-2024, OOS 2025→now, fees both legs. |
| 7 | btc-leads-alts | Lead-lag: BTC big move → alts follow (long/short alts on BTC impulse) | P2 | queued | Hourly/15m candles BTC + top alts. Test signal lag structure IS, OOS confirm. Retail latency OK if effect persists hours. |
| 8 | oi-extreme | Open-interest spikes / long-short-ratio extremes as reversal or continuation signal | P3 | queued | Bybit has OI history endpoint (verify depth); combine with price. Mark UNVERIFIABLE-DATA if history too shallow. |
| 9 | event-drift | FOMC/CPI event drift on BTC (pre/post announcement long/short) | P3 | queued | Small sample honesty: ~40 events since 2024. Data: 5m candles + event calendar (hardcode dates from web). |
| 10 | stablecoin-depeg | Depeg mean-reversion (buy panic, sell repeg) — event TRADING | P3 | queued | Episodic; verify known events + frequency. Tail-risk honest (USTC went to 0). |
| — | funding-harvest | Delta-neutral funding harvest | — | **MARGINAL (baseline)** | VERIFIED iter 2: +10.6%/yr net OOS, $1.45/day @ $5k. DESCOPED (yield) — the bar to beat. verdicts/funding-harvest.md |
| — | poly-deribit-prob | Polymarket vs Deribit implied prob | — | descoped | Owner scope: futures L/S only. |
| — | carry-basis | Cash-and-carry quarterly basis | — | descoped | Yield-like. |
| — | xex-spot-arb | Cross-exchange spot arb | — | descoped | Not directional trading; sampler keeps recording anyway (free data). |
| — | grid-mm | Grid / passive MM | — | descoped | Passive/short-vol, not directional. |
| — | perpdex-incentives | Perp-DEX incentive farming | — | descoped | Farming, not trading. |

## Data-source notes (what works from this machine)
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
