# Practitioner Sweep — Crypto Trading Strategies Reported Profitable, 2025–2026

**Scope:** Read-only web research, 2026-07-17. Sources: r/algotrading, r/quant (Reddit's
own search is poorly indexed by web search / direct fetch of reddit.com and old.reddit.com
is blocked in this environment — see Methodology Note), Hummingbot docs, exchange
research/education (Binance Research, Bybit Learn, Deribit Insights), market-data firms
(Kaiko, Glassnode, Amberdata), quant newsletters (Robot Wealth, Quant Journey, Quantpedia,
Quantt), GitHub repos (Hummingbot, Jesse, Drakkar-Software, freqtrade), and synthesis
articles that read as genuine practitioner content (Everstrike, Block Research).

**Retail lens applied throughout:** $500–$5,000 capital, Windows home PC in Malaysia,
retail (non-colocated) latency, venues = Bybit / OKX / Kraken / KuCoin / Deribit
(Binance restricted, Polymarket home-IP-only — not relevant to this sweep).

**Excluded per instructions (already investigated, dead):** Polymarket binary-merge
arbitrage, Polymarket LP rewards, Polymarket copy-trading, esports prediction betting,
pump.fun sniping/momentum.

---

## Methodology note / limitation

Direct fetches of `reddit.com` and `old.reddit.com` were **blocked** in this environment
("Claude Code is unable to fetch from www.reddit.com"), and WebSearch's indexing of
r/algotrading and r/quant threads is thin — most queries returned zero direct Reddit
links, only third-party articles *describing* what Reddit discusses. This means the
r/algotrading and r/quant coverage below is second-hand (via articles that cite Reddit
sentiment) rather than primary-source thread reads. Hacker News (a discussion of the
Everstrike article, `news.ycombinator.com/item?id=46451344`) also 429'd on every fetch
attempt (3 tries). Where a claim is second-hand, it is marked **[secondhand]**. This is a
real gap — if continuing this research with browser tools (not just WebFetch), re-pull
r/algotrading and r/quant directly and re-attempt the HN thread, which likely has good
practitioner pushback on the Everstrike claims.

---

## Candidates

### 1. Funding-rate arbitrage (delta-neutral spot + perpetual carry)

- **Mechanism:** Buy spot BTC/ETH (or altcoin), simultaneously short the equivalent
  notional on that coin's perpetual future on the same or another exchange. Price risk
  cancels (delta-neutral); you collect the funding payment perpetual longs pay shorts
  every 8h (hourly on Kraken/Hyperliquid) as long as funding stays positive.
- **Who claims it works / evidence quality:** Convergent across many mid-quality sources —
  no single "hero" source, but the numbers agree with each other, which is itself weak
  corroboration. [ArbitrageGhost/Medium](https://arbitrageghost.medium.com/funding-rate-arbitrage-in-2026-the-complete-guide-with-real-calculations-40e6cf341e52),
  [Arbitrage Scanner](https://arbitragescanner.io/blog/crypto-funding-rate-arbitrage-strategy-guide),
  [AlphaexCapital](https://www.alphaexcapital.com/cryptocurrencies/crypto-trading-and-investing-strategies/crypto-derivatives-and-leverage/funding-rate-arbitrage-basics),
  [Everstrike](https://blog.everstrike.io/7-arbitrage-strategies-are-still-accessible-to-retail-quants-in-2025/)
  (mechanism section, no personal numbers). An academic paper
  ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2096720925000818))
  claims up to 115.9% over six months with max loss 1.92% in backtest — treat as
  in-sample/backtest, not a live-fill claim. No screenshots or audited live PnL found from
  an identifiable individual trader (closest thing: the Deribit "live trade example" under
  #2, which is a fixed-funding variant on the same underlying mechanism). **Evidence
  quality: moderate — mechanism is textbook-solid and uncontested, but "proof" is
  guide-writer arithmetic, not verified fills.**
- **Gross vs net of fees:** Gross quoted at 10–30%/yr "normal," spiking to 100%+ annualized
  on hyped altcoins during mania. Net-of-fee reality per the guides themselves: taker fees
  on entry/exit (2 legs × 2 trades = 4 fills), **withdrawal fees called out explicitly as
  "the silent killer"** (a $10 flat BTC withdrawal is 1% of a $1,000 position), and funding
  can flip negative mid-trade, converting yield to cost. At the fee schedules found this
  sweep (OKX 0.08%/0.10%, KuCoin 0.10%/0.10%, Kraken 0.25%/0.40% spot maker/taker at VIP0),
  round-trip cost on a same-exchange spot+perp position is roughly 0.2–0.6% one-time, which
  a multi-week hold easily amortizes — the real threat is withdrawal fees on a **small**
  account and funding reversals, not trading fees.
- **What free data verifies this TONIGHT:** CoinGlass funding-rate comparison page
  (`coinglass.com/FundingRate`) and `coinglass.com/ArbitrageList` show current funding
  across Bybit/OKX/Kraken-type venues for free, live, no signup. Cross-check against each
  exchange's own public funding-rate API (all four accessible venues publish this openly).
  Pull 90 days of historical funding via CoinGlass or exchange APIs and compute realized
  annualized yield net of an assumed 0.1%/leg round-trip — this is a same-night, no-capital
  spreadsheet exercise.
- **Capital fit at $1–5k + kill factors:** Good fit — this is one of the few strategies
  that scales down cleanly to $1–5k (no minimum-tick-size wall like options, no
  competitive-latency wall like queue positioning). **Kill factors:** (1) funding reversal
  — a sustained flip to negative turns yield into cost, especially dangerous if entered at
  a funding extreme instead of average; (2) withdrawal/transfer fees are regressive against
  small accounts; (3) exchange counterparty risk holding collateral on two venues at once
  (explicitly cited as an FTX-echo risk by multiple sources); (4) liquidation risk on the
  short leg if using leverage and not monitoring the delta in real time — several sources
  independently state **"most traders lose money" doing this manually** because they don't
  track delta or fees carefully. Crowd consensus: not dead, but harder than the "free
  money" marketing implies, and margin has compressed as more capital chases it.

---

### 2. Cash-and-carry basis trade (dated futures premium capture, Deribit)

- **Mechanism:** Buy spot BTC, short a dated (expiry) futures contract trading at a
  premium to spot (contango), hold to expiry or premium decay, close both legs, pocket the
  premium. Distinct from #1 in using a *dated* future (fixed known payout) rather than a
  perpetual's variable funding stream.
- **Who claims it works / evidence quality:** **Best evidence of anything in this sweep** —
  [Deribit Insights "Cash & Carry - Live Trade Example"](https://insights.deribit.com/education/cash-carry-live-trade-example/)
  is a **real, sequential, screenshotted trade walkthrough** by an identified Deribit
  educator: 3,000 USDC in, bought spot BTC @ $30,360, shorted Sept future @ ~$30,760 (1.3%
  premium), closed at $26,610/$26,570, netted ~3,032 USDC (~1.06% over the holding period,
  candidly including "I get a little greedy here" execution slop). A companion
  [variable-rate version](https://insights.deribit.com/education/variable-rate-cash-carry-live-trade-example/)
  shows the perpetual-funding variant with real sats-accrued numbers. This is the exchange
  itself publishing a warts-and-all trade log, which is unusually credible — but note
  neither example discloses trading fees paid, so treat the ~1.06%/short-period return as
  gross, not net. **Evidence quality: good** (real trade, real numbers) **but single-source
  and exchange-published (incentive to make the strategy look good), and small sample (one
  trade each).**
- **Gross vs net of fees:** [Quantt's 2026 synthesis](https://www.quantt.co.uk/resources/crypto-quant-strategies-2026)
  and [Robot Wealth](https://robotwealth.com/)-adjacent commentary converge: annualized
  yields **compressed from 30–50%/yr in 2020–2021 to 5–15%/yr "normal" by 2026**, with the
  BIS also publishing on this compression
  ([BIS Working Paper 1087](https://www.bis.org/publ/work1087.pdf)). Deribit options/futures
  fees are capped as a % of premium/notional (check current schedule at trade time) — on a
  1.3%-premium trade the fee bite is a real fraction of profit, not negligible the way it
  is on a fatter basis.
- **What free data verifies this TONIGHT:** Deribit's own public futures curve
  (`deribit.com` — no login needed to view quotes) shows the live basis right now for every
  dated expiry; CoinGlass's Basis page (`coinglass.com/Basis`) aggregates basis across
  Binance/Deribit/OKX for free. You can compute today's annualized basis yield from public
  quotes in minutes.
- **Capital fit at $1–5k + kill factors:** Good — Deribit allows small BTC/ETH clip sizes.
  **Kill factors:** basis has structurally compressed (CME's move to 24/7 futures trading
  in 2026 is called out as a further compression catalyst — institutional liquidity now
  covers hours that used to have gaps); counterparty risk holding both legs on Deribit;
  "slow, low-percentage return" by the exchange's own admission — this is a cash-management
  yield play, not a fast-money strategy, and current 5–15%/yr gross must clear real trading
  fees before it beats simply holding stablecoins at DeFi lending rates (~4–6% APY per
  Aave, candidate #13 below).

---

### 3. Options volatility risk premium (VRP) harvesting — short strangles / covered calls on Deribit

- **Mechanism:** Sell (write) BTC/ETH options — covered calls against spot holdings,
  cash-secured puts, or short strangles/iron condors — to collect premium, betting that
  realized volatility will come in below what implied volatility priced.
- **Who claims it works / evidence quality:** Multiple convergent sources report BTC 30-day
  implied vol averaged **62% through 2025** (vs 15–20% for SPX), and that **"the volatility
  risk premium (implied minus realized) remains positive and not far from its historical
  band... option sellers are still earning typical carry"** as of the 2026 commentary
  found. Deribit is confirmed to hold ~85% of crypto options open interest and to actively
  court retail with **0.1-contract minimum size** and up to 20x leverage — i.e., genuinely
  small-account accessible, unlike CME. **Evidence quality: moderate** — the VRP-positive
  claim is a market-structure generalization repeated across sources, not one trader's
  audited P&L; no individual retail trader's real results were found.
- **Gross vs net of fees:** No net figures found this sweep. The explicit and important
  **caveat**: "VRP turned deeply negative at -25" during a recent stress period, and
  multiple sources warn "a strategy that looked like sensible vol harvesting in one regime
  can become a short-convexity accident in the next" — i.e., this strategy has a fat left
  tail (2026 saw a real liquidation-cascade event, candidate #7, that would have blown
  through short-vol positions). Gross premium collected in calm regimes is real; net
  economics are dominated by the (infrequent but large) tail losses, which is exactly the
  "short volatility" risk profile that has killed retail options sellers in every asset
  class historically.
- **What free data verifies this TONIGHT:** Deribit's public options chain and its own
  DVOL (implied vol index) are free to view without login; you can compare DVOL to trailing
  realized vol computed from free spot OHLCV (e.g., exchange public klines) to see if VRP is
  currently positive right now, tonight, with no capital at risk.
- **Capital fit at $1–5k + kill factors:** Good nominal fit (Deribit's small minimums are
  explicitly retail-friendly) but the **payoff shape is wrong for a $1-5k account**: this is
  a strategy that grinds small premiums and occasionally takes a large drawdown — exactly
  the ruin-risk profile a small, undiversified account is worst-positioned to survive. Kill
  factors: tail/gap risk (crypto moves 10-30%+ in a day with some regularity), the illiquidity
  premium cited (Deribit options book is thin outside the majors, meaning slippage on
  entry/exit), and needing real options-Greeks literacy to size and hedge deltas — a
  materially higher skill floor than #1/#2.

---

### 4. Statistical arbitrage / pairs trading on cointegrated crypto pairs (BTC-ETH)

- **Mechanism:** Test major-coin pairs (BTC-ETH most cited, also ETH-LTC) for
  cointegration (Engle-Granger / Johansen tests), trade the mean-reverting spread —
  long the underperformer / short the outperformer when the spread deviates, exit on
  reversion.
- **Who claims it works / evidence quality:** An academic paper
  ([IJSRA, 2026](https://ijsra.net/sites/default/files/fulltext_pdf/IJSRA-2026-0283.pdf))
  reports **Sharpe ratios of 1.58–2.45** on cointegrated crypto pairs using daily data
  Jan 2022–Oct 2024, net of a stated 0.15%/trade transaction cost, with BTC-ETH exceeding
  Sharpe 2.0. **Evidence quality: flagged as questionable** — IJSRA (International Journal
  of Science and Research Archive) is not a top-tier or widely-cited finance journal (this
  reads as a lower-bar academic venue, possibly close to predatory-journal territory), so
  treat the specific Sharpe numbers as a *hypothesis worth testing*, not a proven result.
  The mechanism itself (cointegration-based pairs trading) is textbook-legitimate
  quant-finance methodology, independently corroborated by
  [Robot Wealth's crypto stat-arb content](https://robotwealth.com/) **[secondhand — could
  not pull specific post text]** and by Quantt's synthesis, which explicitly says the
  BTC-ETH cointegration relationship is "very stable across different market regimes" —
  but Quantt's own "what doesn't work" section separately warns that **naive
  cointegration strategies from 2020–2021 no longer function**, i.e., the crowd view is
  that this needs adaptive/regime-aware implementation now, not a static 2022-style model.
- **Gross vs net of fees:** The academic paper's Sharpe 1.58–2.45 is stated net of a 0.15%
  round-trip-ish transaction cost assumption — reasonable given OKX/KuCoin fee schedules
  found this sweep (0.08–0.10% maker/taker), but daily-rebalance frequency implied by the
  data (daily closes) keeps trade count and cumulative fee drag low relative to
  higher-frequency stat arb.
  No live/forward-tested numbers found.
- **What free data verifies this TONIGHT:** Fully backtestable tonight with zero cost —
  free daily/hourly OHLCV for BTC, ETH, LTC from any exchange's public API (Kraken, OKX,
  KuCoin all have free public kline endpoints, no auth needed) plus `statsmodels`
  (Engle-Granger) or `pykalman` for a dynamic hedge ratio. This is the single most directly
  "verify tonight with free data" candidate on this list, because the paper hands you an
  exact recipe to replicate independently.
- **Capital fit at $1–5k + kill factors:** Good — pairs trading needs no minimum scale
  beyond exchange lot sizes, and BTC/ETH are liquid enough on all four accessible venues
  that a $1–5k account won't move the market. **Kill factors:** the cited Sharpe numbers
  are from a low-credibility journal and need independent out-of-sample verification before
  trusting them (do not size real capital off this paper alone); cointegration
  relationships can break down structurally (regime change) with no advance warning;
  requires real infrastructure (data pipeline + signal computation + order management),
  not a one-click bot.

---

### 5. Weekend / "Monday Asia Open" seasonality momentum

- **Mechanism:** Directional (not market-neutral) strategy exploiting a documented
  return-timing anomaly: momentum/return effects that concentrate in specific windows —
  cited specifically as **Sunday 23:00–00:00 UTC**, aligned with US retail re-entering
  after the weekend and the Asian market open, with weekend momentum stronger on altcoins.
- **Who claims it works / evidence quality:** Academic-leaning source
  ([QuantifiedStrategies.com](https://www.quantifiedstrategies.com/weekend-effect-in-bitcoin/))
  cites a specific backtest: **103 trades, 60% win rate, average gain 2.6%/trade, max
  drawdown 19%, ~10% time-in-market**, computed to ~280% risk-adjusted (28%/yr ÷ 0.09
  exposure fraction) — a real, specific, checkable number, though single-source and the
  exact methodology/date range wasn't fully visible in this sweep. A second source
  ([mlquants Substack](https://mlquants.substack.com/p/are-day-of-the-week-effects-in-cryptocurrencies))
  independently examines day-of-week effects with "intraday evidence from active and less
  active cryptocurrencies" — convergent interest from a second quant-leaning source, though
  its specific verdict wasn't extracted in depth this sweep (worth a direct follow-up read).
  **Evidence quality: moderate** — specific, checkable numbers exist, but from a strategy-
  marketing-adjacent site (QuantifiedStrategies sells strategy code), so independent
  replication is warranted before trusting the win rate.
- **Gross vs net of fees:** ~10% market exposure time means fee drag from ~100 trades/period
  is a real but bounded cost — needs to be subtracted from the stated 2.6%/trade average
  gain; not disclosed whether the cited numbers are gross or net.
- **What free data verifies this TONIGHT:** Directly replicable tonight — free hourly BTC
  OHLCV going back years is available from every major exchange's public API and from
  free aggregators; computing hour-of-week average returns is a trivial pandas groupby.
  This is the second-easiest candidate to verify tonight after #4.
- **Capital fit at $1–5k + kill factors:** Good capital fit, minimal infra (this can be
  executed as a **weekly**, not sub-second, trade — one entry near Sunday evening UTC, one
  exit — making it uniquely tolerant of Malaysia-based retail latency and even manual
  execution). **Kill factors:** this is a **directional** bet dressed as a seasonality
  edge — real drawdown risk (19% cited) unlike the market-neutral carry trades above;
  regime-dependent (a cited structural warning: **CME's move to 24/7 futures trading in
  2026 "would eliminate the classic CME gap pattern entirely,"** and traders were noted as
  having "roughly two months before the pattern changes structurally" — i.e., part of the
  mechanism this anomaly rides on is explicitly expected to erode in 2026); needs multi-year
  out-of-sample testing before trusting, since seasonality effects are a classic overfitting
  trap.

---

### 6. Liquidation-cascade / forced-flow positioning

- **Mechanism:** Position ahead of or during forced-liquidation cascades — thin order
  books mean a forced-sell wave pushes price through a cluster of leveraged stop/liquidation
  levels, creating a temporary overshoot that mean-reverts once forced selling exhausts.
  Practically: watch open-interest/leverage clustering (free heatmaps) and either fade the
  overshoot after a cascade or avoid being caught in one.
- **Who claims it works / evidence quality:** [Block Research's "Crypto Trading Bot: What
  Actually Works in 2026"](https://blockresearch.ai/blog/crypto-trading-bot) explicitly
  lists "Forced Selling/Liquidation Cascades" under strategies that **work**, describing
  the phenomenon as "structurally inefficient" (i.e., a real, recurring microstructure
  effect, not random noise). Market-data confirmation: 2026 events are well documented with
  real numbers — e.g., **"over 65% of liquidations occur in positions using 20x leverage or
  higher"** and a **June 2026 cascade that forced-closed over $3B in 48 hours** as BTC fell
  ~$67k→$59.1k. **Evidence quality: moderate** — the phenomenon is well-evidenced as *real*
  (huge, frequent, well-documented liquidation events), but "works" here is closer to a
  structural/qualitative argument than a rigorous backtested edge with a Sharpe ratio; no
  source in this sweep gave real trade-level P&L for trading *around* cascades specifically.
- **Gross vs net of fees:** Not quantified anywhere found. This would be a
  higher-frequency, higher-skill discretionary-or-semi-systematic strategy, so fee drag
  depends entirely on how often you act — untested claim.
- **What free data verifies this TONIGHT:** Excellent free data available right now —
  CoinGlass's liquidation heatmap and liquidation-by-exchange feed
  (`coinglass.com/liquidations/BTC`) is free, live, no signup, and shows exactly where
  leverage is clustered and where cascades have recently occurred. You could paper-trade
  this concept tonight against live data with zero cost.
- **Capital fit at $1–5k + kill factors:** Reasonable capital fit (no minimum-scale
  requirement), **but latency/reaction-speed matters** during the actual cascade window
  (seconds to low minutes), which cuts against the Malaysia-retail-latency constraint more
  than #1/#2/#5 do. Kill factors: this is trading *into* extreme volatility — the same
  event that creates the opportunity can also liquidate you if positioned on the wrong side
  or with any leverage; requires real-time monitoring infrastructure (or accepting you'll
  miss most cascades if not watching 24/7); very easy to fool yourself with hindsight
  ("obviously that was a cascade to fade") without a pre-committed, backtested rule.

---

### 7. Cross-exchange arbitrage on thin/small markets ("queue positioning," sub-$10M/day pairs)

- **Mechanism:** Rather than competing on BTC/USDT (dominated by market makers like
  Wintermute/Jump), target smaller pairs/venues where big players don't bother —
  cited threshold: **"big players generally don't enter a market unless its volume is at
  least $10M/day."** Capture the bid-ask/queue-position edge via speed or fee advantage in
  markets under that threshold.
- **Who claims it works / evidence quality:** [Everstrike blog](https://blog.everstrike.io/7-arbitrage-strategies-are-still-accessible-to-retail-quants-in-2025/)
  gives the most concrete numeric example in this whole sweep: **a $2M/day market, 2bps
  edge per unit traded, yielding ~$1,000/day** for a retail operator who wins the queue.
  This is a first-person-voiced technical blog (not obvious guru marketing — it discusses
  BitMEX mark-price formulas, options fee structures, and is specific about mechanism), and
  it was substantive enough to reach [Hacker News front-page discussion](https://news.ycombinator.com/item?id=46451344)
  (comments not retrievable this sweep — HN returned HTTP 429 on 3 attempts — **flag for
  follow-up**, HN commenters typically stress-test claims like this hard).
  **Evidence quality: moderate** — concrete worked example from a technically credible
  author, but it is still that author's own illustrative math, not an audited live result,
  and the $1,000/day figure requires **capturing $5M/day of matched volume at 2bps** on a
  $2M/day market — i.e., turning your book over ~2.5x/day, which is a claim about skill/
  infrastructure, not about needing $5M of capital.
- **Gross vs net of fees:** The article is explicit that **"expect to dedicate at least
  half of your monthly profits to exchange fees"** unless using a zero-fee venue — so the
  $1,000/day headline should be read as closer to $500/day net absent a fee-free venue.
- **What free data verifies this TONIGHT:** Partially — you can survey sub-$10M/day pairs
  and their current spreads for free via exchange public order-book APIs (OKX, KuCoin,
  Kraken, Bybit all expose L2 books without auth) to gauge how wide/exploitable spreads
  currently are on candidate thin markets. You cannot verify the *capturable* edge without
  live order placement (paper-trading queue position is not very informative), so full
  verification requires live testing, not just tonight's data pull.
- **Capital fit at $1–5k + kill factors:** Capital fit is fine (small, fast-turnover
  capital, not a large static position) but **this is the most latency/infrastructure-
  sensitive candidate in the list** — it requires being fast and present continuously
  across possibly many thin markets, which is a genuinely hard fit for a solo Windows
  home-PC operator in Malaysia versus a professional running colocated infra, even on
  markets "too small for the big players." Kill factor risk is largely execution/skill,
  not capital: the strategy is explicitly billed as viable for "a single person on their
  laptop for a year or two" **[unverified — Everstrike's own framing, not independently
  corroborated]**, so treat as plausible-but-unproven for this specific operator profile.

---

### 8. New-exchange-listing arbitrage

- **Mechanism:** When a token newly lists on an exchange (especially a smaller
  fast-mover like KuCoin), the price on the new venue frequently diverges sharply from
  where the same token already trades elsewhere (DEX or other CEX) for the first minutes
  to hours, before arbitrageurs converge it.
- **Who claims it works / evidence quality:** A cited (but unlinked in the crawl)
  "2025 Chainalysis report" reportedly found **price discrepancies of 0.5%+ occurring
  thousands of times daily** across major exchanges, and more specifically that
  **"KuCoin experiences massive price discrepancies during the first few hours of a
  listing... 5% to 10% spreads in volatile altcoin markets."** Kaiko Research is cited
  (secondhand, via a synthesis article, original Kaiko report not directly located this
  sweep) as finding the **average arbitrage window for major pairs lasts fewer than 4
  seconds**, and total addressable crypto arbitrage profit **"exceeded $8 billion
  annually."** **Evidence quality: moderate** — the underlying data-firm claims (Kaiko,
  Chainalysis) are credible-sounding but were reached via secondhand summary articles, not
  the primary Kaiko/Chainalysis report — **flag for follow-up: pull the actual Kaiko
  report from research.kaiko.com directly.**
- **Gross vs net of fees:** Not quantified specifically for the listing-arb sub-case; the
  general market's $8B figure is aggregate/industry-wide (overwhelmingly captured by
  professional/institutional players), not a per-retail-trader net number.
- **What free data verifies this TONIGHT:** Partially — you can monitor a specific
  upcoming listing announcement (KuCoin/OKX/Bybit publish listing calendars) and watch the
  public order book live for free, but you'd need to already be positioned/monitoring at
  the exact listing moment — this is a "watch for the next listing" verification, not an
  instantly-testable-with-historical-data one.
- **Capital fit at $1–5k + kill factors:** Reasonable capital fit for the position size,
  but the **4-second window statistic is the whole story here**: this is fundamentally a
  speed/automation game (multiple independent sources converge that "manual arbitrage is
  practically impossible in 2026... automation mandatory"), and a home-PC retail operator
  in Malaysia competing for a 4-second window against colocated bots is a poor latency
  match. Also high execution risk (thin book on a brand-new listing means your own order
  can move the price against you). Best framed as a "know it exists, don't expect to win
  it without real infra investment" entry.

---

### 9. Hummingbot-style market making (pure MM and cross-exchange market making / XEMM)

- **Mechanism:** Continuously quote both sides of the book (buy + sell limit orders) on a
  maker exchange, capturing the spread; XEMM variant hedges any fill immediately on a
  second "taker" exchange to stay flat.
- **Who claims it works / evidence quality:** Hummingbot is the most-cited open-source
  framework for this in every search this sweep ran, and is explicitly the standard
  practitioner tool ("Hyperliquid is now a sponsoring exchange of the Hummingbot
  Foundation"). However, the **official Hummingbot XEMM strategy docs
  ([hummingbot.org](https://hummingbot.org/strategies/v1-strategies/cross-exchange-market-making/))
  contain zero performance metrics, backtests, or case studies** — confirmed by direct
  fetch this sweep. Third-party reviews describe outcomes as **"mixed... market making can
  work under the right conditions, but only after a steep learning curve"** and separately
  that **"arbitrage is harder than it looks because liquidity, fees, and slippage often
  wipe out the edge."** Hummingbot's own **Liquidity Mining policy page explicitly states
  "Hummingbot makes no guarantees or claims that participation... will be profitable."**
  **Evidence quality: weak-moderate** — strong ecosystem/tooling credibility, essentially
  zero quantified proof of retail profitability net of fees.
- **Gross vs net of fees:** On liquid major pairs, spreads are cited as compressed to
  "1–2 bps for BTC-USDT (vs 50–100 bps in 2017)," with professional market makers
  (Wintermute, Jump Crypto) dominating — i.e., on the pairs a retail trader can actually
  get filled on with meaningful volume, the edge is largely gone; the more honest framing
  found is that MM only remains viable for retail on **thin/illiquid pairs**, which
  circles back into the same thin-market dynamics as candidate #7.
  **Directly relevant parallel from this project's own history:** this repo's own
  `HANDOFF.md`/`CLAUDE.md` context documents that Polymarket's binary-merge and LP-maker
  edges were independently found to die once fee-walled/crowded — the same generic pattern
  (thin/uncrowded markets pay, liquid/crowded ones are fee-walled to breakeven-or-worse) that
  crypto market-making sources describe here. Not conclusive for crypto CEXs specifically,
  but a structurally identical failure mode worth taking seriously before allocating time.
- **What free data verifies this TONIGHT:** You can pull free L2 order-book snapshots
  (public APIs, no auth) from OKX/KuCoin/Bybit for candidate thin pairs and estimate
  theoretical spread-capture P&L before deploying Hummingbot live — a legitimate
  tonight-doable sanity check, though it won't capture adverse-selection/inventory risk
  realistically.
- **Capital fit at $1–5k + kill factors:** Workable capital fit for thin pairs (small size
  needed); **Hummingbot's own docs warn of a 2–4 hour minimum config learning curve** and
  operational risk (DEX-leg reliability issues, gas-fee volatility on the taker-hedge leg).
  Kill factor: liquid/major pairs are professional-dominated and compressed to near-zero
  edge; thin pairs carry inventory/adverse-selection risk that no source quantified. Overall
  verdict from the sources themselves: **"no framework can guarantee profitability... depends
  on market conditions, fees, latency, competition, parameter choice, and operational
  discipline"** — an honest but decidedly non-bullish practitioner consensus.

---

### 10. Grid trading bots

- **Mechanism:** Place a ladder of buy/sell limit orders at fixed price intervals within a
  range, profiting from price oscillation without needing directional prediction.
- **Who claims it works / evidence quality:** Extremely widely discussed at the
  retail-platform level (Pionex, 3Commas, Bitsgap all built around this), described
  **[secondhand, via article summaries of Reddit sentiment]** as: "users who stick to
  sideways markets praising grid bot consistency, while those caught in trending markets
  without reconfiguring report significant losses." Cited backtest range: **"annualized
  returns of 15-60% for well-configured grids on major pairs during consolidation
  periods"** — no source, methodology, or independent verification found; this smells like
  marketing-adjacent copy from bot-vendor content, not a rigorous study. **Evidence
  quality: weak** — popular and mechanically simple, but no credible practitioner backtest
  with drawdown-adjusted numbers was found, and the "15-60%" range is suspiciously wide
  (consistent with cherry-picked favorable windows).
- **Gross vs net of fees:** Not disclosed anywhere found. Grid bots trade frequently
  (every grid-line touch), so fee drag is structurally significant and was not addressed
  quantitatively by any source.
- **What free data verifies this TONIGHT:** Fully backtestable tonight for free — grid
  logic is simple enough to backtest against free historical OHLCV in an hour or two of
  scripting, and this is a good candidate to independently fact-check the vendor-marketing
  claims rather than trust them.
- **Capital fit at $1–5k + kill factors:** Good nominal capital fit (this is literally
  marketed at retail sub-$5k accounts). Kill factor, stated bluntly by multiple sources:
  **"a single range break can wipe out weeks of accumulated grid profits"** — in a strong
  trend the bot "either sells too early... or keeps buying into a crash, accumulating
  losses." Crypto's realized volatility and trending behavior (esp. around the liquidation
  cascades in candidate #6) make range breaks a real and recurring risk, not a tail case.
  Net verdict: plausible small edge in chop, structurally exposed to the exact kind of
  violent moves crypto is known for.

---

### 11. Perpetual-futures basis mean-reversion (systematic, not carry-hold)

- **Mechanism:** Distinct from candidates #1/#2 (which hold the carry to collect funding/
  premium): this is a **signal-based** strategy that treats the perp-vs-index basis itself
  as a mean-reverting series — compute the basis, z-score it against its own historical
  mean/stdev, and take (short-duration, often intraday) positions when it deviates >2
  standard deviations, closing on reversion rather than holding for funding income.
- **Who claims it works / evidence quality:** Found via a
  [CoinAPI blog on historical perpetual futures data](https://www.coinapi.io/blog/historical-data-for-perpetual-futures),
  which lays out the exact recipe (pull `DERIVATIVES_MARK_PRICE` and
  `DERIVATIVES_INDEX_PRICE`, subtract, z-score, trade >2σ deviations) as a data-vendor
  methodology example rather than a claimed live result. A related framing from Block
  Research's works/doesn't-work piece separately lists plain funding-rate arbitrage as
  working "when funding goes extreme" — conceptually adjacent. **Evidence quality: weak**
  — this is a recipe/methodology suggestion from a data vendor (motivated to sell API
  access), not a reported live or backtested result from an independent trader.
- **Gross vs net of fees:** Not quantified by any source found.
- **What free data verifies this TONIGHT:** Yes, cleanly — mark price and index price are
  both free/public on every major exchange's API (no auth needed for market data), so the
  z-score signal itself is fully constructible and backtestable tonight at zero cost. This
  is a good "cheap to check, unknown edge" candidate — worth an hour of scripting to see if
  the z-score signal has any real predictive power before believing it.
- **Capital fit at $1–5k + kill factors:** Fine capital fit. Kill factor: this is presented
  as a plausible methodology, not a validated edge — treat as a research task for tonight
  rather than a strategy with practitioner backing. Higher trade frequency than #1/#2 means
  more fee drag to overcome, and no source quantified whether the >2σ signal survives
  transaction costs.

---

### 12. [FLAGGED DEAD] MEV / DEX sandwich & arbitrage bots for a solo retail operator

- **Mechanism:** Extract value from on-chain transaction ordering (sandwich attacks,
  DEX-DEX or DEX-CEX arbitrage, liquidation-bot sniping) by running searcher
  infrastructure that competes for block space.
- **Where the crowd says this edge died (for retail):** Explicit and consistent across
  sources this sweep: MEV is described as **"a winner-take-most market... cumulative MEV
  profits across all blockchains passed $1 billion [cumulative], though that profit is
  highly concentrated in a dozen or fewer searcher teams running at near-hardware speed."**
  Infrastructure cost floor cited: **"$500 to $1,000 per month in infrastructure, plus a
  few thousand USD in working ETH"** for a minimal Rust-based setup, with **"many bots
  operate at a loss after infrastructure costs"** and professional operations spending
  "five to six figures monthly on infra." One of Ethereum's largest sandwich bots was
  reportedly drained in 2026, and malicious npm packages impersonating MEV/arbitrage
  tooling ("ethereum-mev-bot-v2," "hyperliquid-trading-bot") are flagged as an active scam
  vector in this space as of June 2026 — a further sign of a saturated, adversarial,
  low-retail-trust environment.
- **Verdict:** Not included as a live candidate. For a $1-5k, solo, non-colocated retail
  operator this is a clear kill — infra costs alone can exceed the entire trading capital
  budget, competition is professionalized, and the space has an active scam/security-risk
  problem on top of the compressed edge.

---

### 13. [FLAGGED DEAD] Copy-trading / whale-wallet following on Hyperliquid (on-chain)

- **Mechanism:** Use free on-chain leaderboards/trackers (HyperTracker, Hyperdash,
  HyperStats, whale.ag) to identify historically profitable wallets on Hyperliquid and
  mirror their positions, either manually or via a copy-trading tool.
- **Where the crowd says this edge died:** The data is damning and directly quantified —
  **"Of the 82,586 active wallets tracked on Hyperliquid, only 230 have generated over $1M
  in cumulative profit, while the 58,848-wallet 'Unprofitable' cohort represents the
  majority of retail participants"** — i.e., ~71% of tracked wallets are net-unprofitable.
  Separately noted: **"HyperLiquid is fully on-chain and transparent... but there is no
  built-in feature to blindly copy a wallet"** — you'd be building your own copy
  infrastructure to follow a cohort where most participants lose money, and even the
  minority who are profitable are subject to the same post-fill-drift problem this
  project's own research already proved fatal for Polymarket copy-trading (see excluded
  topics — `copy_trading_dead.md`: "-5.1% on turnover despite survivorship tailwind,
  post-fill drift ~0.1c vs 1-2c copier costs"). The mechanism (follow public on-chain
  leaders, eat their execution-quality decay) is structurally the same disease on a
  different venue.
- **Verdict:** Not included as a live candidate — this is the same failure mode already
  proven dead in this project's own prior research, just relocated from Polymarket to
  Hyperliquid. Included here explicitly to document that the sweep checked and the crowd's
  own data (71% unprofitable) independently corroborates the prior finding.

---

### 14. [FLAGGED DEAD] DeFi lending-rate arbitrage (Aave vs Compound spread)

- **Mechanism:** Borrow a stablecoin cheaply on one lending protocol, deposit it for a
  higher yield on another, pocketing the rate spread risk-free (in theory).
- **Where the crowd says this edge died:** Directly and specifically: **"Rates arbitrage
  on Aave and Compound is not currently possible in practice because Aave and Compound do
  not accept each other's tokens as collateral"** — a structural/protocol-level block, not
  a competition problem. Additionally, **"Aave and Compound's wide bid-offer spreads make
  it increasingly difficult to execute rates arbitrage, even if protocols accepted each
  other's tokens as collateral,"** and **"by the time traders compare Aave, Compound,
  Morpho, and CeFi desks, the best borrow rate may already be gone."** Current base yields
  cited are modest anyway (Aave ~4–6% APY on major stablecoins/ETH).
- **Verdict:** Not included as a live candidate — this is mechanically blocked at the
  protocol level for the classic textbook version of the trade, and residual yield-spread
  opportunities (Morpho, CeFi desks) are described as too fast-moving for retail to catch
  reliably. Worth revisiting only if a specific protocol pair is found that does accept
  cross-collateral (not identified this sweep).

---

### 15. [FLAGGED DEAD for retail] Options conversion/reversal (put-call parity) arbitrage

- **Mechanism:** When put-call parity is violated, lock in risk-free profit via a
  synthetic-vs-actual position combining long/short stock (or underlying) with matched
  calls and puts at the same strike/expiry.
- **Where the crowd says this edge died (for retail specifically):** Unambiguous across
  every source found: **"institutional firms need mispricing of only $0.02-$0.05 to
  profit... transaction costs, speed, and margin requirements make these strategies
  virtually impossible for retail traders to execute profitably... by the time a retail
  trader identifies the opportunity and enters orders, the prices may have already
  normalized"** and the strategy **"remains the domain of professional options traders
  such as floor traders and market makers who need not pay broker commissions."** No
  Deribit-specific retail counterexample was found.
- **Verdict:** Not included as a live candidate. Mentioned because it's a natural adjacent
  idea to candidate #3 (options VRP harvesting) and is worth explicitly ruling out rather
  than leaving as an open question — this one is dead for a retail operator on cost/speed
  grounds alone, independent of crypto-specific dynamics.

---

## Cross-cutting observations

- **The single strongest pattern across sources:** every carry-style, market-neutral
  strategy (funding arb, cash-and-carry, VRP harvesting) is independently reported to have
  **compressed materially from 2020–2021 levels** (30–50%/yr basis trades → 5–15%/yr;
  "wild edge... gone, replaced by deeper liquidity, tighter spreads, more institutional
  participation, and considerably more competition"). None of these are "dead," but none
  are the free-money framing that guru-marketing content pitches them as either.
- **Latency/speed-sensitive strategies (queue positioning, new-listing arb, MEV, classic
  triangular arb on major pairs) are the ones most in tension with this operator's actual
  constraints** (Windows home PC, Malaysia, retail latency) — the evidence for these being
  *real* opportunities is often decent, but the evidence for a **solo retail operator on
  this specific setup** being able to capture them is thin-to-negative. This mirrors the
  project's own prior finding pattern (Polymarket arb needing `confirm_hits()` because
  naive snapshots produce phantom edges from latency).
- **Every "dead" candidate documented here (#12–15) died for a *structural* reason**
  (protocol-level collateral block, professionalized infra cost floor, sub-cent
  institutional-only margins, or a proven-elsewhere execution-drift problem) **rather than
  "nobody's tried it,"** which is the more trustworthy kind of dead-end to document.
- **Best tonight-verifiable-for-free candidates, ranked by ease:** #4 (stat arb — full
  backtest scriptable tonight from free OHLCV), #5 (seasonality — same), #11 (basis
  z-score — same), #1 and #2 (funding/basis — live rates are free and public right now on
  CoinGlass/Deribit/exchange APIs, verifiable without capital), #6 (liquidation
  heatmap — free, live, paper-tradeable tonight).
- **Gap to flag:** r/algotrading and r/quant primary threads were not directly readable
  this session (fetch blocked); the Hacker News discussion of the Everstrike article
  (likely the single best source of real practitioner pushback in this entire sweep) 429'd
  on every attempt. Both are worth a direct re-pull with browser-based tools if this
  research continues.

---

## Sources index (all URLs cited above)

- https://blog.everstrike.io/7-arbitrage-strategies-are-still-accessible-to-retail-quants-in-2025/
- https://news.ycombinator.com/item?id=46451344 (blocked — 429 on all 3 attempts)
- https://insights.deribit.com/education/cash-carry-live-trade-example/
- https://insights.deribit.com/education/variable-rate-cash-carry-live-trade-example/
- https://insights.deribit.com/education/cash-and-carry-trades/
- https://www.bis.org/publ/work1087.pdf
- https://www.quantt.co.uk/resources/crypto-quant-strategies-2026
- https://blockresearch.ai/blog/crypto-trading-bot
- https://hummingbot.org/strategies/v1-strategies/cross-exchange-market-making/
- https://hummingbot.org/strategies/v1-strategies/liquidity-mining/
- https://new.hummingbot.io/en/liquidity-mining-policy/
- https://finestel.com/blog/hummingbot-review/
- https://github.com/Drakkar-Software/Triangular-Arbitrage
- https://github.com/jesse-ai/jesse
- https://github.com/freqtrade/freqtrade-strategies
- https://arbitrageghost.medium.com/funding-rate-arbitrage-in-2026-the-complete-guide-with-real-calculations-40e6cf341e52
- https://arbitragescanner.io/blog/crypto-funding-rate-arbitrage-strategy-guide
- https://www.alphaexcapital.com/cryptocurrencies/crypto-trading-and-investing-strategies/crypto-derivatives-and-leverage/funding-rate-arbitrage-basics
- https://www.sciencedirect.com/science/article/pii/S2096720925000818
- https://fundingarbhq.com/funding-arb-guide-2026-infrastructure-tools-strategy
- https://ijsra.net/sites/default/files/fulltext_pdf/IJSRA-2026-0283.pdf
- https://robotwealth.com/blog/ ; https://robotwealth.com/index-of-strategies/
- https://quantjourney.substack.com/s/crypto
- https://quantpedia.com/quantpedia-in-march-2026/
- https://research.kaiko.com/insights/crypto-in-2026-what-breaks-what-scales-what-consolidates
- https://research.glassnode.com/
- https://www.amberdata.io/ad-derivatives
- https://www.quantifiedstrategies.com/weekend-effect-in-bitcoin/
- https://mlquants.substack.com/p/are-day-of-the-week-effects-in-cryptocurrencies
- https://concretumgroup.com/seasonality-in-bitcoin-intraday-trend-trading/
- https://www.coinapi.io/blog/historical-data-for-perpetual-futures
- https://hypertracker.io/ ; https://hyperdash.com/ ; https://hyperstats.org/ ; https://whale.ag/
- https://www.infinity.exchange/article/introducing-rates-arbitrage-to-defi
- https://aave.com/ ; https://aavescan.com/
- https://www.optiontradingpedia.com/conversion_reversal_arbitrage.htm
- https://www.tradealgo.com/trading-guides/options-strategies/conversion-and-reversal-arbitrage-how-market-makers-stay-delta-neutral
- https://www.coinglass.com/FundingRate ; https://www.coinglass.com/ArbitrageList ;
  https://www.coinglass.com/Basis ; https://www.coinglass.com/liquidations/BTC
- https://tradersunion.com/brokers/crypto/view/okex/fees/ (OKX fee schedule)
- https://www.copytradeinsider.com/blog/kucoin-fees-explained/ (KuCoin fee schedule)
- https://www.kraken.com/learn/lowest-fee-crypto-exchange (Kraken fee schedule)
- https://cryptodaily.co.uk/2026/06/mev-bot-drain-attack-surface-ethereum
