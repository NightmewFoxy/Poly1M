# Best Scalping Strategy **Best Entry Point**
- id: kE08FMEfbkE | views: 206000 | length: 627s
- market(s) shown: US30 (15m primary, 1h for S/R markup)
- timeframe(s) taught: 15m entry / 1h context

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: three **smoothed moving averages (SMMA) 21 / 50 / 200** [3:43-3:52, "it's the 21, the 50 and the 200"]. Plus the channel's free TradingView "TMA" indicator with two toggles: engulfing-candle arrows (single arrow) and three-line-strike arrows (double arrow, labelled "3s bear"/bullish) [6:42-7:25].
- Setup/context required: trend filter by the 200 SMMA — "if we are above the 200 moving average we're looking for long positions and for below the 200 we are looking for short positions" [1:39-1:49]. Counter-trend entries only permitted after (a) drawing a trendline on the current trend and price breaking it [3:00-3:16] and (b) the moving averages beginning to "arc"/slope over, i.e. momentum flattening [4:16-4:21, 5:30-5:34].
- Entry trigger: a **three-line strike** — three consecutive candles in one direction followed by one big engulfing candle in the opposite direction, occurring as a rejection off a moving average. Enter **at the close of that engulfing candle** [1:00-1:11, 5:22-5:44 "had you just waited for this three-line strike to form... had your entry set at the close of that candle"]. A plain engulfing candle (single arrow) is the weaker version of the same trigger.
- Stop loss: "stop loss literally cents above the previous high" / at the far end of the engulfing candle [5:44-5:49, 9:29-9:35 "you can keep your stop loss at the end of that candle"]. No R-multiple or ATR-based sizing stated.
- Take profit: target the next moving average — in the worked example the **200 SMMA** [5:49-5:52]. Explicit constraint: "because we are still in an uptrend, meaning we are above the 200 moving average, you don't want to make your take profit lower than that 200 moving average, even if it's a previous support and resistance level" [4:22-4:40]. Worked result: 52 points on US30 in 15 minutes.
- Filters he adds: prefer big-bodied ("big ass") candles over normal-size candles as entries [2:09-2:19]; only take big candles in the direction of the trend, avoid the counter-trend ones [2:39-3:00]; confluence stacking — S/R level + trendline + moving average lining up is "your best bet for an entry" [0:44-0:56]; wait for MAs to stop rising/start arcing before betting against trend [4:10-4:27].

## Vague / untestable / chart-pointed claims
- [2:09-2:19] "you can see the difference between a normal size candle and a big ass candle" — no numeric definition of "big" (no body-size ratio, no ATR multiple). The engulfing-indicator arrow is the only concrete proxy given.
- [4:16-4:21] "wait for these moving averages to start arcing... once they start [arcing] that's when the momentum starts to lose and shift" — no slope threshold or lookback given; purely visual.
- [4:44-4:52] "I figured this was the last rejection that we would have on the 200" — discretionary judgement, stated as a feeling.
- [4:52-5:00] "this is about the point where I started watching US30... for me that was 6:30 p.m." — session time given with no timezone.
- [4:59-5:13] "I actually had an alert set right here to see what would happen if it crossed the 50" — the alert placement is chart-pointed, not a stated rule.
- [7:37-7:47] "I had a feeling that most people would have their stop losses on a long position just below that candle" — stop-hunt reasoning, not a mechanical filter.
- [8:12-8:31] Hourly S/R lines drawn by eye ("we had a rejection here, a rejection here") — discretionary zone drawing.
- [8:54-9:02] "The reason it didn't get back down to this level of previous support is because it was boosted up by the 200 moving average" — post-hoc chart explanation.

## Testability
- rating: MEDIUM (entry, stop, and trend filter are mechanical; "big ass candle" size and MA "arcing" are undefined, and the counter-trend variant needs a discretionary trendline)
- overlap: three-line-strike + 5m/15m-scalp(SMMA) + S/R-retest
- notable quotes:
  - [1:39-1:49] "if we are above the 200 moving average we're looking for long positions and for below the 200 we are looking for short positions"
  - [5:22-5:52] "had you just waited for this three-line strike to form... and then had your entry set at the close of that candle with a stop loss literally cents above the previous high, targeting the 200 moving average"
  - [4:31-4:40] "you don't want to make your take profit lower than that 200 moving average, even if it's previous support and resistance levels"
