# PROMPT: Fix the Railway→IPRoyal tunnel so the LP pilot runs without the home PC

You are Opus 4.8 in Claude Code, working in `C:\Users\foxyc\Desktop\Poly1M`.
Read `CLAUDE.md` first (especially gotcha #1 and the Deployment section),
then the **STATUS LOG at the bottom of this file** — a previous session may
already have done part of this work. Do not redo what's already done.

## Mission

Polymarket order placement needs a residential IP. The cloud pilot
(`lp_quoter.py` on Railway) reached one through the IPRoyal rotating
residential gateway — until **2026-07-02 ~12:50 UTC**, when IPRoyal began
refusing tunnels from hosting-ASN sources: CONNECT accepted, upstream never
answers, every session, 8h silent outage. Moving Railway to asia-southeast1
did NOT help (block is by source classification, not region). Since then the
quoter runs on the owner's home PC and he wants it OFF his PC.

**Goal: restore a cloud→residential order path and cut the pilot back over
to Railway.** The owner believes fixing IPRoyal is easier than replacing it
— try that first, but a different provider is an acceptable outcome.

**Definition of done:** a live GTC order posted FROM the Railway container
THROUGH the proxy goes LIVE on the book and cancels cleanly (the same
verification done 2026-07-02 from home — `local_test_arbitrary.py` shows the
order-signing pattern; a tiny throwaway script inside the container is
fine). Then execute the cutover (below). Anything short of a live order
proving out is NOT done — reads working through the proxy proves nothing
(reads aren't geoblocked).

## Evidence base (2026-07-03, from the previous session)

- Home baseline: same gateway+creds tunnel fine — exit `177.37.232.200`
  (Vivo BR residential), `clob.polymarket.com/time` HTTP 200 in 2s.
  `geo.iproyal.com` resolves to `31.222.226.171` from home (the IP Railway's
  `LP_VIA_PROXY` pins).
- Account is healthy (GB balance not exhausted — home tunnels work).
- `probe_proxy.py` (repo root) produces the full evidence matrix from any
  vantage. Run it inside Railway with:
  `railway ssh -- python probe_proxy.py`
  and compare with a home run (`python probe_proxy.py`). Results append to
  `DATA_DIR/proxy_probe.jsonl`.
- Suspected trigger: the quoter's once-a-minute session-rotation retry spam
  during the 8h outage may have tripped IPRoyal's per-account/per-user abuse
  flag — or IPRoyal introduced a blanket datacenter-source policy. Which of
  the two it is decides the fix; establishing this is your first job.

## Fix avenues, in order

1. **Diagnose from inside Railway** (`railway ssh -- python probe_proxy.py`).
   Expected signature if still blocked: TCP connect PASS, tunnel FAIL
   (timeout). Capture Railway's egress IP+ASN from the probe output — that's
   ticket evidence. If tunnels PASS, the block lifted on its own: jump
   straight to the live-order verification and cutover.
2. **IPRoyal dashboard recon** (dashboard.iproyal.com — owner's Chrome
   likely has a session; use claude-in-chrome, or ask the owner to log in).
   Check: remaining GB balance; any abuse/ToS notice on the account; the
   royal-residential proxy-user settings. **Try creating a FRESH proxy
   user/credential pair** — if the abuse flag is per proxy-user, new creds
   may clear it instantly. Test the new creds via `railway ssh` probe with
   `LP_VIA_PROXY` overridden inline: `railway ssh -- env LP_VIA_PROXY=<new>
   python probe_proxy.py` (redact creds in anything you print/commit).
3. **Route Railway's egress through Cloudflare WARP (free, empirically
   supported).** The home PC's probe shows its direct egress is a Cloudflare
   WARP IP (`104.28.163.100`, Cloudflare ASN 13335 — a datacenter ASN!) and
   IPRoyal accepts tunnels from it. So IPRoyal's filter blocks specific
   hosting classifications, not "anything non-consumer" — Cloudflare's
   network passes. If Railway's connection to `geo.iproyal.com` arrives from
   a WARP IP instead of Railway's ASN, it should pass too. Railway
   containers have no TUN/NET_ADMIN, so use userspace WireGuard: `wgcf`
   (registers a free WARP account, emits a WireGuard profile) + `wireproxy`
   (runs that profile in userspace, exposes a local SOCKS5/HTTP proxy).
   Then chain: quoter → local wireproxy → IPRoyal gateway → residential
   exit. py-clob-client reads an HTTP proxy from the env, and proxy-chaining
   (HTTP CONNECT via an upstream SOCKS) needs a tiny local relay — `pproxy`
   (pip) can chain both hops in one process. Validate the chain with
   `probe_proxy.py` first (point `LP_VIA_PROXY` at the local relay), then a
   live order. Keep the WARP hop OUT of market reads/Telegram (only order
   traffic needs it — same split `lp_quoter.py` already implements).
4. **IPRoyal support ticket / live chat** with the probe evidence. Ask
   explicitly: "are connections from hosting/datacenter source ASNs to the
   royal-residential gateway blocked by policy, or is this an abuse flag on
   my account? Can it be exempted for my account/IPs?" Attach: timestamps
   (block started 2026-07-02 ~12:50 UTC), gateway `geo.iproyal.com:12321`,
   pinned `31.222.226.171`, Railway egress IP/ASN from the probe, the
   CONNECT-accepted-upstream-silent signature, and that the same creds work
   from consumer sources. The owner approves sending — show him the draft
   via the important Telegram bot if he isn't in the session.
5. **IPRoyal static residential (ISP) product** — different gateway
   architecture (direct IP:port endpoints, not the geo gateway); the
   datacenter-source filter may not apply there. Small monthly cost — get
   owner approval by Telegram BEFORE buying. A single static residential IP
   is enough (the quoter needs one stable exit, rotation is unnecessary for
   quoting).
6. **Alternative providers** (only if IPRoyal says "policy, no exemption"
   AND the WARP chain fails):
   candidates Webshare, Decodo (ex-Smartproxy), SOAX, NetNut, PacketStream.
   Selection criteria: allows hosting-ASN clients (ask support BEFORE
   paying), per-GB pricing (quoter uses ~100–300MB/mo), sticky sessions,
   HTTP CONNECT proxy, any-country residential exits. Owner approval before
   any purchase; validate with the probe, then the live order.

## Cutover procedure (after the live-order proof)

Read CLAUDE.md "Deployment" first. Order matters — dual-quoting is the
failure mode (each instance's cancel_all kills the other's orders):

1. Create `data\STOP_LP` on the home PC → home quoter cancel-alls and exits
   at the next 60s cycle. **STOP_LP also silences the home watchdog task —
   LEAVE THE FILE THERE permanently while Railway quotes.**
2. Verify the home quoter exited (no `lp_quoter.py` process) and its ledger
   shows the clean `STOP_LP → shutdown → atexit` cancel trio.
3. On Railway: set `LP_VIA_PROXY` to the WORKING proxy URL (re-pin the
   gateway host to its resolved IP if using geo.iproyal.com — GeoDNS gotcha),
   keep `LP_LIVE=1 LP_SHARES=200 LP_MARKETS=<pinned cond id>`, unset
   `LP_STOP`, redeploy.
4. Watch: `railway logs` + the ledger on `/data` for `startup` + `cycle`
   events with `quotes: 2`; wait for the one-time `scoring_check` = all
   true; confirm no `post_error`. The outage watchdog Telegrams DOWN if the
   proxy dies again — that alert reaching the owner is part of the design.
5. Update CLAUDE.md (Deployment + gotcha #1) and the memory file
   `lp_pilot_cloud.md` to reflect the new state. Telegram the owner a
   completion summary via the important bot.

## Hard rules

- `.env` holds a LIVE wallet private key — never print, commit, or send it.
  Never print proxy credentials either; redact as `//***@` (probe_proxy.py
  already does).
- Railway CLI: every command needs `$env:RAILWAY_TOKEN = $null;` first
  (a dead token in `~/.claude/settings.json` overrides the login).
- Auto-push convention: commit+push cohesive changes to main without asking
  (pushes redeploy Railway; while it idles under LP_STOP that's harmless).
- Spending money (proxy purchase, plan change) needs owner approval via the
  important Telegram bot (`@NightmewFoxyImportantShitbot`, token in
  `~/.claude/settings.json`).
- No metered LLM APIs for any of this — subagents on the subscription only.
- Do NOT `warp-cli disconnect` on the home PC, ever.
- Keep tunnel-retry volume LOW while testing (a handful of attempts, spaced)
  — retry spam is itself suspected of causing the flag.

## STATUS LOG (append findings here, newest first)

- **2026-07-03 ~05:00 UTC (Fable session, RESOLVED — for now):** In-container
  probe from Railway asia-southeast1 passed **8/8**: egress 208.77.246.62
  (AS400940 Railway) → tunnel via pinned 31.222.226.171 AND via
  geo.iproyal.com (resolves to the same IP from SG) → residential exit
  177.37.170.79 → CLOB HTTP 200 in ~2s. **The hosting-ASN block has
  LIFTED.** Best hypothesis: a temporary abuse flag that aged out after
  ~24h of quiet (the once-a-minute rotation spam stopped when the cloud
  quoter went idle under LP_STOP on 2026-07-02 evening). Root cause NOT
  confirmed by IPRoyal — if order posts start failing again with the
  CONNECT-accepted-upstream-silent signature, the flag likely re-tripped:
  keep retry volume low (the quoter's backoff watchdog already does) and
  work avenues 2-4; the WARP-chain avenue (#3) remains the best fallback.
  Cutover to Railway executed the same session (see CLAUDE.md Deployment
  for the state you inherit). Gotchas hit: `railway ssh -- <cmd>` HANGS
  from this machine (banner prints, command never executes — needs a pty?);
  use a temporary probe startCommand + `railway logs` instead. `railway
  logs` streams forever — wrap it in a timed job.
- **2026-07-03 (Fable session, initial):** Home baseline PASS (exit
  177.37.232.200, CLOB 200/2s, geo resolves 31.222.226.171). Account healthy.
  `probe_proxy.py` written. Chrome extension not connected for dashboard
  recon — do it with the owner present if needed.
