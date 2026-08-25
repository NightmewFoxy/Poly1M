# The Ultimate Price Action Trading Guide
- id: r1rrwsXMFCg | views: 17000 | length: 721s
- market(s) shown: **GER40 / German 40 (DAX)** on the 5-minute
- timeframe(s) taught: **5-minute execution**, with **daily** open/high/low levels for S/R; weekly/monthly OHL if swing trading on the daily

## Mechanical rules (only what the video actually states)
Two complete trade recipes are given (breakout, and break-and-retest), both built around the paid "**Price Action Toolkit**" indicator.

### Recipe A — breakout continuation
- Indicators + exact settings: **Price Action Toolkit** with two options toggled on: (1) "**emphasize micro and macros**" — greys out / removes the minor swings so only major structure swings are outlined ([3:07]); (2) "**price volume candles**" — colours candles as big-bearish / little-bearish / big-bullish / little-bullish by volume ([3:41]).
- Setup/context required: an established trend on the 5m; identify the **major (macro) higher high** — explicitly not the minor swings ([3:01]–[3:23]). "The trend is your friend and continuation trades are going to be money in the bank" ([4:24]).
- Entry trigger: price **breaks above the major higher high**, and then **a high-volume candle prints above that zone** — "we had our breakout candle but then we had a high volume candle above that zone, that's when we're interested in taking a long position" ([4:26]–[4:36]). Low-volume breakouts are rejected as traps ([3:36]).
- Stop loss: "**below the previous structure or the nearest swing low**" ([4:36]).
- Take profit: **1:2 risk-to-reward** ([4:41]).

### Recipe B — break and retest, entered off the fib zone
- Setup/context required: same breakout, but wait for the pullback instead of chasing ([4:45]).
- Where the pullback goes: "it usually retraces after a breakout to Fibonacci levels — **the 0.5, the 618**" ([4:56]). Fib is anchored **from the swing high to the swing low** of the broken leg ([5:08]).
- Extra level: enabling the toolkit's **"FIB zone" checkbox** auto-plots the **78.6%** retracement zone ribbon — used to explain why price overshot the raw structure line without invalidating the setup ([5:52]–[6:08]).
- Entry trigger: **a rejection candle off the fib zone, entered after that candle has closed back beyond the previous structure** — "once you get a rejection candle off of this zone continuing to break out of that structure you can take a short position after that candle has closed below that previous structure" ([6:08]–[6:17]).
- Stop loss: **not restated for this recipe**; the stated assumption is that "price isn't going to go back above that Fibonacci zone" ([6:17]) — i.e. the fib zone is the invalidation.
- Take profit: **1:2 risk-to-reward** ([6:21]).

### Support/resistance construction (the one genuinely mechanical level rule)
- Manual definition: a level is where a prior high was, that price later returned to; resistance that breaks becomes support (flip zones) ([0:36]–[0:56], [9:29]–[9:53]).
- Objective version he actually recommends: use **monthly, weekly and daily open / high / close (and low) lines** — via the "multi-timeframe open high low lines" tool. **On the 5m or 15m use the DAILY open/high/low lines; if swing trading on the daily use the WEEKLY or MONTHLY** ([7:44]–[8:13], [9:53]–[10:08]).

### Other stated rules
- **Do not use the toolkit's higher highs/lows as live entry fractals** — "you can't trade off of them because you won't know the micro and the macro swings until far after the price has already gone to the next point of structure" ([6:30]). They are for **looking left** at prior structure to pick targets ([6:43]–[7:24]).
- Reversal detection: **RSI divergence** — price makes a lower low, RSI makes a higher low, coming back into the "**7030 range**" ([1:48]–[2:06]). RSI length never stated.

## Vague / untestable / chart-pointed claims
- [7:38] "how did you know to put it right there — **I have an eye for it so I can just do it off the cuff**" — he openly states the S/R placement is intuition; the daily-OHL method is offered as the substitute for people who can't.
- [2:36] "because I have years of experience I can see this just clear night and day… a lot of people can't do it" — the micro/macro swing distinction is delegated to the paid indicator rather than defined.
- [3:07] "click this boxing emphasize micro and macros, that will get rid of the minor swings" — the actual micro/macro classification logic is inside a closed-source indicator; **not reproducible**.
- [3:41] "price volume candles… big bearish candles, little bearish candles" — no volume threshold is spoken for what makes a candle "high volume"; again inside the indicator.
- [4:07] "these volume candles are going to help you just clearly identify when that high volume is breaking the structure" — chart-pointed.
- [5:44]–[6:08] "how did we know that price is going to reject this area, is it the support and resistance or is it a Fibonacci Zone… it didn't exactly reject this structure line, it went above it which could have stopped a lot of people out" — post-hoc explanation; the 78.6% zone is introduced to rationalise an overshoot, with no rule for when to expect 0.5/0.618 vs 78.6.
- [6:17] "safely know that price isn't going to go back above that Fibonacci Zone" — asserted certainty, no stop rule, no data.
- [1:48]–[2:06] RSI divergence example narrated off the chart; **RSI length never given**, only the 70/30 band.
- [8:31]–[9:00] "this one I believe is also going to be important because it was used multiple times right here, right here and right here" — discretionary level ranking.
- Roughly the final 90 seconds ([10:25]–[12:00]) is a Trade Floor membership pitch; no rules.

## Testability
- rating: MEDIUM — Recipe A (major HH break + high-volume candle above the zone, stop below nearest swing low, 1:2 RR) and the daily-OHL S/R construction are codable; but the "major vs minor swing" filter and the "high volume candle" definition both live inside a closed-source paid indicator
- overlap: market-structure/BOS, S/R-retest (daily/weekly/monthly OHL), fib-scalp (0.5/0.618/0.786), volume-analysis, regular-divergence (RSI), break-and-retest
- notable quotes:
  - [4:26] "we had that higher high right here, we had our breakout candle but then we had a high volume candle above that zone — that's when we're interested in taking a long position, stop loss below the previous structure or the nearest swing low with a 1 to 2 risk to reward ratio"
  - [4:56] "it usually retraces after a breakout to Fibonacci levels — the 0.5 the 618"
  - [7:44] "look at the monthly high open and close, weekly high open and close, and daily high open and close… because I'm on a 5-minute time frame I want to focus on the daily high open and close"
