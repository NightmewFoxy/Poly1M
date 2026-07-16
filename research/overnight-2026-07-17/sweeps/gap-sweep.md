# Gap Sweep — Genuinely New Mechanisms Not Yet Covered

**Date:** 2026-07-17 (final overnight sweep pass)
**Brief:** find up to 5 genuinely different directional crypto futures long/short
mechanisms NOT already tested tonight, with credible 2024-2026 quantified evidence,
executable by a $500-$5,000 retail trader (home PC, Malaysia, Bybit/OKX/Kraken/
Deribit, minutes-to-days holding) using free data. Read-only web research; no
orders; no metered LLM APIs used to produce this file.
**Already tested tonight (do not re-surface unless a source dodges the documented
kill factor):** time-series momentum/trend (MARGINAL), cross-sectional alt momentum
(VIABLE — current leader), Donchian ensembles, RSI/Bollinger mean reversion (DEAD),
pairs/cointegration stat-arb (DEAD), funding-rate fade & follow (DEAD), delta-neutral
funding harvest (descoped baseline), time-of-day/day-of-week seasonality (DEAD net),
pre-FOMC/CPI drift (DEAD), BTC-leads-alts lead-lag (DEAD), intraday first-hours
momentum (DEAD), liquidation-wick dump-buying (MARGINAL-weak), open-interest
extremes (UNVERIFIABLE-DATA), stablecoin depegs (not-a-strategy), CME gap fill
(DEAD), grid/MM/arb/carry (out of scope).
**Editorial note:** this sweep turned up a lot of retail-blog and content-farm noise
(near-duplicate SEO articles, single-anecdote "backtests," vendor marketing dressed
as research). Every entry below distinguishes real academic/institutional sources
from that noise, and says plainly where I could not find credible quantified
evidence rather than padding with narrative-only claims.

---

## Tier 1 — genuinely new mechanisms, credible quantified evidence found

### 1. US-dollar institutional demand flow → BTC drift (ETF flows, verified in real time via regional exchange premium)

- **Mechanism:** Net creation/redemption flow into US spot Bitcoin ETFs (IBIT, FBTC,
  GBTC, ARKB, BITB, etc.) mechanically forces authorized participants to buy/sell
  BTC on the open market. This shows up (a) next-morning in official flow tables and
  (b) in **real time** as a widening/narrowing of the **Coinbase Premium Index**
  (the % price gap between BTC/USD on Coinbase and BTC/USDT on Binance) — Coinbase
  is the exchange of record for US-regulated capital including ETF authorized
  participants, so premium-widening is a live proxy for the same buying pressure
  the next-day flow report will later confirm. **Exact rule tested in the literature:**
  regress/Granger-test daily BTC return on prior-day(s) ETF net flow.
- **Claimed performance + URL + sample period:**
  - Boon Chuan Lim, **"The Price Impact of Spot Bitcoin ETF Flows"** (SSRN, April
    2025) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6592830 — daily data,
    5 largest US spot BTC ETFs, **Jan 2024–Apr 2025 (313 trading days)**. Findings:
    bidirectional Granger causality (flows→returns AND returns→flows, β=0.47,
    t=9.75); **$100M net flow ≈ 53bps same-day BTC return**; flows explain **~21%**
    of daily return variance; paper states flows also predict next-day returns.
  - FalconX, **"What Can Spot ETF Flows Tell Us About the Trajectory of Bitcoin
    Prices?"** — https://www.falconx.io/newsroom/what-can-spot-etf-flows-tell-us-about-the-trajectory-of-bitcoin-prices-a-preliminary-statistical-investigation
    — VAR model, **Jan 11–Oct 11 2024** (10 months daily). Findings: raw correlation
    only **0.30** (R²<10%, much weaker than Lim's 21%); prior-day inflow coefficient
    **0.027** on today's return; Granger F=8.48, p=0.004; impulse-response **peaks
    ~1.2% around days 3-4** then decays. Authors explicitly frame flows as
    leading/predictive, not coincident, but hedge: "not a crystal ball."
  - Corroborating (longer-run, weaker form): **"From Flows to Value: Cointegration
    Between Bitcoin Spot ETF Assets and Bitcoin Price"** (Ledger journal, Dec 2025)
    — https://ledger.pitt.edu/ojs/ledger/article/view/393 — daily data Jan 11
    2024–May 16 2025, finds a long-run cointegrating relationship (10% significance)
    between ETF AUM and BTC price level — supportive but not a short-horizon
    trading signal on its own.
  - **Honest discrepancy:** the two headline studies disagree on effect size by
    ~2x (21% vs <10% of variance explained) despite overlapping windows and the
    same underlying data — treat the true effect as somewhere in that range, not
    at either extreme, and re-estimate yourself before sizing a position off either
    number.
- **Gross/net of fees:** Neither paper models a costed trading strategy — both are
  statistical (regression/Granger/VAR) studies of return predictability, not
  backtested P&L. This must be built from scratch; treat the R²/coefficients as
  raw material, not a proven net return.
- **What free data verifies it tonight:** Official flow tables are free and
  published daily: Farside Investors (https://farside.co.uk/btc/, no signup),
  CoinGlass ETF page (https://www.coinglass.com/etf/bitcoin), SoSoValue, Bitbo. The
  **real-time proxy** (Coinbase Premium Index) is free and continuous via CryptoQuant
  (https://cryptoquant.com/asset/btc/chart/market-data/coinbase-premium-index) or
  CoinGlass (https://www.coinglass.com/pro/i/coinbase-bitcoin-premium-index, API
  documented at https://docs.coinglass.com/reference/coinbase-premium-index) —
  this sidesteps the next-day publication lag on official flow data and can be
  logged by the project's existing sampler pattern immediately.
- **Most likely kill factor:** (1) Official ETF flow data for day T is only
  published the morning of T+1 — by the time you can act, the US session has often
  already partly digested it, and the paper's own admission that flows and returns
  Granger-cause *each other* raises a real confound: both may just be reacting to
  the same macro/risk-appetite catalyst same-day rather than flow *causing* the
  next move. (2) R² in the 10-21% range is a genuinely weak standalone edge — most
  of daily BTC return variance is unexplained by flows, so this is better tested as
  a directional-bias filter (only take longs when trailing 2-3 day flow is
  strongly positive) layered onto an execution rule, not a standalone signal. (3)
  Novelty-decay risk: US spot ETFs are a post-Jan-2024 structure; as the trade
  becomes common knowledge among faster institutional players the edge may compress
  the way funding-rate carry did (documented elsewhere in this hunt).
- **Suggested queue entry:** `etf-flow-coinbase-premium` — P2 (needs its own costed
  backtest built, not reproducible from a source's numbers alone) — data plan:
  Farside daily flow history (free CSV/table scrape) + CryptoQuant/CoinGlass
  Coinbase-premium history, regress next-session BTC perp return, walk-forward
  split, net of taker fees.

### 2. Stablecoin / ETH on-chain exchange-flow → short-horizon BTC/ETH return forecasting

- **Mechanism:** Different from generic "exchange netflow" folklore (see Ruled-out
  section) — this is a specific, peer-reviewable finding: **USDT flowing FROM
  investor wallets INTO exchanges** ("dry powder arriving to buy") **positively**
  forecasts BTC and ETH returns at short intraday horizons, strongest at 1 hour.
  Separately, **ETH's own net inflow into exchanges** (ETH moving toward exchanges,
  typically to sell) **negatively** forecasts ETH's own returns across all
  intraday intervals tested. BTC's own exchange netflow has little standalone
  return-forecasting power (except weakly at 4h) but does negatively forecast BTC
  volatility.
- **Claimed performance + URL + sample period:** Yeguang Chi, Qionghua (Ruihua) Chu,
  Wenyan Hao, **"Return-Forecasting and Volatility-Forecasting Power of On-Chain
  Activities in the Cryptocurrency Market"** (also circulated as "Return and
  Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets"),
  submitted **Nov 2024**. Cross-indexed on 4 independent platforms (unusual
  corroboration for a single paper, raises confidence it's a real, findable
  result): arXiv:2411.06327 (https://arxiv.org/abs/2411.06327), SSRN
  abstract_id=4630115 (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4630115),
  RePEc (https://ideas.repec.org/p/arx/papers/2411.06327.html), ResearchGate
  (https://www.researchgate.net/publication/387931633). Assets: BTC, ETH, USDT.
  Horizons tested: 1h/4h/6h intraday. Sample period per the extracted text:
  **2017-2023** (exact start/end dates not independently confirmed tonight — flag
  for manual check of the full PDF before relying on it).
- **Gross/net of fees:** Not a costed trading backtest — this is statistical
  return/volatility predictability (regression significance), not a P&L
  simulation. The paper's one *economic* application is an options trade ("selling
  0DTE ETH calls is profitable when exchange net inflow is high"), not a directional
  futures rule — useful as corroborating evidence the underlying signal has real
  economic content, but not directly the strategy the owner wants.
- **What free data verifies it tonight:** Exchange-tagged netflow for BTC/ETH/USDT
  is the bottleneck — CryptoQuant and Glassnode both gate 1h-granularity netflow
  history behind paid tiers; the realistic free route is Dune Analytics
  (community SQL over labeled exchange wallets, free account) or building your own
  exchange-wallet tags from free Etherscan/Tronscan APIs. This is meaningfully more
  engineering effort than any other candidate in this sweep.
- **Most likely kill factor:** 1-hour holding period is fee-hostile — even modest
  taker fees (0.055-0.1%) compound fast at hourly rebalancing, and the paper reports
  statistical significance, not a net-of-cost Sharpe, so it is unknown whether this
  survives realistic round-trip costs at $500-5k retail size. Also, free
  1h-granularity exchange-flow data is the hardest data-access problem of anything
  in this file — may be effectively UNVERIFIABLE-DATA tonight without a paid
  CryptoQuant/Glassnode tier, same failure mode already logged for open-interest
  extremes.
- **Suggested queue entry:** `stablecoin-flow-shorthorizon` — P3 (real, different,
  credible mechanism, but likely data-blocked at 1h granularity for free, and fee
  sensitivity at that frequency is a serious open question) — data plan: try Dune
  Analytics free tier for USDT/ETH exchange-tagged flows before declaring
  UNVERIFIABLE-DATA.

---

## Tier 2 — not genuinely new, but cheap follow-ups worth noting since the mission asked

### 3. Volatility-regime gate on the already-tested trend strategy

The mission specifically asked me to check "vol-regime switching (trade trend only
in high-vol)." Honest verdict: **this is a refinement of `tsmom-daily`
(already MARGINAL), not a distinct mechanism** — it conditions the *existing*
tested signal on an independent state variable rather than introducing new
information. Found one recent paper, arXiv:2602.11708, **"Systematic
Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted
Alpha in Cryptocurrency Markets"** (Feb 2026) — full text is unextractable
(compressed PDF stream) beyond confirming it combines trend-following with
volatility-regime-calibrated position sizing; **could not extract a trustworthy
Sharpe/return/sample-period number from it tonight** despite two fetch attempts —
treat as unverified pending manual PDF read. A second candidate,
**"Adaptive Regime-Based Trading on Bitcoin: Backtesting and Walk-Forward
Evaluation"** (ResearchGate) 403'd on fetch and could not be read. General-web
sources describe vol-filtered momentum improving Sharpe from roughly ~1.0 to ~1.2
in one unattributed comparison, and a separate unattributed snippet claimed a
regime-gated system does quarterly mean -0.16% in low vol vs +0.60%/Sharpe 1.01 in
high vol (2020-2024) — **I could not re-locate or confirm the source URL for
either specific number on a follow-up search, so neither should be trusted or
cited as evidence; flagging them only as a reason the idea is plausible enough for
a cheap in-house test.**
- **Why worth a look anyway:** the project already has a working `tsmom-daily`
  backtest harness and OOS data cached. Adding a realized-vol-percentile gate
  (flat/half-size below the Nth percentile, full trend signal above it) is a
  same-day experiment on top of existing code, not a new research effort.
- **Kill factor if tested:** if plain trend is only MARGINAL (+12.1%/yr, Sharpe
  0.49) with fragile parameters, a vol gate adds a second fragile parameter
  (the percentile threshold) on top of already-fragile trend parameters —
  real overfitting risk on a strategy that's already marginal.
- **Not counted toward the "5 genuinely different mechanisms" ask.**

### 4. Google Trends attention/sentiment + momentum hybrid (BTC only)

Also close to already-tested trend, so not counted as new, but documented since it
has an actual quantified backtest behind it (rare in this sweep). Lukáš Zelieska
& Cyril Dujava, Quantpedia, **"Can Google Trends Sentiment Be Useful as a Predictor
for Cryptocurrency Returns?"** (April 2024) —
https://quantpedia.com/can-google-trends-sentiment-be-useful-as-a-predictor-for-cryptocurrency-returns/
— proprietary 17-keyword sentiment index, monthly rebalance, **sample ~2014-Oct
2023**. Rule: buy BTC when (sentiment change AND price change are both positive)
OR (both negative) — momentum-confirms in one regime, mean-reverts in the other.
Claimed **~3.5x total return vs ~2.1x buy-and-hold**, "better" Sharpe/drawdown,
**transaction costs not stated**. Kill factors: BTC-only, **monthly** rebalance
doesn't fit the owner's minutes-to-days holding window, fees unstated, and the
core mechanism (positive-momentum confirmation) overlaps with the already-tested
(marginal) trend strategy — the "new" part is just a sentiment filter on top.

---

## Ruled out tonight — checked, not credible / not genuinely different / not viable

- **Alt sector/narrative basket rotation (AI / memes / L2 baskets).** Explicitly
  asked for in the brief; searched hard. Everything with an actual quantified
  cross-sectional backtest (a "2+ Sharpe ratio" claim from blog.unravel.finance;
  academic trend-factor/3-factor papers; a Journal of Financial and Quantitative
  Analysis piece on cryptocurrency cross-section) turns out to be **single-name
  cross-sectional momentum — the same mechanism as the project's already-VIABLE
  leader (`xsmom-alts`)**, not a distinct basket/sector-level strategy. Everything
  specifically about *sector* or *narrative* rotation (CoinGecko's 2026 narratives
  piece, CCN's sector scorecard, Gate Learn, Sharpe.ai's sector tracker) is
  qualitative commentary with no independent quantified backtest of trading
  themed baskets as a standalone mechanism. **Verdict: not genuinely different
  from the existing leader; no distinct credible evidence found.**
- **Dispersion trades.** Not implementable by this trader in today's crypto market
  structure — real variance-dispersion trading requires liquid options on many
  single names plus an index, and crypto options liquidity outside BTC/ETH on
  Deribit is negligible (no tradeable single-altcoin options market at retail
  size). What crypto media calls "dispersion" (e.g. blockchain.news's "Altcoin
  Dispersion Season 2025") is qualitative breadth/selectivity commentary, not a
  tradeable strategy. **Verdict: not viable, not a real strategy here.**
- **Whale-wallet / "Smart Money" copy-trading (Nansen).** Real mechanism, real
  vendor research (a 2022-vintage backtest claims a "% of Smart Money addresses
  holding" momentum factor beats ETH benchmark + Monte Carlo) —
  https://www.nansen.ai/research/trading-crypto-with-nansen-smart-money,
  https://docs.nansen.ai/api/backtesting-data/historical-smart-money-positions.
  Disqualified on three grounds: (1) published by the company selling the exact
  paid subscription needed to see the labels — conflict of interest; (2) not
  refreshed for 2024-2026, the freshness bar this hunt needs; (3) Smart Money
  labels/API are a **paid** product, failing the free-data requirement outright.
- **Perpetual long/short-ratio contrarian signal.** Mechanistically this is the
  same crowded-positioning proxy as funding rate, which the project already tested
  and killed (`funding-fade`, DEAD both directions) — long/short ratio and funding
  rate are two measurements of the same crowd-positioning phenomenon, so this is a
  duplicate mechanism, not a new one. Evidence quality was also poor: mostly
  near-duplicate SEO articles from a single content farm (ainvest.com) repeating
  anecdotes ("ratio hit 6.03, then -20%") with no defined backtest; one source
  noted on-chain metrics actually outperform the ratio for direction prediction.
  **Verdict: duplicate of an already-DEAD row.**
- **Options skew / put-call skew as a directional entry filter.** Real, well
  documented mechanism on Deribit (25-delta skew z-score) — see Deribit Insights'
  own research (https://insights.deribit.com/industry/skew-curves-shift-towards-calls/
  and similar). But every source found either (a) backtests trading the skew
  itself as an *options* position (risk-reversal P&L), not a directional futures
  signal, or (b) offers narrative-only "extreme put skew = fear = bottom" framing
  with no quantified test of using it to time BTC/ETH futures entries. **Verdict:
  plausible, unproven for the specific directional-futures use case; would have to
  be built from scratch, not verified from any source found tonight.**
- **Order-flow imbalance / CVD (cumulative volume delta) divergence.** Legitimate
  microstructure mechanism, good holding-period fit (minutes-hours), but every
  source found (Bookmap, BackQuant, Phemex Academy, Gate wiki) is retail
  "how to read this indicator" education with **zero quantified out-of-sample
  backtest**. **Verdict: mechanism plausible, no credible evidence located.**
- **New futures/spot listing-announcement drift.** Already on file from tonight's
  academic sweep (`academic.md` Tier 3 #12, "Binance effect" — decayed/front-run).
  Re-checked fresh for anything new in 2024-2026 specifically; found nothing beyond
  generic backtesting-platform pages and an unrelated equity earnings-drift paper.
  **Verdict: nothing new to add — corroborates the existing decayed verdict.**
- **Classic retail "exchange netflow threshold" claims** (e.g. "inflows >30k BTC
  precede a 5.2% drawdown 65% of the time," "whales added 47k BTC then price rose
  170% in 5 months"). These circulate across Medium/Blofin/Altrady/TradeAlgo-style
  content and could not be traced to any primary, reproducible backtest — they
  read as single-anecdote marketing copy, not evidence. Distinguish this sharply
  from Tier 1 #2 above, which is a real peer-reviewed/cross-indexed paper testing
  a more specific, narrower claim (stablecoin flow, not raw BTC netflow, at
  intraday horizons). **Verdict: the popular retail version is not credibly
  backtested anywhere found tonight.**

---

## Bottom line for the ranked shortlist

Two candidates cleared the bar (genuinely different mechanism + credible
2024-2026 quantified evidence + free-data path): **US institutional demand flow
(ETF flows, verified in real time via Coinbase premium)**, and **stablecoin/ETH
on-chain exchange-flow short-horizon forecasting**. Everything else the brief
specifically asked about — alt-sector/narrative rotation, dispersion trades,
vol-regime switching, and the classic on-chain whale-flow narrative — was checked
honestly and either turned out to be the same mechanism as something already
tested tonight, not implementable in current crypto market structure, or not
backed by any credible quantified source found. No padding added beyond that.
