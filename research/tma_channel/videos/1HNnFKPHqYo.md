# Bearish Candlestick Patterns (that work) - Day Trading
- id: 1HNnFKPHqYo | views: 68000 | length: 269s
- market(s) shown: unnamed (results quoted in pips, so FX); TradingView charts
- timeframe(s) taught: unstated for the demo chart. Only remark on timeframe: dark cloud cover is "better on the daily time frame for swing Traders" [1:51]-[1:59], which he says he does NOT trade.

## Mechanical rules (only what the video actually states)
This is a pattern-catalogue video, not a full strategy. The one place it becomes a system is the "10 pip box" demo at the end.
- Indicators + exact settings: TradingView built-in **"All Candlestick Patterns"** indicator. Exact setup he gives [2:55]-[3:30]:
  1. Indicators tab -> type "all patterns" -> under Technicals pick "All Candlestick Patterns", add to chart/favourites.
  2. Open its settings -> select **"No detection"** for trend detection -> set **pattern type = Bearish**.
  3. Enable only: shooting star, hanging man, gravestone doji, engulfing, dark cloud cover, evening doji star, evening star, three black crows.
- Setup/context required: **be in a downtrend** — "look for a downtrend" [3:31]-[3:34]; "I cannot emphasize enough how important it is to trade with the trend" [4:10]-[4:15]. Rationale given up front: "price continues in the direction that it's going 60% of the time" [0:00]-[0:13]. He prefers shorts: "I'm a big fan of short positions because they have a higher likelihood of playing out, price loves to drop" [3:34]-[3:43].
- Entry trigger: the indicator printing an arrow above price for any of the enabled bearish patterns -> short.
- Stop loss / Take profit: a **"10 pip box"** — a fixed 10-pip target (and, by his tally of wins vs "stopped out", an equivalent fixed-pip stop; the stop distance is never stated explicitly) [3:34]-[3:53].
- Filters he adds (all stated as improvements, not applied in the demo):
  - Trade only WITH the trend.
  - Couple the signal with price action, areas of support and resistance, and breaks of structure — "you could have easily eliminated half of these trades and only taken the good signals" [4:00]-[4:10].
- Pattern definitions actually given (the only numeric one is the shooting star):
  - **Shooting star**: long upper wick, **body approximately one-third of the total candle length** [2:36]-[2:50]. Opposite of the hammer.
  - **Hanging man**: "head on top, body on bottom"; the hammer is "accompanied with the arm" — whichever way the NEXT candle goes is usually the direction price moves ("the arm swings the hammer in that direction") [2:54]-[1:19].
  - **Gravestone doji**: open exactly equals close, with a long upper wick [1:19]-[1:29].
  - **Engulfing** (his favourite), traded as a **three-line strike**: three consecutive bullish candles followed by one engulfing bearish candle [1:29]-[1:45]. Bearish three-line strike preferred "because price loves to drop much faster than it likes to go up".
  - **Dark cloud cover**: daily/swing pattern; he dismisses it.
  - **Evening star / evening doji star**: he puts these in the same category as the three-line-strike engulfing — a very small doji/star candle followed by an engulfing candle = a momentum shift [2:00]-[2:24].
  - **Three black crows**: bullish momentum up, then three solid bearish candles [2:29]-[2:55].

## Vague / untestable / chart-pointed claims
- [0:09]-[0:13] "price continues in the direction that it's going 60% of the time" — no source, no market, no timeframe, no definition of "continues"; an unbacked base-rate claim used to justify the whole approach.
- [3:43]-[3:53] "you got your 10 Pips here here here here here, stopped out stopped out stopped out, here here here here and stopped out" — the entire performance demo is chart-pointed counting with no stop size, no sample size, no date range, no net result. Un-auditable.
- [3:34]-[3:36] "going to draw my 10 pip box again" — the box's STOP side is never specified; only the 10-pip profit side is named.
- [4:00]-[4:10] "if you coupled that with price action and traded areas of support and resistance as well as breaks of structure you could have easily eliminated half of these trades" — hindsight claim; no rule for WHICH half to eliminate.
- [3:31] "look for a downtrend" — downtrend is never defined (no MA, no structure rule, no lookback).
- Most pattern definitions are qualitative: "long wick on the top", "head on top body on bottom", "such a small candle" — only the shooting star gets a ratio (1/3 body).
- [1:00]-[1:17] The "hammer and the arm" rule (next candle's direction decides) is stated as "usually" — no probability and no timeframe.
- No session, time, day or news filter anywhere. No timezone. No R multiple other than the implied fixed-pip box.

## Testability
- rating: MEDIUM (the signal source is a named, exactly-configured public TradingView indicator and the exit is a fixed 10-pip target — but the stop distance is never stated and "downtrend" is undefined, so two required inputs are missing)
- overlap: candlestick-pattern (+ three-line-strike, which he names as his favourite), with a stated but unimplemented trend-filter / S-R / BOS confluence layer
- notable quotes:
  - [2:40] "you're looking for a long wick on the top and you want the body of the candle to be approximately one-third of the total length of the candle"
  - [1:30] "it is the engulfing candle formation, I like to trade this with a three-line strike meaning three subsequent bullish candles and then one engulfing bearish candle"
  - [3:12] "open up the settings, select no detection and select bearish as the pattern type"
