# Best Scalping Indicator **JUST GOT BETTER**
- id: 10SNAXJkgbg | views: 420000 | length: 746s
- market(s) shown: AUDUSD
- timeframe(s) taught: 1h for the S/R markup → 15m for rejections/entries ([1:29] "usually i do my one hour markup and then i take it down to the 15 minute chart"); his own demo trade was taken on the **5m** chart ([4:55])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - The channel indicator **"Arty the Moving Average official indicator" by Phoenix Binary**, v2, public on TradingView.
  - **21, 50, 200 SMOOTHED moving averages.** v1 also had a **100** period; v2 removes it by default (toggleable back on) — [2:50]–[3:01] "we've gotten rid of the 100 period moving average... I don't personally like to trade off the 100." MA type is selectable (smoothed / simple / exponential / weighted); **he prefers smoothed** ([6:14]–[6:21]).
  - The **200 SMMA is now colour-dynamic** to show momentum; a **momentum cloud between the 21 and 50** changes hue (red → orange → green) with momentum.
  - **Engulfing candle ("big ass candle") and three-line-strike** markers, each with a **strict** mode: strict three-line-strike = the final engulfing candle engulfs **all three** prior candles; strict big-ass-candle = fully engulfs the previous candle. Strict = fewer but more substantial signals ([6:29]–[6:57]).
  - **ATR (average true range)** table in the top-right corner, new in v2, with entry / stop / break-even / take-profit levels computed live.
  - Companion **TMA divergence indicator**: RSI with a floating moving average through it, plotting regular and hidden bullish/bearish divergences (not yet public at the time of the video).
- Setup/context required: **Above the 200 SMMA → look for buys; below the 200 SMMA → look for sells** ([3:04]). The base setup is a cross past the 200, then a **retest of the 21 or the 50**, then trend continuation ([3:30]–[3:39]).
- Entry trigger: A **rejection off the moving average** followed by trend continuation, signalled by a **big-ass (engulfing) candle or a three-line strike** ([3:41]–[3:57]). For **reversal** scalps: a loss of momentum plus a **colour shift in the cloud between the 21 and 50**, with the moving averages "swooping" ([11:07]–[11:22]).
- Stop loss: two stated formulations —
  1. **2× the size of the engulfing candle** ([3:58] "your stop-loss is going to be about 2x the size of that engulfing candle").
  2. **2× the ATR** at that moment ([8:08] "keeping your stop loss at 2x the atr is going to be a good way to set your stop loss"; he also mentions 1.5× as an alternative at [7:58]). Worked value: on the 5m chart the ATR read **3.3 (= 3.3 pips)**, so a 2× ATR stop = 6.6 pips.
- Take profit: **4× the engulfing candle = 2:1 risk-to-reward** ([4:02] "your take profit is 4x that engulfing candle 2-1 risk to reward ratio"). 2:1 is his stated preference for all scalping trades ([9:00]). With the v2 momentum cloud he says you can instead **hold until the cloud loses momentum / changes colour** rather than exiting at 2R ([4:28]–[4:39]). For swing use, **1:5** is suggested ([9:07]–[9:12]). When scalping reversals: **target the next moving average** — [5:29]–[5:36] "when i'm trading reversals i'm always targeting the next moving average and so here i simply targeted the 200."
  - **Break-even level** = an ATR multiplier tuned to your broker's spread + commission; his own setting was **0.4 × ATR** because his spreads are low ([8:41]–[9:19]).
  - Example settings he demonstrates together: stop = 2× ATR, break-even = 0.4× ATR, R:R = **1:4** ([9:12]–[9:24]).
- Filters he adds:
  - Session shading: **Tokyo / London / New York** — pick one for backtesting and live ([7:02]–[7:09]).
  - **Day-of-week filter**: the indicator lets you enable only certain weekdays; his stated example is **"Tuesday, Wednesday and Thursday, avoiding Monday and Friday"** ([7:13]–[7:18]).
  - Do the 1h S/R markup **before** any indicator goes on the chart ([1:18]–[1:29]); those levels are the take-profit targets.
  - Extra confluence: a **bullish divergence plus a big-ass candle** = "you're good to go on a scalp" ([11:55]–[12:01]).

## Vague / untestable / chart-pointed claims
- [1:18]–[1:29] S/R markup on the 1h is by eye; those levels are the stated targets.
- [4:19]–[4:39] The momentum-cloud hold: "it'll actually show you a hue of red showing you the strength of the momentum of that move letting you hold your trade longer" — hue intensity is not a threshold; the exit becomes visual.
- [5:16]–[5:29] His demo trade entry: "i saw this trend line right here being broken with that big ass candle at that point i see the clouds start turning green so i got in on my entry right here" — hand-drawn trendline plus a colour judgement; not reconstructible.
- [5:39]–[5:57] The demo trade result is given loosely: "it's like 13 15 pips or something from my recollection", size 0.01, held overnight — one anecdote, no stop or target recorded.
- [3:58] vs [8:08] Two different stop rules (2× engulfing-candle size vs 2× ATR) are given in the same video without a rule for which applies when.
- [11:16] "once you get these huge momentum shifting candles and the moving averages start swooping" — "swooping" is a visual slope judgement with no threshold.
- The ATR length used in the indicator table is never stated (only its printed value, 3.3 on the 5m).
- The divergence indicator's detection logic is unspecified; he elsewhere notes it "doesn't always print".

## Testability
- rating: MEDIUM (direction filter, retest, engulfing/three-line-strike trigger and the 2× / 4× candle stop-target pair are mechanical, but the video carries two competing stop rules, an eyeball momentum-cloud exit, and hand-drawn S/R targets)
- overlap: 5m-scalp(SMMA) — this is the tooling upgrade for that system; plus candlestick-pattern (engulfing / three-line-strike), session-filter, regular- and hidden-divergence (companion indicator), S/R-retest
- notable quotes:
  - [3:58] "your stop-loss is going to be about 2x the size of that engulfing candle and then your take profit is 4x that engulfing candle 2-1 risk to reward ratio"
  - [8:08] "keeping your stop loss at 2x the atr is going to be a good way to set your stop loss"
  - [7:13] "you can set certain days of the week that you trade and only have it say on tuesday wednesday and thursday avoiding monday and friday"
- relation to other videos: explicit v2 update of his earlier "best scalping indicator" video (v1 had the 21/50/100/200 SMMA set); the underlying system is the one taught in wbfXaqjIrJ0. Note the contradiction with wbfXaqjIrJ0's single stop rule (2× entry candle) — this video adds the ATR-based alternative.
