# Breakout Strategy - You're Trading at The Wrong Time!
- id: KYZ3gFl6GW0 | views: 58000 | length: 322s
- market(s) shown: AUDUSD ("this is Australian dollar Us doll[ar]", [0:56]); he also names AUDCAD, AUDNZD, GBPJPY, NZDUSD as valid Tokyo-session pairs
- timeframe(s) taught: 5-minute for the breakout candle closure, 1-minute for the refined pullback entry ([4:50]–[4:58])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: A **session indicator** (his affiliate link, first in the description) that marks the **New York, Tokyo and London sessions**, shows **the first hour of each session**, and plots **DR and IDR ranges** — "that's the defining range and the implied defining range" ([3:36]). No numeric settings are given.
- Setup/context required: The **first hour of a session** defines the range. Trade only the **breakout of that session's first-hour range**, in the session that is geographically correct for the pair: "you only want to do this with pairs that trade in that vicinity of the planet so Australia Japan and New Zealand any one of those currencies in your pair is good" for the Tokyo session ([2:25]–[2:48]).
- Entry trigger: **Candle closure outside the outer edge of the DR/IDR range** — "I only want you to trade breakouts of the outer edge of this range candle closure outside of the range" ([3:43]–[3:54]). Refined version for full-time traders: on the 5m see a candle close above the range, then drop to the **1-minute chart and wait for the breakout to pull back into the zone** and give an entry signal ([4:43]–[5:04]) — "wait for a breakout and then a pull back those are the best entries".
- Stop loss: **Halfway through the range** — "as a general rule of thumb halfway through this Zone just above that or below that should be your stop loss" ([3:54]); restated as "50% area for your stoploss" ([4:16]). I.e. the midpoint of the first-hour/DR range.
- Take profit: **1:2 risk-to-reward** ([4:18], and the worked example "minus 1% plus 2% up 1% for the day" at [3:32]).
- Filters he adds:
  - **Do not trade the first hour of any session.** "this indicator shows you the first hour of the trading session which most people like to avoid myself included ... what I would like you to do is not trade this little window whatsoever or anything within this little window" ([1:28]–[1:47]). He compares it to an American-football juke — a fake move one way then the other. He suggests extending those lines out on the chart so you can see when not to trade.
  - **Session-time table by home time zone** (his zone is European, and he uses "my time zone" throughout): Tokyo session begins around **3:00 a.m.** European time ([1:13]) and to trade the Tokyo breakout from Europe you must be up at **2:00 a.m.** ([2:19]). North/South America should target the **London session breakout** by waking a few hours early ([2:52]–[3:00]). The dead zone he warns about: **10–11 p.m.** European time has "huge spikes in the spread of the price because the market is transitioning into the following day" ([1:00]–[1:07]).
  - **Skip consolidation days**: "stay out of the market on days when the price is consolidating because it's not breaking out of these ranges" ([4:34]).
  - Alert-based execution for people at work: set price alerts on the first-hour range edges, enter on the signal, then leave it unmanaged ([3:07]–[3:27]) — he flags this as "less consistent because you won't be able to monitor trades".

## Vague / untestable / chart-pointed claims
- [0:44] "so for me in my time zone this is 9:00 a.m. and this is 5:00 p.m." — his time zone is only described as European (elsewhere on the channel UTC+2); the session windows are never given as absolute UTC times, so the whole time-of-day rule set needs a timezone assumption to code.
- [3:36] DR / IDR are named but **not defined numerically** — he never says what fraction of the first-hour range the IDR is (in the common ICT/DR-IDR definition DR = high-to-low including wicks, IDR = body-to-body, but he does not say this). The rule "breakouts of the outer edge of this range" therefore depends on which of the two lines the indicator draws.
- [3:54] "as a **general rule of thumb** halfway through this Zone just above that or below that should be your stop loss" — self-flagged as a rule of thumb, and "just above/below" the midpoint has no defined buffer.
- [4:00] "you can fine-tune the rules of these strategies" — explicit admission the rule set is not final.
- [3:28] "so for example this Breakout you would have lost that trade but this breakout you would have won minus 1% plus 2% up 1% for the day" — a two-trade chart-pointed sample, not a backtest.
- [4:58] "wait for the break out and then they pull back into The Zone **with an entry signal right here**" — the 1m "entry signal" is pointed at on screen and never defined (candle pattern? indicator?). Frame-check needed.
- [2:07] "this happened in 2 hours this happened in 2 hours" — chart-pointed observation about breakout speed, no rule.
- [1:15] "I could wake up at 5 a.m. and start trading but again the market is a little bit consolidating" — no volatility measure given for "consolidating".

## Testability
- rating: MEDIUM — the skeleton is genuinely mechanical (first-hour range of a named session, no trades inside that first hour, entry on a candle CLOSE outside the range, stop at the range 50%, target 1:2 R, pair must belong to that session's region). The blockers are the undefined DR-vs-IDR edge, the unstated absolute timezone, and the undefined 1m pullback "entry signal".
- overlap: **session-filter** (primary — this is the channel's clearest time-of-day video) + opening-range breakout / S-R-retest (breakout then pullback re-entry). Uses a paid session indicator rather than the channel's usual SMMA/divergence toolkit.
- notable quotes:
  - [1:43] "what I would like you to do is not trade this little window whatsoever or anything within this little window" (the first hour of a session)
  - [3:43] "I only want you to trade breakouts of the outer edge of this range candle closure outside of the range as a general rule of thumb halfway through this Zone just above that or below that should be your stop loss"
  - [2:25] "you only want to do this with pairs that trade in that vicinity of the planet so Australia Japan and New Zealand any one of those currencies in your pair is good"
