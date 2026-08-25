# I Gave AI 6 Years of Data. This Is What It Found.
- id: HCiMznnYMiI | views: 3000 | length: 874s
- market(s) shown: **EURUSD** (the only pair tested). He suggests viewers try GBPUSD, USDJPY, oil [12:07]-[12:11], [12:43]
- timeframe(s) taught: intraday session-based. The Tokyo range is built from a session window and traded at the London open; the execution timeframe is never named, but he references "specific 15-minute time buckets like the ORB strategy" [3:16]-[3:19] as one of the *failed* experiments, not this one

## Mechanical rules (only what the video actually states)
This is the most mechanical video on the channel: an AI-assisted research log ending in a fully-specified **failed-breakout mean-reversion** system with Pine Script and MT5 EA implementations.

- Indicators + exact settings: **none traditional** — "no 17 indicators, no MACD combined with RSI combined with a 200 moving average" [6:36]-[6:43]. The only inputs are:
  1. **Session range** (Tokyo/overnight high and low)
  2. **Relative volume** of the breakout candle
- Setup/context required — the range filter:
  - Establish the **Tokyo session range** before London opens.
  - **Only narrow ranges qualify: "the current maximum was around 21.72 pips, the size of the range"** [5:55]-[6:01]. Ranges wider than ~21.72 pips are skipped.
- Entry trigger — a **failed breakout / fake-out fade**, in three steps [6:02]-[6:30]:
  1. After London opens, wait for price to **break out of either side** of the Tokyo range. Do **not** trade the breakout itself.
  2. The breakout must have **relative volume >= 1.6x**: "we look at the relative volume of that breakout — the current threshold is 1.6 times relative volume" [6:07]-[6:14].
  3. Price must **fail to continue and come back inside the range boundary**. Then:
     - Broke **above** the range high, re-entered the range -> **SHORT**
     - Broke **below** the range low, re-entered the range -> **LONG**
- Stop loss: **not stated in the video.** He lists stop placement as one of the questions he *asked* the AI ("Where should the stop loss go? Halfway in between the range or on the other side of the range?" [4:41]-[4:45]) but never reports which answer won. This is the single biggest gap.
- Take profit: **the midpoint of the overnight/Tokyo range** — "the take profit is then calculated as the middle point of that overnight range" [6:30]-[6:36].
- Filters he adds:
  - Range-width cap ~21.72 pips (above).
  - Relative-volume threshold 1.6x (above).
  - **Session timing, and it is decisive.** Two configurations reported: range/trading window **2:00 a.m. to 10:00 a.m. broker time**, versus the same window shifted one hour later, **3:00 a.m. to 11:00 a.m.** [9:18]-[9:27]. Timezone is explicitly **broker/server time**, and he flags this as the bug that broke reconciliation: "eventually we found it and it was the time zones — they change multiple times per year and they're different based on where your server is; so we corrected the trading view strategy to use the local server time based on London open and suddenly the number of trades exploded" [7:22]-[7:36].
  - Trading costs are explicitly included in the research ("after costs of trading, basically the spread and commissions" [5:09]-[5:13]) — the original plain-breakout version was **profitable gross and unprofitable net of costs**, which is why it was discarded [5:04]-[5:16].

## Reported backtest results (three environments)
| Environment | Trades | Winners | Win rate | Profit factor |
|---|---|---|---|---|
| TradingView Pine, full deep backtest | 232 | 176 | 75.86% | ~1.26 |
| MT5 EA, broker historical data | 103 | 75 (28 losers) | 72.82% | 1.30 |
| MT5 EA, session shifted 3am-11am | 27 | 23 (4 losers) | 85.19% | 2.69 |
[7:40]-[8:31], [9:27]-[9:40]

Discarded earlier variants, with numbers: the "candle DNA" pattern miner produced "around a 29% win rate and a profit factor of 0.54" [2:50]-[2:57], described as garbage and killed.

## Vague / untestable / chart-pointed claims
Unusually few — but the ones present are load-bearing:
- **No stop-loss rule is ever stated.** [4:41] poses the question and it is never answered. The reported 75%/85% win rates and profit factors cannot be reproduced without it.
- "**Relative volume 1.6x**" [6:12] — relative to *what* baseline is never defined (average volume over how many bars? same time-of-day average? session average?). Two implementations with different baselines will not agree, and he himself notes TradingView and MT5 have "different volume data" [8:36]-[8:40].
- "**Around 21.72 pips**" [5:58] — a suspiciously precise optimised number described as "the current maximum", i.e. a fitted parameter. He explicitly warns about exactly this: "the more parameters I optimize against, the easier it becomes to accidentally build something that's absolutely incredible only on past data and then completely useless on trading future price action" [10:35]-[10:47].
- **The 85.19% variant is 27 trades.** He calls this out himself as the honest-broker moment: "conveniently forget to mention it's only 27 trades" [9:55]-[9:59]. Not a usable result.
- "**6 years of data**" is in the title but the actual sample period is never stated in the transcript; only trade counts are given.
- Whether entry is on **candle close or on the touch** back inside the range is raised as a question ("Should the trade enter on close of candle or as it breaks the range?" [4:48]-[4:53]) and never answered for the final version.
- The precise definition of "**comes back inside the boundary**" (close inside? touch inside? within N bars of the breakout?) is not given.
- Whether **2am-10am** is the range window, the trading window, or both is ambiguous from the wording "calculating the range from 2:00 a.m. until 10:00 a.m." [9:21] — an 8-hour "Tokyo range" that stays open past the London open reads more like a combined session-and-trading window.

## Testability
- rating: **HIGH** (highest in this batch) — range definition, width filter (21.72 pips), volume filter (1.6x), direction logic, and target (range midpoint) are all numeric and stated as if/then rules; he ships Pine Script + MT5 EA files. Downgraded from "fully mechanical" only by the **missing stop loss**, the undefined relative-volume baseline, and the ambiguous session-window wording — but those are three fillable blanks, not discretion.
- overlap: **session-filter** (Tokyo range / London open) + **market-structure/BOS** in its failed-breakout form (fade the fake-out) + volume filter. This is the only video in the batch that is fully algorithmic and cost-aware; it explicitly supersedes his older "trade the London open off the Tokyo range" breakout strategy, which he reports **lost money after spread and commissions** [4:59]-[5:16].
- notable quotes:
  - [5:52] "You establish the Tokyo range. We only care about relatively narrow Tokyo sessions. The current maximum was around 21.72 pips, the size of the range."
  - [6:09] "We look at the relative volume of that breakout. The current threshold is 1.6 times relative volume... if price breaks up above that range high, comes back into the boundary, we're looking for a short."
  - [6:30] "The take profit is then calculated as the middle point of that overnight range. And that's basically it. Range, breakout, volume, failure, mean reversion."
