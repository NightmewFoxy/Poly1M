# How to Make a Trading Bot Part 3
- id: axcP2CeIYe8 | views: 66000 | length: 521s
- market(s) shown: not explicitly named in this part; Part 2 (hr-ejTXEFPE) set the
  bot on NAS100 and the point/lot sizing here is consistent with an index
- timeframe(s) taught: unstated in words (Part 2 established 5m; this video never
  restates the timeframe)

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **21 EMA** — this is the only indicator. He calls
  it "a simple EMA" at [1:57] and "my 21 EMA filter" at [5:04]; the optimizer
  settled on "the EMA was 21" at [2:42]-[2:46]. (He also loosely calls it "a
  simple moving average" at [6:20] — inconsistent wording, but the bot parameter
  is an EMA period.)
- Original idea (abandoned, did not work): **two-line strike** — "two bearish
  candles one bullish candle enter a trade opposite" for a short; opposite for a
  long ([0:19]-[0:24]). He could not get it to trade.
- Entry trigger (the version that actually runs), [0:33]-[1:01]:
  - **Sell:** every time a bearish candle prints subsequent to a bearish candle,
    i.e. **the low of the entry candle is below the low of the previous candle** →
    enter a sell at that candle.
  - **Buy:** mirror — a bullish candle whose **high is higher than the previous
    candle's high** → enter a long.
  - So it re-enters on every continuation candle, stacking entries down/up a leg.
- Trend filter, [2:03]-[2:15]: "if the candles were below the 21 EMA then it would
  enter a short position; if the bullish candle was below the 21 EMA it would not
  take the trade" — i.e. **only short below the 21 EMA, and long signals below
  the EMA are rejected.** He credits this with "eliminating one bad signal".
- Stop loss: **15 points** (optimizer result, [2:36]-[2:39]).
- Take profit: **50 points** (optimizer result, [2:39]) — so roughly **1:3.3 R**.
- Position size: **0.16 lots on a $100,000 account** ([2:39]-[2:42]).
- Session filter: settings expose a **start hour and end hour, each 0–23**
  ([1:44]-[1:52]). Optimized result: **"it only trades for one hour a day"**
  ([2:46]-[2:48]), and on the chart replay he says "this is the only time that it
  enters trades at about **6 a.m.**" ([5:09]-[5:11]) — timezone not stated
  (Part 2 used broker server time).
- Trades **every single day Monday through Friday** ([5:20]-[5:22]).
- Optimization procedure he prescribes ([2:18]-[2:35], [2:55]-[3:06]): optimize
  stop loss, take profit, lot size, EMA period, start hour, end hour — set a low
  value, a high value and an increment for each. Run on "opening price only"
  (minutes) rather than "every tick" (17–25 hours).
- Optimization-graph read: "by the end of the optimization graph you want to see
  a majority of the points up here" — clustered high, not sporadic ([3:13]-[3:20]).
  Sort results by profit, by drawdown, or by **profit factor — higher is better**
  ([3:29]-[3:37]).

## Reported backtest result (stated numbers)
- Backtest window **July 1 2022 → August 11 2023**, $100,000 start ([3:48]-[3:55]).
- Flat for ~3–4 months, took off "around November" ([4:03]-[4:12]).
- **+$81,635 profit**; **42 consecutive losses** producing **$10,000 drawdown**
  which "would have failed a challenge"; **halving lot size** → ~$40,000 profit
  and no challenge breach ([4:11]-[4:41]).
- Win rate: shorts 29%, longs 25% — "approximately a 25 to 30 percent win rate ...
  but because the risk to reward ratio is so good you can have a really low win
  rate and still have a profitable account" ([4:41]-[4:58]).

## Vague / untestable / chart-pointed claims
- [1:41]-[1:44] "as you can see right here you want in the settings a start hour
  and an end hour" — chart-pointed at an MT4 settings dialog; the actual optimized
  hour is only given later as "about 6 a.m." with no timezone.
- [5:04]-[5:18] "here is my 21 EMA filter and then this is the only time that it
  enters trades ... you can see all of these trades took profit down here and then
  this one got stopped out" — pure chart pointing, no extractable rule beyond what
  is listed above.
- [5:22]-[5:31] "take this information with a grain of salt because spreads during
  specific hours are different so you need to adjust that in your testing" — a
  caveat, no numeric spread assumption given.
- [6:01]-[6:02] "the more filters you add on your Bot the better it's going to
  perform" — unfalsifiable as stated (contradicts standard overfitting concerns,
  and he himself warns backtests decay at [5:33]-[5:38]).

## Notes on relation to other videos
- Direct continuation of **Part 2 (hr-ejTXEFPE)**, and it **replaces** Part 2's
  engulfing-candle entry entirely: the engulfing/3-candle definition is gone,
  swapped for the simpler "candle extends beyond previous candle's low/high"
  continuation entry, plus the 21 EMA and hour filters that Part 2 only floated as
  future ideas.
- Part 2's optimizer found stop/target tuning "insignificant"; here the same knobs
  optimize to SL 15 pts / TP 50 pts, so the numbers are only comparable after the
  entry logic change.
- He explicitly **refuses to distribute the bot** ([6:27]-[7:36]) — reasoning:
  liability, and crowding ("if you give it to a hundred thousand people it'll just
  stop working").

## Testability
- rating: HIGH (entry, trend filter, SL, TP, lot size and session-length are all
  numeric; the single gap is the timezone of the ~6 a.m. one-hour window)
- overlap: three-line-strike (the abandoned two-line-strike origin),
  candlestick-pattern / momentum-continuation entry, session-filter,
  5m-scalp(EMA trend filter), bot/automation
- notable quotes:
  - [0:33]-[0:41] "every time there was a subsequent bearish candle after a bearish
    candle meaning that the low of the entry candle was below the low of the
    previous candle it would enter a cell position"
  - [2:03]-[2:13] "if the candles were below the 21 EMA then it would enter a short
    position if the bullish candle was below the 20 EMA it would not take the trade
    thus eliminating one bad signal"
  - [2:36]-[2:48] "a stop loss of 15 points and a take profit of 50 points lot size
    was a 0.16 on a 100 000 account the EMA was 21 and it only trades for one hour
    a day"
