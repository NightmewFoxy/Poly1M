# DECISIONS — tradeoffs, rejected approaches, and verbal-only plans

A record of *why* the project looks the way it does. Most of these were
discussed in Claude Code sessions and exist nowhere else. Dated where it
matters; "owner" = NightmewFoxy.

## The big pivot: prediction → arbitrage (2026-06-10)

**Rejected: every form of "predict the outcome and bet".** A full on-chain
reconstruction of the account's lifetime (78 trades) proved the esports
research bot wins *less* often than its entry prices imply at every price
band — Claude's `true_prob` estimates carry no information the market lacks,
because Polymarket esports odds mirror sharp bookmaker lines. As a pure
taker the bot also pays the spread plus 2% fee on wins, so zero edge means
guaranteed negative expectancy. Full numbers in `HISTORY_FINDINGS.md`.

We explicitly considered and rejected the "tune it harder" path:
- **MIN_GAP_PP filter** (only bet ≥3pp gaps): shipped, trades after it went
  0/7. Filtering noise doesn't create signal.
- **Position rotation** (swap held positions for ≥5pp-better new ideas):
  shipped, then **disabled in code** (commit e653aaa) once we realized it
  structurally selects for the model's *largest errors* — the ideas that
  look 5pp better than held ones are disproportionately the ones where the
  estimate is most wrong.
- Price-band restrictions, confidence gating, stake sizing: all variations
  change the noise, not the sign.

**Also killed: the BTC 5-minute sniper** (2026-05-15) after losing -$25 on
$150 cycled. Removed from the repo entirely; only HISTORY_FINDINGS.md
remembers it.

**Adopted: arbitrage only.** Two mechanisms verified live on real order
books on 2026-06-10:
1. **Binary merge:** ask(YES)+ask(NO) < $1.00 → buy both; a YES+NO pair is
   worth exactly $1 at resolution (or instantly via CTF `mergePositions`).
2. **Neg-risk convert:** in a winner-take-all event, a full NO set always
   pays ≥ N−1; `convertPositions` redeems it immediately. If
   sum(NO asks) < N−1, that's free money.

**Rejected as NOT-an-arb: "buy all YES when they sum < $1".** Verified that
big Polymarket events have no catch-all "Other" outcome (Presidential 2028 =
36 named candidates only), so an unlisted winner zeroes the whole basket.
The discount is risk premium, not mispricing. The scanner deliberately does
not implement it.

## Measurement before commitment (2026-06-11 → 06-12)

**Decision: don't scale capital until arb flow is *measured*, not
estimated.** Hence `measure_arb.py` on Railway: 24h of logged scans →
capturable-$/day at $100/$1k/$10k tiers → PROVEN (≥$2/day persistent on
$100) / MARGINAL (≥$0.50) / NO verdict to Telegram. Thresholds were chosen
as "clearly worth the effort / beer money / stop".

**Rejected: the v1 measurement methodology and its $30.88/day result.** v1
counted edges computed from book snapshots taken seconds apart (chunked
fetches) and included paused markets whose displayed books can't be hit.
When v2 re-checked each hit ~2s later on a single simultaneous `/books`
request, most v1 "edges" evaporated (first v2 scan: 4 raw → 2 confirmed).
Standing rule: **never report an arb number that hasn't survived
`confirm_hits()`**, and never mix v1 (`arb_log.jsonl`) with v2
(`arb_log_v2.jsonl`) data.

**Verdict design choices:** episodes are deduped by (kind, title) across
consecutive scans — a persisting opportunity counts once, because you'd
drain its depth once; and only *persistent* episodes (seen in ≥2 consecutive
60s scans) drive the verdict, because one-scan blips aren't catchable by a
60s-cadence home bot. Both choices deliberately bias the verdict
*conservative*.

## Executor v1 scope (2026-06-12)

Built `arb_executor.py` in parallel with the measurement (real fills are
better evidence than any log), but with deliberately tiny scope:

- **Binary-merge only; neg-risk converts scanned but NOT executed.** A
  convert needs N legs filled near-simultaneously plus an on-chain
  `convertPositions` call through the proxy wallet — too much build for a $3
  test bankroll, even though the confirmed flow so far is *mostly converts*.
  This is consciously deferred, not forgotten.
- **Hold-to-resolution instead of on-chain `mergePositions`.** A filled
  YES+NO pair pays $1/set at resolution with zero extra plumbing; merge
  needs web3 signing through the proxy. Cost: capital locked until
  resolution + manual UI claim. Acceptable at $3, must be revisited at scale.
- **$3 rails** (`ARB_MAX_EXPOSURE=3`, `ARB_MAX_PER_OPP=3`): the point was
  proving the pipe end-to-end, not making money. Edge floor at execution is
  1.0c vs the scanner's 0.5c because the final re-snapshot, order latency,
  and rounding dust eat into detected edges.
- **Legging policy:** FAK with the live ask as a hard cap (zero slippage
  ticks) — a moved book gives a $0 no-fill, never a worse price. Thinner
  leg first (most likely to vanish). If leg 2 misses: chase it up to
  breakeven minus 0.2c (any price ≤ 1−paid1 still can't lose at
  resolution); failing that, unwind leg 1 at the bid and book the small
  loss as the cost of legging risk; failing *that*, hold the naked leg,
  retry selling every cycle, and freeze all new trading until it clears.
  This ladder was chosen over "fire both legs concurrently" for
  debuggability at tiny size.
- **Kill switch is a file (`data/STOP_ARB`), not an env var**, so the owner
  can stop it without touching the running window; and the executor
  deliberately ignores the old bot's `TRADING_ENABLED` flag so the two
  systems can't interfere.
- **Top-up signal instead of auto-sizing:** when a hit needs more than the
  remaining budget to clear the ~$1.05/leg exchange minimum, the bot
  Telegrams "top up to capture these" once per market per run. The owner
  wanted evidence of missed opportunities before committing more capital.

## Infrastructure decisions

- **Execution lives on the home PC, measurement on Railway** — Polymarket
  403s order placement from all datacenter IPs, home (Malaysia) IP works.
  The earlier workaround (IPRoyal residential proxy fronting Railway) was
  used in the prediction era; the proxy in `.env` is now stale and the arb
  executor explicitly blanks it to connect direct. Paying for a fresh
  residential proxy was considered and **rejected for now**: at current
  edge sizes the proxy fee likely exceeds the arb income, and home
  execution is free. Revisit only if the verdict is PROVEN and uptime
  matters.
- **Railway keeps running measurement, not the old bot.** `railway.toml`'s
  startCommand was switched from `python main.py`; restoring the old bot is
  a one-line revert that nobody should make (see HANDOFF Track 3).
- **No database** — append-only JSONL ledgers + small JSON state files,
  by deliberate preference for inspectability at this scale.

## Verbal-only ideas (never started, in rough priority)

1. **Neg-risk convert executor** — multi-leg FAK + `convertPositions`. The
   most likely real money. Prereq: bankroll that clears N× the per-leg
   minimum (N=13–16 outcomes ⇒ ~$15–20 minimum per opportunity).
2. **Fee-rate awareness** — read each market's fee before trusting an edge
   (the measurement report's own caveat; see HANDOFF gap #1).
3. **On-chain `mergePositions`** to recycle capital same-day instead of
   waiting for resolution (this is what `web3` was added to requirements
   for).
4. **CLOB websocket book feed** to react in seconds instead of the 45s poll
   (this is what `websockets` was added for). Only worth it after 1–3.
5. **Maker-side variant** (rest limit orders inside the spread on both
   sides) was mentioned once as "how the pros actually do it" — never
   analyzed seriously; treat as a research question, not a plan.

## Calibration notes for whoever inherits this

- The owner's stated ambition is large ("Poly1M") but decisions have been
  consistently evidence-first: measure, verdict, only then scale. Keep that
  discipline; the repo's own history (HISTORY_FINDINGS.md) is the best
  argument for it.
- Honest current read: binary-merge flow at home-PC speed is probably beer
  money; the open question the v2 verdict answers is whether even that is
  real. The asymmetric upside is the convert executor, which nobody has
  built. The only lifetime-positive line on this account so far is the
  owner's two manual bets.
