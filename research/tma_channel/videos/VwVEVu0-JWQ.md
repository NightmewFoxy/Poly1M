# Divergence Trading Strategy
- id: VwVEVu0-JWQ | views: 839000 | length: 743s
- market(s) shown: EURAUD, AUDUSD (forex examples), US30 and GER30/German 30 (indices examples)
- timeframe(s) taught: **1 hour** — "all this analysis was done on the one hour time frame and I suggest you do this on a higher time frame" [8:47-8:58]; concept said to work on all timeframes but with more false signals below

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **RSI only**, no other indicator. Built-in Relative Strength Index, **length 14 (leave it)**, colour yellow, **upper band and lower band both changed to 50**, drawn as a **solid line** (not dotted) [2:02-2:20]. Explicit rationale: "looking at the market as overbought or oversold is the wrong way to trade the RSI — the RSI is a momentum indicator" [2:24-2:36].
- Setup/context required: four divergence types, defined numerically by swing comparison:
  - **Regular bullish** (reversal): price makes a lower low, RSI makes a higher low. Worked example: RSI bottom 1 = **19**, bottom 2 = **21** [3:11-3:23].
  - **Regular bearish** (reversal): price higher high, RSI lower high [5:27-5:34].
  - **Hidden bullish** (continuation): price higher lows, RSI lower low [6:15-6:24].
  - **Hidden bearish** (continuation): price lower highs, RSI higher high [7:09-7:23].
  - He tells beginners to trade **only the hidden divergences**, because they are with-trend: "the number one rule in day trading... is the trend is your friend" [5:41-6:01].
- Entry trigger:
  - Regular divergences: wait for a solid rejection. "This candle is too small for a rejection so you want to wait for a subsequent candle in that direction" — i.e. **enter at the close of the second rejection candle** [3:37-4:01, 4:52-5:01].
  - Hidden divergences: the rejection candles here are the strongest, so **one big fat rejection candle is enough** — "instead of waiting for two you can trade just off of this one" [7:26-6:55].
  - Optional extra confirmation for regular divergences only: draw a trendline across the highs (downtrend) or lows (uptrend) and require price to **break the trendline**, entering at the **close** of the breakout candle — "always wait for the close of the candle because... it could wick back down being a false breakout" [9:21-10:30].
- Stop loss: **below the wick of the signal candle** for longs / **above the previous high (or the high of that candle)** for shorts [3:50-3:53, 5:01-5:05, 7:38-7:40, 10:51-10:54]. For hidden bullish he says target/anchor "the bottom of that big move candle" [6:58-7:01].
- Take profit: **fixed 1:2 risk-to-reward** — stated for every one of the four setups [4:00-4:04, 5:05-5:07, 6:58-7:03, 7:40-7:43]. Scale-out rule: at the 1:2 target **close 90% of the trade and move the stop on the remaining 10% into profit**, then let it ride [4:04-4:18]. Beginners: "just take 100% of the trade right here at a one to two" [4:24-4:29].
- Filters he adds: prefer the 1h or higher because divergences "hold more weight" and lower timeframes have more false signals [8:50-9:00]; trendline-break confirmation applies **only** to regular (reversal) divergences, "it's only for the regular bullish divergence or the regular bearish divergence trades" [9:25-9:30]; before clicking any button, check for a divergence and a trendline break [11:00-11:16].

## Vague / untestable / chart-pointed claims
- [3:37-3:46] "watch a solid rejection — this candle is too small for a rejection" — no numeric size threshold for what makes a candle count as a rejection.
- [6:49-6:52] / [7:31-7:35] "we get this big fat rejection candle and these are the ones that are the strongest" — "big fat" undefined.
- [2:46-3:11] Which swing lows are compared for the divergence is chosen by eye ("my eye is always going to the RSI to spot a big fat divergence"); no swing-detection rule or lookback.
- [5:11-5:21] "once you get out of being a beginner day trader you can continue to hold these trades depending on the strength of the movement" — discretionary hold extension.
- [6:28-6:46] The oversold/overbought explanation for hidden divergence ("it became more oversold at this point than at this point... so it should continue up") is an argument, not a threshold.
- [10:31-10:47] The German-30 trendline example adds a retest step ("we came up to retest, rejected down and formed a new trend") that is not in the stated rule list.
- [7:52-8:47] P&L figures (36 pips, 41 pips, 100-point move, 321-point move with a 158-point stop) are quoted without entry/exit timestamps, so they cannot be reconciled with the stated 1:2 rule (321/158 ≈ 2.03R, consistent; the others are unverifiable).

## Testability
- rating: HIGH (RSI settings, all four divergence definitions, entry candle, stop placement and 1:2 target are all explicit; only "big enough rejection candle" and swing selection are discretionary)
- overlap: regular-divergence + hidden-divergence (this is the canonical TMA divergence video)
- notable quotes:
  - [2:02-2:20] "leave the length at 14... change the upper band and lower band to 50 and 50, making it a solid line, not a dotted line"
  - [3:37-4:04] "this candle is too small for a rejection so you want to wait for a subsequent candle in that direction — at that point you can put in your order with a stop loss below the wick of this candle... set your risk to reward ratio for a one to two"
  - [4:04-4:18] "once this target hits I want you to close ninety percent of your trade, move your stop loss for the remaining ten percent into profit so it's a completely 100% risk-free trade"
