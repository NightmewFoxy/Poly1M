# Directional Crypto Futures Strategies — Overnight Sweep

**Date:** 2026-07-17 | **Scope:** Directional long/short perps & futures trading only.
Explicitly excluded: staking, passive yield, delta-neutral carry/funding harvesting,
pure arbitrage, market making, airdrop farming. Retail frame: $500–$5,000 capital,
Windows home PC in Malaysia, retail latency (minutes-to-days holding, not HFT),
venues Bybit/OKX/Kraken/KuCoin/Deribit.

## Method note & how to read this

This is a web-research sweep, not a backtest — nothing here has been independently
re-verified against live data yet (that's the point of the "verify tonight" column).
Sourcing quality varies wildly across this space: I hit paywalls and bot-blocks on
several primary academic PDFs (Reading University's repo, SSRN direct PDFs, HSE
conference proceedings, ScienceDirect abstracts, one Springer article all returned
403s / bot-verification walls / undecoded binary to my fetch tool) and had to rely on
search-engine-synthesized summaries and secondary citations for those. Where that
happened I've flagged it explicitly — treat the specific numbers in those spots as
"probably roughly right, re-verify before sizing." I did get full clean extractions
from several sources (Starkiller Capital, Presto Research, briplotnik's Medium
writeup, Quantpedia, CoinGecko, and a few others).

**Credibility tiers used below:**
- **A** — peer-reviewed finance journal / NBER, or a named quant fund publishing
  methodology + numbers they're accountable for (Presto Research, Starkiller Capital).
- **B** — reputable data/research vendor (Kaiko, CoinGecko, Grayscale, Quantpedia)
  or a serious independent quant blogger showing full methodology.
- **C** — retail trading-education sites, SEO content, unattributed indicator
  claims. Treated as "hypothesis, not evidence" — included only because the brief
  asked me to sweep these families exhaustively and be honest about what's actually
  out there (mostly noise).

Every candidate below states gross-vs-net-of-fees explicitly because this is the
single biggest way retail backtests lie — see this project's own
`HISTORY_FINDINGS.md`/`arb_fee_wall.md` precedent: a strategy that looks great
fee-blind can be a loser once 0.06–0.1% taker per side is applied, especially at
high turnover.

---

## TL;DR — ranked candidates (credibility × profitability)

| # | Strategy | Family | Credibility | Profitability verdict |
|---|---|---|---|---|
| 1 | Volatility-managed time-series momentum (BTC/ETH) | 1 | A/B | Likely positive, moderate confidence |
| 2 | Pre-FOMC announcement long drift | 8 | B (contested) | Plausibly positive, low $ ceiling |
| 3 | Intraday time-series momentum, vol-conditional | 1/6 | A | Plausible, needs 2024-26 re-verification |
| 4 | Simple dual-MA / MACD trend following (baseline) | 1 | C/B | Feeds into #1; alone, weak evidence quality |
| 5 | Weekend / day-of-week seasonality long bias | 6 | B (weak journal) | Real but small edge, Sharpe ~0.07 |
| 6 | Academic cross-sectional 3-factor momentum | 2 | A (but rebutted) | Contested — may be statistically illusory |
| 7 | Cross-sectional momentum, cost-modeled backtest | 2 | A | Decayed to negative out-of-sample |
| 8 | Funding-rate cross-sectional decay factor | 3 | A | Good gross Sharpe, fee-fatal at retail |
| 9 | BTC-beta-neutral residual mean reversion | 2/9 | B (single source) | Plausible but execution-heavy, borderline in-scope |
| 10 | CPI announcement drift | 8 | B | **Debunked** — no consistent effect |
| 11 | Funding-rate extreme-value contrarian fade | 3 | A/C mixed | **Mostly debunked** at single-asset level |
| 12 | Liquidation-cascade capitulation mean reversion | 4 | C (+1 tangential A) | Unquantified — narrative only |
| 13 | Open-interest quadrant / CVD divergence | 5 | C | Unquantified — blog-level only |
| 14 | CME weekend futures gap-fill | 6 | C | **Regime-broken** — 24/7 CME launched May 2026 |
| 15 | BTC→altcoin lead-lag rotation | 7 | A (wrong horizon) | Real effect is HFT-only; retail horizon is narrative |

---

## 1. Volatility-managed (risk-managed) time-series momentum — BTC/ETH daily

**Entry/exit rule:** Standard construction (Barroso–Santa-Clara risk-managed
momentum, adapted to crypto by the sources below): rank/sign each asset's recent
trend (formation window on the order of 1–4 weeks of daily returns), then **size the
position inversely to trailing realized volatility** so that each position targets a
constant ex-ante volatility budget (commonly ~20–40% annualized in the crypto
literature), rebalanced daily or weekly. Long when trend positive and vol-scaled
size > 0, short (or flat) when negative. This is functionally "trade the trend, but
downsize hard exactly when the market is most dangerous" — the opposite of what
naive fixed-size trend followers do.

**Claimed performance:** Ao Yang (2025), *"Cryptocurrency Market Risk-Managed
Momentum Strategies,"* Finance Research Letters — risk-managing conventional
crypto momentum lifted **average weekly returns from 3.18% → 3.47%** and
**annualized Sharpe from 1.12 → 1.42**. Notably the paper finds the improvement in
crypto comes from *higher returns*, not tail-risk mitigation the way it does in
equities — crypto momentum apparently doesn't suffer the same prolonged
"momentum crash" dynamic once risk-managed. Independently, an unaffiliated quant
blogger (briplotnik, June 2025, Binance data 2017–present) reports a
volatility-filtered momentum variant at **Sharpe ≈1.2** vs ≈1.0 for the raw z-score
momentum version, and a combined momentum + mean-reversion blend at **Sharpe
1.71, 56% annualized, t-stat 4.07**, explicitly stating "realistic fills, slippage,
and costs were integrated." Quantpedia's simplest version (D1H1 MACD filter +
trailing stop, Gemini data Dec 2018–Nov 2025) reaches **Sharpe 1.07, Calmar 0.87**
— consistent directionally but the gap to Yang's/briplotnik's numbers shows how
much the risk-management layer matters.
[Ao Yang FRL abstract](https://www.sciencedirect.com/science/article/abs/pii/S1544612325011377) ·
[XJTLU mirror](https://scholar.xjtlu.edu.cn/en/publications/cryptocurrency-market-risk-managed-momentum-strategies/) ·
[briplotnik Medium](https://medium.com/@briplotnik/systematic-crypto-trading-strategies-momentum-mean-reversion-volatility-filtering-8d7da06d60ed) ·
[Quantpedia multi-timeframe trend](https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/)

**Gross or net:** Mixed by source — Yang's abstract doesn't specify cost treatment
(I could not get past the ScienceDirect 403 to check); briplotnik explicitly claims
costs/slippage are included; Quantpedia's number is silent on costs (treat as
gross-ish). **Re-verify cost assumptions before trusting the Sharpe number.**

**Verify tonight with free data:** `data.binance.vision` daily/hourly klines for
BTCUSDT & ETHUSDT (spot or perp) back to 2020+, zero auth needed. Compute
trailing realized vol (e.g. 20-day stdev of daily returns), a simple trend signal
(e.g. sign of 20–50 day return), vol-scale the position, and walk it forward —
this is a one-evening backtest in pandas.

**$1–5k fit & kill factors:** Excellent fit — single-instrument (BTC, maybe +ETH),
no minimum-notional problem, daily/weekly rebalance keeps turnover low enough that
0.06–0.1% taker fees are a minor drag, not fatal. Kill factors: (a) crypto-specific
"no momentum crash" claim in Yang (2025) is a single paper — the older, better
established finding (see #6/#7) is that crypto momentum SILVER a severe crash
happened (-255% at end of 2020, 3x larger than the worst equity momentum crash,
per a ScienceDirect tail-risk study found in this sweep) — the two claims are in
tension and should make you size conservatively regardless of which is right;
(b) parameter/lookback choice is under-specified in the secondary sources I could
access — you must pick your own lookback/vol-target and there's real risk of
overfitting to 2020-2024 if you don't hold out 2025-2026; (c) crypto trend
strategies broadly are having a rough 2025 in the analogous traditional-CTA space
(SG Trend Index down ~9% YTD through April 2025) — regime risk is real, trend
following is not a free lunch in any asset class right now.

---

## 2. Pre-FOMC announcement long drift

**Entry/exit rule:** Go long BTC roughly 24 hours before the scheduled FOMC
statement release (2:00pm ET on FOMC decision day) — i.e., enter near the prior
day's close — and exit/flatten before or at the announcement itself, since the
positive drift is specifically a *pre*-announcement phenomenon. A more aggressive
version flips flat-to-short across the announcement window itself given the
documented same-day reversal (below).

**Claimed performance:** Search-engine-synthesized findings across academic
literature on Bitcoin's FOMC reaction (a mix of Pyo & Lee (2020), *"Do FOMC and
macroeconomic announcements affect Bitcoin prices?,"* Finance Research Letters 37,
and a 2026 KSE University master's thesis by Illia Nazaruk) report **Bitcoin rising
~0.96% the day before FOMC announcements, then falling ~1% on the announcement
day itself** — consistent with the well-established equity-market "pre-FOMC
announcement drift" (Lucca & Moench, NY Fed, 2015: pre-FOMC returns account for
**>80% of the entire US equity risk premium since 1994**, a genuinely
famous/robust finding in traditional finance that gives this crypto analog real
prior plausibility). **Important caveat: I could not independently verify the
0.96%/-1% figures against primary full text** — both the Pyo & Lee ScienceDirect
page and the Nazaruk thesis PDF failed to render through my fetch tool (paywall /
raw-binary issues), so this number comes from a secondary synthesis, not a number
I read myself off a table. Re-derive it from data before trusting it.
[Pyo & Lee, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S154461231930159X) ·
[Nazaruk thesis PDF](https://kse.ua/wp-content/uploads/2026/05/illia-nazaruk_268722_assignsubmission_file_nazaruk_final_thesis.pdf) ·
[Lucca & Moench, NY Fed](https://www.newyorkfed.org/research/staff_reports/sr512.html)

**Gross or net:** Not stated in any source found — this is a raw price-drift
measurement, not a fee-aware backtest. With only 8 trades/year the fee drag is
trivially small regardless (see below).

**Verify tonight with free data:** FOMC meeting dates are public and free
(federalreserve.gov calendar, or just hard-code the ~8 dates/year). Pull BTC daily
closes from `data.binance.vision` and compute the return from close(FOMC day − 1)
to close(FOMC day) and from close(FOMC day) to close(FOMC day + 1) across every
FOMC date 2020–2026. This is a 30-minute verification, trivially cheap to do before
risking anything.

**$1–5k fit & kill factors:** Great capital fit (one BTC perp position, sized
however you like) and the lowest effort/complexity of anything on this list — no
automation strictly required, you could place this by hand 8x/year. Kill factors:
(a) tiny sample — only ~8 events/year, so even years of data is only a few dozen
independent observations, meaning the "statistical significance" claimed by any
single paper is inherently fragile and one or two bad prints will look like the
effect broke; (b) low frequency caps total $ contribution — this cannot be a
primary strategy, only a supplementary low-risk overlay; (c) the *other* Bitcoin/FOMC
paper this sweep found (CoinGecko's CPI study, and the "FOMC days themselves do
not generate significant abnormal returns" line from an earlier academic summary)
suggests the announcement-*day* effect (as opposed to pre-announcement drift) is
NOT reliable — don't confuse the two.

---

## 3. Intraday time-series momentum, conditional on high volatility

**Entry/exit rule:** Shen, Urquhart & Wang (2022), *"Bitcoin intraday time-series
momentum,"* Financial Review 57(2):319–344 — the first half-hour return of the
(UTC) day positively predicts the last half-hour return, **but only on days with
high realized volatility**; on medium/low-volatility days there's no such
relationship. Practical rule: measure the sign/magnitude of BTC's first 30-minute
return each day; if the day's realized volatility (e.g., vs. a trailing average) is
elevated, take a position in that direction sized to capture the last-30-minute
window, otherwise stand aside.

**Claimed performance:** Published in a legitimate finance journal (Financial
Review) — this is one of the more credible single findings in this whole sweep.
**I was blocked from the full-text PDF by both the Reading University repository
(Anubis bot-wall, "access denied") and a raw-binary decode failure on retry**, so I
have the abstract-level finding but not the exact quantified return/Sharpe numbers,
nor the precise definition of "high volatility day" (percentile cutoff), nor
confirmation of the exact entry timing (does the position open at the START of the
last-30-min window, or is it held continuously from the first 30 minutes?). Sample
period is pre-2021 based on the 2021 revision date on the working paper — **this
needs re-running on 2024-2026 data before you trust it in the current market
structure** (spot ETFs, very different liquidity/participant mix now).
[Wiley (paywalled)](https://onlinelibrary.wiley.com/doi/pdf/10.1111/fire.12290) ·
[Reading repo (bot-blocked for me)](https://centaur.reading.ac.uk/100181/)

**Gross or net:** Unknown — could not access.

**Verify tonight with free data:** `data.binance.vision` 1-minute or 5-minute
klines for BTCUSDT, enough to build the first-30-min / last-30-min return series
and a volatility filter, across several years. This is fully replicable tonight but
will take longer than the daily-bar strategies above (more data wrangling).

**$1–5k fit & kill factors:** Fits fine capital-wise (single instrument). Kill
factors: (a) this needs to run automated (checking a 30-minute window daily near a
specific UTC cutoff) — not a "check your phone once a day" strategy, it needs a
scheduled script; (b) intraday means more fills relative to $ at risk than the daily
version, so 0.06-0.1% taker fees matter more — must size the edge against realistic
costs, which I can't do without the actual magnitude numbers; (c) genuinely unknown
whether "high volatility day" intraday momentum survived the 2021→2026 change in
market structure (ETF flows, more institutional participation) — this is the
biggest open question mark on this candidate.

---

## 4. Simple dual-moving-average / MACD trend following (the "dumb baseline")

**Entry/exit rule:** Two variants found: (a) 20-day/100-day moving-average
crossover — long when fast MA > slow MA; (b) Quantpedia's MACD(12,26,9) on 1H bars,
filtered to only take trades in the direction of the daily-timeframe MACD trend
("D1H1"), with either a fixed 1-bar hold or a trailing-stop exit ("close at the
close of the first negative bar").

**Claimed performance:** A retail-strategy site (QuantifiedStrategies.com — I could
not get past its bot-verification wall to confirm the full page, so this is
secondhand via search snippet) claims the 20d/100d crossover produced **116%
annualized return, Sharpe 1.7** since 2012, versus buy-and-hold, with the best
Sharpe clustering around a 10–30 day fast MA. Quantpedia's own MACD variants
(full data pulled successfully, Dec 2018–Nov 2025, Gemini exchange): raw MACD
crossover only **4.6% annualized, Sharpe 0.33** (barely better than nothing);
adding the daily-trend filter improves it to **6.6% annualized, Sharpe 0.80, max
drawdown -12.4%** (vs -23.9% unfiltered); adding a trailing stop gets to
**Sharpe 1.07, Calmar 0.87**. Compare all of these against simple buy-and-hold
Bitcoin over the same window (**60%+ annualized but with an 80% drawdown**) — the
real pitch of trend-following here is drawdown control, not return maximization.
[Quantpedia](https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/) ·
[QuantifiedStrategies (bot-walled for me)](https://www.quantifiedstrategies.com/trend-following-and-momentum-on-bitcoin/)

**Gross or net:** Quantpedia's numbers appear to be **gross of fees/slippage** (no
disclosure of cost treatment found on the page). The QuantifiedStrategies 116%/1.7
number should be assumed gross and probably curve-fit — that class of site
routinely publishes fee-blind, non-out-of-sample backtests; treat as marketing, not
evidence, until independently reproduced.

**Verify tonight with free data:** Trivial — daily BTC closes from
`data.binance.vision`, compute two SMAs, backtest the crossover. Do this before
#1's more sophisticated version so you have a baseline to compare the
volatility-scaling uplift against.

**$1–5k fit & kill factors:** Fine capital fit, this is the easiest strategy on the
entire list to implement (a spreadsheet could do it). Kill factor: this is the
*least credible* evidence quality on the list for something ranked this high — I'm
including/ranking it mainly because it's the natural on-ramp to #1 (you need the
baseline before the upgrade) and because Quantpedia's numbers, while unimpressive
in raw Sharpe, at least came from a source that disclosed its full methodology and
drawdown numbers rather than cherry-picking a headline return.

---

## 5. Weekend / day-of-week seasonality — long bias into weekends

**Entry/exit rule:** Two related findings: (a) a 7-day-momentum strategy applied
specifically on weekends outperforms the same strategy applied on weekdays; (b) at
hourly resolution, essentially all of the "day-of-week" anomaly collapses into a
single specific window: **Sunday 23:00–00:00 UTC**, when US retail re-enters the
market — meaning daily-bar analyses that credit "Monday" are actually smearing a
Sunday-night effect across the wrong calendar day.

**Claimed performance:** *"The Weekend Effect in Crypto Momentum"* (ACR Journal,
10 coins incl. BTC/ETH + 8 alts, Jan 2020–Apr 2025, 1,672 days): weekend mean daily
return **0.26% vs weekday 0.14%** for BTC/ETH (**+86% relative**), and for altcoins
like DOGE **0.52% vs 0.21%** (**+148% relative**); BTC weekend momentum
significant at **p=0.016**, DOGE at **p<0.001**. A $1 investment 2020–2025 grows to
**$1.85 weekday-only vs $2.47 weekend-only** for BTC. But the risk-adjusted size is
small: **weekend Sharpe only 0.067–0.072** vs weekday 0.029–0.040 — statistically
real, economically modest. Separately, mlquants (Substack, methodology-focused
critique of prior day-of-week literature) argues the entire effect is really one
specific hour (Sunday 23:00-00:00 UTC) and that daily-bar seasonality studies are
mis-specified.
[ACR Journal](https://acr-journal.com/article/the-weekend-effect-in-crypto-momentum-does-momentum-change-when-markets-never-sleep--1514/) ·
[mlquants](https://mlquants.substack.com/p/are-day-of-the-week-effects-in-cryptocurrencies)

**Gross or net:** Not addressed in either source — both are raw-return studies,
not fee-aware backtests.

**Verify tonight with free data:** `data.binance.vision` hourly or daily klines,
trivial to bucket by day-of-week/hour-of-week and compare mean returns tonight.

**$1–5k fit & kill factors:** Good capital fit (single-instrument, low turnover —
you're just choosing WHEN to hold your existing trend/momentum position more
aggressively, not a separate trading system). Kill factors: (a) **credibility
concern on the primary source** — "Advances in Consumer Research" (ACR Journal) is
a marketing/consumer-psychology outlet, not a finance journal; a quantitative
crypto-momentum paper appearing there is an odd fit and should raise your
eyebrow about peer-review rigor even though the reported statistics look clean;
(b) a separate, more conventional finance-journal study cited in this same sweep
("Revisiting seasonality in cryptocurrencies," Finance Research Letters 2024)
concluded flatly that **"robust return abnormalities are not found, only lower
trading activity on weekends"** — i.e., there is a real, credible academic paper
directly contradicting the ACR weekend-momentum finding; (c) even if real, Sharpe
~0.07 is a very small edge to trade on its own — this is a tilt/overlay, not a
standalone strategy.

---

## 6. Academic cross-sectional 3-factor momentum (Liu–Tsyvinski–Wu)

**Entry/exit rule:** Liu, Tsyvinski & Wu, *"Common Risk Factors in Cryptocurrency,"*
Journal of Finance 77(2):1133-1177 (2022; NBER WP 25882, 2019) — weekly-rebalanced
long-short portfolio, long past-return winners / short past-return losers across
a broad cryptocurrency universe, one of ten factor-portfolios tested, all of which
the paper claims are subsumed by a 3-factor (market, size, momentum) model.

**Claimed performance:** The momentum strategy generates **statistically
insignificant weekly excess returns (~0.6%) in the below-median-size group but a
statistically significant ~4.2%/week in the above-median-size group** (per
secondary summary — I could not pull exact numbers from the abstract page itself).
This is the single most prestigious citation in this whole sweep — Journal of
Finance is a top-3 finance journal.
[NBER](https://www.nber.org/papers/w25882) ·
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3379131) ·
[Yale Econ summary](https://economics.yale.edu/research/common-risk-factors-cryptocurrency)

**⚠ Directly contested by a more recent, methodologically-focused paper:**
Grobys & Shahzad, *"Cryptocurrency Momentum: Is It an Illusion?,"* International
Journal of Finance & Economics (2024/2025) — argues the realized variance of
crypto momentum portfolio returns follows a **power law with infinite theoretical
variance**, which means **"t-statistics or Sharpe ratios do not exist"** for the
strategy in a statistically rigorous sense — i.e., the momentum premium reported
by papers like Liu-Tsyvinski-Wu may not be a stable, tradeable property of the
data at all, but an artifact of applying standard finite-variance statistics to a
fat-tailed process. This is about as strong a "brutally skeptical" academic
rebuttal as exists in this literature.
[Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/ijfe.70036) ·
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4633099)

**Gross or net:** Gross — gestures toward "sizable and statistically significant
excess returns" with no fee/borrow-cost treatment visible in what I could access.
Shorting altcoins at retail scale also has practical borrow/margin-availability
issues on perps that a pure academic long-short paper wouldn't model.

**Verify tonight with free data:** Hard to fully replicate tonight — needs a broad
cross-sectional universe (dozens of coins) with clean historical daily prices;
`data.binance.vision` covers Binance's listed pairs (large but not the paper's full
universe), good enough for a partial replication.

**$1–5k fit & kill factors:** Poor at this capital level for genuine replication —
a properly diversified long-short cross-sectional book needs enough coins per side
that per-leg notional falls below efficient sizing once you're spreading $1-5k
across 10-20+ legs. Kill factors: (a) the illusion-critique above is a serious,
recent, specific statistical objection, not generic skepticism — take it
seriously; (b) even setting that aside, this is a research-grade academic
factor, not a retail-ready trading system — no specific venue/execution guidance.

---

## 7. Cross-sectional momentum, cost-modeled practitioner backtest (Starkiller Capital)

**Entry/exit rule:** Rank assets by trailing 30-day return, long-only top quintile,
7-day holding period, weekly rebalance (Thursdays 00:00 UTC). Universe: coins on
≥3 exchanges (≥1 CEX) with ≥$5M average daily volume on at least half of the prior
30 days.

**Claimed performance:** Starkiller Capital (Leigh Drogen's crypto quant fund — a
real institutional player, not a blog) — full sample Apr 2018–Nov 2022: top
quintile **37.8% annualized** vs equal-weighted universe **11.7%** vs BTC **28.7%**,
but **max drawdown 75%+**. Critically, they split in-sample vs out-of-sample:
**in-sample (Apr 2018–Mar 2021) top quintile 69.17% annualized**; **out-of-sample
(Mar 2021–Nov 2022) top quintile -2.35% annualized** — the strategy's edge did not
survive out of sample. With a modeled 50bps average trading cost, returns drop a
further **30 points in-sample / 12 points out-of-sample**.
[Starkiller Capital](https://www.starkiller.capital/post/cross-sectional-momentum-in-cryptocurrency-markets)

**Gross or net:** Both shown — gross headline numbers AND a specific cost
sensitivity (50bps average cost assumption), which is unusually transparent for
this space and raises my trust in the source even though the result is negative.

**Verify tonight with free data:** Partially replicable via `data.binance.vision`
(volume + price filters, weekly rebalance, quintile sort) — a good weekend project,
maybe not a single-evening one given the universe-construction work.

**$1–5k fit & kill factors:** Same capital-fit problem as #6 (needs many legs).
Kill factor is the headline finding itself: **this is the most rigorously
documented cross-sectional momentum backtest found in this entire sweep, and it
shows the edge decayed to negative out-of-sample once the sample extended past
March 2021.** I'm ranking it above the purely-academic #6 specifically because its
honesty about decay is worth more than an untested academic claim — this is
closer to "here's a strategy that stopped working, know that before you build it"
than a recommendation to trade it.

---

## 8. Funding-rate cross-sectional decay-linear factor (stat-arb)

**Entry/exit rule:** Presto Research (real crypto prop-trading/market-making firm)
tested a cross-sectional signal: `scale(indneutralize(decay_linear(funding_rate,
24) − decay_linear(funding_rate, 6), IndClass.universe), 2e6)` — i.e., a
fast-minus-slow decayed funding-rate momentum/mean-reversion factor, cross-
sectionally neutralized by industry class, applied to the top 50 liquid
USDT-margined Binance perps on 5-minute bars.

**Claimed performance:** "Highly favorable annualized returns and Sharpe ratio"
(exact numbers not disclosed in what I could extract) — **but Presto themselves
flag the fatal flaw: "daily turnover is extremely high for inclusion in a
statistical arbitrage strategy,"** and the backtest explicitly **does not include
any transaction costs**. Separately, the same piece directly tested whether
single-asset funding-rate *changes* predict *future* price changes and found
**"near-zero correlation... zero R-squared and the large p-value... the model has
no prediction power"** for 7-day-ahead returns — funding rate changes DO
correlate strongly with *concurrent* price changes (R²=12.5%, p=1.91e-115) but
that's describing the present, not forecasting the future.
[Presto Research](https://www.prestolabs.io/research/can-funding-rate-predict-price-change)

**Gross or net:** Explicitly **gross** — "not considering any transaction cost,"
per Presto's own writeup. This is one of the most honest cost disclosures in the
whole sweep, precisely because it's a negative/cautionary finding.

**Verify tonight with free data:** Binance Futures REST API
(`fapi.binance.com/fapi/v1/fundingRate`) gives full funding-rate history for free;
combine with `data.binance.vision` price data. The single-asset predictability
regression (funding change → forward 7-day return) is a very quick test to run
tonight and is the most valuable thing to check first, since it's the cleanest
falsification of the "funding rate predicts price" folk claim.

**$1–5k fit & kill factors:** Poor fit — this needs a 50-asset universe and very
high turnover (5-minute rebalancing cadence) to realize the "highly favorable"
gross Sharpe; at $1-5k the per-leg notional would be tiny and fees would dominate
long before the signal's raw edge could offset them. This is the textbook case of
"real signal, retail-un-tradeable" — the exact same shape as this project's own
finding on Polymarket binary-merge arb (`arb_fee_wall.md`): the edge exists
gross, dies net of realistic costs.

---

## 9. BTC-beta-neutral residual mean reversion on altcoins

**Entry/exit rule:** Regress each altcoin's returns on BTC over a rolling 180-day
window, isolate the coin-specific (idiosyncratic/residual) return, and trade
mean-reversion in the Z-scored residual (long oversold residuals, short overbought
ones), normalized/balanced across the book.

**Claimed performance:** briplotnik (independent quant blogger, full methodology
disclosed, Binance data 2017-present) reports **Sharpe ≈2.3**, described as
"particularly strong post-2021" — the same writeup found momentum (#1/#4) worked
better pre-2021 and this residual-reversion approach took over as the better
performer in the post-2021 regime. A 50/50 blend of this with momentum reached
**Sharpe 1.71, 56% annualized return, t-stat 4.07**, claimed net of realistic
fills/slippage/costs.
[briplotnik Medium](https://medium.com/@briplotnik/systematic-crypto-trading-strategies-momentum-mean-reversion-volatility-filtering-8d7da06d60ed)

**Gross or net:** Claimed net (costs/slippage "integrated") but this is a single
unaffiliated source with no independent replication found — treat the exact Sharpe
number skeptically pending your own verification.

**Verify tonight with free data:** `data.binance.vision` daily data for BTC +
altcoin universe, rolling OLS beta, residual Z-score — very doable tonight for a
handful of large-cap alts (ETH, SOL, etc.), though the "post-2021 particularly
strong" claim specifically needs 2022-2026 data to check, which is exactly the
window you have.

**$1–5k fit & kill factors:** **Scope caveat: this sits closer to the line the
owner asked to exclude.** It's not delta-neutral funding-carry and it's not
market-making, but it IS a market-neutral-*style* relative-value construction
(hedged vs. BTC beta) rather than a naked directional bet — the P&L driver is
"this coin's price versus what its beta to BTC implies," which is a genuine
directional bet on each coin's residual, so I've kept it in, but flag it for the
owner to judge on intent. Practical kill factors: (b) needs a multi-leg book
(BTC hedge + several altcoin residual positions) — same minimum-notional/fee-drag
problem as #6-8 at $1-5k, worse because you're also paying to maintain the BTC
hedge leg; (c) single non-academic source, unreplicated.

---

## 10. CPI announcement drift — DEBUNKED, included for completeness

**Entry/exit rule:** The naive hypothesis: trade BTC directionally around monthly
US CPI prints, expecting a consistent reaction (e.g., long into cooler-than-expected
prints).

**Claimed performance:** CoinGecko Research (Jan 2022–Oct 2024): **"Inflation rate
reports (CPI) don't significantly affect the Bitcoin price"** — inconsistent
correlation. Example: May 2024 CPI cooled from 3.5%→3.4% annualized and BTC rose
7.02% the next day (consistent-ish), but Mar→Apr 2022 CPI dropped from 8.5%→8.3%
and **BTC fell -11%** (opposite of the naive expectation). Their conclusion: Fed
balance-sheet/hiking-cycle policy dominates any direct CPI-print effect. This
matches the "FOMC days themselves do not generate significant abnormal returns...
news related to GDP and CPI shows no statistically significant relationship with
Bitcoin returns" line found from an independent academic summary earlier in this
sweep — two independent sources agreeing there's no reliable edge here.
[CoinGecko](https://www.coingecko.com/research/publications/cpi-announcements-affect-bitcoin-price)

**Gross or net:** N/A — there's no consistent effect to net costs against.

**Verify tonight with free data:** BLS CPI release calendar is free/public;
`data.binance.vision` for BTC prices around each date. Cheap to confirm the null
result yourself in under an hour, which might be worth doing once just to convince
yourself not to bother building this.

**$1–5k fit & kill factors:** N/A. **Don't trade this.** Included specifically
because the brief asked for a brutally skeptical sweep of family #8, and "the
obvious guru-content idea doesn't actually work" is itself a useful, actionable
finding — it tells you not to waste development time here and to distinguish CPI
(no effect) from FOMC (real pre-drift, see #2) even though both feel like
"the same kind of trade" superficially.

---

## 11. Funding-rate extreme-value contrarian fade — mostly debunked

**Entry/exit rule:** The popular retail version: when funding rate (annualized)
exceeds some extreme threshold (~30-50%+ APR) sustained for multiple days, fade the
crowded side (short into extreme-positive funding, long into extreme-negative),
on the theory that crowded leveraged positioning precedes liquidation-driven
reversals.

**Claimed performance:** This is almost entirely retail-blog/content-mill
territory (multiple similarly-themed ainvest.com articles, Phemex/Altrady/
Zipmex educational pages) asserting things like "historical extremes like 6.03
(bullish) and 0.44 (bearish) long/short ratios have reliably preceded 20%
corrections" **with no backtest, no sample period, no statistical test cited
anywhere I could find.** Set against this: Presto Research's clean regression
(see #8) found **near-zero, statistically insignificant predictive power** from
funding-rate changes on 7-day-forward single-asset returns. Most damning: **an
empirical counter-example found in this sweep — Bitcoin's aggregate funding rate
was positive on all but 26 days of all of 2024, while BTC more than doubled and
hit a new all-time high in December 2024.** A naive "fade sustained positive
funding" strategy would have been short-biased through nearly the entire best
year of the cycle. "Extreme funding precedes corrections" is a survivorship-biased
story people tell about the *specific* corrections that did happen, not a
forward-looking edge.

**Gross or net:** N/A given the above — there's no credible net edge established to
begin with.

**Verify tonight with free data:** Binance/Bybit funding-rate history APIs (free)
+ forward BTC/alt returns. Trivial to run the "does extreme funding predict the
next N days' return" regression yourself tonight — I'd suggest doing exactly this
before writing off or trusting either side of this debate, since the retail-blog
claims and the Presto null result can't both be fully right and only your own
regression will resolve it for your exact universe/thresholds.

**$1–5k fit & kill factors:** Capital fit would be fine (single-instrument) IF the
signal worked. Kill factor is the evidence itself: credible source (Presto) found
no single-asset predictive power; the sources claiming otherwise are uniformly
low-credibility with zero disclosed methodology.

---

## 12. Liquidation-cascade / stop-hunt mean reversion (buying capitulation wicks)

**Entry/exit rule:** Wait for a liquidation cascade to visibly exhaust (spike in
forced-selling volume that fails to push price meaningfully lower / large limit
bids absorbing the flow), then take a long position betting on the V-shaped
snapback.

**Claimed performance:** **No rigorously quantified backtest found anywhere in
this sweep** despite specifically searching for one — every source (Amberdata,
Mudrex, XT Exchange/Medium, Pintu Academy, bit.com) describes the *mechanism*
qualitatively (cascades, "liquidation hunting," reflexive feedback loops) with
zero win-rate, magnitude, or time-window statistics. The one adjacent academic
paper — Cheng, Deng, Wang & Yu (2021), *"Liquidation, Leverage and Optimal Margin
in Bitcoin Futures Markets,"* Applied Economics, BitMEX data — establishes a
**base rate** (daily forced liquidations average 3.51% of outstanding longs and
1.89% of outstanding shorts, with liquidated traders averaging ~60x leverage) but
does **not** test liquidations as a forward-return-predictive signal. The
October 10-11, 2025 event (**$19B liquidated in ~24h, 70% of $9.89B in forced
liquidations happened in just 40 minutes — a 14.6x-86x acceleration vs. the
surrounding rate**) is a vivid, real, well-documented case study of the mechanism
existing, but one event is not a backtest.
[Cheng et al. (arXiv)](https://arxiv.org/abs/2102.04591) ·
[insights4vc on Oct 2025](https://insights4vc.substack.com/p/inside-the-19b-flash-crash) ·
[CoinGecko Oct 10 explainer](https://www.coingecko.com/learn/october-10-crypto-crash-explained)

**Gross or net:** N/A — no quantified strategy exists to apply costs to.

**Verify tonight with free data:** Binance/Bybit provide free real-time
liquidation-order-stream endpoints (not deep history via free tier, but you can
start logging tonight) and free OHLCV around known past cascade dates (e.g. Oct 10
2025, various 2024 dates) via `data.binance.vision` 1-minute bars — you could build
your own event study of "N-minute/hour forward return after a liquidation-volume
spike" from scratch, which as far as I can tell nobody has published rigorously.
That itself is notable: this is a **credible-sounding, widely-repeated retail
narrative with a real underlying mechanism, that nobody publishing has actually
backtested** (or if they have, it's proprietary and not shared) — the most
interesting "do the work yourself" opportunity on this list precisely because
it's underexplored, but also the least evidenced pick in this entire sweep.

**$1–5k fit & kill factors:** Capital fit fine if it worked (single instrument,
event-driven). Kill factor: zero quantified evidence — this is pure hypothesis
until you or someone else backtests it.

---

## 13. Open-interest quadrant / long-short-ratio / CVD divergence signals

**Entry/exit rule:** The "four-quadrant" framework: cross price direction (up/down)
against OI direction (up/down) — price↑+OI↑ = new longs entering (healthy trend);
price↑+OI↓ = short-covering rally (unhealthy, fade candidate); price↓+OI↑ = new
shorts entering (healthy downtrend / "often the bottom is in" per one source);
price↓+OI↓ = long liquidation/capitulation. Overlay taker buy/sell ratio (CVD) as a
confirming/diverging signal.

**Claimed performance:** Entirely blog/indicator-page level (CryptoCred Medium,
CoinGlass wiki, TradingView indicator description pages, Bikotrading Academy).
One TradingView indicator page claims **"the Q4 long signal has shown statistically
validated edge in backtesting; the Q3 short signal has not — markets tend to
continue higher after short-cover exhaustion, making Q3 short worse than a coin
flip"** — but no actual numbers, sample, or methodology accompanies this claim; it
reads as an indicator-seller's pitch, not evidence. **No credible academic or
named-fund source in this sweep quantifies OI/CVD signals as forward-return
predictors.** The closest thing to real evidence is tangential: an "informed
trading" paper found sell-dominated informed order flow "significantly led to
decreased concurrent Bitcoin returns" and buy-dominated flow "related positively"
— but that's contemporaneous, not predictive, and I could not access the full
paper to check methodology or journal quality.
[TradingView OI quadrants](https://www.tradingview.com/script/D5187oQf-Open-Interest-Price-Quadrants-GBB/)

**Gross or net:** N/A.

**Verify tonight with free data:** Binance/Bybit futures OI history endpoints are
free but typically **limited to ~30 days of lookback** on the free tier — a real
constraint for backtesting this properly; you'd need to start logging yourself
going forward, or find a paid history source (CoinGlass/CryptoQuant paid tiers, out
of scope for a free overnight check). Taker buy/sell volume is available similarly
limited. This is the hardest candidate on the list to verify tonight specifically
because of free-data history limits, not analytical difficulty.

**$1–5k fit & kill factors:** Capital fit fine if real. Kill factor: essentially
no rigorous quantified evidence exists in what I could find — treat as an
untested hypothesis, same caveat as #12, but with the added practical problem
that free historical OI/CVD data is thin, making it slower to even test properly.

---

## 14. CME weekend futures gap-fill — regime-broken as of this year

**Entry/exit rule:** Historically: when CME Bitcoin futures reopen Sunday at a
price different from Friday's close (created by CME's weekend closure), fade the
gap on the expectation it fills as liquidity normalizes Monday.

**Claimed performance:** Reported fill rates vary wildly by source — 68%, ~77%,
70-90%, and one outlier claiming 98.75% (79/80 gaps) — this spread itself is a red
flag about methodology consistency across the retail sources reporting it (Bitget,
Coinfomania, various crypto-news sites; no academic source found). Gap size
matters: sub-$700 gaps reportedly filled at 92% within 30 trading days per one
2020-2025 dataset.

**⚠ This strategy's underlying mechanism no longer exists.** CME moved Bitcoin
(and other crypto) futures to **24/7 trading on May 29, 2026** — confirmed via a
Yahoo Finance piece on Bitcoin's **first gap-free Monday (June 1, 2026)**, which
eliminated the weekend-closure pattern that had existed since December 2017.
Today's date in this sweep is **2026-07-17**, i.e. this regime change happened
**seven weeks ago** — no new CME gaps are forming anymore. Legacy gaps on the
chart may still exert some pull, but the entire generative mechanism (weekend
market closure creating a spot/futures dislocation) is gone.
[Yahoo Finance — first gap-free Monday](https://finance.yahoo.com/markets/crypto/articles/bitcoin-first-cme-gap-free-174649486.html)

**Gross or net:** N/A given the above.

**Verify tonight with free data:** Moot for future trades. You could verify the
*historical* fill-rate claim via free CME continuous-contract data (e.g. Yahoo
Finance `BTC=F`), but there's little point building this now.

**$1–5k fit & kill factors:** **Dead strategy, don't build it.** Additional
practical kill factor even setting aside the regime change: CME itself isn't
reachable through any of the owner's listed venues (Bybit/OKX/Kraken/KuCoin/
Deribit) — you'd need a separate CME futures broker relationship, and the
closest retail-accessible proxy (trading the equivalent weekend dislocation on a
perpetual, which never closes and thus never truly "gaps" the same way) is a
different, unvalidated strategy, not this one.

---

## 15. BTC → altcoin lead-lag rotation

**Entry/exit rule:** The retail narrative: Bitcoin moves first, capital rotates
into ETH and then further out the risk curve into altcoins with a lag, so you buy
alts after confirming a BTC move.

**Claimed performance:** The only rigorously quantified lead-lag study found in
this sweep (independent quant blogger sotofranco.dev, 1ms/10ms/100ms/1000ms bins,
Jan 2025 + full-year-2025 Binance spot data, 500k+ windows, z-tests) found a real,
statistically unambiguous, **direction-reversing** effect: **below ~15-20ms, ETH
leads BTC; above ~15-20ms (from 100ms on up), BTC leads ETH** (z=38.17 at 100ms
full-year). This is genuinely rigorous — but **entirely inside HFT territory**.
The author's own conclusion, which I fully endorse: **"zero tradeable value for
retail or minute-to-hour timeframes... by the time retail traders execute orders
(seconds minimum), these microstructure effects vanish into noise."** At longer
horizons, the "BTC leads early bull cycle, alts rotate in later" story is
qualitative/narrative across every source found (market commentary, not
backtests); one weak quantified data point — daily-lagged BTC values showing
"positive significant interactions with ETH, ADA, BNB" but not XRP, from an
obscure conference paper — doesn't specify a usable lag window (1 day? 3 days?)
or magnitude.
[sotofranco.dev](https://www.sotofranco.dev/blog/posts/btc-eth-lead-lag)

**Gross or net:** N/A — no retail-actionable magnitude exists to net costs
against.

**Verify tonight with free data:** `data.binance.vision` 1-minute klines for
BTC/ETH/majors are enough to test daily-to-multiday lag windows yourself
(cross-correlation of BTC return at t against altcoin return at t+1, t+2, ... days)
— worth doing, since the existing evidence is either too fast to use (HFT) or too
vague to use (narrative), and this specific gap is cheap to fill yourself tonight.

**$1–5k fit & kill factors:** Would fit fine capital-wise if a retail-horizon lag
window existed and were quantified — it currently isn't, in any source I found.
Kill factor: the one really rigorous study on this topic proves the real effect
is inaccessible at retail latency; everything at retail-accessible horizons is
unquantified narrative. This is a genuine research gap, not a ready strategy.

---

## Cross-cutting kill factors (apply to everything above)

1. **Fees.** At 0.06-0.1% taker per side (0.12-0.2% round trip), any strategy
   with weekly-or-faster full-book turnover across many legs (candidates #6, #7,
   #8, #9) needs a real, sustained per-trade edge well above ~20-30bps just to
   break even before counting slippage — this project's own Polymarket fee-wall
   finding (`arb_fee_wall.md`) is the same lesson in a different market: gross
   edges evaporate net of realistic costs far more often than backtests admit.
2. **Regime dependence is the norm, not the exception**, across nearly every
   family here: cross-sectional momentum decayed post-March-2021 (#7); momentum
   vs. mean-reversion dominance flipped around 2021 (#1/#9); CME gaps stopped
   existing in May 2026 (#14); traditional trend-following CTAs (the closest
   TradFi analog to #1/#4) are down ~9% YTD through April 2025. Nothing here is
   a "set and forget forever" edge.
3. **Minimum notional / basket-size problem at $1-5k.** Anything requiring a
   diversified multi-leg book (10+ longs/shorts) — candidates #6, #7, #8, #9 —
   is structurally a worse fit for this capital band than single-instrument
   BTC/ETH strategies (#1, #2, #3, #4, #5). This is probably the single most
   important practical filter for this specific owner/capital size: **prefer
   single- or dual-instrument directional strategies over cross-sectional
   basket strategies**, even when the basket strategy's raw academic credibility
   is higher.
4. **Survivorship/narrative bias in retail sources.** Family #4 (liquidations)
   and #5 (OI/CVD) are dominated by content that describes mechanisms
   vividly and truthfully but has never actually been backtested for
   forward-return predictability anywhere I could find — "sounds right" and "is
   quantifiably true" are different claims, and most of the crypto-Twitter/blog
   content on these two families conflates them.

## Free data cheat-sheet (no metered API keys needed)

| Need | Free source |
|---|---|
| Historical daily/hourly/1-min OHLCV, spot & perps | `data.binance.vision` (bulk CSV, no auth) |
| Binance funding-rate history | `fapi.binance.com/fapi/v1/fundingRate` |
| Bybit klines / funding / OI (OI capped ~short lookback) | Bybit v5 public market endpoints |
| OKX klines / funding | OKX public market endpoints |
| FOMC meeting dates | federalreserve.gov calendar |
| CPI release dates | bls.gov economic calendar |
| CME BTC futures continuous contract (for historical gap verification only) | Yahoo Finance `BTC=F` |

## Bottom line

The strongest, most-corroborated, most retail-executable idea in this sweep is
**#1, volatility-managed time-series trend following on BTC/ETH** — it's the only
candidate with (a) genuine multi-source convergence (an academic-adjacent journal
paper, an independent quant blogger, and a quant-research shop all pointing the
same direction), (b) a capital structure that fits $1-5k cleanly, and (c) low
enough turnover that realistic fees don't obviously kill it. **#2 (pre-FOMC drift)**
is the best supplementary/low-effort overlay — cheap to verify, cheap to run, low
$ ceiling but also low risk of being wrong given the strong equity-market prior.
Everything cross-sectional (#6-#9) is real research but a poor structural fit for
this specific bankroll. Families #4 and #5 (liquidations, OI/CVD) are the
biggest "opportunity gap" in the literature — widely believed, mechanistically
plausible, and essentially unbacktested in public — which makes them either a
genuine edge waiting to be quantified, or a widely-repeated myth; tonight's data
pull won't be enough to resolve that, only a real project would.
