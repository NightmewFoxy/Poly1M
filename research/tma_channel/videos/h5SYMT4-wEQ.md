# Fibonacci Trading With Divergences Tutorial
- id: h5SYMT4-wEQ | views: 18000 | length: 287s
- market(s) shown: GBPUSD [2:02] and AUDUSD (named as the reverse-correlated pair — "Australian dollar, US dollar" [2:16-2:21])
- timeframe(s) taught: unstated

## Mechanical rules (only what the video actually states)
The densest mechanical video in this batch. Three distinct setups.

- Indicators + exact settings: RSI (length NOT stated) + Fibonacci retracement tool. Levels named explicitly: **0.5, 0.618, 1**. He shows his fib tool settings on screen twice and says "These are my Fibonacci tool settings. You can take a screenshot. And then this is the bottom half of the settings" [1:10-1:20] — the actual values are NOT spoken, so they must be recovered from the video frames.
- Setup/context required: a trending market. Regime note: "September to November is like follow the trend type of trading. Never trade against the trend" [0:12-0:25]. Core reframe of the whole video: after a REGULAR divergence, do not expect a full reversal — "instead of looking for regular bullish or bearish divergences and expecting a full-on reversal, I want you to expect a pullback into a Fibonacci zone and a continuation" [0:25-0:37].

**Setup 1 — regular BEARISH divergence, traded as a continuation (long side, GBPUSD uptrend):**
- Signal: "we made higher highs, but if you look at the RSI, the RSI made a lower high. This is a regular bearish divergence" [0:43-0:50].
- Then: wait for the pullback, "draw your Fibonacci tool from the bottom to the top of the move" [1:04-1:10].
- Entry: "set up a limit order right here" [1:31] — placed in the gold zone (the 0.5-0.618 band, made explicit in Setup 2).
- Stop loss: "put your stop loss between the one and the 618. Eyeball it right in the middle" [1:31-1:38].
- Take profit: "target the previous high point in an uptrend" [1:38-1:44].
- Result: "This is going to give you a 1:2 risk-to-reward ratio because you're anticipating a double top, not a full-on continuation" [1:44-1:50].

**Setup 2 — regular BULLISH divergence, mirrored short (AUDUSD downtrend, reverse-correlated to GBPUSD):**
- Signal: "price made a lower low while the RSI made a higher low" [2:16-2:28].
- Fib drawing: "draw your fib tool from the top of the move to the bottom of the move, **including the wicks**" [2:28-2:33].
- Entry: "Place a limit order between the 0.5 and the 618" [2:33-2:38].
- Stop loss: "with your stop loss between the 618 and the one" [2:38].
- Take profit: "your take[profit] is going to be the previous low" [2:38-2:45].
- Result: "Again, that's going to get you a 1:2 risk-to-reward ratio" [2:45].
- He calls these "A++ golden setups" [2:45-2:52].

**Setup 3 — HIDDEN divergence, trend continuation:**
- "follow our trend line and draw Fibonacci retracements every single time that price breaks previous structure" [3:03-3:10].
- Signal definition, spelled out: price made "our original high, a lower high, a lower high, and a lower high", while the RSI made "our original high, a lower high, a lower high, and a **higher** high. Price made a lower high, RSI made a higher high. This is a hidden bearish divergence in a downtrend" [3:29-3:54].
- "If you just inverse it, that's how it's going to look for a hidden bullish divergence" [3:54-4:01].
- Entry rule: "If you're in a trend continuation trade and you see one of these and the RSI spikes and makes a higher high in a downtrend, game over. A++ trading setup" [4:01-4:14].
- Confluence noted: all the pullbacks "retraced relatively close to the Fibonacci gold zone before they continued down in the original trend" [3:17-3:29].
- Stop/target for Setup 3: NOT stated (presumably inherits the fib rules above, but he doesn't say so).

- Filters he adds: trend direction only ("Never trade against the trend" [0:18-0:25]); a seasonal note (Sept-Nov = trend-following season) [0:12-0:18]; reverse-correlation awareness — "While GBPUSD is trending up, reverse correlated pairs like Australian dollar US dollar are going to be trending down" [2:09-2:21].

## Vague / untestable / chart-pointed claims
- [1:10-1:20] "These are my Fibonacci tool settings. You can take a screenshot." — the settings are shown, never spoken. **Frame-check required** to recover them; without them the exact fib level set is unknown (though 0.5 / 0.618 / 1 are named in speech).
- [1:31-1:38] "Eyeball it right in the middle" — the stop is explicitly eyeballed rather than pinned to a level (approximately the 0.809 midpoint of 0.618-1.0, but he never says that).
- [1:31] "set up a limit order right here" in Setup 1 — chart-pointed; the exact level is only inferable from Setup 2's "between the 0.5 and the 618".
- [1:38-1:44] "target the previous high point" — which previous high (the divergence high? an earlier swing?) is shown but not defined verbally.
- RSI length/period is never stated in the entire video — a hard blocker for exact reproduction, though 14 is the platform default.
- [0:12-0:25] "September to November is like follow the trend type of trading" — a seasonality claim with no data, and it also silently date-limits the whole lesson.
- [1:50-1:55] "what usually happens is like a liquidity sweep or a double top and then price consolidates" — asserted frequency, no measurement.
- [3:03-3:10] "every single time that price breaks previous structure" — "previous structure" undefined.
- [2:45-2:52] "These are A++ golden setups" and [4:06-4:14] "game over. A++ trading setup" — grading language with no win rate or expectancy attached.
- Setup 3 has no stop-loss or take-profit rule at all.

## Testability
- rating: HIGH (Setups 1 and 2 are fully mechanical: divergence definition, fib anchors including wicks, limit entry in 0.5-0.618, stop between 0.618 and 1.0, target = previous swing extreme, 1:2 RR. Only two gaps: the unstated RSI length and the "eyeball the middle" stop precision — both easily parameterised for a backtest.)
- overlap: regular-divergence + hidden-divergence + fib-scalp — this video is the join between all three families. Combines with bCX4YgXUQYs's gold-zone definition (0.5-0.618) which is stated identically here.
- notable quotes:
  - [2:28-2:45] "draw your fib tool from the top of the move to the bottom of the move, including the wicks. Place a limit order between the 0.5 and the 618 with your stop loss between the 618 and the one, and your take[profit] is going to be the previous low."
  - [0:25-0:37] "instead of looking for regular bullish or bearish divergences and expecting a full-on reversal, I want you to expect a pullback into a Fibonacci zone and a continuation"
  - [3:44-3:54] "Price made a lower high, RSI made a higher high. This is a hidden bearish divergence in a downtrend."
