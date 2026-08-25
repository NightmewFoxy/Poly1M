# How to Trade Liquidity on the 5 Minute Chart Day Trading Strategy
- id: LD1FEbwXU4o | views: 99000 | length: 312s
- market(s) shown: AUDUSD — "that's when I was able to enter my trade at 61408 on Australian dollar" ([4:07], i.e. 0.61408)
- timeframe(s) taught: Daily / 4-hour for marking levels; 5-minute for entries ("drop to the 5minut or the 1 minute chart if you're feeling a little bit risky", [2:06]). This video is the lower-timeframe companion to an earlier daily-timeframe liquidity video, made in answer to a viewer comment ([0:05], [0:17]).

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **None.** Tools only: the horizontal-line/position tool for S/R levels, plus the standard **volume** panel. No moving average, no oscillator, no settings of any kind are named.
- Setup/context required: Four-step process, stated explicitly.
  1. **Mark higher-timeframe liquidity first** — "Start with the daily or the 4hour chart. Mark the most recent swing highs and lows and clean levels that haven't been tapped yet" ([1:36]). Use the horizontal tool to mark all S/R, then identify the **untapped** levels — "areas that have not been tapped yet where the liquidity should be living" ([2:00]).
  2. **Drop to the 5m (or 1m)** and wait for one of those marked levels to be hit.
  3. **Look for the trap** — "Price will often wick above resistance, pause, then dump or wick below support and reverse. That is your confirmation" ([2:54]).
  4. **Use volume or candles for entries** — "Look for exhaustion candles, long wicks, bearish or bullish engulfing or a volume divergence" ([3:19]).
- Entry trigger: Price rapidly approaches the marked HTF level, **volume spikes**, price gives **a quick tap and a rejection wick** through the level, and the rejection candle (in his worked trade, an **engulfing candle with wicks on both candles**) prints — enter on that rejection ([2:13]–[2:34], [3:56]–[4:07]).
- Stop loss: In the worked trade, "I kept my stop loss **below the current London low**" ([4:11]) — i.e. beyond the session extreme just made, not at the entry candle.
- Take profit: **1:2 risk-to-reward**, stated three times ([2:34], [2:48], [4:17]). No trailing, no partials.
- Filters he adds:
  - **Session filter:** "use session times like the London or New York open. That's when the most stop hunts happen" ([4:39]).
  - **Never pre-empt the level:** "avoid entering before the price taps the liquidity zone. Wait for confirmation" ([4:34]).
  - **Never chase breakouts:** "do not chase the breakouts. Wait for price to trap traders and fade the move" ([4:47]). The whole method is fade-the-breakout, not trade-the-breakout.
  - **Double-tap rule:** "if price rejects the same area twice, it could be a full reversal double bottom with the bar not closing below the area of support and resistance that you marked up and getting another trade 1:2 risk-to-reward ratio" ([2:38]) — i.e. a second entry is allowed on the second rejection, conditional on **no candle closing beyond the level**.
  - Context used in the worked example: a **weekend gap** at the week's open left price below a marked daily support, biasing him long ([3:39]–[4:32]).

## Vague / untestable / chart-pointed claims
- [1:18] "The key is to look for clean price action that's just a little too clean. equal highs, trend lines, or zones that look perfect. That's the bait." — "too clean" / "look perfect" is pure aesthetic judgement; no tolerance for what counts as equal highs (in pips or ticks).
- [1:43] "clean levels that haven't been tapped yet" — no rule for how far back to look, how many levels to mark, or what counts as "tapped".
- [2:13] "Look for price rapidly approaching a zone. You want to see **volume spike**" — no volume threshold (multiple of average, lookback) is given.
- [2:16] "a quick tap, and a rejection" — "quick" and "rejection" are undefined; no wick-to-body ratio, no maximum number of bars spent at the level.
- [3:22] "Look for exhaustion candles, long wicks, bearish or bullish engulfing or a **volume divergence**" — four alternative triggers offered with no priority and no definition of the volume divergence.
- [4:07] The entry price 0.61408 is given but the stop and target prices are not, so the actual R of the worked trade cannot be reconstructed.
- [4:11] "below the current London low" — well-defined only if you fix the London session boundaries, which he never states here.
- [3:34]–[3:56] The level markup, the gap, and the approach are all narrated by pointing at the chart; the specific daily level he used is never given as a price. Frame-check needed.
- [0:44] "Market makers push price into liquidity to fill large orders. Period." — narrative rationale, not a testable rule.

## Testability
- rating: LOW — every step is a judgement call: which levels to mark, what counts as untapped/clean, what a volume spike is, what a rejection looks like. Only the exits are hard (1:2 R; stop below the session low). A backtest would have to invent the level-selection logic, which is the entire edge as described.
- overlap: S/R-retest and liquidity-sweep/stop-hunt (fade-the-breakout) family; secondary session-filter (London/NY open) and candlestick-pattern (engulfing, exhaustion wick) elements; explicitly the lower-timeframe sequel to his daily-timeframe liquidity video.
- notable quotes:
  - [1:13] "Your job, find where the obvious trades are sitting, and do the opposite."
  - [2:21] "you are simply waiting for one of these levels to be hit and then you're looking for that rejection wick ... you can get into your scalping trade and get a 1 to 2 risk-to-reward setup"
  - [4:47] "do not chase the breakouts. Wait for price to trap traders and fade the move."
