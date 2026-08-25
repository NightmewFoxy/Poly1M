# Heikin Ashi Scalping Strategy
- id: ITi9HRzS__E | views: 333000 | length: 364s
- market(s) shown: unnamed; quoted in **points** not pips and traded via **MT4** [2:30]-[2:33], so likely an index/CFD — the instrument is never stated
- timeframe(s) taught: **15 minute** — "with this one trade on a 15 minute time frame that's 160 points with a 46 point stop loss" [3:03]-[3:09]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  1. **Heikin Ashi candles** — chart type switched from Japanese candlesticks to HA [1:45]-[1:53]. He states the HA formula explicitly at [1:13]-[1:29]: close = a quarter of (open + high + low + close); high = the maximum of the high, open or close; low = the minimum of the low, open or close; open = half of (previous open + previous close).
  2. **50 period moving average** — "add a **50 period** moving average, whether it's **exponential or smoothed it does not matter**, it's whatever your preference is, just to give you a basic indication of what the trend is" [1:53]-[2:03]. So: length 50, type deliberately unspecified/free.
- Setup/context required: **Trade with the 50 MA slope.** "as you can see the line is going down we are in a downtrend, we should be looking for short positions" [2:05]-[2:11]. Two trade types are taught:
  - **Trend continuation:** price crosses through the 50 and **rejects off the 50** — "with trend continuation trades you can basically take any time that it rejects off of the 50" [3:31]-[3:38].
  - **Trend reversal (counter-trend scalp):** a **break and retest of a trend line** — "what i want you guys to look for is a break and a retest of a trend line, breaking the trend line coming down to retest" [4:17]-[4:25].
- Entry trigger: **The first no-wick Heikin Ashi candle; enter on the OPEN of the NEXT candle.** Stated three times:
  - [2:18]-[2:30] "as price crossed through the 50 and rejected off of the 50 we are looking for that **first no wick candle** to form; once it is formed, **on the open of the next candle you enter your position**, pull up your MT4 and click sell or buy."
  - [3:45]-[3:50] "you wait for the first no wick bullish candle to form and then you get in on the next one."
  - [4:56]-[5:01] "you wait for the first no-wick candle, get in on the next one."
  Rationale given: "if you look at hike and ashy candles and you see a no-wick candle that is a change of momentum... that is a definitive one candle: hey, this is your entry" [5:22]-[5:46].
  Preceding shape he wants: "having a nice smooth move up as we start getting smaller candles and then we get a no wick candle — that is your signal to get ready to enter" [1:31]-[1:45].
- Stop loss: **switch the chart back to normal Japanese candlesticks to place stops and targets** [2:33]-[2:41].
  - Continuation trade: stop **at the 50 MA** — "what i want you to do is target that 50 as your stop loss" [2:45]-[2:50]. Example: **46 point stop** [3:05]-[3:09].
  - Reversal trade: stop **on the trend line** — "set your stop loss on that trend line" [5:03]-[5:06]. Example: **64 point stop** [5:09]-[5:11].
- Take profit:
  - Continuation trade: **look left, find the previous swing, and put TP where price has crossed the most — not at the absolute edge of it** [2:50]-[3:00]; restated as "simply just target the previous swing low" [3:57]-[4:00]. Example: **160 points** on a 46-point stop [3:05]-[3:09] (~3.5R).
  - Reversal trade: target is **the 50 MA** — "catch the retest of that trend line and get the move up to the 50, because you're not sure if it's going to go past it but you know it should go to it" [4:33]-[4:45]. Example: **177 point take profit** on a **64 point stop** [5:09]-[5:11] (~2.8R).
  - Management: **set and forget** — "set your trade and leave it, don't look at it" [3:09]-[3:12].
  - Optional scale-out: "close **80 to 90 percent** of your trade at your first take profit level and then basically trailing stop loss the rest **until you start seeing the opposite color** being formed" [4:02]-[4:15]. (Opposite-colour HA candle = the trail exit.)
- Filters he adds:
  - Continuation trades are valid on **any** 50-MA rejection **"as long as there was no big divergence beforehand"** [3:31]-[3:41] — divergence is a veto, but no indicator or setting for it is given here.
  - Reversal trades: **only take the retest if the distance from the trend line to the 50 is big enough.** "if that move is big enough — for example this break of the trend line and the 50 was too small, this one is too small, but this one had a nice decent move in it" [4:47]-[4:57]. No minimum distance is given.
  - Scope framing: this is a scalp, not a reversal thesis — "this is scalping, not expecting a full-blown trend reversal to the moon" [4:25]-[4:33].
  - The optional trail requires confidence "in that momentum move" [4:00]-[4:04].
  - Expected behaviour after a correct entry: "usually your move will happen all in one solid color of heikin ashi — it'll all be red or it'll all be green" [3:20]-[3:29].

## Vague / untestable / chart-pointed claims
- [1:53]-[2:03] "whether it's exponential or smoothed it does not matter" — leaves the MA type genuinely unspecified; EMA(50) and SMMA(50) give different rejection points, so the backtest must fork.
- [2:18]-[2:22] "as price crossed through the 50 and rejected off of the 50" — "rejected off the 50" is never defined (touch? wick through? close back across? within how many pips?). This is the main discretionary gap in the continuation setup.
- [2:50]-[3:00] "just look left, find that previous swing, your take profit level should be right where the price has crossed the most, not at the absolute edge of it" — chart-pointed; no lookback window, no volume tool, no numeric offset from the swing extreme.
- [3:38]-[3:41] "as long as there was no big divergence beforehand" — divergence indicator, length, and "big" are all unstated; unbacktestable as written.
- [4:17]-[4:25] "a break and a retest of a trend line" — the trend line is drawn by eye; no anchor rule, no break definition (close vs wick).
- [4:47]-[4:57] "this break of the trend line and the 50 was too small, this one is too small, but this one had a nice decent move in it" — pure chart selection; the filter that decides which reversal setups to take has **no threshold at all**.
- [4:02]-[4:15] "close 80 to 90 percent" — the split itself is a range, and "if you feel really confident in that momentum move" makes the whole scale-out discretionary.
- [1:31]-[1:45] "as we start getting smaller candles and then we get a no wick candle" — the shrinking-candle precondition is unquantified (how many? how much smaller?), though the no-wick candle itself IS mechanical.
- [5:14]-[5:17] Explicitly declines to fully specify: "i'm gonna allow you guys to do your own research on this one because i really don't want to make a 45 minute video on how hike and ashy candles work."
- Cross-reference: builds on his earlier Heikin-Ashi **swing trading** video [0:28]-[0:35], [5:48]-[5:53]; this one adapts the same no-wick concept to scalping.

## Testability
- rating: MEDIUM (the entry trigger is unusually crisp and fully mechanical — first no-wick HA candle, enter next open — and the stop levels are objective, 50 MA or trend line; the gaps are the MA type being left free, the undefined "rejection off the 50", the eyeballed trend line, the "big enough move" reversal filter, and the visual TP placement)
- overlap: candlestick-pattern (Heikin Ashi no-wick trigger) + moving-average-rejection trend filter + trend-line break/retest; TP-at-most-traded-price echoes the volume-profile idea without the tool
- notable quotes:
  - [2:22] "we are looking for that first no wick candle to form; once it is formed, on the open of the next candle you enter your position"
  - [1:53] "add a 50 period moving average, whether it's exponential or smoothed it does not matter, it's whatever your preference is, just to give you a basic indication of what the trend is"
  - [5:22] "if you look at hike and ashy candles and you see a no-wick candle that is a change of momentum... that is a definitive one candle: hey, this is your entry"
