# The Best Fibonacci Trading Strategy
- id: _iM7tC5QHns | views: 30000 | length: 187s
- market(s) shown: German 40 (DAX) — "Today's move on German 40 was absolutely textbook perfect"
- timeframe(s) taught: unstated (intraday — he closes trades "towards the end of the day"); the fib is drawn on whatever chart he is on

## Mechanical rules (only what the video actually states)
This is the clearest fully-numeric setup in the batch: the **"33% rule"** for timing when to draw the fib and where to place a pending order.

- Indicators + exact settings:
  - **Fibonacci retracement tool** (third icon down the left-hand toolbar in TradingView). His usual levels are shown on screen but not read out; the one change he tells you to make is: **add an extra level with the value 0.33**, then click OK [0:25–0:35].
  - No other indicator.
- Setup/context required: **a momentum move that breaks the previous structure.** "The momentum move that breaks the previous structure is what you want to measure from top to bottom in a bearish move" [0:53–1:02].
- Fib anchoring: draw the tool across that structure-breaking impulse — **top to bottom for a bearish move** (mirror for bullish).
- Trigger condition (the 33% rule): **wait until price has retraced 33% of that move.** "You wait until price has reached the 33%, which means of that move it's gone backwards or up in price 33% of that move" [1:02–1:20].
  - While the impulse is still extending, **re-draw the fib on every candle close**: "you continue taking your Fibonacci retracement tool on every single candle that closes until a retracement move starts going to the 33%" [1:27–1:39].
- Entry — two variants, he prefers the first:
  1. **Pending limit order at the midpoint between the 0.5 and the 0.618** — "I prefer to split the difference and put it right in the middle" [1:21–1:52].
  2. **Rejection-candle entry**: wait for a rejection candle to close, enter at the close [2:06–2:20].
- Stop loss:
  - Variant 1: **between the 0.618 and the 1.0** [1:52].
  - Variant 2: **above the previous structure** [2:09].
- Take profit: **the previous low** (for a short; mirror for a long) — stated for both variants [1:58, 2:12].
- Resulting R multiples he quotes: **1 : 2.5 for the limit-order variant** [2:00]; **1 : 1.8 for the rejection-candle variant, "depending on the size of the bearish candle"** [2:17].
- Filters he adds: time-of-day exit discretion only — he closed the second trade early "because it was getting towards the end of the day, I wanted to be out of that trade" [2:37–2:42]. No session, no news, no day filter stated.
- Repetition rule: after the trade plays out and price retraces again, re-anchor the fib top-of-move to bottom-of-move and repeat [2:21–2:36].

## Vague / untestable / chart-pointed claims
- [0:09] "these are my normal Fibonacci retracement tool settings... they keep your charts the cleanest" — the full level set is shown on screen but **never spoken**; only the added 0.33 is stated.
- [0:53] "the momentum move that breaks the previous structure" — "previous structure" is never defined (no swing-lookback, no close-vs-wick rule), so the fib anchor points are discretionary. This is the main gap.
- [1:21] "your entry price is either the .5 or the 618, I prefer to split the difference" — the midpoint (≈0.559) is a personal preference, not a tested level.
- [1:52] "your stop loss is between the 618 and the one" — a **range**, not a level; the exact stop is unspecified, which is why the quoted 1:2.5 cannot be reproduced exactly.
- [1:58] "your take-profit is going to be the previous low" — which previous low is chart-pointed.
- [2:17] "that's going to get you a 1 to 1.8 depending on the size of the bearish candle" — RR floats with the trigger candle, so the rejection variant has no fixed R.
- [2:31] "entering in a short position, stop-loss between here, take profit here" — pure chart-pointing on the second example.
- [2:40] "because it was getting towards the end of the day I wanted to be out of that trade, so I closed it early" — discretionary early exit with no time rule.
- No timeframe is ever named; no backtest, no sample. The entire evidence base is one day's two trades on GER40.

## Testability
- rating: MEDIUM (levels, entry, stop zone, target and R are all numeric and stated — the one discretionary gap is defining "the momentum move that breaks previous structure" that anchors the fib)
- overlap: fib-scalp (0.33 trigger / 0.5–0.618 golden-zone entry) + market-structure/BOS
- notable quotes:
  - [0:30] "Add an extra one and give it the number 0.33."
  - [0:53] "The momentum move that breaks the previous structure is what you want to measure from top to bottom in a bearish move... you wait until price has reached the 33%."
  - [1:46] "You set a pending order splitting the difference between the 0.5 and the 618. Your stop loss is between the 618 and the one and your take-profit is going to be the previous low. That's going to give you a one to 2.5 risk-to-reward trade."
