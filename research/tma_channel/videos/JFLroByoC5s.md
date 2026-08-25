# Best Scalping Indicator **EVER**
- id: JFLroByoC5s | views: 33000 | length: 170s
- market(s) shown: unstated (generic TradingView chart)
- timeframe(s) taught: unstated — no timeframe is ever named in this video

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **Heikin Ashi candles** (a chart type, not a paid indicator — the whole point of the video is that it is free) plus the **Fibonacci retracement tool**. His fib settings are dictated at [2:20]–[2:38]: levels **0, 0.382, 0.5, 0.618, 1, -0.5, -0.618, -1**, all coloured white **except the 0.5 which is red**. "this is all you're going to need ever."
- Setup/context required: A **big impulse move**. Drag the fib tool "from the top of the swing to the bottom of the swing in a downtrend and from the bottom of a swing to the top of a swing in an uptrend" ([0:28]). Then wait for a retracement into the **0.382-to-0.618 band** ([0:37]).
- Entry trigger: Switch the chart to Heikin Ashi (top toolbar > candle-type dropdown > Heikin Ashi) and, once price has retraced to any of the fib levels, **enter only on a Heikin Ashi candle with no upper wick** (short case): "enter only on these candles with no upper Wick" ([1:10]). For the continuation entries he generalises it as "the first hik and ashy candle with no Wick" ([2:02]).
- Stop loss: **never stated.** No stop rule appears anywhere in this video.
- Take profit: Primary/safest target = the **0 level**, i.e. where price extended the most (the swing extreme): "the safest Target for these Fibonacci trades is where price extended the most the zero level reason being is cuz we might make a double bottom" ([1:28]). At that level, either move take-profit/stop to break even or **cash out 50% of the position** ([2:08]). If price breaks through, hold for the **fib extensions -0.5 and -0.618** ([1:41]) for "potentially a 1 to three" ([1:49]).
- Filters he adds: **Depth-of-retracement rule** — "the deeper the retracement the better your risk to reward is going to be" ([1:20]), with three worked R values named: a shallow entry = **1:1**, deeper = **1:1.9**, deepest = **1:4** ([1:25]). **Trend-strength rule** for which fib level to expect: "the stronger the trend the shorter the retracement" ([0:40]). Continuation/re-entry rule: "every time price moves and breaks out of previous structure you take another FIB tool from the bottom to the top wait for price to retrace and get in on the first hik and ashy candle with no Wick" ([1:51]).

## Vague / untestable / chart-pointed claims
- [0:14] "you want a big impulse move" — no definition of "big" (no ATR, candle count, or % move threshold), and the swing high/low anchors are picked by eye.
- [0:40] "the stronger the trend the shorter the retracement" — "strength" is never measured; there is no rule mapping strength to 0.382 vs 0.5 vs 0.618.
- [1:14] "this is a good one this is a good one and this is a good one" — the three qualifying entry candles are pointed at on screen; the surrounding disqualified candles are not described. Frame-check needed to confirm what "no wick" tolerance he actually accepts (Heikin Ashi candles rarely have a literally zero-length wick).
- [1:25] The 1:1 / 1:1.9 / 1:4 figures are read off the chart for three specific entries; since no stop rule is given, these R values cannot be reconstructed.
- [1:51] "every time price moves and breaks out of previous structure" — "previous structure" is not defined (no swing-detection rule).
- [2:11] "cash out 50% of your trade however you want to set up your risk" — explicitly left to the viewer.
- [0:20] "you guys already know how to use FIB retracements I've taught it 500 times on this channel" — the fib mechanics are assumed from other videos; this video only adds the Heikin-Ashi entry trigger.
- The title says "indicator" but the video's actual content is a chart-type + drawing-tool combo; no indicator is installed.

## Testability
- rating: MEDIUM — the entry trigger (first Heikin Ashi candle with no wick against the trade direction, inside the 0.382-0.618 retracement) and the target (fib 0 level, then -0.5 / -0.618 extensions, 50% off at the 0 level) are codeable, and the exact fib level set is given. Blocking gaps: **no stop-loss rule at all**, and impulse-swing detection is discretionary.
- overlap: fib-scalp + candlestick-pattern (Heikin Ashi); same Heikin-Ashi-no-wick entry trigger he uses in "When to Enter a Trade - The Right Way" (HeNqrn_JO8k, [4:22]), where it is bolted onto a PD-array pullback instead of a fib retracement — the two videos share one entry primitive across different context filters.
- notable quotes:
  - [0:36] "you're going to want the price to retrace anywhere between the 382 and the 618 the stronger the trend the shorter the retracement"
  - [1:05] "once you do that and price has retraced to any of these Fibonacci levels I want you to enter only on these candles with no upper Wick"
  - [1:28] "the safest Target for these Fibonacci trades is where price extended the most the zero level ... but if it does break through these levels you're looking for FIB extensions to the ne[gative] .5 and the Nega[tive] 618"
