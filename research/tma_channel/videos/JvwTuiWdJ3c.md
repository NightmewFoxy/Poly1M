# Heikin Ashi Divergence Strategy
- id: JvwTuiWdJ3c | views: 27000 | length: 228s
- market(s) shown: unstated (generic chart; a range from "December 20th last year" to "today" is shown at [0:55])
- timeframe(s) taught: 15-minute (primary) and 1-hour ("a quick and simple strategy that's going to work on the 15minute and the 1 hour time frame", [0:16]); "the 1 hour is more for swing trading I like 15 minute" ([1:22])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **RSI** — length never stated, but the levels are: **70 / 30** ("divergences that are within the 7030 range", [1:41]) and RSI is described as a momentum indicator. **Heikin Ashi candles** for the entry trigger. Cosmetic but explicit: recolour candles to **yellow = bullish, white = bearish** instead of red/green — "your brain does weird psychological things when you see red and green fear anxiety" ([0:34]–[0:48]).
- Setup/context required: A **trending, non-flat market**. "when price is trading in a Range like this for a long period of time ... what I want you to look for is nice trending Market ... when markets are flat it's boring and dangerous" ([0:49]–[1:16]). Then look for the trend to be exhausting.
- Entry trigger (three conditions, stated together at [3:32]): "you're looking for a **Divergence**, a **failure to make a higher high or a lower low**, and your **first hik and ashy candle with no Wick**."
  1. **Regular bearish divergence**: price makes a higher high while RSI makes a lower high — "we created another higher high while the RSI made a lower high ... a lower high in an uptrend is what we call a loss of momentum" ([2:02]–[2:14]). The divergence must sit **within the 70/30 RSI band** ([1:41], [2:38]).
  2. **Structure confirmation**: price then **fails to make a higher high** ([2:35]).
  3. **Entry candle**: switch to Heikin Ashi; enter on the first **bearish candle with no wick on top** — "that is your entry point" ([2:53]–[3:01]). (Long side is the mirror: failure to make a lower low + bullish HA candle with no bottom wick, by symmetry — he only spells out the short case.)
- Stop loss: "an entry here with a **stop loss above here**" ([3:09]) — pointed at the chart, evidently above the recent swing high / the rejection high. Not stated in words as a rule.
- Take profit: **1:2 risk-to-reward** as the default — "all you're going to do is a 1 to two risk to reward ratio that's all you will ever need if you do that consistently you will make money" ([3:11]). Alternative discretionary exit: "hold these trades until you see your first bullish candle or the first candle that changes color", which on his example gave **1:2.4** ([3:21]–[3:31]).
- Filters he adds: RSI must have been "overbought overextended for a long period of time" before the divergence ([1:33]); the divergence itself must be inside the 70/30 range; skip long-ranging/flat markets entirely.

## Vague / untestable / chart-pointed claims
- [1:33] "the RSI is going to be overbought overextended **for a long period of time**" — no bar count or duration threshold.
- [1:44] "I bet we can find an example right here if we use our highlighter tool on these high points I bet we could find a Divergence in between at least two of these" — the divergence swing pair is chosen by eye after the fact; no swing-detection rule (fractal size, lookback, minimum separation) is given. This is the classic divergence-mining problem.
- [1:41] "divergences that are within the 7030 range" — ambiguous as spoken: it could mean the RSI pivots must be *outside* 70/30 (overbought/oversold) or that price has come back *inside* the band. At [2:38] he says "we are now trading within the 7030 range of the RSI right here at this point I am looking for short positions", implying the *entry* happens once RSI re-enters the band. Frame-check needed.
- [2:35] "once this happened and we failed to make a higher high right here" — chart-pointed; how long you wait for that failure is undefined.
- [3:03] "this right here is the first candle that rejected from here had a no Wick candle" — chart-pointed. Also, a Heikin Ashi candle with a literally zero-length wick is rare; the tolerance he accepts is only visible on screen.
- [3:09] "an entry here with a stop loss above here" — the stop is purely chart-pointed; no verbal rule.
- [3:21] "hold these trades until you see your first bullish candle or the first candle that changes color" — conflicts with the 1:2 fixed target given ten seconds earlier; he offers both without saying which to use.
- [3:41] "back test it let me know what your results are" — he has not backtested it himself; no stats are claimed.

## Testability
- rating: MEDIUM — RSI divergence + failure-to-make-a-new-high + first-no-wick-Heikin-Ashi-candle + fixed 1:2 R is close to fully mechanical, but RSI length is never given, the swing-pair selection for the divergence is eyeballed, and the stop is only pointed at.
- overlap: **regular-divergence** (price HH / RSI LH) — the channel's core divergence family — combined with candlestick-pattern (Heikin Ashi no-wick entry) and market-structure (failure to make a higher high). The Heikin-Ashi-no-wick entry primitive is the same one used in HeNqrn_JO8k ([4:22], PD-array context) and JFLroByoC5s ([1:10], fib-retracement context); this video attaches it to divergence instead.
- notable quotes:
  - [3:32] "it's a very simple recipe you're looking for a Divergence a failure to make a higher high or a lower low and your first hik and ashy candle with no Wick"
  - [2:02] "we created another higher high while the RSI made a lower high showing us a very important thing a lower high in an uptrend is what we call a loss of momentum"
  - [3:11] "all you're going to do is a 1 to two risk to reward ratio that's all you will ever need if you do that consistently you will make money"
