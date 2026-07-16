# OVERNIGHT CRYPTO STRATEGY HUNT — PROTOCOL (frozen 2026-07-17)

## Mission
Owner is asleep. This loop hunts **crypto trading strategies** all night (Polymarket
is considered already-searched; only genuinely NEW Polymarket mechanisms count, and
cross-venue crypto×Polymarket ideas ARE in scope). For every candidate strategy the
loop must **verify profitability itself** with real data — never accept a source's
claimed returns. Maintain a morning-ready ranked answer at all times.

**Morning protocol:** when the owner interrupts (any message), STOP looping and answer
instantly from LEADERBOARD.md: the single best strategy, its verified numbers
($/day at $1k and $5k capital), max drawdown / blow-up modes, ops burden, and the
concrete next step to deploy it. If everything is DEAD, say so plainly and rank the
least-dead with what would change the verdict. This project's history rewards honesty
over optimism (esports bot -$134 lifetime, arb fee-walled, LP vol-trap, copy-trading
dead, PumpFun dead OOS).

## Hard rails (violating any = stop that action, never the loop)
1. **READ-ONLY research.** No orders, no live trading, nothing that spends money.
   Never touch `.env` / private keys, the live bots, Railway, production code,
   `requirements.txt`, or the repo's `./data` dir. ALL writes stay under
   `research/overnight-2026-07-17/`.
2. **No metered LLM APIs — owner's hard rule.** All thinking = the main agent +
   Agent-tool subagents on the subscription (use `model: sonnet` for search sweeps
   and mechanical data-fetch tasks; keep backtest design/judgment in the main loop).
   Any script written must be purely mechanical (HTTP to public non-LLM endpoints,
   file IO, math). Never import `anthropic`, never read LLM API keys.
3. **Telegram silent overnight.** ONE message to the important bot only if the loop
   is fatally broken/blocked (so the owner sees it on waking). No progress chatter.
4. Never ask the user anything until morning. Never wait on input.
5. Do not re-run/restart any of the project's bots (`lp_quoter`, `arb_executor`,
   `main.py`, `measure_arb`). They are shut down; leave them shut down.

## State — files are the ONLY trusted memory (conversation gets summarized)
Base dir: `C:\Users\foxyc\Desktop\Poly1M\research\overnight-2026-07-17\`

| File | Purpose |
|---|---|
| `PROTOCOL.md` | This file. Frozen — do not edit mid-night. |
| `LEDGER.md` | Single source of truth: strategy queue + statuses, data-source notes (what APIs work from here), iteration log (one line per iteration). Re-read FIRST every iteration. |
| `LEADERBOARD.md` | Ranked verified strategies. Top line = `CURRENT BEST: <name> — <one-para why + $/day at $1k / $5k>`. Update after EVERY verification. |
| `verdicts/<slug>.md` | One per verified strategy: mechanism, sources, backtest design, data used, cost assumptions, numbers, failure modes, verdict. |
| `sweeps/<name>.md` | Raw search-sweep findings (subagents write here). |
| `data/` | Downloaded market data, sampler JSONL, backtest scripts. `.gitignore` blocks raw data; commit only `.py`/`.md`. |

Statuses: `queued` → `verifying` → `VIABLE` / `MARGINAL` / `DEAD` / `UNVERIFIABLE-DATA`
(the last one must state exactly what data would settle it).

## Iteration algorithm (each loop firing = exactly one pass)
0. Read `LEDGER.md` + `LEADERBOARD.md`. Check the two samplers are alive
   (background task list, or file mtime under `data/`); relaunch if dead and note it.
   Triage any newly finished sweep outputs into the queue (dedupe!).
1. **If ≥1 `queued` candidate:** take the highest-priority one → `verifying`.
   Get real data → write a mechanical backtest under `data/` → run it → write
   `verdicts/<slug>.md` → set final status → update LEADERBOARD (recompute CURRENT
   BEST). A big job may span 2 iterations max; leave a NEXT-STEP note in LEDGER.
2. **Else (queue < 3):** search sweep. Use WebSearch/WebFetch directly and/or ≤3
   background `sonnet` subagents on distinct source families. Sources: arXiv q-fin,
   SSRN, QuantPedia, QuantConnect/r-algotrading, Hummingbot community, exchange
   research blogs (Binance/Bybit/Deribit/Kaiko/Glassnode), funding & basis dashboards,
   reputable CT quant writeups. Enqueue: name, mechanism, source URL, one-line
   hypothesis, data plan, prior (P1/P2/P3).
3. Append one iteration-log line to LEDGER (UTC time + MYT, what was done, next step).
4. `git add research/overnight-2026-07-17 && git commit` every iteration.
   `git push` only if ≥2h since last push (each push redeploys parked Railway —
   harmless but don't spam).
5. End with ScheduleWakeup (60–120s; after 08:00 MYT / 00:00 UTC, if queue is empty
   and sweeps are dry, throttle to 1800s heartbeats), passing the exact `/loop`
   prompt. NEVER end an iteration without it — unless the owner has interrupted.
   If woken by a task-notification instead of the timer: triage it, update LEDGER,
   and do NOT double-schedule (a wakeup is already pending).

## Verification bar (be brutal — two phantom-edge postmortems live in this repo)
- **Reproduce it yourself** on real historical data and/or live overnight sampler
  data. Free sources: `data.binance.vision` (bulk candles/funding, no key),
  Bybit/OKX/Kraken/KuCoin public REST, Deribit public API, CoinGecko, Polymarket
  Gamma/CLOB reads. Cache under `data/`.
- **Net of ALL costs:** taker 0.10% / maker 0.02% unless a better verified tier;
  half-spread + ≥1 tick pessimistic slippage per fill; funding/borrow at realized
  historical rates; cross-venue transfer costs AND time-risk; Polymarket taker fees
  (most crypto markets are fee-walled now — verify per market via CLOB
  `taker_base_fee`, never assume 0).
- **No lookahead, no survivorship.** Any tunable parameters ⇒ in-sample/out-of-sample
  split or walk-forward; report OOS ONLY (the PumpFun lesson).
- **Capital realism:** owner deploys ~$500–$5,000, retail latency (home PC in
  Malaysia, Cloudflare WARP egress; optionally a cheap VPS). No colocation fantasies.
  Note venue access/KYC from Malaysia (Binance restricted in MY — web blocked, data
  endpoints usually fine; Bybit/OKX/Kraken/KuCoin fine; Polymarket orders home-IP
  only; Deribit fine). A strategy that can't be executed at $1–5k retail = DEAD
  regardless of paper Sharpe.
- Report per strategy: expected **$/day at $1k and $5k**, max drawdown, blow-up
  modes, ops burden (hands-on hours/week), and capacity ceiling.

## Search space (crypto, retail-executable)
Funding-rate harvesting (delta-neutral spot+perp), cash-and-carry quarterly basis,
cross-exchange spot arb, triangular arb, stat-arb/pairs on cointegrated coins,
time-series momentum & trend (BTC/ETH/alts, daily/4h), overnight/weekend/intraday
seasonality, mean reversion, volatility strategies on Deribit (covered calls, short
straddles — price the tail honestly), grid/maker-rebate market making, listing &
delisting events, stablecoin depeg reversion, perp-DEX incentive harvesting
(Hyperliquid & clones), on-chain/flow signals, altcoin rotation, lending/borrow rate
spreads, **Polymarket×Deribit implied-probability arb on crypto price-target markets**
(novel, in scope), anything credible the sweeps surface.

## DO NOT re-investigate (verdicts already on file)
Polymarket binary-merge arb (fee-walled), Polymarket LP rewards (volatility trap,
~$36/day plateau at $13.5k), Polymarket copy-trading top-100 (dead, -5.1%/turnover),
esports prediction betting (dead), PumpFun sniping/momentum (all 4 variants dead OOS,
2026-07-06). Only revisit if a source shows a SPECIFIC new mechanism that dodges the
documented kill factor.

## Samplers (mechanical, read-only, background)
- `data/sampler_xex.py` — cross-exchange top-of-book for BTC/ETH/SOL (Bybit spot+perp,
  OKX spot+swap, Kraken, KuCoin, Binance-if-reachable) every 60s → `data/xex_spreads.jsonl`.
- `data/sampler_funding.py` — funding-rate snapshots (Bybit all-linear, OKX majors,
  Binance fapi if reachable) every 300s → `data/funding_snaps.jsonl`.
- Build a Polymarket-vs-Deribit sampler only when that candidate reaches verification.
- Errors are written as JSONL rows too — an unreachable venue is itself a finding.

## SCOPE AMENDMENT — owner directive 2026-07-17 02:50 MYT (overrides Search space)
Goal restated by owner mid-run: **find the highest-profitability TRADING strategy —
crypto futures, longing and shorting.** EXCLUDE anything staking/investing/passive-
yield-like and "everything unrelated to trading". Concretely:
- IN SCOPE (priority): directional long/short futures/perp strategies — trend &
  time-series momentum, cross-sectional momentum (long winners/short losers),
  mean reversion, breakouts, funding-rate-as-SIGNAL (fade crowded positioning —
  directional, not harvest), liquidation-cascade/wick reversion, open-interest &
  long-short-ratio signals, lead-lag (BTC→alts), session/seasonality effects,
  event trading (FOMC/CPI drift), pairs/stat-arb long-short on perps, vol-scaled
  variants of all of the above.
- OUT OF SCOPE (descoped): funding HARVEST (delta-neutral carry — verified, kept
  as baseline), cash-and-carry basis, cross-exchange/triangular arb, grid/passive
  MM, perp-DEX incentive farming, Polymarket×Deribit relative value, lending/
  staking anything. Their queue rows stay for the record, marked `descoped`.
- The verified funding-harvest baseline (~10.6%/yr net OOS) is the bar: an
  in-scope strategy that can't beat it net OOS is not worth the owner's time.
- Leverage: perps allow it; report results at 1x AND note how leverage scales
  return/drawdown/liquidation risk honestly.

## Failure handling
API/geo/rate failures: log to LEDGER data-source notes, fall back to an alternate
venue or `data.binance.vision` dumps, keep going. If ALL model work starts failing
(usage-limit exhaustion suspected): write a LEDGER note; the pending wakeup retries
automatically when quota resets. The loop only ends when the owner interrupts.
