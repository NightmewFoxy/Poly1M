# How to Trade Gold - Ride Massive Trends Using this Method
- id: MKJz4yURCEs | views: 501000 | length: 450s
- market(s) shown: **Gold / XAUUSD** ("this is gold on the daily time frame", [2:52]). Bonus tip names US30 and GBPJPY as other suitable trending pairs ([6:43]).
- timeframe(s) taught: **Daily** for direction, structure and S/R; **1-hour** for entries ([1:00]–[1:11])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **None.** The method is chart-type + drawing tools only: **Heikin Ashi candles** (the calculation is explained at [1:35]–[1:44]: average of the previous period's OHLC, with the current open = average of the previous open and close), the **line chart** used as a markup aid, and the **horizontal line tool** for S/R. Optionally **TradingView alerts** for opposite-colour HA candle closes ([7:02]).
- Setup/context required:
  1. Daily chart, **switch to a line chart** to mark S/R — "completely ignore these candles and change your chart to a line chart. Then you will use your horizontal tool to mark up areas of support and resistance where price bounced off of it or broke through it and then used it as support" ([3:01]–[3:19]).
  2. Confirm current price sits **between a marked resistance and a marked support** ([3:28]).
  3. Switch the chart to Heikin Ashi and read momentum by **body size**: "The larger sized hyenashi candles means very strong momentum and the smaller-sized hyenashi candles means very weak momentum" ([2:03]).
  4. Trend-exhaustion sequence to watch for: large same-colour bodies, then shrinking bodies, then **a HA candle with wicks on BOTH top and bottom**, then opposite-colour candles growing in size ([2:14]–[2:32]).
- Entry trigger: **The first Heikin Ashi candle of the colour change that has no wick on the trade-direction side, entered on that candle's close.** Long: "bullish candles with no wicks on the bottom" ([6:32]). Short: "what you should be waiting for here is a bearish hike and ashy candle with no wick on the top. You can enter in a trade once that candle closes" ([4:25]–[4:31]). "The first hike and ashy candle in the color change is the one that you want to be looking at, but more specifically the one that has no wick on the bottom. That's going to be a strong beginning of the new trend" ([2:32]–[2:43]).
- **Explicit entry checklist** ([5:11]–[5:29]): (a) the **daily** chart must show an uptrend; (b) the breakout must be **above daily resistance**; (c) the **1-hour** Heikin Ashi candle closes with **no bottom wick**; (d) **strong body size** ("a little bit larger, showing momentum"); (e) price is **not in the middle of a consolidation zone**.
- Stop loss: **Not stated as a placement rule.** The only stop content is optional trailing: "You can tighten your stoploss after major swings are formed. This is basically creating a comfortable trailing stop-loss" ([6:05]) — flagged as optional.
- Take profit: **No target at all — exit is signal-based.** "Exit only when an opposite color hyenashi candle closes. Ignore small pullbacks as long as the candle stays bullish" ([5:55]–[6:02]); restated at [6:38] "exit only when the hyenashi candle closes in the opposite color". No R multiple, no level target. Holding rule while in the trade: "you're simply holding the trade as long as you get bearish candles. You keep holding the trade" ([4:34]).
- Filters he adds:
  - **Trending instruments only** — "Stick to trending pairs like gold, like US30, and probably even GBP JPY. Try to avoid ranging markets. If you're looking at an asset class that's just trading sideways for days, weeks, and months, this is not going to work for you" ([6:43]–[7:00]).
  - **Multi-timeframe confirmation of continuation**: if the 1h trend stalls at a marked daily support and candles turn, go back to the daily — "if you see another gigantic no wick bearish candle, you can hold the trade until the next day" ([4:56]–[5:08]).
  - Double-top context in the worked example: "this price rejected this level of resistance twice, creating a double top and this showing our first no wick candle as a trend reversal. This is our potential entry" ([3:49]–[4:03]).
  - **Bonus execution tip:** "You can use small pending orders just above that no-wick candle high. That way, you don't miss the faster breakouts" ([5:31]).
  - Behavioural rule after entry: "You do absolutely nothing. You patiently wait until those hyenashi candles tell you that it's time to exit" ([5:45]).

## Vague / untestable / chart-pointed claims
- **No stop-loss placement rule is given anywhere** — the biggest hole. Without it the strategy has no defined risk and no R can be computed.
- [5:21] "**strong body size**, meaning a little bit larger, showing momentum" — no threshold (no ATR multiple, no % of average body).
- [5:27] "price is **not in the middle of a consolidation zone**" — consolidation is never defined numerically.
- [5:14] The checklist contradicts the worked example: the checklist is written entirely long-side ("daily must show an uptrend", "breakouts above daily resistance", "no bottom wick"), while the trade actually demonstrated at [4:25] is a **short** off a daily double top with a no-top-wick bearish candle. The two are mirror images but he never reconciles them, so the daily-trend condition's direction is ambiguous.
- [3:11] Marking S/R "where price bounced off of it or broke through it and then used it as support" — level selection is discretionary; no rule for how many touches, how far back, or level tolerance.
- [4:07] "if we're looking at the current time right here, it's 9:00 a.m." — timezone not stated, and no session filter is actually part of the rules.
- [2:36] "the one that has no wick on the bottom" — Heikin Ashi candles rarely have a mathematically zero wick; the tolerance he accepts is only visible on screen. Frame-check needed. (Same undefined tolerance as JFLroByoC5s and JvwTuiWdJ3c.)
- [4:43]–[4:54] "you know that this downtrend is losing momentum and price may find support at this zone" — chart-pointed, no rule.
- [6:07] "tighten your stoploss after major swings are formed" — "major swing" undefined; explicitly optional.
- No backtest, win rate, or trade count is claimed anywhere in the video — he ends with "Try this method out and let me know how it goes" ([7:14]).

## Testability
- rating: MEDIUM — entry (first opposite-colour 1h Heikin Ashi candle with no wick on the trade side, closing above/below a marked daily level) and exit (first opposite-colour HA close) are fully mechanical and would code in a few lines; the "no wick" tolerance, "strong body size", the daily S/R markup, and the **complete absence of a stop rule** are the gaps.
- overlap: candlestick-pattern (**Heikin Ashi**) trend-following + S/R-retest, on a daily/1h multi-timeframe frame. This is the swing-trading, exit-on-colour-change relative of the same **HA-no-wick entry primitive** used in HeNqrn_JO8k ([4:22], PD array), JFLroByoC5s ([1:10], fib retracement) and JvwTuiWdJ3c ([2:53], RSI divergence) — four videos, one entry trigger, four different context filters. Uniquely, this video pairs it with a **signal-based exit instead of a fixed R multiple**, which contradicts the fixed 1:2 default given in JvwTuiWdJ3c and LsCAATCjF3Y.
- notable quotes:
  - [2:32] "The first hike and ashy candle in the color change is the one that you want to be looking at, but more specifically the one that has no wick on the bottom. That's going to be a strong beginning of the new trend."
  - [5:55] "Here are your exit rules. Exit only when an opposite color hyenashi candle closes. Ignore small pullbacks as long as the candle stays bullish."
  - [5:11] "Here is your checklist. The daily charts must show an uptrend. The breakouts must be above the daily resistance. The 1-hour hike and aashy candles closes with no bottom wick. strong body size ... and that price is not in the middle of a consolidation zone."
