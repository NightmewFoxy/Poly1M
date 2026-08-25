# How to Make a Trading Bot Part 2
- id: hr-ejTXEFPE | views: 102000 | length: 407s
- market(s) shown: NAS100 (stated at [2:58] and [3:59]); MT4 strategy tester
- timeframe(s) taught: 5m (entry/execution timeframe, stated repeatedly)

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: none in the working version. Only candlestick
  price action (engulfing definition below). He mentions at [6:30] that a moving
  average filter *could* be added ("whether price is above or below a specific
  moving average") but does not specify one for this bot.
- Setup/context required: default trading window 08:00–14:00 **server time**
  ("8 AM to 1400 server time so 8 AM to 2 PM", [1:07]-[1:13]) — made adjustable
  in the EA settings. Timezone is broker server time, not stated in UTC.
- Entry trigger (attempt 1, the one he prompted ChatGPT with at [1:15]-[1:37]):
  - Buy: a bullish engulfing 5m candle that **engulfs the previous two candles**;
    order entered at current market price; trade only fires **once the 5m candle
    has closed**.
  - Sell: mirror — bearish engulfing candle engulfing the previous two candles.
  - Explicit 3-candle definition given at [3:21]-[3:40]: "the total calculations
    are for three candles and based on the high open low close of the candles.
    Bullish engulfing candle: the first five minute candle is bearish, second
    candle is also bearish, and the third candle's closing price is higher than
    the highest price of the first candle in the series of three candles.
    Opposite for bearish engulfing."
- Entry trigger (attempt 2, the version that finally compiled and traded,
  [4:04]-[4:12]): "if a bullish engulfing five minute candle closes enter a Buy
  trade at the current ask price"; sell rules exact opposite. Lot size 0.01
  (spoken "zero one" for lot size — [4:10]).
- Stop loss:
  - Attempt 1: buy SL = **lowest price of the entry candle**; sell SL = **highest
    price of the entry candle** ([1:39]-[1:45]).
  - Attempt 2: fixed **1000 ticks** for both buy and sell ([4:15]-[4:18]).
    He notes 1000 ticks ≈ 10 points on NAS ([5:26]-[5:30]).
- Take profit:
  - Attempt 1: **2× the stop loss** (2R) for both buy and sell ([1:45]-[1:48]).
  - Attempt 2: fixed **2000 ticks** = 2× the 1000-tick stop ([4:18]-[4:21]).
- Risk sizing: "risk one percent of account balance per trade", bot auto-computes
  from balance ([0:56]-[1:02]) — in attempt 1 only; attempt 2 uses fixed 0.01 lots.
- Optimization grid he actually ran ([5:24]-[5:52]):
  - Stop loss: start 500 ticks (5 points), step 100 ticks (1 point), up to
    15 points.
  - Take profit: start 10 points, step 100 ticks (1 point), up to 5000 ticks
    (50 points).
  - Model = **"opening prices only"**, justified because "our bot trades on the
    closing prices so it doesn't need every tick" ([5:58]-[6:06]).
- Filters he adds: trading-hours window only (see above). Result of optimization:
  "a bunch of passes ... discarded as insignificant which means there's no benefit
  in adjusting the stop loss and the take profit" ([6:09]-[6:18]).

## Reported backtest result (not a rule, but a stated number)
- [4:53]-[5:09]: initial deposit $100,000, ended **-$53,649**, **74 consecutive
  losses**, 27% win rate on shorts, 30% on longs. He calls it "absolutely horrible."

## Vague / untestable / chart-pointed claims
- [6:22]-[6:34] "all we have to do is add code ... to give it more parameters for
  trading, for example the trading hours whether it's 8 AM to 11 A.M or whether
  price is above or below a specific moving average" — MA length/type never given;
  the 8–11 window is floated as an example, not a rule.
- Server time is the reference timezone for 08:00–14:00 but the broker/server
  offset is never stated, so the window is not reproducible without knowing the
  broker.
- "zero one" lot size at [4:10] is ambiguous between 0.01 and 0.1; transcript is
  literal "zero one".

## Testability
- rating: HIGH (fully mechanical — every entry, stop, target and session number is
  numeric; only the server-time offset and the optional MA filter are unspecified)
- overlap: candlestick-pattern (engulfing), session-filter, bot/automation
  (three-line-strike adjacent — the "engulfs previous two candles" definition is
  effectively a 3-candle strike variant)
- notable quotes:
  - [1:15]-[1:25] "for a Buy trade if a bullish engulfing candle prints that
    engulfs the previous two candles then the bot will enter buy order at the
    current market price the trade will only happen once the 5-minute candle is
    closed"
  - [1:39]-[1:48] "the stop loss for a buy will be the lowest price of the entry
    candle ... the take profit will be two times the stop loss for both buy and
    sell trades"
  - [3:23]-[3:37] "bullish engulfing candle the first five minute candle is
    bearish second candle is also bearish and the third candle's closing price is
    higher than the highest price of the first candle in the series of three
    candles"
