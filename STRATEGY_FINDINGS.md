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

## Addendum 2026-08-24: RSI regular-divergence + confluences (YT K7vFNn7fZ7Y) on BTC 15m

Same YouTuber as the 2026-08-21 hidden-divergence test ("The Moving Average").
This video: regular divergence on 15m + confluence stack (RSI<50 line cross,
break of structure, below 21-SMMA, optional three-line-strike trigger), SL at
divergence extreme, 1.5-2R targets. Backtest: `backtest_regdiv15m.py`,
BTCUSDT 15m, 2y (2024-08 -> 2026-08), no-lookahead fractal pivots.

- Naive divergence-only (what he warns against): n=1775, -0.16%/trade net. Dead.
- With confluences (tier B): n=439, win 42%, **gross +0.12%/trade** — the
  filter genuinely adds signal, robust across long/short (both +), both years
  (+0.17% yr1, +0.08% yr2 — decaying), and pivot/window params (+0.03..+0.15%).
- But net of 0.075%/side taker fees: **-0.03%/trade, -12% total. DEAD.**
  Even futures maker+taker (~0.06% RT) barely breaks even on the yr2 edge,
  before slippage. Three-line-strike trigger (tier C) doesn't rescue it.

Verdict: the video's core claim ("raw divergence loses, confluences fix it")
is directionally right — it's the only retail-TA template tested so far with
a robust positive gross edge — but the edge (~0.1%/trade) is below retail
round-trip costs. Sub-cost anomaly, not a strategy. No bot.

### Follow-up 2026-08-24: maker fees + timeframe sweep (regdiv tier B)

**Timeframe sweep (gross, TP 1.5R):** 5m -0.02%/trade, 15m +0.12%, 30m +0.14%,
1h -0.47%, 4h +0.01%. The edge lives ONLY in the 15m/30m band — neighbors are
flat-to-negative, which smells like band-specific luck rather than a general
phenomenon. 1h is outright bad.

**Maker-entry sim (15m, Binance futures fees: 0.018% maker / 0.045% taker-SL,
limit at signal close, filled only when a later bar trades through it):**
100% of signals fill at 0bp offset; net +0.070%/trade, +31% total over 2y
(n=438). Wider offsets don't help. So maker execution DOES flip the sign on
paper — but the year-2 gross edge (+0.08%) nets to ~+0.03%/trade at these fees,
inside noise (full-sample t~2.6, borderline), before slippage/queue reality.

Verdict unchanged: paper-positive at maker fees on exactly one timeframe with
a decaying, borderline-significant edge = not fundable. No bot.

### Follow-up 2026-08-24 (2): most profitable timeframe + settings (regdiv tier B)

Full sweep 5m..4h + settings grid (order type, TP 1.5/2/3R, SL pad, BE-move),
net of Binance futures fees (maker 0.018%, taker 0.045%), maker fills modeled
as limit-at-close filled only when a later bar trades through it.

Winner: **30m, TP 2R, maker limit entry ~10bp beyond close, no BE-move**:
BTC n=197, +0.55%/trade net, +107%/2y, t=2.3. Passes ETH out-of-sample
(+1.19%/trade, +223%, t=3.3) — the 15m top settings FAIL on ETH (-0.01%).
Robustness: BTC and ETH positive in BOTH years (decaying: BTC +0.66% yr1 ->
+0.38% yr2; ETH +1.93% -> +0.64%). SOL is firmly negative (-0.37%/trade,
26% win) — the edge is majors-only, not universal. BE-move at 1R destroys
every config (worst rows of the grid). TP 3R also bad.

Assessment: this is the strongest result of the whole retail-TA research
program — two assets, both years, OOS-confirmed, net of realistic maker fees.
Still fragile: single timeframe band, decaying edge, t-stats only 1.2-1.7 on
the yr2 halves, and the maker-fill model ignores queue position. If anything
ever graduates to a paper-trading bot from this program, it's this config.

## Addendum 2026-08-26: FULL TheMovingAverage channel mined — verdict on every strategy he teaches

Entire channel enumerated (407 videos + 743 shorts + 34 streams; shorts/streams
skipped as clip-derivatives), 166 strategy-relevant videos transcribed and
rule-extracted by Opus subagents into `research/tma_channel/videos/`, every
mechanical family backtested on 2y BTC (build) + ETH (OOS) + SOL, Binance
USDT-perp fees, honest maker fills, no-lookahead pivots. Full write-up:
`research/tma_channel/SYNTHESIS.md`; scripts in `research/tma_channel/backtests/`.

**Every standalone family he teaches is DEAD on crypto net of fees**: fib
golden-zone (his most-repeated), SMMA 21/50/200 flagship scalp, three-line
strike, Heikin-Ashi no-wick, hidden divergence (re-confirmed), SuperTrend
(fails OOS), StochRSI, RSI band-rejoin, SMMA200 retest, session ORB, his own
MT4 bots' entries, and the Tokyo-range fade (a genuine forex edge that simply
doesn't port — crypto has no quiet Tokyo session). ~25 videos gate their entry
on closed-source paid indicators (untestable by construction). Day-of-week
filters (no-Monday, Tue/Wed/Thu) failed placebo tests → rejected.

**The one survivor and one genuine improvement:** the already-live regdiv 30m
config, plus his "London open → NY close only" session rule (entries
07:00-21:00 UTC). BTC +0.25%/trade net (positive BOTH years — the unfiltered
baseline's yr2 is negative), ETH +0.50%, robust to window +/-2h, offset
0-20bp, TP 1.5-3R, both trade sides; portfolio max-DD drops 24.4% -> 16.9%.
SOL still negative. 1h still dead. Edge still decaying ~50%/yr.

**Honest correction to the 2026-08-24 numbers:** re-implementing the incumbent
exactly per `paper_regdiv.py` on fresh 2y data gives BTC +0.07%/trade (yr2
NEGATIVE) and ETH +0.59% - materially weaker than the +0.55%/+1.19% logged
from the (uncommitted) grid script. The paper bot is the arbiter; treat these
lower numbers as the standing estimate. ETH carries the edge.

**$1000 projection (best config: regdiv 30m BTC+ETH + sess filter, half
notional per trade, 1x, compounding):** 2y backtest 1000 -> 1767 USDT (+77%),
split +49.8% yr1 / +17.9% yr2, max DD ~17%, worst single trades -7.4% at 1x
(any leverage beyond ~3x on full notional courts liquidation; 20x = death,
unchanged). Forward-honest expectation = the decayed yr2 rate, ~+15-18%/yr
(~150-180 USDT/yr on 1000), with real odds the edge keeps decaying to zero.
No leverage-fueled shortcut exists in this data.

**Proposed (NOT launched) paper-bot change:** add `SESS_UTC=7-21` entry-hour
gate to `paper_regdiv.py` (skip signal bars outside 07:00-21:00 UTC; manage
open positions unchanged). One-line change, cuts the drawdown-heavy Asia-hours
trades that made BTC yr2 negative. Owner to approve before touching the live
paper bot.

### Follow-up 2026-08-26: "more trades" study (owner request)

Four frequency-scaling paths tested, each mapped to his own videos:
1. **More pairs** (his multi-chart watchlist): sess-regdiv 30m on 7 more
   majors — BNB/DOGE/AVAX/LINK ~zero, XRP −0.41%/tr, ADA −0.61%, LTC +0.27%
   (t=0.6, yr2 ~0 = noise). With SOL already negative: **the edge exists on
   BTC+ETH only.** Universe expansion adds losing trades, not volume. DEAD.
2. **Lower TF** (his 15m/5m scalp versions): 15m ETH negative w/ session
   filter. DEAD (re-confirmed).
3. **Fewer confluences** (his "pick 3-4 confluences"): dropping BOS doubles
   signals and kills the edge (BTC +0.03%, ETH −0.05%); RSI-50 and SMMA21
   turn out ~redundant once BOS holds — **BOS is the entire filter**, which
   is literally what his video preaches. DEAD.
4. **Overlapping signals** (the bot currently drops signals while in a
   position): the only honest path. BTC 159→337 trades/2y at BETTER
   +0.31%/tr (both yrs +); ETH 175→342 at diluted +0.12%/tr. Portfolio sim
   with his 1%-risk-per-trade sizing, max 3 concurrent/symbol: 27 trades/mo
   (vs 14), +23.8%/yr, maxDD 18.3%, peak notional 2.45x. BUT at constant
   risk%, extra concurrency does NOT raise return (10.1→10.6%/yr) while
   doubling DD (5.2→11.7%) — overlap adds turnover, not edge-per-risk.

Verdict: trade count can be ~doubled via concurrent-position slots without
degrading per-trade edge on BTC (ETH dilutes), but the profit lever is risk
per trade, not trade count. The channel's own advice ("Trade Less Win More",
"1 Trade a Day") is directionally correct for this edge.

### Follow-up 2026-08-26 (2): BTC-only variant (owner question)

Sess-filtered regdiv 30m, BTC alone, 1000 USDT, 2y:
- Non-overlap, 100% notional/trade (1x): n=159 (6.6/mo), 1000->1380
  (+17.5%/yr), maxDD 23.4%. Notably EVEN across years (+17.0% yr1 / +17.9%
  yr2) - the only config tested with no visible decay.
- Overlap conc3 @ 1% risk/trade: n=321 (13.4/mo), 1000->1392, maxDD 14.7%,
  peak notional 2.4x. Same return as A, lower DD, twice the trades.
- Overlap conc3 @ 1.5% risk: 1000->1685 (+30%/yr), DD 18.6%, peak 3.0x -
  approaching the leverage zone where a -7% worst-trade cluster hurts.

vs BTC+ETH (+77%/2y): higher total, but ETH is the decaying leg (+0.86% ->
+0.19%/tr) while BTC+sess is the stable one. BTC-only trades stability for
~half the backtest return; BTC-vs-ETH correlation (~0.8) means the pair adds
little diversification - ETH's contribution is return, not smoothing.

### Follow-up 2026-08-26 (3): owner's remix — divergence + 21SMMA cross only (no BOS)

Rules as specified: RSI(14) regular divergence sets direction; enter when a
candle CLOSES across the SMMA21 in that direction (within 40 bars); SL at
divergence extreme; TP 2R; incumbent execution (maker 10bp/TTL4). BTC only.

TF sweep (BTC): 5m negative; 15m ~zero; **30m the winner again**:
+0.117%/tr net, n=353 (14.7/mo - 2.2x the incumbent's trade count), positive
BOTH years (+0.128/+0.104); 1h inconsistent; 4h +1.41%/tr but n=44 with yr2
negative = small-sample yr1 spike, rejected. The "cross" event beats the
"already-beyond" state version everywhere.

1000 USDT, BTC-only, 100% notional 1x: 1000 -> 1,376 (+37.6%/2y, +17.3%/yr),
maxDD 18.3% - same money as the full-confluence BTC-only config with double
the trades.

Robustness caveats (why it does NOT replace the incumbent):
- **Fails ETH out-of-sample** (-0.004%/tr; with sess filter -0.170%). The
  BOS confluence is what makes the edge transfer across assets.
- **Session filter FLIPS it negative on BTC** (1000->991) - opposite
  interaction vs the incumbent config = fragility flag on both.
- Per-trade edge less than half the confluence version; shorts negative in
  the sess-filtered split.
Verdict: legitimate BTC-only cousin with 2x activity and matching total
return, but strictly less robust. Suitable as a paper-bot B-strategy at
most; his own "wait for the structure break" warning is what the ETH failure
empirically confirms.

### Follow-up 2026-08-26 (4): owner's touch-21SMMA rule — hidden divergence comes back to life

Owner's rule from live-chart discussion: divergence sets direction, enter when
price TOUCHES the SMMA21 (stop/limit resting AT the prev-bar MA level, not a
close-through). SL divergence extreme, TP 2R, entry charged as TAKER
(conservative - the touch could rest as a maker limit).

Surprise result: with the touch entry, REGULAR divergence goes flat but
HIDDEN divergence - dead in every close-entry test - becomes the program's
best performer. Mechanism: hidden div = pullback within a trend, and the
touch entry sells/buys the retest OF the 21MA at a better price; it is
"trade the 21-SMMA pullback in an established trend", with the divergence
as the trend qualifier.

BTC 15m: +0.27%/tr (yr1 +0.50/yr2 +0.12); ETH 15m OOS: +0.56%/tr
(+0.74/+0.39) - **4/4 asset-years positive, the only config besides the
incumbent to pass**. Long AND short positive on both assets. Sess 07-21
helps BTC (+0.32) and is neutral on ETH. 30m is BTC-yr1-driven; 5m BTC
negative (band-edge fragility, familiar smell); SOL incoherent (unchanged).

Portfolio BTC+ETH 15m, 50% notional each, 1x: n=474 (19.8/mo - the "more
trades" wish granted), 1000 -> 2,297 (+130%/2y; yr1 +79%, yr2 +28%),
**maxDD 33%** (double the incumbent's 17%).

Caveats before anyone falls in love: this is the Nth config iterated against
the SAME 2y of data in one session - accumulated researcher-degrees-of-
freedom risk is real even with the OOS asset; the yr2 drawdown is 33%; and
the band-edge (5m BTC negative) mirrors the fragility pattern of every
prior config. Verdict: strongest paper candidate of the whole program after
the incumbent; belongs in the paper bot as a tagged B-strategy so live data
can adjudicate. NOT a replacement for the incumbent yet.

### Follow-up 2026-08-26 (5): detector audit — matching Arty's ACTUAL method

Owner correctly suspected the backtest detector differs from how the videos
find divergences. Confirmed by re-reading the three definitive videos
(VwVEVu0-JWQ, 3APFZa1AQNw, udwkldark34):
- He spots swings ON THE RSI first ("my eye always goes to the RSI"), then
  reads price; my detector finds PRICE fractal pivots and reads RSI there.
- He connects ADJACENT prominent swings; my implementation pairs each new
  pivot with the OLDEST stored pivot within 60 bars (quirk), skipping peaks.

Built a faithful Arty-style detector (arty_div.py: RSI-series fractal 3/3
swings, adjacent pairs, price extreme +/-2 bars around each RSI pivot,
optional 70/30 out-then-back qualifier) and re-ran everything:

| config (15m/30m as before) | my detector | HIS detector |
|---|---|---|
| hidden + touch21, BTC 15m | +0.29%/tr | **-0.05%/tr DEAD** |
| hidden + touch21, ETH 15m | +0.56%/tr | **-0.03%/tr DEAD** |
| regular + confluences + sess, BTC 30m | +0.25%/tr | +0.01% (yr1 -0.34) |
| regular + confluences + sess, ETH 30m | +0.50%/tr | **-0.26%/tr DEAD** |
| regular + 70/30 secret sauce + touch, BTC | — | +0.13%/tr, BOTH yrs + (48% win, t=1.3) |
| regular + 70/30 secret sauce + touch, ETH | — | +0.07%/tr (yr1 neg) |
| hidden + 70/30 qualifier | — | n=0 (logically impossible - the filter only applies to regular, as his video states) |

Conclusions:
1. **His authentic method mostly LOSES on crypto.** Every profitable config
   of this program rides on the mechanical variant I coded (price-fractal
   pivots, far divergence extreme as SL), NOT on his visual method. The far
   SL anchor (the thing his adjacent-swing method removes) appears to be a
   load-bearing part of the edge - wide structural stops that rarely get
   swept.
2. The ONE his-exact-method config in the green is his true signature trade:
   regular divergence + "first divergence out of the 70/30 range" + entry on
   return: BTC +0.13%/tr net, positive both years, 48% win rate - real but
   thin (about half the B-strategy's edge).
3. Meta-lesson logged: two reasonable formalizations of the same YouTube
   strategy produce opposite signs. "Backtested his strategy" is always
   really "backtested one formalization" - and raises the data-mining
   caution on our positive results another notch. The paper bot remains the
   arbiter.

### Follow-up 2026-08-26 (6): the photo-method (prominent adjacent swings) — FINAL BEST CONFIG

Owner pinned Arty's method to the canonical frame (GER40 1h, all four
divergence types drawn between ADJACENT PROMINENT swings). With swing width
raised to match that prominence (fractal 8 bars each side on the RSI series,
adjacent pairs, gap<=100), his method + the owner's touch-21SMMA entry at
30m becomes the best result of the entire program:

- BTC 30m: +0.52%/tr net, n=181, 48% win, yr1 +0.33/yr2 +0.70, t=2.07
- ETH 30m: +0.73%/tr net, n=166, 42% win, yr1 +1.20/yr2 +0.34, t=1.55
- 4/4 asset-years positive; LONGS AND SHORTS positive on both assets
  (BTC 49.5%/46.7% win) - first config to pass every split.
- Portfolio (50% notional each, 1x): 1000 -> 2,646/2y (+165%), yr1 +71% /
  yr2 +55% (least decay in the program), maxDD 22.4%, 14.5 trades/mo.
- Worst single trades -12.1%/-9.5% at 1x: lr8 swings put SLs FAR away;
  fixed-notional sizing is inappropriate - size by risk (e.g. 0.5-1% equity
  per trade) and cap notional.

Fragility flags (unchanged in spirit): 6th in-sample iteration - mining
risk is at its highest; lr=5 neighbour at 30m is weak on BTC (~+0.03%/tr);
BTC 15m lr8 yr1 is flat. The parameter plateau is not smooth. Paper trading
remains the arbiter before any capital.

### Follow-up 2026-08-26 (7): owner's line-of-sight divergence definition

Owner pinned the actual selection rule: no bar-count at all - ANY two swings
qualify "as long as there's nothing blocking the full divergence line".
Coded exactly (los_div.py): anchors = 2/2 local extremes; pair = most recent
previous extreme whose straight connecting line is unpierced (tested price-
line-only and price+RSI-lines-both-clean, the photo's version); hidden div +
touch-21SMMA entry, SL far anchor, TP 2R, entry charged taker (conservative;
the resting limit at the MA would mostly earn maker, ~+0.027%/tr).

Result: positive in 7/8 asset-TF-year cells, no blow-up year anywhere, and
the frequency matches the owner's eyeball (~2,700 raw divergences/asset on
15m = 3.7/day). Per-trade edge is THIN (+0.03..+0.29%/tr): clean-line pairs
include many small nearby swings -> tight SLs, churn, fees bite.
Portfolios (BTC+ETH, 50% notional each, 1x, one position per asset):
- 30m: n=669 (27.9 tr/mo), 1000 -> 1,588/2y, maxDD 22.6% (yr1 +14.7%, yr2 +38.4%)
- 15m: n=1449 (60.4 tr/mo), 1000 -> 1,696/2y, maxDD 24.0% (yr1 +46.2%, yr2 +16.0%)

Detector-formalization league table (hidden+touch, BTC+ETH, 2y):
1. lr8 prominent adjacent swings, 30m: 1000->2,646, 14.5 tr/mo - best money
2. LOS (owner's rule), 30m/15m: 1000->1,588/1,696, 28-60 tr/mo - most
   faithful to the videos, most cells positive, thinnest per-trade edge
3. price-fractal skip-pair (mine), 15m: 1000->2,297 but maxDD 33%
4. small-swing adjacent (lr3): DEAD
All four are "the same strategy" as taught on YouTube. The formalization IS
the strategy.
