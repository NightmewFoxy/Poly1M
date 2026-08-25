# Price action trading strategy with trend reversals
- id: GGD9kjgHViI | views: 104000 | length: 837s
- market(s) shown: US30
- timeframe(s) taught: 15m (stated at [1:00] "us 30 right here on a 15 minute time frame"; same TF used throughout)

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: RSI (length never stated). Levels used: **70 / 30 overbought-oversold**; he insists the divergence pivot must be beyond those, not at 60/65 or 40/45 ([8:49]–[9:28]). Cosmetic settings he applies: yellow line, upper and lower bands removed, middle band solid, background off ([2:46]–[2:58]). He also references his own "divergence indicator" script that TradingView won't let him publish ([2:35]).
- Setup/context required: Naked chart first, then draw trendlines connecting as many rejection points as possible; also (optionally) big horizontal S/R zones. Trade is a **trend reversal** (counter-trend), which he repeatedly flags as the riskiest kind.
- Entry trigger: Three conditions together — (1) a **regular RSI divergence** with the RSI pivot beyond 70/30 ("a nice big fat angle", [5:01]); (2) price **breaks the trendline**; (3) **the next candle after the break does not break back inside** — i.e. a break-and-retest confirmation. Entry at the close of that confirming candle. [6:01] "where this next candle did not break below that trend line this would have been a nice indication for me like okay now we can think about taking long positions". He also gives a trend-continuation variant: rejection off the newly drawn trendline + a **hidden bullish divergence** (price higher low, RSI lower low) → enter at the close of that candle ([11:21]–[11:43]).
- Stop loss: **NOT the swing low.** Rule: put it at **the bottom of the candle that actually broke the trendline**. [6:16]–[6:34] "there's a lot of people that like to put their stop loss below the swing low but when you see huge candles like this it's not intelligent to have a 230 point stop loss on us 30. so what i would do is just go to the bottom of that candle that signified the actual break out of that trend line". For the three-line-strike continuation entry: stop "just below the bottom of that candle" ([11:01]).
- Take profit: 1:2 R, or 1:5 "if you're skittish" ([7:07]–[7:11] — stated in that order, so the mapping of which is which is garbled). For the three-line-strike continuation trade: "go for one to two" ([11:03]).
- Filters he adds: Risk 1% of account per trade ([6:52]). Prefer with-trend over reversal trades. Avoid entering on the single break candle — always require the break-and-retest. Be extra cautious in whipsaw/"noise" zones. No session, day-of-week or news filter in this video.

## Vague / untestable / chart-pointed claims
- [1:56]–[2:12] "i just drew up general areas of resistance that i saw where the price rejected consistently as many points as i can connect the dots with" — discretionary trendline/zone drawing, the core input of the whole method.
- [4:57]–[5:05] Divergence quality judged by eye: "that's not a definitive divergence like you want to see a nice big fat you know angle" — no numeric slope/pip/RSI-delta threshold.
- [5:26]–[5:31] "i would be very cautious on breaks and retests right here" / "this one would have been attractive to me but i would have watched to see what happened with this next candle" — discretionary trade selection.
- [7:22]–[7:31] Trendlines can be drawn "from the bodies or the wicks... it's all subjective i like wicks sometimes" — he explicitly declares this input subjective.
- [8:35]–[8:47] "you have to deploy patience", "know that the traps are always there" — motivational, not a rule.
- [11:17]–[11:23] "if i haven't seen a good divergence here i don't know for sure but let's just check the rsi" — divergence detection is visual/after-the-fact.
- RSI length is never stated anywhere in the video (only the 70/30 levels and cosmetic settings).
- [6:24] The "230 point stop loss on us 30" is cited as an example of a bad stop, not as a parameter.

## Testability
- rating: MEDIUM (entry logic is nearly mechanical — divergence beyond 70/30 + trendline break + non-reversing next candle + close entry + stop at break-candle low + 1:2 — but trendline drawing and "big fat" divergence quality are discretionary, and RSI length is missing)
- overlap: regular-divergence + hidden-divergence + market-structure/BOS (trendline break-and-retest); three-line-strike appears as a bonus entry; S/R-retest as an add-on
- notable quotes:
  - [9:24] "anything higher than 70 or lower than 30 like we hit here we got a 23.5 on the rsi so once that happens you don't want to immediately get in for a buy what you'd like to do is wait for the divergence"
  - [6:30] "what i would do is just go to the bottom of that candle that signified the actual break out of that trend line"
  - [8:30] "you don't want like the one candle to break a trend line because the next one most likely is going to go the opposite direction you always want that break and re-test"
