# STRATEGY FINDINGS — full validation of every Polymarket profit path (2026-07-02)

One day of data-first validation of every strategy proposed for this account.
Companion to `HISTORY_FINDINGS.md` (which killed the prediction bot). Every
number below was measured against live Polymarket data or backtested from
public records — nothing is estimated from vibes. Scripts live in the session
scratchpad; conclusions are mirrored in the agent memory.

---

## 1. Copy-trading the top-100 highest-net-profit traders — DEAD (all variants)

**The ask:** copy the top-100 net-profit leaderboard, ideally "at the exact
second or millisecond they execute."

**Cohort fact:** Polymarket's `/v1/leaderboard` API returns ONE PnL list,
capped at 50 wallets, identical for every time window (1d/7d/30d/all tested —
same list). "Top 100 by net profit" therefore resolves to the same top-50
cohort no matter how it's phrased. There is no alternative cohort to try.

**Backtest method:** each trader's last 14 days of trades (public data-api),
replayed chronologically; copy every BUY ≥ $50 notional with a fixed $10
stake; mirror their SELLs as exits; mark open positions at current /
resolution prices; charge the copier reality (+1c latency/spread slip + the
taker fee on fee-walled markets).

**Results (4,344 copies, ~$43k simulated turnover; reproduced in a second
run at n=3,921):**

| Variant | Result |
|---|---|
| Realistic (+1c slip, real fees) | **−5.0% to −5.1% on turnover** |
| Median single trader copied | −3.5% (only 16/39 positive) |
| Fee-free markets only | **n = 0** — these traders made zero copyable fee-free trades in 14 days |
| High-activity grinders only (≥100 trades), realistic | −3.87% |
| **UTOPIA: their exact fill price, zero slip, zero fees** | **−0.57%** |
| Grinders-only utopia | −0.11% |

**The millisecond question, answered by measurement:** average price drift
after their LARGE (≥$500) fills, measured from THEIR OWN fill price (n=80):
+0.11c at 10 min, +0.05c at 1 h, +0.08c at 6 h, +0.26c at 24 h — fewer than
half drift positive at all. A copier pays ~1–2c in slip+fees to harvest
~0.1c of drift. **Speed is irrelevant: even a zero-latency copier pays the
post-impact price (their order already consumed the book), and the "utopia"
row shows even their exact prices lose money.** Their leaderboard profit
comes from positions built earlier, maker fills, and sizing — not from the
visible trade stream. The visible trades are the exhaust, not the engine.
Practical note: the fastest physically possible copy from this PC is ~0.5–2 s
via the CLOB websocket; no colocation exists for Polymarket.

**Also biased in the strategy's favor:** the cohort was selected BECAUSE the
backtest window went well for them (survivorship), and it still lost.

## 2. Binary-merge / neg-risk arbitrage — DEAD (re-verified)

The 2026-06-15 fee-wall conclusion re-verified from scratch: per-category
taker fees (sports 3%, politics/tech/finance 4%, econ/culture/weather 5%,
crypto 7%; formula `rate × p × (1−p)` per share, taker-only) now cover 534 of
the top 600 markets = **90% of all 24h volume**; only geopolitics is
fee-free. Fresh probes (40 min live, both mechanisms, fee filter off) + a
deep scan (top ~2,000 markets): **zero fee-free arbs; zero net-positive
fee-walled arbs.** The only persistent "arb" found (NBA neg-risk convert,
0.6–0.7c gross) nets −2c/set after fees — it rests on the book precisely
because fees make it untakeable. The CLOB `taker_base_fee` flag still
matches Gamma `feesEnabled` (50-market cross-check, 0 mismatches), so the
executor/scanner fee gates remain valid.

## 3. Outsized LP reward pools — TRAPS (three mechanisms, all measured)

Polymarket pays ~$72k/day in maker rewards. Every abnormally attractive pool
decomposed into danger pay once netted against its own price history:
- **Iran/Hormuz cluster** ($200–700/day pools, thin competition): 12–17
  hourly moves ≥10c in 9 days → adverse-fill cost 3–10× the reward.
- **Fee-walled sports** (up to $8k/day pools): in-play flow.
- **"Victor Marx CO Governor"** ($800/day pool, 79% naive share): live
  recount knife-edge (~1,350 votes); count-feed watchers snipe resting quotes.
Also dead ends: fresh-pool frontrunning (`startDate` is monthly config
rotation, $59.5k of pools all showed 07-01); date-ladder dominance arbs
(mechanism genuinely riskless, books kept clean — one $0.21 instance found).

## 4. What SURVIVES — the only validated ways to make money here

1. **"Boring basket" LP rewards** — quote both sides (two BUYS) of calm,
   deep, long-dated reward markets at mid±1c, behind the walls that absorb
   toxic flow. Live-measured accrual pace: **~$27/day on $3k virtual**
   (paper sim, Polymarket's own scoring formula, zero fills in the measured
   window). Realistic after haircuts: **$5–15/day on ~$1.5–3k ≈
   0.3–1%/day**, bounded single-event downside. Payout machinery verified
   real (third-party accounts receive daily payouts at 00:10–00:17 UTC);
   order path verified live from this account. Remaining unknown = the
   actual $ Polymarket pays THIS account (competitor reaction) — resolvable
   with a **$65 (single-sided) or $200 (two-sided) micro-pilot** on the
   calm Fed-September market (model: $1.51/day resp. $4.49/day; answer
   arrives with the first 2–3 midnight-UTC payouts). Tool: `lp_quoter.py`
   (dry-run default, LP_LIVE=1 to trade, STOP_LP kill, cancel-all dead-man).
2. **Hedged holding rewards** — 3.25–4% APY on position value, paid daily,
   on eligible markets; a full YES+NO set is ~$1 at any price → riskless
   parking yield. ~$0.40/day per $2k. Verified paying via public feeds.
3. **Manual near-certainty entries** (settlement lag / post-determination
   buys) — the only pattern with a positive lifetime record on this account
   (+$22.59 manual vs −$134 all bots). Episodic (~$16 capturable found in
   one scan), carries UMA-resolution tail risk; keep it human, not a bot.

**Nothing on Polymarket is simultaneously meaningfully profitable and
risk-free for this account.** The honest portfolio answer remains: the
owner's time compounds better in the proven notes business; the strategies
above are side-yield at best.

## 5. Scaling answer: can LP rewards reach RM200 (~US$45)/day? (goal set 2026-07-02)

Method: for all 58 long-dated reward markets with pool ≥ $50/day, model
net $/day = pool × our scoring share (competitor Q read from the live book,
saturating as we grow) − pessimistic adverse-fill cost (assumes every ≥2c
hourly jump in the market's own 14d history fills our full quote), then
allocate capital greedily in $250/side steps. Script: scale_curve.py
(session scratchpad).

- **Naive optimizer (no guards):** RM200/day at ~$5.5k full-model, ~$24k at
  a 50% haircut — but it gets there by piling up to $8k into thin books at
  24–74% pool share, including a LIVE World Cup market that slipped a lying
  endDate past the filter. That is precisely the trap signature of §3.
- **Trap-guarded (≤$1k/side per market, ≤35% pool share, ≤4c/$/day adverse
  cost, >21d to resolution):** only 20 calm markets qualify, carrying
  $4.3k/day of total pool money. The capital curve **plateaus at ~$36/day
  model on $13.5k deployed** ($11–18/day after the 50–70% haircut). Under
  conservative assumptions RM200/day is NOT inside today's calm pools at any
  capital.
- **Strictly zero-risk RM200/day does not exist on Polymarket:** the only
  riskless yield (hedged holding-reward sets, 3.25–4%/yr) needs ~$410k
  parked to spit out $45/day.

The honest route is a ladder gated by the micro-pilot's calibration factor
**k = actual paid / model** (the pilot's model number is $4.49/day):

1. **Stage 0 — $210 pilot** (running plan; Fed-September market): 2–3
   midnight-UTC payouts measure k.
2. **Stage 1 — if k ≥ 0.5:** $1–3k across 5–8 calm markets → RM25–75/day
   while measuring k at basket scale.
3. **Stage 2 — scale to what k implies for RM200/day:** k≈1 → ~$6–8k;
   k≈0.5 → ~$24k and accepting relaxed guards (more markets, bigger pool
   shares = more trap exposure); k < 0.3 → the goal is not achievable at
   minimal risk; stop and say so.

Caveats at scale: the two Fed-hike markets are correlated (cap combined
macro exposure); model yields this high (~100%/yr) decay as competitors
notice; pools rotate monthly — re-screen before every tranche.

### Empirical proof from real payouts (same day, no capital spent)

The model above was then checked against REAL people's payouts, all from
public feeds (data-api `/activity?type=REWARD`, `/value`, Blockscout token
balances; scripts harvest_lps.py / true_yield.py in the session scratchpad).
Harvested 60 wallets trading the calm reward markets; 28 receive REWARD
payouts; **13 were paid TODAY (2026-07-02) in the 00:10–00:17 UTC window** —
the machinery pays, on schedule, right now.

- **12 wallets average ≥ $45/day (RM200/day) from rewards alone** — the goal
  income is being earned on Polymarket today, at scales from $46/day
  (0xb687…, $54k portfolio) to $4,200/day (0xc602…, $65k portfolio).
- **Small-capital operators exist:** 0xa3282… earns $45.04/day avg on ~$3.0k
  visible capital ($2,578 USDC + $449 positions) ≈ 1.5%/day realized — full
  model yield, i.e. empirical k ≈ 1 for a competent operator. 0xd23f8… earns
  $67.65/day on $1.9k visible positions. Caveat: visible-capital snapshots
  can undercount (some account types hold collateral elsewhere — several
  whale wallets show $0 USDC at their data-api address), so treat these
  yields as upper bounds; even at 3–5× hidden capital the RM200/day entry
  point stays in single-digit $k.
- **The rewards aren't danger-pay being clawed back** for the comparable
  operator: 0xa3282…'s public PnL curve rose +24% over the last month
  ($78.6k → $97.5k cumulative), volatile but steadily up.

Status of the ladder after this: the WAY is proven at mechanism level
(pools pay daily; RM200/day incomes exist; a same-shape small operator
realizes ~model yield). What remains OUR-account-specific — the share our
particular quotes capture — is exactly what the $210 pilot measures. It is
calibration, not validation.

## Operational discoveries (cost real debugging time — don't relearn)

- **Cloudflare WARP on the home PC geoblocks orders** (egress = Singapore,
  proxy-flagged → CLOB 403). Fix (applied): `warp-cli tunnel host add
  clob.polymarket.com`. NEVER `warp-cli disconnect` — the machine loses all
  connectivity. If orders 403: check `warp-cli tunnel host list` first.
- CLOB order-status reads lag a few seconds after post/cancel; a stale
  `LIVE` right after a cancel is normal — re-check `get_open_orders`.
- `prices-history` works with `interval=max&fidelity=60`; `startTs/endTs`
  params silently return nothing.
- `are_orders_scoring` gives per-order reward eligibility straight from the
  CLOB — use it on day one of any LP run instead of trusting the model.
