# The Best ATR Indicator for Setting Stoploss
- id: dfijk5dkito | views: 379000 | length: 471s
- market(s) shown: EURUSD (price ~1.1783 at time of recording)
- timeframe(s) taught: unstated — he says "your stop loss at this level right here on this timeframe" [3:01] without ever naming the chart timeframe

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  1. **Built-in TradingView "Average True Range"** — default settings kept, only the colour changed (red -> yellow) for visibility [1:56]-[2:14]. Reads out in pips.
  2. **"Average True Range Trailing Stops, colored by HPotter"** from the TradingView *public library* — "the second option down" when searching "average true range" [3:35]-[3:48]. Explicit inputs: **"the nATR is going to be 5 and the nATR multiplier is going to be 3.5"** [4:03]-[4:08]; inputs otherwise "keep exactly as they are"; style = 100% colour, second-thickest line on both red and green.
  3. **Three SMMAs (smoothed moving averages)** — search "SMA", add three times: **21 (white), 50 (blue), 200 (yellow)** [5:15]-[5:43]. He explicitly calls them "smoothed moving averages", i.e. SMMA not SMA.
- Setup/context required: "never ever, ever enter a trade without a specified stop-loss set into place" [0:53]. Direction must agree with the MA stack before entering — "you want to make sure you're going in the right direction before you place a trade" [6:40]; being long inside a strong downtrend is called "reckless" [6:20]. In a downtrend the stated correct action is "waiting for a rejection on the 50 line" [6:24].
- Entry trigger: **none defined.** No entry condition is given in this video; entries in the examples are asserted ("you would set your long position right here" [4:44]). Only forward-looking directional hint given: "if we break through this 50 moving average, your target can be this 200 moving average" [6:07]-[6:12].
- Stop loss: **two alternative rules, both stated numerically.**
  - Rule A (plain ATR): read the ATR value in pips, then **"do 1.5 or 2x what the ATR is telling you"** [2:45]-[2:52]. Worked example: ATR = 3.6 pips -> "stretch it to 7 pips" [2:55]-[2:59], so the ~2x variant is the one demonstrated.
  - Rule B (preferred): place the stop **below the green ATR-trailing-stop line when uptrending, above the red line when downtrending** — "I suggest above this line when it's downtrending... and below [it] when it's uptrending" [4:36]-[4:44]. Worked example gave a **13-pip** stop.
  - He states Rule B is better: "there are better ATR indicators versus you having to set the price manually just based on this line" [3:21]-[3:27], and "this does not work all the time" about Rule A [3:18].
- Take profit: **fixed 2:1 risk-reward** in both worked examples — 7-pip stop -> "14 pips" [3:09]-[3:16]; 13-pip stop -> "your take profit level is going to be 26 pips" [4:47]-[4:52]. Alternative use: **trail the ATR line as a trailing stop** and exit when it is hit — "keeping this as a stop-loss initially and then continuing using it as a trailing stop-loss... you would have only gotten stopped out right here" [6:56]-[7:08], claimed result "a 93 pip take profit" [7:19].
- Filters he adds: MA-stack trend filter only (price below 21/50/200 = downtrend, don't buy). No session, day-of-week or news filter mentioned.

## Vague / untestable / chart-pointed claims
- [2:30]-[2:40] "if you were to enter a trade with a stop loss more than 3.6 pips the likelihood of you getting stopped out is less" — asserted, no data; also which chart timeframe the 3.6-pip ATR came from is never stated, so the number cannot be reproduced.
- [2:45] "do 1.5 or 2x what the ATR is telling you" — two different multipliers offered with no rule for choosing between them; only the 2x version is demonstrated.
- [4:36] "I suggest above this line when it's downtrending or... below when it's uptrending" — the ATR-trailing-stop line already flips side with trend, so "above/below" is partly redundant; exact offset from the line is never given (0 pips? 1 pip?).
- [4:44] "you would set your long position right here" — entry point pointed at on the chart, no rule.
- [5:47]-[6:04] "we've been in a clear downtrend trading below all of the moving averages... now we are starting to break through the 21 and now we're starting to go up to the 50" — chart narration; "break through" is not defined (close beyond? touch? wick?).
- [6:24]-[6:34] "waiting for a rejection on the 50 line, which it's almost doing right here, actually might go up just above it and then start continuing down again" — "rejection" undefined; explicitly speculative.
- [6:47]-[7:08] "if you were to use this at any entry point in a clear and concise downtrend... you're doing really really well and you would have only gotten stopped out right here" — post-hoc chart narration on a single visible window, no trade count, no sample, no stats.
- [7:19] "that right there is a 93 pip take profit" — a single cherry-picked trailing-stop outcome from the same chart, presented as evidence.

## Testability
- rating: MEDIUM — the two stop-loss rules and the 2:1 target are fully specified with exact indicator settings (nATR 5, multiplier 3.5; 1.5-2x ATR), so the exit half is directly codeable. The gap is that **no entry rule exists at all** in this video, and the chart timeframe is never named, so a backtest must borrow entries and a timeframe from elsewhere.
- overlap: risk-management / stop-placement (ATR) + 5m-scalp(SMMA) MA stack (the same 21/50/200 SMMA set used across the channel) + a passing S/R-retest idea ("rejection on the 50 line")
- notable quotes:
  - [2:45] "what you want to do is do 1.5 or 2x what the ATR is telling you. So at this point the ATR is 3.6 pips. What you want to do is stretch it to 7 pips"
  - [4:03] "the nATR is going to be 5 and the nATR multiplier is going to be 3.5"
  - [4:47] "your stop loss would be below this green line which would be at 13 pips and your take profit level is going to be 26 pips"
