# How to Make a Trading Bot Part 1
- id: MJ2WL4ld3Fo | views: 507000 | length: 635s
- market(s) shown: none specific — the EA is deliberately written in **ticks, not pips or points**, so it can be tested "on anything" [6:05]-[6:14]
- timeframe(s) taught: **5-minute** — stated explicitly and repeatedly: "all of this will happen on a five minute time frame... because I want this to be a scalping bot" [1:37]-[1:52]

## Mechanical rules (only what the video actually states)
This is a ChatGPT -> MQL4 EA build tutorial, and the strategy he dictates to the AI is fully specified as if/then logic. He names it himself: **"it's like a three-line strike that I've taught on this channel, but it's a two-line strike"** [3:13]-[3:19].

- Indicators + exact settings: **10 EMA** — the only indicator. Named at [2:16], [3:02], [7:49], [7:56]. No other indicator, no MA type ambiguity (explicitly EMA).
- Setup/context required: price on the correct side of the 10 EMA. He frames it as trend continuation: "if it's above the 10 EMA you want it to take long positions because it's a trend continuation; if it is below the 10 EMA it's also a trend continuation, a downtrend" [7:47]-[8:01].
- Entry trigger — a **two-candle "two-line strike" engulf, on the 5m, filtered by the 10 EMA**:
  - **BUY:** "first there must be two five-minute bearish candles and then the third candle must be bullish and close above the highest price of both the previous candles" [1:52]-[2:02] **AND** "the bullish candle close is above the 10 EMA" [2:16]-[2:19] -> **enter buy at market price** [2:19]-[2:22].
  - **SELL:** "there must be... two five-minute bullish candles and then the third candle must be bearish and close below the lowest price of the two previous bullish candles" [2:41]-[2:54] **AND** "the bearish candle closes below the 10 EMA" [2:59]-[3:04] -> **enter sell at market price** [3:04]-[3:06].
  - Note his live self-correction at [2:54]-[2:57]: he says "highest price — sorry, lowest price" for the sell condition; the intended rule is **below the lowest of the two prior bullish candles**.
  - Execution basis: **candle close, not tick** — in the strategy tester he selects "opening prices only because we are doing it on candle closures not when a tick happens" [6:20]-[6:25].
- Stop loss: **one tick beyond the entry candle's extreme.**
  - Buy: "a stop loss one tick below the entry candle['s] lowest price" [2:22]-[2:37] (he adds "lowest price" as an explicit clarification: "I've added lowest price because you need to be hyper specific" [2:35]-[2:37]).
  - Sell: "a stop loss one tick above the entry candle's highest price" [3:06]-[3:11].
- Take profit: **2R, measured in ticks** — "the take profit again should be two times what the stop loss is in ticks" [3:11]-[3:13]. Confirmed in the recap: "the take profit was two times the risk — stop loss down here, take profit up there" [8:14]-[8:24].
- Filters he adds:
  - **Trading-hours window, default 8:00 AM to 1:00 PM server time**: "by default I want it to have trading hours between 8 AM and 1 PM server time" [3:52]-[3:58]. Rationale given: "most bots fail during non-market hours... especially if it's an EA crossover, because during Tokyo session it just like does this and it doesn't really work that well" [3:58]-[4:12].
  - **Default lot size 0.01**: "in the settings the trade size for each trade — by default I want it to be 0.01 lots" [6:47]-[6:55] (added after the first test placed no trades because size was never specified).
  - All parameters must be **exposed as adjustable EA inputs** for optimisation: stop loss in ticks, take profit in ticks, and the active time-of-day window [3:44]-[3:52].

## Build/optimisation workflow stated (the other half of the video)
- MetaTrader -> Tools -> MetaQuotes Language Editor -> New -> Expert Advisor -> tick "OnChartEvent" and "OnTester" -> delete the generated template [0:30]-[1:08].
- Paste ChatGPT's code -> Compile -> paste the compiler errors back to ChatGPT -> repeat. Shown live: **9 errors -> 3 errors -> 0 errors** [5:00]-[5:45].
- Test window used in the demo: **July 1 to July 31** of that year, model = "opening prices only", account $100,000 [6:14]-[6:31].
- Optimisation: give each input a start value, an end value and a step increment, then run the optimisation icon; sort results by highest profit [9:09]-[10:02].
- Honest caveats: his own real bot **"took about six months of coding back and forth"** [7:32]-[7:36] and has "like a good 400 versions" [8:46]-[8:49]; "the results won't be that great" on first compile [9:06]-[9:09]; and don't over-parameterise — "don't do too many because you won't be able to strategy test it... it'll say it's too many parameters" [4:18]-[4:39].

## Vague / untestable / chart-pointed claims
Very few — this video is unusually rule-complete because it is dictating to a compiler. The gaps:
- **The "third candle" wording is loose.** He says "there must be this specific series of three five-minute candles" [1:43] but then defines only two bearish candles plus one bullish — so the "third" candle *is* the entry candle. Ambiguous whether the two prior candles must also satisfy any condition relative to the 10 EMA (never stated).
- **Whether the engulf must exceed both prior candles' highs by close or by the candle's high** is stated as close ("close above the highest price of both the previous candles" [1:57]) — but "highest price" of a candle could mean the high or the body top; not disambiguated.
- **No market or pair is ever specified**, and no spread/commission assumption is mentioned anywhere — the backtest is run cost-blind.
- **"Server time" [3:56] has no timezone attached** — the 8 AM-1 PM window is broker-dependent and therefore not reproducible across brokers.
- **No results are reported.** The bot never places a trade in the video ("just as I thought, it's not entering any trades" [6:41]-[6:44]), and after the lot-size fix he never shows a backtest result. The video ends on "it might not work great but it might work enough for you to have a little bit of passive income" [10:30]-[10:33].
- [8:01]-[8:12] "because I'm amazing at graphic design, this is what it should have looked like" — the pattern is shown as a hand-drawn diagram rather than a chart instance; the rule is stated in words so this is illustrative, not load-bearing.
- [9:38]-[9:55] "it will back test every single minute variation of your bot using different settings to give you the best results... you can sort that by highest profit" — brute-force parameter search recommended with **no out-of-sample or walk-forward step mentioned at all**. This is the video's biggest methodological hole, and it directly contradicts the discipline he shows later in HCiMznnYMiI ("does this actually survive when tested on the data we haven't seen?").

## Testability
- rating: **HIGH** — entry (2 opposite-colour 5m candles + engulfing close beyond both extremes + close on the correct side of the 10 EMA), stop (1 tick beyond entry candle extreme), target (2x stop in ticks), timeframe (5m), session window (08:00-13:00 server) and size (0.01) are all stated numerically. Only downgrades: no pair, no timezone anchor for "server time", no cost model, and no reported results.
- overlap: **three-line-strike** (explicitly — he calls this a "two-line strike" variant of the three-line strike he teaches elsewhere) + **candlestick-pattern** (engulfing) + **session-filter** (8 AM-1 PM server) + 5m scalp with a 10 EMA trend filter. Note the MA here is a **10 EMA**, not the channel's usual 21/50/200 SMMA stack.
- notable quotes:
  - [1:52] "first there must be two five-minute bearish candles and then the third candle must be bullish and close above the highest price of both the previous candles... and the bullish candle close is above the 10 EMA, then enter a buy trade at market price with a stop loss one tick below the entry candle['s] lowest price"
  - [3:11] "the take profit again should be two times what the stop loss is in ticks, so it's like a three-line strike that I've taught on this channel, but it's a two-line strike"
  - [3:52] "by default I want it to have trading hours between 8 AM and 1 PM server time, so most bots fail during non-market hours"
