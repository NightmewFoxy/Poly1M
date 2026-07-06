# Poly1M — Polymarket trading bots

## What this project actually is (read this first)

This repo contains **two generations** of Polymarket trading code:

1. **Legacy: an esports prediction bot** (`main.py` + most of the repo).
   Scanned esports markets, had Claude+web-search estimate true probabilities,
   bet $10 on +EV gaps. **It lost money — lifetime -$69.47 on esports,
   -$134.47 across all bot strategies** — and on-chain analysis proved no
   parameter tuning fixes it (see `HISTORY_FINDINGS.md`, the single most
   important document in this repo). It is retired but the code is kept
   because `polymarket_client.py` (order signing, auth, market data) is
   reused by generation 2.

2. **Current: pure arbitrage** (`arb_scanner.py`, `arb_executor.py`,
   `measure_arb.py`). No prediction, no edge estimates — only mechanically
   guaranteed profit: buying YES+NO of a binary market for < $1.00 total
   ("binary merge arb"), and detecting neg-risk NO-set conversions. This is
   the only strategy whose worst case is ~breakeven instead of -100%.

The owner's goal: prove arb flow is real and capturable, then scale capital
into it. Everything in flight is about that proof (see `HANDOFF.md`).

## Architecture

```
── Generation 2 (ACTIVE) ──────────────────────────────────────────────
arb_scanner.py        Read-only scanner: binary-merge + neg-risk-convert
                      detection, with confirm_hits() re-verification.
                      Works from any IP (market data isn't geoblocked).
arb_executor.py       LIVE trader for binary-merge arbs. Home PC only.
                      Imports scan/confirm from arb_scanner, orders via
                      polymarket_client. Kill switch: data/STOP_ARB file.
measure_arb.py        24h opportunity-flow logger + $/day report + verdict
                      via Telegram. This is what Railway currently runs.
lp_quoter.py          Maker bot for LIQUIDITY REWARDS (the post-fee-wall
                      strategy, validated 2026-07-02 — see memory
                      lp_rewards_path.md): quotes both sides (two BUYS) of
                      calm long-dated reward markets at mid+/-1c. DRY RUN by
                      default; LP_LIVE=1 + home IP + funded account to trade.
                      Kill: data/STOP_LP, or env LP_STOP=1 + restart (remote
                      kill for cloud). Cancel-all on start/stop/crash.
                      Verifies its own reward eligibility via CLOB
                      are_orders_scoring. Review the auto-picked basket and
                      pin with LP_MARKETS before going live (Gamma endDates
                      lie, gotcha #9, so near-resolution sports can slip in).
                      LP_SHARES=N sizes both sides at exactly N shares (how
                      to sit at rewardsMinSize on 200-share pools);
                      LP_VIA_PROXY=<url> = cloud mode via residential proxy.
                      Outage watchdog (2026-07-03, after 8h of silent post
                      failures): 10 consecutive failed posts => Telegram
                      alert + flatten book + exponential-backoff probing
                      (2->15 min) instead of once-a-minute session-rotation
                      spam (suspected of tripping IPRoyal's abuse flag);
                      re-alerts hourly, notifies on recovery.
                      LP_PROXY_ALT_HOSTS=<host,host> = fallback proxy
                      gateways, probes cycle through them (Railway has
                      geo.iproyal.com as alt to the pinned IP). Failed
                      cancels no longer drop the order id from tracking
                      (the 2026-07-03 stale-order bug: a live No bid sat
                      unmanaged on the book for 8h because a failed
                      cancel+post overwrote its id with None).
start_lp_pilot.cmd    Double-click launcher for the $210 Fed-September
                      micro-pilot (LP_LIVE=1, LP_SHARES=200, market pinned).
start_arb.cmd         Double-click launcher for the executor (own window).
start_measure.cmd     Double-click launcher for the measurer.

── Generation 1 (RETIRED, partially reused) ───────────────────────────
main.py               Old esports bot loop (discover→research→trade→notify).
polymarket_client.py  REUSED BY GEN 2: Gamma discovery, CLOB orders
                      (place_market_buy/sell), auth, balances, positions.
research.py           Claude + web_search probability estimates + EV math.
research_cache.py     4h TTL verdict cache (data/research_cache.json).
positions.py          positions.json persistence, resolution checks, PnL.
telegram_notif.py     Old bot's Telegram messages (trades, history, PnL).
config.py             SHARED: env loading. Imported by both generations.
logger_setup.py       Stdout + rotating file logging (data/bot.log).
preflight.py          Env/IP/Telegram/Anthropic/CLOB/Gamma sanity check.

── One-shot helpers ───────────────────────────────────────────────────
derive_api_creds.py            Mint CLOB API creds from the wallet key.
register_deposit_wallet_key.py POLY_1271 (sig_type=3) API-key registration.
                               NOT needed for this account (it's sig_type=1);
                               kept from the debugging saga.
local_test_order.py            Sign+place a $1 test order (esports pick).
local_test_arbitrary.py        Same but for any condition_id; forces direct
                               egress (clears proxy env vars).
```

## How to run

```powershell
# setup (Python version pinned in .python-version)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# .env already exists locally (gitignored, contains the LIVE private key).
# Fresh machine: copy .env.example, fill it, run python derive_api_creds.py.

python preflight.py                  # full sanity check before anything live
python arb_scanner.py                # one read-only scan, prints table
python arb_scanner.py --loop 60      # rescan forever
python arb_executor.py --once        # ONE live cycle (real money), then exit
python arb_executor.py               # live trading loop (or start_arb.cmd)
python measure_arb.py --report       # summarize data/arb_log_v2.jsonl
python main.py                       # old esports bot — DO NOT restart it
                                     # casually; it is net-negative by design
```

There is **no test suite**. The smoke tests are `--once`, `preflight.py`, and
`local_test_order.py` / `local_test_arbitrary.py` (interactive, asks before
posting).

## Deployment (Railway)

> **🛑 PROJECT SHUT DOWN 2026-07-06 (owner request "shut down this entire
> project").** Live state at shutdown: home quoter stopped via `data\STOP_LP`
> (triple cancel-all confirmed — no resting quotes); the **home-PC watchdog
> scheduled task was DELETED** (`schtasks /Delete /TN "Poly1M LP watchdog"`),
> so nothing auto-restarts the quoter anymore; `data\STOP_ARB` pre-armed. No
> open positions (`/value`=$0), trading wallet `0x832Ddc…` holds $0 USDC — the
> 200-No/Fed-Sep pilot is fully closed out. **Railway was LEFT PARKED as-is**
> (owner's call): service still `● Online` but idle under `LP_STOP=1`
> (not quoting, not trading). To fully revive: re-create the watchdog task,
> delete both STOP files, flip `LP_STOP`, and re-read the pilot playbook.
> Everything below describes the pre-shutdown pilot and is kept for that revival.

- Repo auto-deploys from GitHub `main` (https://github.com/NightmewFoxy/Poly1M).
- `railway.toml` `startCommand` is the source of truth for what Railway runs
  (the `Procfile` mirrors it). Currently: `python lp_quoter.py` — but **the
  cloud pilot is PARKED under `LP_STOP=1` since 2026-07-06 ~01:45 UTC: the
  IPRoyal block RETURNED on 2026-07-05** (504 Gateway Timeout storm through
  the pinned gateway — DNS unchanged, so not a retired IP; quoter logs went
  silent 22:11 UTC). During that blind window the No bid FILLED (200 No @
  0.76, ~$152, 16:52–19:54 UTC) and a stale 200sh Yes bid @ 0.22 sat
  unmanaged until cancelled by hand from home 2026-07-06 ~01:45 UTC. The
  documented rollback was executed: `LP_STOP=1` + redeploy on Railway,
  local `data\STOP_LP` deleted → **the HOME PC is the quoting host again**
  (one-sided for now: only ~$47 cash remains, the No bid post_errors
  "not enough balance"; owner to decide whether to sell the 200 No).
  The 2026-07-03 "abuse flag aged out" hypothesis is now doubtful — the
  block re-tripped despite the backoff watchdog. **`IPROYAL_FIX_PROMPT.md`
  is the playbook to restore cloud** (probe → fresh proxy-user creds →
  WARP-chain → ticket → other providers). Service vars still set:
  `LP_LIVE=1`, `LP_SHARES=200`, `LP_MARKETS=<pinned Fed-Sep cond id>`,
  `LP_VIA_PROXY=<IPRoyal url, host pinned>`,
  `LP_PROXY_ALT_HOSTS=geo.iproyal.com`, plus `LP_STOP=1`.
  Maker fills are INVISIBLE in data-api `/trades` by default — pass
  `takerOnly=false` or you'll wrongly conclude nothing filled.
  **CLI gotcha:** `railway ssh -- <cmd>` hangs from this machine (banner,
  then nothing) — run one-shots via a temporary `startCommand` and read
  `railway logs` (which streams forever; wrap in a timed job).
- The Railway CLI is installed locally and logged in (foxychua01@gmail.com,
  project linked). **Quirk:** `~/.claude/settings.json` injects a DEAD
  `RAILWAY_TOKEN` env var that overrides the CLI login — every `railway`
  command must be prefixed with `$env:RAILWAY_TOKEN = $null;` (PowerShell)
  or `unset RAILWAY_TOKEN` (bash) until that line is deleted.
- A persistent volume is mounted at `/data` with env `DATA_DIR=/data`, so
  `lp_quoter_log.jsonl` (and the old arb logs) accumulate across deploys.
- **Every push to main redeploys Railway and restarts the quoter** —
  graceful (cancel-all on shutdown, re-quote ~1 min later) but don't push
  trivia; each push briefly takes the quotes off the book.
- The `STOP_LP`/`LP_STOP` pair prevents dual-quoting (each instance's
  cancel_all kills the other's orders): whichever side is NOT quoting must
  hold its kill switch. Currently the LOCAL `data\STOP_LP` exists (home
  quoter idle — the file also silences the home watchdog task) and
  Railway's `LP_STOP` is deleted (cloud is the quoting host). Flip BOTH
  when moving the pilot; deleting the local STOP_LP alone starts a
  dual-quote war within ~5 min (watchdog).

## Critical gotchas (each one cost real debugging hours)

1. **Geoblock — order placement 403s from ALL cloud/datacenter IPs**
   (Railway, AWS, GCP, Azure, Fly, Render…): `403 Trading restricted in your
   region`. Market *reads* (Gamma, CLOB books) work from anywhere. The
   owner's home IP (Malaysia) works for orders. Hence the split: measurement
   on Railway, execution on the home PC. Do not suggest another cloud
   provider as a fix — they're all blocked. The `OUTBOUND_PROXY` value in the
   local `.env` is the IPRoyal **rotating residential** gateway from the old
   Railway trading era — **RE-VERIFIED ALIVE 2026-07-02** (it's a GB traffic
   balance, no expiry; pinned `country-br`, sticky 30-min sessions, Vivo
   residential exits; a live GTC order was posted through it, went LIVE, and
   cancelled cleanly). This is the sanctioned PC-off trading path:
   `lp_quoter.py` takes `LP_VIA_PROXY=<that url>` — orders route through the
   proxy, reads/Telegram stay direct. Unknown: remaining GB balance (IPRoyal
   dashboard); the quoter uses ~100–300MB/month, and order failures Telegram
   loudly if it runs dry.
   **GeoDNS gotcha (cost the 2026-07-02 Railway flip 30 min of 504s):**
   `geo.iproyal.com` resolves per-region; the node Railway US-West gets
   fast-504s every request from datacenter sources, while the node Malaysia
   resolves to (31.222.226.171) accepts them fine. The Railway
   `LP_VIA_PROXY` therefore pins the gateway HOST TO THAT IP instead of the
   hostname. If proxied orders ever 504 again in a storm (fast ~3s
   responses, every session rotation failing), suspect the pinned IP was
   retired — re-resolve `geo.iproyal.com` from a residential vantage and
   re-pin.
   **The home PC runs Cloudflare WARP**, which routes egress through a
   Cloudflare (Singapore) IP and 403s orders too (discovered 2026-07-02).
   Fixed via split tunneling: `warp-cli tunnel host add clob.polymarket.com`
   (already applied; survives reboots but not a WARP reset). Do NOT
   `warp-cli disconnect` — the machine loses all connectivity. If orders 403
   from this PC, first run `warp-cli tunnel host list` and re-add the host.

2. **`POLYMARKET_FUNDER_ADDRESS` is NOT the UI's "deposit address".** The UI
   Cash→Deposit address (`0x54C8C1A0...`) is only where USDC arrives. Orders
   need the derived POLY_PROXY trading wallet:
   `0x832Ddc3fa9d43c03071736Fe566B0Ae0D6B964ac` for this account, with
   `POLYMARKET_SIGNATURE_TYPE=1`. Wrong funder → 400 "maker address not
   allowed, please use the deposit wallet flow" (the wording is a red
   herring; it is not a Privy/sig_type=3 problem). To find the right funder
   for any account: place one trade in the web UI, read `maker_address` from
   `GET /data/trades`.

3. **Market BUYs must use `create_market_order`, never `create_order` (limit)
   at a marketable price with FOK.** The CLOB enforces 2-decimal maker
   amounts on market-style fills; limit-at-market-price computes up to 5
   decimals on 0.001-tick markets and gets rejected with "invalid amounts".
   `polymarket_client.place_market_buy()` does this correctly.

4. **`neg_risk` and `tick_size` must be passed at order signing**
   (`PartialCreateOrderOptions`) and must come from **CLOB
   `get_market_meta()`, not Gamma** — Gamma's `negRisk` is occasionally
   null/wrong, and signing against the wrong exchange contract returns 400
   `order_version_mismatch`. Snap prices to the actual tick.

5. **`arb_executor.py` must fix env vars BEFORE `import config`** (config
   reads env once at import). It sets `MAX_PRICE=0.999` (the .env's 0.80 cap
   silently blocks arb legs priced above 80c inside `place_market_buy`) and
   blanks all proxy vars (orders must go direct from the home IP). If you
   create any new order-placing entry point, replicate that preamble or
   refactor it properly.

6. **Paused markets show phantom books.** Markets with
   `acceptingOrders=false` (live sports near resolution) keep displaying
   their last order book — quotes you cannot hit. They look like persistent
   free arbs. Both the scanner and the executor filter them; any new scanning
   code must too.

7. **Phantom edges from non-simultaneous snapshots.** The wide scan fetches
   books in 50-token chunks ~0.15s apart; on a fast market YES and NO get
   snapshotted at different moments and a fake edge appears. **Never count an
   arb hit without `arb_scanner.confirm_hits()`** — it re-fetches all legs of
   a hit in ONE request ~2s later. This is the v1→v2 methodology lesson: v1
   measured $30.88/day that did not exist.

8. **Exchange minimum ≈ $1 notional per leg** (`MIN_LEG_NOTIONAL_USD = 1.05`
   in the executor). With a tiny bankroll most hits are unaffordable — the
   executor Telegrams "SKIPPED (bankroll)" once per market per run.

9. **Gamma quirks:** `clobTokenIds` and `outcomePrices` sometimes arrive
   JSON-stringified; parse defensively. `enableOrderBook=false` means
   AMM-only, untradeable via CLOB. Field names vary across data-api
   endpoints (`asset` vs `tokenId`, `cashPnl` vs `realizedPnl`…).

10. **Windows console is not UTF-8.** Print market titles through
    `arb_scanner._ascii()` or you'll crash on `'` and similar characters.

11. **`.env` is gitignored and contains a LIVE wallet private key.** Never
    commit it, never print it, never send it to Telegram.

12. **Dead requirements:** `websockets` and `web3` are in requirements.txt
    but imported nowhere. Safe to ignore (or remove).

13. **Polymarket fee-walls the liquid markets — the binary-merge edge does NOT
    survive it.** CLOB `get_market` returns `taker_base_fee`/`maker_base_fee`:
    0 on slow politics markets, but nonzero on the high-volume sports/Fed
    markets (observed `taker_base_fee=1000`), and that fee exceeds a ~1c merge
    edge. The v2 "PROVEN ~$6/day" report (2026-06-15) was computed fee-free and
    so counted fee-walled markets as profit; net of fees those are losses. The
    stack is now fee-aware: `get_market_meta()` returns the taker fee,
    `arb_scanner.confirm_hits()` drops any hit on a nonzero/unknown-fee market
    (`FEE_FREE_ONLY`; env `ARB_FEE_FREE_ONLY=0` disables), the executor's
    `try_capture` refuses fee/unknown markets (`fee_skip`/`fee_unknown`), and
    measurement writes a fee-aware **v3** log. A 30-min fee-free probe
    (`probe_zero_fee.py`) found zero fee-free arbs.

## Home-PC watchdog (installed 2026-07-03, REMOVED 2026-07-06)

> **🛑 The scheduled task "Poly1M LP watchdog" was DELETED at the 2026-07-06
> project shutdown — it no longer runs and no longer resurrects the quoter.**
> The `.ps1` monitor script (`C:\Users\foxyc\.claude\poly1m_lp_monitor.ps1`)
> is left in place but inert. To revive the pilot you must re-create the task
> (see the retire/re-add note at the end of this section). The rest of this
> section describes the watchdog as it worked while active.

**While the CLOUD quotes (state since 2026-07-03 ~05:06 UTC), the local
`data\STOP_LP` stays in place and this watchdog idles by design — it is the
dormant failover, not dead weight. Deleting STOP_LP = dual-quoting against
Railway within ~5 min.**

Two artifacts OUTSIDE the repo keep the local pilot alive unattended:
`C:\Users\foxyc\.claude\poly1m_lp_monitor.ps1` + scheduled task
**"Poly1M LP watchdog"** (every 5 min, current user; was 15 until
2026-07-03). If `data\STOP_LP` is absent and no `lp_quoter.py` process
exists — or one exists but the ledger has been silent >10 min (hung) — it
(re)starts `start_lp_pilot.cmd` and Telegrams the owner via the important
bot (token read from `~/.claude/settings.json` at runtime, never stored).
Restarts throttled to 1/3min, alerts to 1/30min; actions logged to
`%LOCALAPPDATA%\poly1m_lp_monitor.log`. **Consequence: closing the pilot
window no longer stops the pilot — it auto-restarts within ~5 min. The ONLY
clean stop is creating `data\STOP_LP`.**
**Hard-kill safety (2026-07-03):** window close / logoff / OS shutdown
skip Python's atexit entirely — the pilot's first 26h had 10 startups and
ZERO clean shutdowns, leaving quotes unmanaged up to 15 min (one 200sh fill
landed while nobody was home). `lp_quoter.py` now registers a Windows
console-ctrl handler (`_install_console_handler`) that cancel-alls inside
the ~5s termination grace and writes a `console_kill` ledger event. Also
set on this laptop: lid-close on AC = do nothing (battery still sleeps),
sleep/hibernate on AC already 0. A `Stop-Process -Force`/BSOD still can't
run cleanup — the next startup's cancel-all (≤5 min via watchdog) is the
backstop. The quoter itself holds a
single-instance lock (localhost port 47391, env `LP_LOCK_PORT`), so a
stray second launch exits with a Telegram instead of a cancel-all war.
Retire with: `schtasks /Delete /TN "Poly1M LP watchdog" /F`.

## Kill switches

- **Arb executor:** create the file `data/STOP_ARB` → clean shutdown at the
  next 45s cycle, with a Telegram confirmation. (Deleting the file re-arms;
  the executor must be relaunched manually.)
- **LP quoter:** create `data/STOP_LP` → cancel-all + clean exit at the next
  60s cycle. It also cancel-alls on startup, shutdown and any crash — a
  resting quote surviving a dead bot is its worst failure mode. On cloud
  (no shell): set env `LP_STOP=1` and restart the service → cancel-all,
  then idles (doesn't exit, so restart policies can't spam cancel/notify).
  **STOP_LP is also the watchdog's off switch** — without it the scheduled
  task resurrects the quoter within ~5 min (see Home-PC watchdog above).
- **Old bot:** `TRADING_ENABLED=false` env → research-only dry run. The arb
  executor deliberately IGNORES this flag; STOP_ARB is its only switch.

## Data files (under `DATA_DIR`, default `./data`, Railway `/data`)

| File | Writer | Meaning |
|---|---|---|
| `arb_executor_log.jsonl` | arb_executor | Append-only event ledger (captured / faded / too_small / unwound / naked / errors). **Absence of this file = the executor has never logged a single event.** |
| `arb_positions.json` | arb_executor | `{"open": [...], "naked": [...]}` — held YES+NO sets awaiting resolution, and stuck one-sided legs. |
| `STOP_ARB` | you | Kill switch (existence-checked, content ignored). |
| `arb_log_v3.jsonl` | measure_arb | v3 = confirmed + FEE-AWARE measurement (zero-taker-fee markets only). Current methodology, on the Railway volume. |
| `lp_quoter_log.jsonl` | lp_quoter | Append-only event ledger (cycles / fills / vol_pulls / cancel_alls / scoring checks / crashes). |
| `STOP_LP` | you | LP quoter kill switch (existence-checked, content ignored). |
| `arb_log_v2.jsonl` | measure_arb | v2 confirmed-methodology log — fee-BLIND, counts fee-walled markets as profit. Superseded by v3; never mix. |
| `arb_log.jsonl` | (v1, local) | CONTAMINATED v1 measurement — phantom edges. Never mix with v2/v3. |
| `positions.json` | old bot | Old bot's open/resolved positions. |
| `research_cache.json` | old bot | 4h TTL Claude verdict cache. |
| `bot.log` | old bot | Rotating log (5MB ×3). |
| `history_dump.json` | one-off | Raw on-chain dump used for HISTORY_FINDINGS.md. |

## Conventions

- **Auto-push:** in this repo, every cohesive change is committed and pushed
  to `main` immediately without asking (owner's standing instruction —
  Railway deploys from main). Remember the redeploy-restarts-measurement
  caveat above.
- All tunables are env vars with defaults in `config.py` / module constants;
  the owner tunes via `.env` or Railway variables, not code edits.
- Every JSON state file is written atomically (tmp file + replace) except
  the executor's `arb_positions.json` (plain write — known minor weakness).
- All user-facing events go to Telegram (`TELEGRAM_BOT_TOKEN`/`CHAT_ID` in
  env). Notifications use `httpx ... trust_env=False` so a stale proxy env
  can't break them.
- Style: plain Python, type-hinted dataclasses where it matters, module-level
  constants for knobs, docstring at the top of each file explaining intent —
  the docstrings are accurate and worth reading; they document *why*, not
  just what.
