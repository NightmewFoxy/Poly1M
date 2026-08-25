# US30 Trading Strategy
- id: UxsoJpfZ4Zc | views: 283000 | length: 484s
- market(s) shown: US30
- timeframe(s) taught: **15 minute** chart, with an explicit preference for higher — "I want you to focus on a higher time frame, even 15 minutes is a little bit low" [1:08-1:18]. This is the long-hold counterpart to his US30 scalping video.

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **Smoothed moving averages 21 / 50 / 100 / 200** (four of them here, not three) — white, green, yellow, red. Either add the built-in "smoothed" four times or use the "three smoothed moving averages" script if you're on the free tier [1:18-1:55]
  - **RSI length 14**, colour yellow, **upper and lower band both set to 50**, solid line [1:55-2:19]
- Setup/context required:
  - Trend filter: **above the 200 SMMA look for longs, below it look for shorts** [2:21-2:33]
  - No-trade filter: "you also do not want to trade when it looks like this — if it's flatlined and dead there is low momentum causing spikes up and down and there's no clear trend"; wait for **clear spikes and dips** above or below the 200 [2:33-2:53]
  - Market structure: a downtrend is a staircase of lower highs and lower lows; the **break in structure** is price breaking the previous high (or low) and thereby leaving the staircase [2:53-3:24]
  - The stated mistake to avoid: "they see a break in structure but they do not wait for **new structure to be formed**" — you must get a clear new high and clear new low, ignoring "tiny little steps" [3:29-3:49]
  - Confirming: after the break, all moving averages should be **fanning out** [3:24-3:29]
- Entry trigger: **after new market structure has formed, enter on the bounce off the 200 SMMA** — in the example the bounce is marked by a large wick into the 200 ("represented by this huge ass wick, this is where you would have gotten in") [3:49-4:04]. Then check the RSI is on the correct side of 50 (above 50 for the long) as the final confirmation [6:34-7:14].
- Stop loss: **below that wick** (the wick of the bounce candle off the 200) [4:04-4:07]. Then, as soon as the trade is in profit, **move the stop into profit immediately** — "like 50 bucks, 20 bucks" rather than risking any loss [4:16-4:51].
- Take profit: no fixed R multiple and no fixed level — it is a **trailing-stop hold**. Trail the stop on the **200 SMMA** first, then step it up to the next moving average as price advances, but "make sure you don't get too close to the price because you could get stopped out on a quick correction" [4:51-5:08]. He shows that trailing on the 50 or 21 would have stopped you out while trailing on the **100** kept you in [5:08-5:18]. Late-trade management: "you could close 90% of your trade, take your profits, secure that, and then move your stop loss up to the 21 or the 50" [6:11-6:30]. Worked result: **778 points on US30 over 4 days 16 hours** [5:18-6:07].
- Filters he adds: RSI above 50 = bullish momentum, below 50 = bearish, used only as a post-analysis confirmation [6:34-7:14]; **plus the direction of the 200 itself** — "you also have to take into consideration what direction that 200 moving average is going: if it's going down like this you're only looking for short positions, if it's going up like this you're only looking for long positions" [7:14-7:28].

## Vague / untestable / chart-pointed claims
- [2:33-2:53] "if it's flatlined and dead" / "wait for clear spikes and dips like this" — the no-trade filter is purely visual, no ATR, slope, or MA-separation threshold.
- [3:29-3:49] "don't get bothered by these tiny little steps, these do not equate for a higher low and a higher high — you want them to be clear and concise like this is a high and this is a low" — the core structure rule is explicitly eyeballed; no minimum swing size in points or bars.
- [3:49-4:04] "once this new market structure is formed and it bounces up, this is your indication, clearly bouncing off of the 200 period moving average represented by this huge ass wick" — chart-pointed entry; no rule for how deep the wick must pierce the 200 or what counts as a bounce.
- [3:24-3:29] "all the moving averages are fanning out showing a clear and concise momentum move" — "fanning out" has no numeric definition.
- [4:16-4:51] "once you get into profit put your stop loss into profit immediately... like 50 bucks, 20 bucks" — dollar amounts are account-specific, not a scalable rule; and moving the stop to breakeven-plus immediately is in tension with the trailing-on-the-200 rule that follows.
- [4:51-5:08] "make sure you don't get too close to the price because you could get stopped out on a quick correction" — which moving average to trail on is chosen after the fact (he shows the 100 worked and the 50/21 didn't).
- [6:11-6:19] "this is a ridiculous trade to continue to hold at this point" — the decision to take the 90% off is a judgement call with no trigger.
- [5:18-6:07] The 778-point open trade is shown as an unclosed position, so the final result is unknown.

## Testability
- rating: MEDIUM (trend filter, structure-break concept, entry location and initial stop are stated, but "clear and concise" structure, the wick-bounce, and the choice of trailing MA are all discretionary; there is no fixed exit)
- overlap: market-structure/BOS + 5m-scalp(SMMA) trend filter + trailing-MA exit
- notable quotes:
  - [2:21-2:33] "when you are above the 200 smoothed moving averages you want to look for long positions, and when you are below the 200 smoothed moving average you want to look for short positions"
  - [3:29-3:38] "this is the mistake that most traders make: they see a break in structure but they do not wait for new structure to be formed"
  - [4:51-5:08] "you use this 200 period moving average as your new trailing stop loss, [and] as it gets higher and higher you can then subsequently move your stop loss to the next moving average"
