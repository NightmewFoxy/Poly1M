# RSI Divergence Trading Strategy
- id: K7vFNn7fZ7Y | views: 670000 | length: 778s
- market(s) shown: EURUSD (the worked example's pip count is stated on "euro usd", [10:13])
- timeframe(s) taught: **15m** primary ("a nice middle of the range time frame", [2:40]); 1m allowed only with higher-timeframe (30m/1h/15m) top-down analysis first

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: three **smoothed** moving averages — inputs **21, 150, 200** ([1:32] "the first one 21 the next 150 the next one 200"). NOTE: he says 150 here, but later in the same video refers to "the 50 moving average" ([7:02]) — see contradiction note below. RSI: built-in, **length 14, source close**, with the **upper band and lower band both changed to 50** ([1:46]-[2:05]) so the RSI shows a single 50 line instead of 70/30.
- Setup/context required: A trend in place making higher highs / higher lows (for the short case), i.e. a staircase up, with divergence forming at the top of the range. Explicitly requires waiting out strong momentum — he shows RSI travelling 18 → 89 in one swing as an example of momentum too strong to fade ([4:54]-[5:18]).
- Entry trigger: **six confluences must all be present** before entering (his own count, [8:30]-[8:57] and [9:44]):
  1. Price making **higher highs** (bearish case);
  2. RSI making **lower highs** — the divergence;
  3. A **break of market structure** (price falls below the prior higher low, killing the staircase);
  4. **Break below the moving averages with a retest** of one (he describes breaking the 21 SMMA, retesting it, then cascading below the 50);
  5. **RSI trading below the 50 level** ([7:14] "the rsi level finally got below the 50 level showing a downtrend");
  6. A **three-line strike**: three consecutive candles in one direction followed by an engulfing candle in the opposite direction ([9:07]-[9:16]).
  Actual fill: **on the close of the engulfing candle of the three-line strike** — [9:26] "once this candle closes you get in right here".
- Stop loss: **never stated** in this video. The only stop discussion is of other people getting stopped out above the swing high.
- Take profit: **"ride this sucker down until you're satisfied with your profits"** ([9:30]) — discretionary. One alternative given: **target the 200 moving average** ([10:03] "you could have actually targeted the 200 moving average on this trade"). The worked example is quoted at **45 pips** on EURUSD ([10:16]).
- Filters he adds: Patience filter — do not enter on the divergence alone; the momentum-strength filter (if the RSI just ran ~18→89, go *with* it, don't fade it). For 1m use: same rules exactly, but start analysis on 30m/1h/15m first to avoid trading against the higher-timeframe trend ([10:55]-[11:15]).

## Vague / untestable / chart-pointed claims
- [1:32] "21 the next 150 the next one 200" vs [7:02] "below the 50 moving average" and [6:56] "breaking through the 21 period moving average" — the middle MA is stated as **150** in setup but referred to as **50** during the analysis. Every other video in this channel family uses 21/50/200; this is likely a misspeak at [1:32] but cannot be resolved from the transcript. Needs a frame check of the indicator panel.
- [4:32]-[4:52] "how do you avoid getting in right here and then getting stopped out right here... wait... patience is very important" — the core "how long to wait" instruction has no numeric form (no candle count, no minimum divergence swing separation).
- [5:35] "you have to wait even longer just to avoid the trap" — undefined amount of extra waiting, purely discretionary, and the sole answer to the strategy's central failure mode.
- [4:54]-[5:06] "the rsi went from an 18 up to an 89 in one big swoop... that's momentum" — a single example; no threshold is given for how large an RSI excursion disqualifies a fade.
- [6:37]-[6:47] "we've had a higher high right another higher high and a higher low and another higher high all of which have an rsi divergence attached" — chart-pointed swing labelling; no swing-detection rule (fractal size, lookback) is stated, so "higher high" and "lower high" are eyeballed.
- [8:00] "if you can get a retest on a moving average with that downtrend i mean you are a safe bet" — "a" moving average is unspecified (21? 50/150?); the retest is chart-pointed.
- [9:30] "until you're satisfied with your profits" — no exit rule; makes the strategy unbacktestable as stated unless the 200-MA target ([10:03]) is adopted.
- [9:33]-[9:40] "in this one trade if you're looking at rsi divergence you got stopped out three times... but if you were patient... you had six confluences" — the loss count comes from an unstated stop placement.
- No stop-loss rule is given anywhere in the video, so R multiple is undefined.

## Testability
- rating: MEDIUM — the confluence stack is unusually explicit and 5 of the 6 items are near-mechanical (divergence, RSI<50, MA break+retest, BOS, three-line strike close entry), but there is **no stop rule at all** and the exit is "when satisfied", plus the 150-vs-50 MA ambiguity. Fully specifying it requires two invented parameters.
- overlap: regular-divergence (primary), plus three-line-strike, market-structure/BOS, S/R-retest (MA retest), 5m-scalp(SMMA) chart template. He cross-references his market-structure video and his "trading off of the moving averages" videos as prerequisites ([8:14], [9:51]).
- notable quotes:
  - [7:47] "the confluences that you're looking for is higher highs on the price action lower highs on the rsi with a break below the 50 level to show that the trend is actually reversing"
  - [9:07] "a three-line strike is three subsequent candles in one direction and then an engulfing candle in the opposite direction... once this candle closes you get in right here"
  - [1:56] "you need to change the upper band and the lower band to 50"
