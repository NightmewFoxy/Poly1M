# Best Crypto Trading Strategy
- id: uagC-2UjAO0 | views: 77000 | length: 473s
- market(s) shown: **BTCUSD** [0:09], examples run from Wednesday 1 November 2023 forward
- timeframe(s) taught: **1-hour chart, 4-hour higher-timeframe confluence** — "my chart time frame is 1 hour, my higher time frame Confluence is on the 4 Hour" [7:08]-[7:10]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **Gann box used as a PD array** — "it's just a gan box that shows you red on top and green on bottom. PD Ray stands for premium and discount" [0:25]-[0:32]. Settings shown on screen only.
  - **"Outback" by TTF** (paid) — prints kangaroo buy/sell symbols. Stated settings: "**I'm using case two**, my chart time frame is 1 hour, my higher time frame Confluence is on the 4 Hour, and I've literally turned everything off except for the buy and sell signals" [7:01]-[7:15]. Optional extras he names but did not use: higher-timeframe stochastic, the moving average, daily bias, previous day high/low [7:17]-[7:24].
- Setup/context required:
  - Identify **the move that broke previous structure** and draw the PD array (Gann box) over exactly that move; "previous structure is denoted here by the top of the PD array" [1:52].
  - **Structure break requires a candle CLOSE beyond the previous high, not a wick** — "candle closure above the previous high points, not just the Wicks" [2:47]-[2:49]; restated "this move did not break structure because it's a wick" [4:53]-[4:55].
  - Directional bias by half: "when markets are bullish you want to get in on discounted prices, when markets are bearish you want to get in on premium prices" [0:32]-[0:38]. Longs come from the **lower half** of the PD array, shorts from the **upper half**.
- Entry trigger: an **Outback kangaroo signal** taken only in the correct half of the PD array.
  - Primary (what he recommends): "usually what I do with PD arrays is only look for buy positions in these lower halves. I completely disregard any sell positions" [1:13]-[1:21].
  - Advanced/optional: short from a premium area down into the discount area as a scalp before the long — "if you are in an area of Premium you can take a short position into the area of discount, very very short term, before looking for your longer position on the bottom half" [1:34]-[1:45].
  - **Once price has reached the lower half, shorts are switched off:** "after price has gotten into the lower half of this PD you are no longer taking short positions until you get above the previous structure" [3:01]-[3:07].
  - **Skip signals whose candle closes at/near the 50% line:** "this candle closure was at the 50% level — not good to take a scalp down" [4:10]-[4:15]; "both of these candle closures are too close to the 50% range so we don't take that" [4:42]-[4:47].
- Stop loss:
  - In high-volatility pushes: "**you can move a couple of ticks above the previous candle**" [3:29]-[3:32] (he notes the raw stop "is ridiculous because there was a lot of volatility").
  - **Trailing rule (explicit):** "every single one of these trades, once it created a new PD array, this lower half is now your new moving and floating stop loss... you move your stop loss, essentially a trailing stop loss, for all of these trades to hold them longer" [5:22]-[5:42]; and "once price comes back and breaks the lower half of this PD array, all of your long positions get closed" [5:45]-[5:52].
- Take profit: **1 to 1.5 risk-to-reward is the default** — "we're doing 1 to 1.5 risk to reward ratios here" [1:59]-[2:04]. Held/trailed longs produced 1:5 in his examples ([2:33]) but that is an outcome, not a rule. Scalps down to the **50% level** of the PD array are the short target: "taking a short position down to that 50% level" [2:40].
- Filters he adds:
  - **Bias flip after a stop-out:** "once you get stopped out on a trade you should reverse your bias from long to short" [3:39]-[3:44].
  - Bias also flips when the PD array structure itself breaks: "now the PD array structure has been broken so now our bias is switched to long" [4:05]-[4:09].
  - Claimed cumulative result: "totalled all up, **up 97.7% since November**" [6:45]-[6:50] from the listed trade-by-trade percentages [5:55]-[6:40].

## Vague / untestable / chart-pointed claims
- [7:01] "I'm using case two" and "these are my settings" — the **Outback indicator is closed-source and paid**; "case 2" is meaningless outside the product. The entry signal cannot be reproduced. This is the dominant testability blocker.
- [0:53]-[1:06] "this indicator... is extremely complex and can be used so many different ways, it genuinely could fill up a 4-hour video. I have broken this down into the simplest most understandable way" — explicit admission that what is shown is a simplification of undisclosed logic.
- [0:25] Gann box settings are visual only (never spoken). Whether "lower half" means the 0–50% band of a 0/0.5/1 grid, or a finer Gann subdivision, is not determinable from the transcript.
- [1:47]-[5:05] The entire middle of the video is rapid chart narration ("this is the next move that broke previous structure... 1 to 1.5... take profit hit") with no dates, no prices and no way to verify. The 97.7% figure is assembled from these narrated outcomes.
- [3:25]-[3:32] "when you have big pushes like that you can move a couple of ticks above the previous candle" — this is a **discretionary override of the stop rule**, triggered by an unquantified "big push"/"a lot of volatility". Fatal for a mechanical backtest: it lets the stop shrink after the fact.
- [4:42] "too close to the 50% range" — no numeric tolerance given for how close is too close.
- [2:04]-[2:10] "depending on your skill level and if you want to do trailing stop losses" — the choice between fixed 1:1.5 and the trailing PD-array stop is left to the trader, so the same signal set yields wildly different equity curves (1.5R vs the 97.7% total).
- The stated 97.7% mixes 1:1.5 scalps with trailed positions and two still-open trades ("you still in two open positions plus 25" [6:27]) — an open-trade mark-to-market counted as realised.

## Testability
- rating: MEDIUM (structure-break definition is unusually crisp — candle close, not wick — and the PD-array half rule, 50%-line skip, bias-flip-on-stop and trailing-stop rules are all stated; but the entry is a paid black box and the stop has a discretionary volatility override)
- overlap: PD-array/premium-discount (Gann box) + market-structure/BOS + proprietary-signal entry. Same PD-array machinery as trx_M2Bss-c and x1-InyOycus, but here the divergence leg is replaced by the Outback signal.
- notable quotes:
  - [2:47] "candle closure above the previous high points, not just the wicks"
  - [3:01] "after price has gotten into the lower half of this PD you are no longer taking short positions until you get above the previous structure"
  - [5:22] "every single one of these trades, once it created a new PD array, this lower half is now your new moving and floating stop loss"
