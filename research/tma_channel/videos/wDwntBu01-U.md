# The Best Kept Secret (VOLUME PROFILES)
- id: wDwntBu01-U | views: 344000 | length: 330s
- market(s) shown: **GBPUSD** — "This is GBP USD on a 1H hour time frame" [0:52]
- timeframe(s) taught: **1-hour**

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **Volume Profile — Session Volume**, the TradingView built-in: "go into the indicators tab and click the technicals, the third option is volume profiles, I want you to select this one right here, volume profile session volume" [2:13]-[2:24]. No period/row-size settings given.
  - **VWAP** ("volume weighted average price") [4:17]-[4:21]. No anchor or settings given.
  - **RSI** — used once for divergence, **no settings and no levels stated** [1:08]-[1:16].
  - Trend line drawn by hand.
- Setup/context required:
  - An established trend with a **trend-line break and retest**: "a nice clear downtrend with a break of that trend line, a retest of that trend line and away up" [0:56]-[1:03].
  - A **regular bullish divergence**: "we were making lower lows but on the RSI we were making higher lows showing us a clear and concise Divergence" [1:08]-[1:16].
  - A **round-number level**: "a very important level on GBPUSD are even numbers — 1.3000" [1:21]-[1:28].
  - The high-volume node of the **previous session** becomes the S/R for the next: "this middle area where the volume was the highest, that's going to be your support and resistance for the next time frame" [2:41]-[2:48]; confirmed at [4:47]-[5:04] ("in the previous session this was the high volume area, this is now the level of support").
- Entry trigger — **the stated volume-profile rule, and he explicitly contradicts the common usage:**
  - Trend-continuation entry: on a counter-trend retest of the trend line, "wait until it got **through** that high volume area, then get into your position, because at this high volume area is where the pressure is going to push that market down continuing the trend" [2:55]-[3:08].
  - Explicit contrast: "a lot of people use these volume profiles as entries for their trades — that's the area that they want to get to and then get in their trade — **but I found that it works best if it's LEAVING that area**. If you are trading with the trend and the price is leaving that high volume profile area, you want to ride that trend down" [3:19]-[3:45].
  - VWAP direction filter: "**trade longs above the VWAP and shorts below the VWAP**, but overall in consensus with what the price is doing whether it's in an uptrend or a downtrend" [4:36]-[4:47].
- Stop loss: not stated as a rule. The one trade cited was "**just for 20 Pips with a 10 pip stop-loss**" [1:32]-[1:36] — i.e. a 1:2 R on GBPUSD 1H — but no placement logic is given.
- Take profit: **exit on volume decay, not a level** — "ride that Trend down until the volume starts decreasing and then get out of your position, because what we're seeing here is a loss of momentum" [3:42]-[3:53]. Also stated as a benefit: "if you get it as it's leaving that area and then the volume starts decreasing showing a loss of momentum, you can ride trades for much longer" [3:57]-[4:08].
- Filters he adds:
  - Avoid entering *inside* the high-volume node: "high volume, high volatility, easily stopped out in this area" [3:53]-[3:57].
  - Session framing: sessions are London (Europe), New York (Americas), Tokyo [1:51]-[2:06]. **No session times or timezone given.**
  - Explicit "don't use this yet" caveat: "a fun indicator that I want you guys to start learning and start training on — not implement this right away, I want you to be educated on this first" [2:06]-[2:13].

## Vague / untestable / chart-pointed claims
- [3:42]-[3:53] "**until the volume starts decreasing**" — the core exit rule, and it is entirely unquantified: no volume MA, no lookback, no % drop threshold, no bar count. This is the single biggest gap.
- [3:32]-[3:42] "price is **leaving** that high volume profile area" — no definition of what "leaving" means (close beyond the node's edge? beyond the VAH/VAL? beyond POC?). He never uses the terms POC / value area high / value area low at all, so which boundary matters is undetermined.
- [2:41]-[2:48] "this **middle area** where the volume was the highest" — the node is identified by eye, not by POC or a value-area percentage.
- [1:03]-[1:08] "a way up, a direction up, a rejection up, it went up" — chart-pointed narration of the setup.
- [1:08]-[1:16] The RSI divergence has **no length and no 70/30 filter** here, unlike udwkldark34 and trx_M2Bss-c. Cannot be reproduced from this video alone.
- [1:32] The trade itself ("20 pips, 10 pip stop") is reported after the fact from a Telegram post; no entry rule ties the 20/10 to the chart, and it is a single sample.
- [4:21]-[4:36] "I want you to use this [VWAP] as a trend indication — as the price came up here and rejected the trend line and then started trading below the VWAP, you know that it's going to keep pushing down" — assertion, no confirmation rule (close below VWAP? for how many bars?).
- [2:55]-[3:08] The trend-line retest that triggers the setup is drawn discretionarily.
- No R multiple, no position sizing, no session times, no news filter, no explicit stop rule.

## Testability
- rating: LOW (the direction filter — long above VWAP, short below — is the only fully mechanical element; the entry ("leaving the high-volume area"), the node identification and the exit ("volume starts decreasing") are all qualitative, and there is no stop rule)
- overlap: volume-profile (primary) + VWAP + S/R-retest (previous-session high-volume node as next session's S/R) + regular-divergence and trend-line-break as unquantified context. His highest-viewed video in this batch by 3x, and one of the least mechanical.
- notable quotes:
  - [3:19] "a lot of people use these volume profiles as entries for their trades... but I found that it works best if it's leaving that area"
  - [2:41] "this middle area where the volume was the highest, that's going to be your support and resistance for the next time frame"
  - [4:36] "you just want to trade longs above the VWAP and shorts below the VWAP, but overall in consensus with what the price is doing"
