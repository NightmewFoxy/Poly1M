# How to Backtest PROPERLY
- id: R3T1zRyZdMc | views: 494000 | length: 1116s
- market(s) shown: EURUSD ([0:48] "let's jump into the charts and take a look at euro usd")
- timeframe(s) taught: **5 minute** ([7:53] "i'm on a five-minute chart"); trading window is a London-session block

## Mechanical rules (only what the video actually states)
This is a **methodology** video (how to backtest), but it contains a full worked trade with explicit rules.

### Backtest methodology (the actual subject)
- **Only backtest during the hours you actually trade.** [2:12] "you should only be back testing your strategy at the time that you actually trade". His stated reason: the London session's signals differ from New York's, and the Asian session "is mostly consolidation so there's no point in back testing your strategy at that time" ([2:06]).
- **Draw two vertical lines** on the chart marking the start and end of your daily trading window, and repeat this bracket for **100 trading days** ([2:57]-[3:19], [11:19] "i want you to do that 100 times").
- His own window: **London open until about lunchtime**; concretely in the worked example he starts analysis around **7:00-7:20 a.m. chart time**, market open at **9:00 a.m.**, and the window ends around **12:00 p.m.** ([8:26], [8:51], [12:47] "from 7 am to 12 or whatever your trading window is"). **Timezone never stated** — chart-local time only.
- **Use TradingView bar replay**, not a static chart, so future candles are hidden ([4:22]-[4:36], [5:42]-[6:23]). Replay speed set to roughly one candle per 1-2 seconds.
- Sample-size argument: 100 tests give a real win/loss rate; "if you back test it five times and then go full cowboy on it odds are it's gonna be a lower percentage than you anticipated" ([4:04]).
- **Rules-based only:** [14:27] "you have specific rules that you set up and you do not get into a trade unless that trade meets all of your rules". No-trade days are expected and correct.
- **Progression:** 100 backtests → if the win rate and risk:reward are acceptable → **forward test on demo for 1-2 weeks** trading only in those hours → if profitable ("in the blue"), go live ([17:53]-[18:06]).
- **Daily targets/limits:** a daily profit goal (he cites "2 percent today or four percent today") and a **daily loss limit of 1%**; when either is hit, stop for the day ([3:15]-[3:29]).

### The strategy demonstrated inside the backtest
- Indicators + exact settings: **21 and 200 moving averages** (he calls them "the 21 day moving average" / "the 200 moving average" on a 5m chart; type not stated here). A 21/200 crossover is used as the strawman example at the start ([1:02]).
- Setup/context required: **Trading below the 21 = shorts only; above the 21 = longs only** ([7:28] "now that we're trading below the 21 day moving average i'm only pretty much looking for short positions"). Direction is decided during pre-market analysis and written down ([8:37]-[8:43]).
- Entry trigger — the **trap/fake-out pattern**: do not trade a big directional spike; wait for the **opposite candle**, and **if that opposite candle is engulfing, that is the trap — enter in the engulfing candle's direction** ([9:26]-[9:38] "wait until you see the opposite candle... if that opposite candle is engulfing that's a trap and you should go in the opposite direction"). In the worked example: an 8 a.m. bullish spike bounced off the 200 MA, ran up on long green wicks, then printed a **big bearish engulfing** → short.
  - Second entry type shown in a later day ([16:24]-[16:34]): **rejections off the 21** in the direction of the new trend, targeting the 200.
  - Also required before entering a fresh break: **break and retest** — [14:18] "it might actually come back up and test the 21 day moving average if we have that break and retest and then a continuation on the downside then we can get in on a short position if not you do not trade that day".
- Stop loss: **deliberately wide at the open** because of morning volatility ([10:32] "i'm keeping my stop loss quite large at this point because there's a lot of volatility in the market in the morning"), placed a **comfortable distance beyond the previous swing** so wicks can't take it out ([16:38] "keeping my stop losses at a nice distance away from previous lows... you put it a nice comfortable distance below"). Then **moved to the 200 MA / into profit (breakeven+) once the trade is running** ([12:08]-[12:32] "you can actually set your stop loss to a little bit in profit that way this trade is zero risk whatsoever").
- Take profit: Multiple, in priority order as stated:
  1. A pre-set pip goal — the worked example's original target was **50 pips** ([12:44]), with "20 pips 30 pips" cited as reasonable ([10:44]).
  2. **Exit on a break of market structure / onset of consolidation**, even if the target isn't hit — [11:30] "once market structure is broken that's when you want to get out of a trade"; he closes at +25-30 pips on that basis.
  3. **Hard time exit: close at the end of your trading window**, never hold overnight ([12:44]-[13:14] "it is now the end of our trading day... right now we're up 30 pips close your trade take your profits").
  4. In the later example, **target the 200 MA** from a 21-MA entry, accepting **1:1 R** because the 200 was close ([16:47]-[17:02]).
- Filters he adds: London-session window only; **one pair at a time** ([14:02] "because i only trade that pair"); **no-trade when consolidating** — MAs close together / 21 near the 200 is "a clear sign of consolidation" ([15:26]-[15:35], and a whole 7am-12pm window that moved only **19 pips** is skipped, [15:41]-[15:51]); don't trade the exact market open because of open fluctuation ([8:56]).

## Vague / untestable / chart-pointed claims
- **No timezone anywhere.** "7 a.m.", "9 a.m.", "12" and "london opens" are all chart-local and never pinned to GMT/UTC or a broker server time. Any reproduction has to guess.
- [3:23] "i'm only willing to lose one percent per day" vs "i wanna make you know two percent today or four percent today" — the daily limits are illustrative, not prescribed.
- [9:14]-[9:22] "you want to see these like big spikes in one direction and wait" — "big spike" unquantified.
- [9:33] "if that opposite candle is engulfing that's a trap" — engulfing is definable, but which spike qualifies as the setup and how many candles may intervene is not stated.
- [10:32] "i'm keeping my stop loss quite large" / [16:38] "a nice comfortable distance below" — the stop distance is never given in pips or ATR. Since take profit is partly R-based, this makes R indeterminate.
- [11:41]-[11:50] "i'm seeing market structure right here being respected creating you know lower highs and lower lows but right here i'm starting to see a little bit of consolidation so at this point you could close your trade" — the exit is a visual judgement; "a little bit of consolidation" has no rule.
- [13:52]-[13:59] "when it's consolidating like this i tend to not trade it... so i wait until i see that rejection and spike in that direction" — chart-pointed no-trade filter.
- [15:26] "look at how close this 21 moving average is to the 200 this is a clear sign of consolidation you want to see a nice fan out" — no separation threshold.
- [16:24] "i see these rejections start to happen right here here and here so i'm placing a trade right here on the 21 moving average" — "rejection" undefined (same gap as `G5jeEqP3wlo`).
- MA **type** is never stated in this video (elsewhere on the channel: smoothed). He also says "21 day moving average" while on a 5m chart — sloppy naming, not a real daily MA.
- [17:09] "two of them i did not trade at all and two of them were winners" — he demonstrates **4 days, not the 100 he prescribes**, and reports 2/2 wins. No losing trade is ever shown, which is exactly the cherry-picking the video criticises.
- **Contradiction with `G5jeEqP3wlo`:** that video says "do not look at previous market structure" and to set-and-forget a 1:2 R; here the exit is explicitly driven by market-structure breaks and manual early closes.

## Testability
- rating: MEDIUM — as a **backtest protocol** it is highly actionable and near-mechanical (session-bracketed windows, replay-only, 100 samples, then demo forward-test, then live), and it is the channel's clearest statement that signals must be filtered by trading hours. As a **strategy**, the demonstrated trades are LOW: entry depends on undefined "big spikes"/"rejections", the stop is "comfortably" wide with no number, and the exit mixes a pip target, a discretionary structure-break close, and a time stop.
- overlap: session-filter (the video's central thesis), market-structure/BOS, S/R-retest / break-and-retest, candlestick-pattern (engulfing trap entry), 5m-scalp(SMMA) family (21/200 MA bias). Cross-references his scalping video twice as the strategy being tested ([8:09], [14:52] "i'm going to scalp between these moving averages").
- notable quotes:
  - [2:12] "you should only be back testing your strategy at the time that you actually trade"
  - [3:36] "for every single trading day that you do you want to set up two vertical lines in the time range that you're actually on the charts trading and i want you to do that 100 times"
  - [9:33] "if that opposite candle is engulfing that's a trap and you should go in the opposite direction"
