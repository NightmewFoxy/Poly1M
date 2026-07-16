# LEDGER — overnight crypto strategy hunt (2026-07-17)

Single source of truth. Re-read FIRST every iteration. Conversation context is NOT
trusted memory.

## Strategy queue

Priorities: P1 = high prior AND verifiable tonight with free data. P2 = worth it.
P3 = long shot / probably UNVERIFIABLE tonight. Statuses: queued / verifying /
VIABLE / MARGINAL / DEAD / UNVERIFIABLE-DATA.

| # | slug | strategy | prior | status | notes |
|---|---|---|---|---|---|
| 1 | funding-harvest | Delta-neutral perp funding harvesting (short perp + long spot when funding high, rotate) | P1 | queued | Data: Bybit funding history API, data.binance.vision fundingRate dumps, OKX funding history. Backtest 2024→now, costs = 4 taker legs + spread. Live breadth from sampler. |
| 2 | tsmom-daily | Time-series momentum / trend on BTC+ETH+SOL (daily, long-flat or long-short) | P1 | queued | Data: daily candles 2019→now (data.binance.vision / OKX). Walk-forward, report OOS only. Fees negligible at daily cadence but include. |
| 3 | poly-deribit-prob | Polymarket crypto price-target markets vs Deribit options-implied probability (buy cheap side / structural mispricing) | P1 | queued | NOVEL cross-venue. Need: matching expiries, Deribit mark IV → digital price via d2, Polymarket book + taker fee per market (CLOB get_market meta). Build sampler at verification time. Polymarket orders = home IP only (fine). |
| 4 | carry-basis | Cash-and-carry: long spot vs short quarterly future (OKX/Deribit/Binance quarterlies) | P2 | queued | Data: current + historical term structure. Annualized basis net of fees; compare vs funding-harvest. |
| 5 | seasonality | Overnight/weekend/hour-of-day seasonality on BTC/ETH | P2 | queued | Data: hourly candles 2021→now. Honest multiple-hypothesis discipline (many tests ⇒ strict OOS). |
| 6 | pairs-statarb | Pairs/stat-arb mean reversion (ETHBTC ratio; cointegrated alt pairs) | P2 | queued | Data: daily+4h candles. Cointegration in-sample 2022-2024, trade OOS 2025-2026 with fees. |
| 7 | xex-spot-arb | Cross-exchange spot arbitrage (Bybit/OKX/Kraken/KuCoin) | P2 | queued | Verdict from tonight's live sampler: distribution of cross-venue spreads vs 2×taker+withdrawal. Expect DEAD but cheap to verify. |
| 8 | stablecoin-depeg | Stablecoin depeg mean-reversion (buy the depeg, sell the repeg) | P3 | queued | Episodic; backtest known events (USDC 2023-03, USDR, FDUSD 2024-04 etc.) + frequency estimate. Likely MARGINAL due to rarity + tail risk. |
| 9 | grid-mm | Grid trading / maker-rebate passive MM on ranging pairs | P3 | queued | It's short-vol in disguise. Backtest a grid on 2024-2026 hourly data incl. trend regimes; be honest about inventory blowups. |
| 10 | perpdex-incentives | Perp-DEX incentive harvesting (Hyperliquid points/rebates, new-venue airdrops) | P3 | queued | Probably UNVERIFIABLE-DATA tonight; desk-check economics + risks, mark accordingly. |

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
