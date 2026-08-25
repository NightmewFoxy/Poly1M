# How to Set Alerts in Tradingview ***Strategy Included***
- id: XyKYSy5C9Kc | views: 204000 | length: 530s
- market(s) shown: **US30** [2:45]-[2:47], [4:38]-[4:41], [7:18]-[7:23]
- timeframe(s) taught: **5 minute** — "what you're waiting for is a five-minute candlestick to close above that frankfurt session box" [2:04]-[2:12]; "because this is a five-minute chart" [3:21]-[3:22]

## Mechanical rules (only what the video actually states)
This is a stripped-down two-indicator subset of his 5-minute scalping strategy: "hopefully you watched my previous video about a five-minute scalping strategy — this is basically just **two parts of that strategy**... i'm just using **two of the four indicators** that i discussed" [0:51]-[1:11]. The other two indicators are deferred to that video [8:29]-[8:38].

- Indicators + exact settings:
  1. **FX Market Sessions** indicator ("this box right here is called the fx market sessions") — used to draw the **Frankfurt session** box [1:11]-[1:16].
  2. **VWAP** ("the blue line is the v whap line") [1:13]-[1:16]. No anchor/period stated (TradingView default assumed, never said).
  No moving average, no RSI, no fib in this video.
- Setup/context required:
  - Trade the **Frankfurt open, which opens one hour before the London session** [0:56]-[1:03]. **No timezone or clock time is ever stated** — he only says "set your alarm to wake you up at eight o'clock... by the time nine o'clock rolls around" [1:24]-[1:37], which is his personal routine, not a chart-time spec.
  - Wait for the indicator to finish bracketing the **first trading hour**, then **draw a horizontal line across the top and the bottom of that box** [1:37]-[1:52].
  - **VWAP is the direction filter:** "one of the things you're looking for is above or below this v-wap line — because we are trading **above the v-wap line** i want you to **only take into consideration long positions**" [1:52]-[2:04].
- Entry trigger: **A 5-minute candle CLOSING above the Frankfurt session box** (for longs; mirror implied for shorts) — "what you're waiting for is a five-minute candlestick to close above that frankfurt session box" [2:04]-[2:12]. Confirmed at entry time: "the price had crossed that line and closed above that level" [4:46]-[4:52]. He calls this "just using these two confluences" (VWAP side + box-close breakout) [3:38]-[3:42].
- Stop loss: **the OPPOSITE side of the Frankfurt session box** — "your stop loss is going to be the bottom of this frankfurt session" [3:55]-[4:01]. Example: **50 point stop on US30** [7:18]-[7:23].
- Take profit: **measured-move multiples of the Frankfurt box height.** "your take profit levels are going to be **intervals of the size of this frankfurt session** — choose your rectangle tool, trace it to the exact size of that frankfurt session, and then just drag it to the top of that frankfurt session to see where your first take profit level is... then just do that again" [4:01]-[4:30].
  - So **TP1 = box top + 1x box height; TP2 = box top + 2x box height.**
  - Stated R/R goal: "what i want you to target is either a **one to one or one to two risk to reward ratio**" [3:50]-[3:55].
  - Example outcome: **50 point stop, 81 point take profit** on US30 [7:18]-[7:23]; TP1 took **3 hours 40 minutes** to hit [6:28]-[6:33].
- Filters he adds:
  - **Position splitting:** on MT4 "put in two trades of equal size, so each trade only risking **half a percent, one percent in total**; your first trade closes at take profit one and your second trade closes at take profit two" [5:04]-[5:19]. On cTrader, use one position with partial-close percentages [5:19]-[5:27].
  - **Set TradingView price alerts on entry line, stop and both take profits**, and then leave the charts [3:42]-[3:50], [4:30]-[4:44]. The stated purpose is psychological: "the whole purpose of setting alerts is to ease the trader psychology because a lot of people, when they watch price reversing on them, they will close the trade early and not let it play out" [5:44]-[5:55].
  - Warning that the **New York open** produces "crazy fluctuations" mid-trade that scare people out [6:55]-[7:08] — an observation, not a rule to exit.

## Vague / untestable / chart-pointed claims
- [0:56]-[1:03] "the frankfurt open which opens up one hour before the london session" — **no clock time and no timezone given**, and no session-end time; the box depends entirely on the FX Market Sessions indicator's own (unshown) settings. This is the biggest reproducibility gap for a session-based rule.
- [1:11]-[1:16] "the blue line is the v whap line" — VWAP anchoring/period never specified (daily? session?).
- [0:51]-[1:11] Two of four indicators are deliberately omitted; the full confluence set is not in this video, so trading it as written is knowingly incomplete.
- [3:38]-[3:42] "just using these two confluences you can safely take a trade right here" — "safely" asserted, no win rate, no sample.
- [3:21]-[3:32] "this alert might show up right after the close of that first hour... but it also could consolidate for an hour" — **no expiry rule**: how long the breakout signal stays valid after the session box closes is never stated.
- No rule for what happens if price closes back inside the box, no rule for the short-side mirror (only stated by implication), no rule for taking a second signal the same day, and no day-of-week or news filter.
- [7:29]-[7:40] "that could have been a profitable trade of eighty-two dollars, eight hundred and twenty dollars or eight thousand two hundred dollars" — contract-size illustration, not a result.
- Whole video is a **single cherry-picked example trade** in TradingView **replay mode** [1:03]-[1:07]; no backtest, no sample.
- Cross-reference: explicitly a subset of his "five minute scalping strategy" video, which is also the VWAP-update video (Z__54ssczD0) in this same batch — check that one for the two missing indicators.

## Testability
- rating: MEDIUM (the entry, stop and both take profits are fully mechanical and geometric — box-close breakout, opposite-box-side stop, 1x/2x box-height targets, plus an explicit VWAP-side filter and a stated position split — the one blocking gap is that the Frankfurt session window is never given a clock time or timezone, and VWAP anchoring is unspecified)
- overlap: session-filter (Frankfurt opening-range breakout) + VWAP; opening-range-breakout with measured-move targets. Subset of the 5m-scalp(VWAP) family.
- notable quotes:
  - [2:04] "what you're waiting for is a five-minute candlestick to close above that frankfurt session box"
  - [3:55] "your stop loss is going to be the bottom of this frankfurt session and your take profit levels are going to be intervals of the size of this frankfurt session"
  - [1:58] "because we are trading above the v-wap line i want you to only take into consideration long positions"
