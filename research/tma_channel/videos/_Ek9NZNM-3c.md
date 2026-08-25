# 3 Line Strike Indicator FREE***
- id: _Ek9NZNM-3c | views: 112000 | length: 273s
- market(s) shown: AUDUSD (Australian dollar / US dollar)
- timeframe(s) taught: **5-minute** ("on the five minute time frame" [0:47]); no HTF context used

## Mechanical rules (only what the video actually states)
This is an indicator-release/tool-tour video; the trade rules are carried over from a previous three-line-strike video and restated here as a worked example.

- Indicators + exact settings:
  - **"Three Line Strike" by TTF** — free on TradingView, found by typing "three line strike" into the indicator search; "it's the only one in existence" [0:12–0:33].
  - Plots bearish and/or bullish three line strikes as red/green arrows.
  - Optional setting: **show standard engulfing candles** by ticking bearish and bullish in the settings [1:23–1:33].
  - Optional cosmetic: "meme icons" replace the arrows — **peach = bearish, eggplant = bullish** [1:36–1:56].
  - Alerts: click the indicator → add alert; alert conditions available are **any alert function (up or down), bearish three line strike, bullish three line strike, bearish engulfing, bullish engulfing** [2:52–3:46]. Free TradingView plan = one alert.
- Setup/context required: none stated beyond being in the London session (below).
- Entry trigger: the three-line-strike signal printed by the indicator (the pattern itself — 3 candles then an engulfing strike — is defined in his other videos, not here).
- Stop loss: **10 pips** [1:10, 2:41].
- Take profit: **20 pips** — i.e. a fixed **1 : 2** [1:14, 2:44].
- Position sizing: **1% risk / 2% take profit per trade**; 4 winners → "a solid eight percent" [2:52–3:01].
- Filters he adds: **London session** — "right now I'm in New York time, so this is 3 a.m. New York time, which would be what, 9 a.m., so London session essentially" [2:26–2:38]. That is the only filter; all four signals shown fell in that window.
- Results claimed: **4 trades, 4 winners** on AUDUSD 5m during one London session with the 10-pip SL / 20-pip TP, = +8% at 1% risk [2:20–3:11].

## Vague / untestable / chart-pointed claims
- [1:32] "if you guys remember my three line strike video that I just made, if you had a 10 pip stop loss on these things with a 20 pip take profit would have worked out really well for you" — the pattern definition and the origin of 10/20 pips are outside this video; no backtest, no sample size.
- [0:56] "you got some really phenomenal results from the trading right here... one, two, three and four" — he hand-circles four winning signals on one chart; **losing signals in the same window are not shown or counted**. Pure cherry-pick, no win-rate.
- [2:26] "this is 3 a.m. New York time, which would be what, 9 a.m., so London session essentially" — he is guessing the conversion out loud; **the actual session window and timezone are never fixed** (3am NY is 8am London in winter, 8am in summer — his "9 a.m." is his own local Europe time, not London).
- [2:41] "10 pip stop loss with a 20 pip take profit" — stated for AUDUSD 5m only; no rule for scaling the pip distances to other instruments or volatility.
- [3:04] "if you did one percent risk and two percent take profit you would have had a solid eight percent during london session" — arithmetic on 4 hand-picked winners, not a tested result.
- No rule at all for: which signals to skip, trend/structure context, max trades per session, or what to do when signals cluster.
- He states up front the video was recorded on vacation under a blanket and closes with "yeah that video was not my best work" [3:51] — it is a product announcement, not a strategy lesson.

## Testability
- rating: MEDIUM (the indicator is FREE and public, the pattern is a standard three-line strike, and the exit is a hard 10-pip stop / 20-pip target — but the session filter is fuzzy and no filtering rule is given, so "take every signal" is the only codable version)
- overlap: three-line-strike + candlestick-pattern; session-filter (loosely)
- notable quotes:
  - [0:24] "All you got to do is type in three line strike into the indicator search and it will pop up — three line strike by TTF."
  - [2:41] "10 pip stop loss with a 20 pip take profit — you can see this worked out four times in your favor."
  - [2:54] "If you did one percent risk and two percent take profit you would have had a solid eight percent during London session on Australian dollar US dollar."
- update relationship: explicitly a follow-up to an earlier three-line-strike strategy video ("my three line strike video that I just made") — this one adds the free TradingView indicator and alerts to those same 10/20-pip rules. See also `XMOo4_r5qlA.md`, which defines the pattern (3 bearish + 1 bullish engulfing, entry at candle close, stop below) but gives no pip targets.
