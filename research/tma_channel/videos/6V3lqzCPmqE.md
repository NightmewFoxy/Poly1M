# RSI Divergence Trading Strategy
- id: 6V3lqzCPmqE | views: 185000 | length: 417s
- market(s) shown: US30 (Dow); brief mention that the same eye goes to RSI on any pair
- timeframe(s) taught: **15-minute for analysis, 1-minute for the entry** — "I did all of my analysis on the 15 minute and then to find my sniper entry I got down to the one minute" [5:11]-[5:20]. He explicitly warns off the 1m as a standalone: "I don't suggest everybody trade on the one minute chart, it's super volatile and nine times out of ten you'll get stopped out" [4:34]-[4:42]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **RSI**: TradingView built-in "Relative Strength Index", **length left at default** (never changed on screen), colour -> yellow, and the key change: **"you're going to change the upper band to 50 and the lower band to 50"** [2:18]-[2:24], background removed. So the RSI is used as a single **50-level** midline, not 70/30.
  - **Moving averages: 50 and 200, plus 21** — "first we're gonna do the 50 and the 200, let's just do the 21 for good measure" [1:22]-[1:27]. Type (SMA/EMA/SMMA) is never stated in this video; he calls the 21 "the 21 day moving average" [5:26] on a 15m chart, which is loose wording.
- Setup/context required:
  1. A **clear prior trend** on the entry-direction's opposite side — "lower lows and lower highs means a clear and concise downtrend" [2:49]-[2:53], price trading below the 21.
  2. **Momentum loss / consolidation** after that trend — "we started to consolidate and I was like cool, we're losing momentum; what happens when you lose momentum, the price tends to go the opposite direction" [1:46]-[1:58].
  3. Price **far extended away from the MAs on the 15m** — "you can see how massively far away we were from these moving averages, and what does price like to do? Price likes to go back to moving averages when it's over-extended" [5:02]-[5:12].
- Entry trigger: a **regular bullish RSI divergence, but only a repeated/"extremely clear" one, confirmed by RSI crossing above 50.** Stated in three parts:
  - Divergence definition: price makes **lower lows** while RSI makes **higher lows** [3:26]-[3:32].
  - **Reject the first divergence.** "yes we are creating a higher low on the RSI and creating a lower low on the price action but the price still continued to go down; I like to wait until the RSI divergence is extremely clear — like look at this: a low, a higher low, a higher low, a higher low" [3:26]-[3:44]. So he wants a **series of at least three consecutive higher RSI lows**, not a two-point divergence.
  - **RSI must break above the 50 level**: "then we break above the 50 level; when the RSI is above the 50 level that's showing bullish momentum, that means it's no longer bearish" [3:45]-[3:55].
  - Then a **final retest down** ("it came down one more time" [3:55]) and the entry is taken on the upward slope of the RSI. Executed fill: **32,372** [4:08].
  - **Second entry (add-on):** after price moved in his favour it pulled back and printed "this big long rejection wick" — he entered again at **32,417** [4:20]-[4:30]. "Big long rejection wick" is not quantified.
- Stop loss: **never stated.** No stop rule, no stop price, no R multiple appears anywhere in this video.
- Take profit: **the 21 moving average measured on the 15m chart**, placed slightly inside a round number. "I had previously marked up my levels of where that previous moving average was and I actually just took it up to the 21 day moving average which was just around 32,500, and so I know that with even numbers market likes to hesitate so I did it two dollars below" [5:20]-[5:44]. So: **TP = the 21 MA level, minus $2 if that level sits on a round number.**
- Filters he adds:
  - Round-number avoidance: exit **$2 short of an even number** (US30 dollars) [5:34]-[5:44].
  - Trend-alignment before the divergence hunt: he only looks for divergence once trend momentum is dying, not during the trend ("going with the trend is extremely easy... this is so easy to make money off of" [1:04]-[1:16] describes the prior phase, not the divergence trade).
  - Explicit scope limit: this is a **scalp**, not a swing — "that's not my strategy, I was in it for a scalp, I wanted a quick move, take my money, walk away" [6:11]-[6:17].
- Result reported: lot size **0.02 on US30**, two trades, **$251 and $161 = ~$400**, held overnight into market close [5:44]-[5:59].

## Vague / untestable / chart-pointed claims
- [3:35]-[3:44] "I like to wait until the RSI divergence is extremely clear" — "extremely clear" is the entire filter that separates the losing divergence from the winning one, and it is qualitative. He demonstrates it as three-plus consecutive higher RSI lows on the chart, but never states that as a rule.
- [3:55]-[4:04] "it came down one more time just to [mess] with people and that's when I saw this nice sloping upward and I was like cool, I'm getting in right here" — the actual entry candle is pointed at; "nice sloping upward" has no threshold (slope over how many bars?).
- [4:20]-[4:30] "came down and we got this big long rejection wick, I got in on another position at 32,417" — wick length undefined (no ATR multiple, no body:wick ratio).
- [1:46]-[1:58] "we started to consolidate" — consolidation never defined (no range width, no bar count).
- [5:02]-[5:12] "you can see how massively far away we were from these moving averages" — "massively far away" not quantified (no % distance, no ATR-from-MA measure). This is load-bearing: it is the reason he expects mean reversion to the 21.
- [5:20]-[5:34] "I had previously marked up my levels of where that previous moving average was" — the target is taken from a *previously marked* 15m MA level rather than the live MA value, so the TP is a hand-drawn horizontal, not a computable MA read.
- [2:26] RSI "background is useless" and default length never spoken aloud — the RSI **length must be inferred as 14 (TradingView default)**; the video never says the number.
- **No stop loss is given anywhere.** Any backtest must supply one, which materially changes the result.
- [6:00]-[6:11] "why didn't you hold that, you could have made so much more" — post-hoc discussion of the bigger move he missed; not a rule.

## Testability
- rating: MEDIUM — entry has three concrete, codeable conditions (price lower low, RSI higher low, RSI crosses above 50) plus a stated multi-swing repetition, and the TP rule (the 21 MA, minus $2 at round numbers) is concrete. Two real gaps: **no stop loss at all**, and the "extremely clear divergence" / "over-extended from the MAs" qualifiers are discretionary.
- overlap: regular-divergence (this is the channel's canonical RSI-divergence video, referenced as the missing piece of the scalping video) + 5m-scalp(SMMA)-style MA mean reversion for the target + multi-timeframe (15m context / 1m trigger)
- notable quotes:
  - [2:18] "you're going to change the upper band to 50 and the lower band to 50... and that's what your RSI should look like"
  - [3:35] "I like to wait until the RSI divergence is extremely clear, like look at this: a low, a higher low, a higher low, a higher low, and then we break above the 50 level"
  - [5:26] "I actually just took it up to the 21 day moving average which was just around 32,500, and so I know that with even numbers market likes to hesitate so I did it two dollars below"
