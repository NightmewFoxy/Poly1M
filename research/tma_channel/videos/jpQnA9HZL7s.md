# Trend Reversal Trading Strategy
- id: jpQnA9HZL7s | views: 283000 | length: 284s
- market(s) shown: unstated (chart pair never named; forex implied — profits quoted in pips)
- timeframe(s) taught: **1 minute** ([0:53] "this is on a one minute chart"), with an explicit warning that beginners should not trade it

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: three **smoothed** moving averages — **21, 50, 200** period ("not an exponential not a simple smoothed moving average", [1:09]-[1:32]). Plus the **"engulfing candle indicator" by RMUNOZ** from the TradingView public library ([2:31]-[2:36]) — prints small green/red arrows on engulfing candles.
- Setup/context required: An existing clear trend that is losing momentum, with price **breaking through** the moving averages rather than testing and rejecting off them ([1:56]-[2:02] "not testing it like it did here in the downtrend but breaking through the moving averages").
- Entry trigger: Wait for the **"curve"/"swoop" to appear in the moving averages in sequence** — first the **21** starts curving, then the **50** starts curving, then a **slight bow in the 200** ([2:18]-[2:27]). Once that three-MA curve sequence is present, enter on **any engulfing candle in the new trend's direction** ([2:27]-[2:52]; bearish engulfing for a down-reversal, bullish engulfing for an up-reversal).
- Stop loss: **not stated anywhere in this video.**
- Take profit: **not stated as a rule.** Only a cited outcome: "you could have nailed 20 pips out of this move easily that happened in 30 minutes" ([4:13]-[4:23]).
- Filters he adds: Do not attempt to predict the top/bottom — [3:54] "i don't suggest anybody try to predict the top of this market like you need to literally be nostradamus". No session, day or news filter given. Beginner filter: demo only / don't trade 1m if new ([0:55]-[1:05]).

## Vague / untestable / chart-pointed claims
- [2:03]-[2:27] "at this point you start seeing the moving averages swoop... you want to see the curve... you want to see it start in the 21 then start curving the 50 and then start seeing a slight bow in the 200" — the entire entry condition. "Curve", "swoop" and "slight bow" have **no numeric definition** (no slope threshold, no angle, no lookback, no cross requirement). This is the single load-bearing rule of the video and it is purely visual.
- [2:44] "an engulfing candle is a candle that completely eats the candle next to it in the opposite direction" — a definition, but "you could have gotten in on any of these engulfing candles" ([2:49]) means multiple valid entries with no selection rule.
- [3:05]-[3:20] "we have massive bearish momentum right here like these are big fat candles on a one minute chart and you can see the 21 is swooping the 50 is starting to curve and the 200 is starting to bow" — chart-pointed; "big fat candles" is not quantified (no ATR or pip threshold).
- [3:41]-[3:48] "if we play this out it keeps going down and the moving averages cross over one another that is the curve that you want to see" — here he equates the curve with an MA **crossover**, which would be mechanical, but it contradicts entering earlier on the curve-before-cross. Which of the two is the actual trigger is unresolved.
- [4:13] "you could have nailed 20 pips out of this move easily" — single hand-picked example, and with no stop rule the R is undefined.
- No stop loss, no take profit, no risk:reward, no session filter, no market named.

## Testability
- rating: LOW — the only entry condition ("see the curve in the 21, then 50, then 200") is a visual judgement with no numeric proxy given, and the video contains **no stop-loss and no take-profit rule at all**. A backtest would have to invent the slope definition, the stop and the target.
- overlap: 5m-scalp(SMMA) family (same 21/50/200 SMMA template, same RMUNOZ engulfing-candle indicator as the 1m scalping video), candlestick-pattern (engulfing entry), applied to trend-reversal rather than trend-continuation. Effectively the reversal counterpart of `-za-CIJbwxs` (1 Minute FOREX Scalping Strategy), which teaches the same tools but trend-following and *does* give a stop/target.
- notable quotes:
  - [2:18] "you don't want to see the curve in just one moving average you want to see it start in the 21 then start curving the 50 and then start seeing a slight bow in the 200"
  - [2:27] "at that point you can get on any engulfing candle"
  - [4:03] "when you start seeing a curve in the moving averages that's when you know the trend reversal is in effect"
