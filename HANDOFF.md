# HANDOFF — state of in-flight work as of 2026-06-13

Written at the end of the last Claude Code session on this project. Read
`CLAUDE.md` first for architecture, then this for what's actually running
and what to do next. `HISTORY_FINDINGS.md` explains *why* the project is
where it is.

## TL;DR

- The strategy pivoted from "predict esports outcomes" (proven net-negative,
  -$134.47 lifetime across bots) to **pure arbitrage**.
- Two things were set in motion on 2026-06-12:
  1. A **24h arb-flow measurement (v2)** on Railway that ends by Telegramming
     a PROVEN / MARGINAL / NO verdict.
  2. A **live arb executor on the home PC** with tiny $3 rails.
- **At handoff time the executor is NOT running** (no python process on this
  machine) and has **never recorded a single event** — `data/
  arb_executor_log.jsonl` and `data/arb_positions.json` do not exist, which
  per its own code means zero captures, zero skips, zero errors ever logged
  locally. It announced itself live on Telegram on 2026-06-12 (bankroll
  $3.14), so it ran at least briefly; the window was likely closed or the PC
  restarted. Nothing is lost — there are no open arb positions to babysit.
- **First action for whoever picks this up: check the owner's Telegram** for
  the v2 measurement report/verdict (due ~24h after the last Railway deploy
  on 2026-06-12, i.e. around now).

## Track 1 — Arb-flow measurement v2 (Railway) — RUNNING or just finished

**What it is:** `measure_arb.py --hours 24 --notify` (see `railway.toml`
startCommand). Scans every 60s, re-verifies every hit on a simultaneous book
snapshot (`arb_scanner.confirm_hits`), appends to `/data/arb_log_v2.jsonl`,
and after 24h Telegrams a report with capturable $/day at $100/$1k/$10k
capital tiers plus a verdict:

- ≥ $2.00/day persistent on $100 → **PROVEN** (build/run the executor seriously)
- ≥ $0.50/day → **MARGINAL** (beer money)
- below → **NO** (skip; the flow is too thin)

"Persistent" = the opportunity survived ≥2 *consecutive* 60s scans; the
verdict deliberately ignores one-scan blips a 60s home bot can't catch.

**Why v2 exists:** v1 (local `data/arb_log.jsonl`, 2026-06-10) measured
$30.88/day, which was **phantom** — chunked book fetches snapshotted YES and
NO seconds apart on fast live-sports markets, and paused markets
(`acceptingOrders=false`) displayed unhittable books. v2's first scan showed
the real ratio: 4 raw → 2 confirmed, both small neg-risk converts. Never
quote v1 numbers.

**State/caveats:**
- Every git push redeploys Railway and **restarts the 24h window** (the
  jsonl log persists on the volume, so `--report` over the accumulated log
  still works, but the clean 24h run restarts). The handoff commit itself
  will do this — so after this push, expect the next verdict ~24h later.
- After the 24h run exits cleanly, Railway does NOT restart it
  (`restartPolicyType = "ON_FAILURE"`). The service then sits idle until the
  next push or a manual redeploy. Decide after the verdict whether to keep
  the Railway service at all (it costs money to keep deployed).
- Known measurement honesty gaps (stated in the report itself): assumes 100%
  fill at displayed depth and **zero trading fees**.

## Track 2 — Live arb executor (home PC) — BUILT, TESTED LIVE, NOT RUNNING

**What it is:** `arb_executor.py` — binary-merge only. Every 45s: scan →
confirm → for each confirmed hit re-snapshot both legs in one request →
FAK-buy the thinner leg first with **zero slippage allowance** → buy the
second leg, chasing up to breakeven (any price ≤ 1 − paid1 still can't lose)
→ if leg 2 misses entirely, unwind leg 1 at the bid → if even that fails,
hold the "naked" leg, keep retrying to sell it, and **take no new positions
until it clears**. Captured pairs are held to resolution ($1/set paid then;
claim in the Polymarket UI) instead of calling on-chain `mergePositions`.

**Rails (env-overridable):** `ARB_MAX_EXPOSURE=3`, `ARB_MAX_PER_OPP=3`,
`ARB_MIN_EDGE_CENTS=1.0`. Kill switch: create `data/STOP_ARB`.
Launch: double-click `start_arb.cmd` (must be the home PC — cloud IPs are
geoblocked for orders; see CLAUDE.md gotcha #1).

**Honest status:**
- It went live 2026-06-12 with a **$3.14 bankroll**, which is below the
  ~$2.10+ a typical hit needs (exchange minimum ≈ $1.05 per leg), so it was
  expected to skip most opportunities and Telegram "top up to capture".
- Zero captures to date. No ledger file exists locally → it never even hit a
  loggable event (faded/too_small/captured) before it stopped running, OR it
  simply saw no confirmed hits in its short run. Both are consistent with
  the thin v2 flow.
- **Diagnosis of "why no results": this is not a bug.** The executor's
  plumbing was smoke-tested (`--once`), the order path is the same
  `place_market_buy` proven live on 2026-05-14, and the scan path is the
  same code v2 measurement uses. The bottlenecks are (a) bankroll below
  exchange minimum and (b) genuinely thin confirmed flow. Whether to fix (a)
  is the owner's call pending the Track 1 verdict.

**Known gaps / fragile bits (in priority order):**
1. **Fee blindness.** The executor never reads a market's fee rate. Most
   Polymarket markets are 0-fee today, but the measurement report explicitly
   warns the executor must check `feeRateBps`/market fees before trusting a
   1c edge. A 1c edge on a fee-charging market could be a guaranteed *loss*.
   Fix: read the fee from CLOB market meta in `try_capture()` and require
   `edge > fees + EXEC_MIN_EDGE_CENTS`.
2. **Hold-to-resolution ties up capital** for hours-to-weeks per set and
   adds a manual UI-claim step. Fine at $3; unacceptable at $1k. The scale
   fix is calling CTF `mergePositions` on-chain after both legs fill
   (Polygon gas ~cents) — deliberately not built for the $3 test
   (DECISIONS.md).
3. **`arb_positions.json` is written non-atomically** (plain
   `write_text`) — a crash mid-write could corrupt state. Low probability,
   easy fix (tmp+rename like positions.py does).
4. **`_skip_notified` resets on restart** → after each relaunch the first
   sighting of each too-small market re-pings Telegram. Cosmetic.
5. **45s scan cadence is slow** vs. professional arb bots; binary edges
   observed on 2026-06-10 lasted ~20 minutes, but the competitive ones
   vanish in seconds. If the verdict is PROVEN and capital scales, the
   upgrade path is the CLOB websocket feed (the `websockets` dep is already
   in requirements but unused — that was the verbal intent behind it).

## Track 3 — Legacy esports bot — RETIRED, do not restart

`main.py` still works but is proven -EV (see HISTORY_FINDINGS.md: the bot
wins *less* often than entry price implies at every price band; the last 12
positions went 0/12). Rotation was built, shipped, and then **disabled in
code** because it structurally selects for the largest model errors. The
MIN_GAP_PP=3 filter shipped and did not help (0/7 after). There are no open
positions: the on-chain reconciliation at the last boots showed the book
flat, and no positions.json exists locally. If anyone restarts it, it will
trade real money within minutes — `TRADING_ENABLED=false` first.

## Not built / half-finished inventory

| Item | Status | Notes |
|---|---|---|
| Neg-risk convert execution | NOT BUILT (scanner only) | Needs N simultaneous NO legs + on-chain `convertPositions` via the proxy wallet. The v2-confirmed flow so far is mostly these, so this is likely where the real money is — but it's the hard 20%. |
| On-chain `mergePositions` | NOT BUILT | Executor holds to resolution instead. Build when capital > ~$100. |
| Fee-rate check in executor | NOT BUILT | Gap #1 above. Do this before any bankroll top-up. |
| Auto-redeem of resolved arb sets | NOT BUILT | Owner claims manually in the UI (gasless there). |
| Websocket book feed | NOT STARTED | `websockets` dep pre-added, zero code. |
| `web3` dependency | UNUSED | Was for on-chain merge/convert plans. |

## Exact next steps, in priority order

1. **Read the Telegram verdict** from the Railway v2 run (or run
   `python measure_arb.py --report` against the Railway volume's
   `arb_log_v2.jsonl` — note the local `data/` only has contaminated v1).
2. **If verdict is NO:** stop here. Tear down the Railway service, leave the
   executor off, and don't spend more on this. The honest base case given
   v2's early data (2 confirmed hits/scan, mostly converts the executor
   can't trade) is that binary-merge alone is beer money at best.
3. **If MARGINAL/PROVEN:** add the fee-rate check to `try_capture()`
   (gap #1), then top up the bankroll to ~$20–50 so hits clear the $1.05/leg
   exchange minimum, then relaunch via `start_arb.cmd` and let it run for a
   week. Real fills are the ground truth the measurement can't give.
4. **If real fills confirm the edge:** build neg-risk convert execution
   (multi-leg + `convertPositions`) — that's where v2's confirmed flow
   actually lives — and on-chain `mergePositions` to recycle capital.
5. Housekeeping whenever convenient: atomic writes for
   `arb_positions.json`, remove dead deps, decide the Railway service's fate.

## Operational facts someone will need

- Trading account: POLY_PROXY funder
  `0x832Ddc3fa9d43c03071736Fe566B0Ae0D6B964ac`, sig_type=1. Live private key
  and all API creds are in the local `.env` (gitignored) and in Railway
  service variables. The UI deposit address is different — see CLAUDE.md
  gotcha #2 before touching `POLYMARKET_FUNDER_ADDRESS`.
- Bankroll at executor launch: $3.14 USDC. Lifetime account damage from the
  prediction era: -$134.47 (bots) / +$22.59 (the owner's two manual bets —
  make of that what you will).
- Telegram: the project bot token/chat for trade notifications is in `.env`
  (`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`); the owner also has a separate
  IMPORTANT-only bot configured globally in `~/.claude/settings.json`.
- GitHub: https://github.com/NightmewFoxy/Poly1M (push to main = Railway
  redeploy = measurement window restart).
