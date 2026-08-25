# 1 Minute FOREX Scalping Strategy
- id: -za-CIJbwxs | views: 535000 | length: 562s
- market(s) shown: AUDUSD ([0:49] "australian dollar us dollar one of my favorite currency pairs to trade")
- timeframe(s) taught: **1 minute** only; trades last 5-7 minutes ("in and out in five six seven minutes max", [9:06])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - Three **smoothed** moving averages: **21, 50, 200** ([1:30] "the 21 period the 50 period and the 200 period smoothed moving average"; at [1:52] he reads the inputs back as "250 and 21", i.e. 2-00, 50 and 21).
  - **Stochastic RSI** with settings **3, 3, 14, 8** ([2:04] "you are going to change these settings to 3 3 14 and eight") — i.e. K=3, D=3, RSI length=14, Stochastic length=8 in TradingView's field order.
  - **Engulfing candle indicator by RMUNOZ** from the TradingView public library ([2:11]-[2:21]).
- Setup/context required:
  - **Directional bias from the 200 SMMA**: [2:24] "if we are above this 200 moving average we are looking for long positions if we are below it we are looking for short positions".
  - **Second bias filter from the Stochastic RSI midline**: draw an imaginary line halfway; trading **below the midline = sell positions only**, above = buys ([5:01]-[5:11]). He explicitly rejects using StochRSI as overbought/oversold.
  - **Structure must be formed** in the trade direction: consistent **lower lows and lower highs** for shorts ([4:11]-[4:18]).
  - **Momentum requirement**: the move must be at roughly a **45-degree angle** ([8:11]-[8:19] "you'll be able to tell the momentum because it'll be at about a 45 degree angle... more of a flat you don't want to trade that").
- Entry trigger: A **"trap"** — a fake bounce off a moving average or a resistance zone that looks like continuation in the wrong direction — followed by a **big engulfing candle in the trade direction**, entering **only on the close of that engulfing candle** ([5:53]-[6:22] "when the candle closes only when the candle closes because it could be this huge fat candle but then at the last second reject up and you get this really long wick").
- Stop loss: **2.5 pips** with a 5-pip target (2:1 R), or the "super safe" variant **5-pip stop / 5-pip target (1:1)** ([5:38]-[6:04]). Requires a tight broker spread — he says a **1 pip spread** is workable and warns the spread will hurt a 2.5-pip stop.
- Take profit: **5 pips, then exit** — [5:16] "i want you to get into a position to get five pips and then gtfo". Cited examples: 5 pips in 5 minutes, 5 pips in 7 minutes; four such trades = 20 pips in 26 minutes ([7:30]-[7:44]).
- Filters he adds:
  - **Session filter: London.** [2:58] "do not test this strategy at times that you do not trade i trade the london session maybe an hour before"; [3:21] "i usually do not get in until london session has opened and has been about 15 minutes into the session". **No timezone or clock time is given** — "London session" only.
  - **Stop when consolidation starts**: [6:49] "if you are consolidating if you see a loss of momentum get out because this is not scalping you can't scalp when it's consolidating".
  - **One big move per day only**: [6:28] "you do not want to use this strategy for the entire day you are waiting for the one big move of the day".
  - **Trend-following only for beginners** — reversal attempts are an advanced extension ([7:47]-[8:02]).
  - Demo first until consistently profitable.

## Vague / untestable / chart-pointed claims
- [2:33]-[2:51] "you are looking for the traps to be set... a potential bounce off of a moving average or hitting a resistance zone making it look like it's going in one direction and then a huge engulfing candle as the fake out" — "trap" has no numeric definition; the resistance zone is drawn by eye. This is the entry condition, so it is the biggest gap.
- [2:53] "you have to wait for that big engulfing candle" — "big" is unquantified (the RMUNOZ indicator would fire on any engulfing candle, so an extra size filter exists but is unspecified).
- [3:28]-[3:41] "when you see huge red candles like this that's a clear indication that there might be some momentum... so i waited a bit and then i waited and it broke through these moving averages" — chart-pointed; how long "a bit" is, is not stated.
- [4:11] "now we're waiting for structure to be formed... you want to see lower lows consistently and lower highs consistently" — no swing-detection rule or minimum number of swings.
- [4:30]-[4:39] "technically you could have traded off of any one of these engulfing candles" — multiple valid entries, no selection rule.
- [5:01] "if i draw an imaginary line halfway in between" the StochRSI — the midline value is not spoken (50 on a 0-100 StochRSI), and the line is drawn by hand.
- [6:40]-[6:47] "we were consolidating from this point to this point and that is one hour and six minutes without a trade" — chart-pointed consolidation definition.
- [8:05] "you should be getting about an 80 win rate when the momentum is going like this" — unsupported claim, no sample, and conditional on the undefined momentum state.
- [8:11] "about a 45 degree angle" — angle on a chart is scale-dependent and therefore not a real, reproducible measure.
- [8:20]-[8:35] "when you get more advanced you can actually see when it's playing along the moving averages and then rejecting off of them... i got 10 pips out of this one move" — a different (non-engulfing) entry mentioned in passing with no rules.
- Session filter has **no clock times and no timezone**, so it must be pinned externally.

## Testability
- rating: MEDIUM — indicator settings, both bias filters, entry-on-close-of-engulfing, and the stop/target (2.5/5 pips, or 5/5) are all exact and numeric, which is unusually complete for this channel. The discretionary gaps are the "trap" pattern, the "big" qualifier on the engulfing candle, and the consolidation/45-degree momentum screen.
- overlap: 5m-scalp(SMMA) family (21/50/200 SMMA + RMUNOZ engulfing indicator), candlestick-pattern (engulfing entry), session-filter (London), market-structure (LL/LH requirement). Same toolkit as `jpQnA9HZL7s` (Trend Reversal) but trend-following, and unlike that video this one **does** give a stop and a target. He refers to it repeatedly elsewhere as "the most lethal one minute forex scalping strategy".
- notable quotes:
  - [5:16] "i want you to get into a position to get five pips and then gtfo"
  - [5:38] "you set it to five pips and you set your stop loss at two and a half pips"
  - [2:24] "if we are above this 200 moving average we are looking for long positions if we are below it we are looking for short positions"
