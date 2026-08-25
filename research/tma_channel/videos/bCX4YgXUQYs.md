# Best Trend Trading Indicator
- id: bCX4YgXUQYs | views: 13000 | length: 219s
- market(s) shown: unstated (chart shown, symbol never named)
- timeframe(s) taught: 1 minute (explicitly — "If you're scalping on the one minute time frame" [0:00]; "If you are not comfortable with the one minute time frame, please do not trade this strategy" [0:15])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: Fibonacci retracement tool — "gold zone between the 0.5 and the 618" [1:18-1:25]. Plus "Happy Trail", a PAID TTF indicator ("about 20 bucks a month" [3:29]) used only to time the entry candle; its internals are never disclosed.
- Setup/context required: TRENDING market only — "you want trending markets. That's the only way that Fibonacci retracements are going to work" [0:45]. Structure pattern named: "momentum down, a pullback, momentum down, a pullback, momentum down" [0:50-0:56]; every pullback is a fib retracement. A fresh fib is drawn on EVERY new leg: "every time price breaks previous structure and starts pulling back, I want you to put a new Fibonacci retracement tool" [1:29-1:36].
- Entry trigger: TWO versions given.
  1. "Quick and dirty" (no indicator): enter short anywhere in the 0.5–0.618 gold zone [1:18-1:25].
  2. With Happy Trail: wait for a Happy Trail signal candle inside the retracement — that candle is the entry [2:36-2:43].
- Stop loss: version 1 — "your stop loss to be the previous high" [1:25]. Version 2 — "you simply go to the previous high point, which is this candle right here" / "your stop-loss above the previous structure" [2:12-2:24], described as "a very tight stop-loss" [2:36].
- Take profit: version 1 — "your take[profit] to be the previous low. That's going to give you just over a 1:1 risk-to-reward ratio" [1:25-1:29]. Version 2 — fixed "1:1.5 risk-to-reward ratio" [2:18, 2:24, 2:36].
- Filters he adds:
  - Session windows, stated WITH timezone: "if London market opens up at 9:00 a.m. London time, I want you to trade between 10 and 2:00 p.m. That gives you a 4 hour window" [2:48-2:56]; "If you are trading New York session, I want you to trade between 10 and 2 PM New York time, Eastern Standard Time" [3:03-3:09].
  - Daily loss stop: "once you get a happy trail signal with a very tight stop-loss and a 1 to 1.5 risk-to-reward ratio and you lose a trade, you're done for the day. That means that trend is over. Market structure has been broken" [2:36-2:48]. i.e. ONE loss = stop trading for the day.
  - Volume/liquidity: only trade "peak market volume and high trading times" — London and New York sessions [0:25-0:39].

## Vague / untestable / chart-pointed claims
- [0:50-0:56] "as you can see right here, we have a momentum down, a pullback, momentum down" — the leg definition (what counts as one impulse worth fibbing) is shown on chart only, never quantified.
- [1:29-1:36] "every time price breaks previous structure" — "previous structure" is undefined (prior swing high/low? fractal? close beyond?).
- [1:50-2:07] Happy Trail is a paid black box; the entry candle in version 2 cannot be reproduced without buying it. This is the single blocking gap for backtesting version 2.
- [2:12-2:18] "we simply go to the previous high point, which is this candle right here" — chart-pointed; whether the stop sits at the wick or the body of that candle is not said.
- [2:43-2:48] "That means that trend is over. Market structure has been broken." — asserted, not derived; the loss is treated as proof of a regime change without any independent structure test.
- Fib zone direction: he only demonstrates the SHORT side. The long-side mirror is implied but never spelled out.

## Testability
- rating: MEDIUM (version 1 is fully mechanical — 1m, session-boxed, fib 0.5–0.618 entry, prev-high stop, prev-low target; version 2 is blocked on a paid indicator)
- overlap: fib-scalp (gold zone 0.5–0.618) + session-filter; the 1-loss-and-done daily rule ties to his risk-management videos.
- notable quotes:
  - [1:18-1:29] "just enter in a short position around the gold zone between the 0.5 and the 618. I want your stop loss to be the previous high and your take[profit] to be the previous low. That's going to give you just over a 1:1 risk-to-reward ratio."
  - [2:48-3:09] "if London market opens up at 9:00 a.m. London time, I want you to trade between 10 and 2:00 p.m. ... If you are trading New York session, I want you to trade between 10 and 2 PM New York time, Eastern Standard Time."
  - [2:36-2:48] "once you get a happy trail signal ... and you lose a trade, you're done for the day."
