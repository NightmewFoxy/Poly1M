# Best Scalping Indicator **FREE**
- id: 6mr-XMcYU5c | views: 296000 | length: 735s
- market(s) shown: unstated pair (chart re-used from his "naked trading" video); strategy claimed generic
- timeframe(s) taught: unstated — indicator explicitly said to adapt across timeframes ("whichever time frame you're on")

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: the free **"Arty / TMA" + "TMA Divergence"** TradingView indicators (2 slots, added via the Discord links) [4:14-4:24]. Bundled contents, all default — "you do not need to adjust any of the settings" [4:24-4:34]:
  - **Smoothed moving averages (SMMA)**: 21 = white, 50 = green, 100 = yellow (optional, he turns it off — "I don't really like using the 100"), 200 = red [4:49-5:05, 8:06-8:15]
  - **RSI length 14**, colour yellow, **no upper/lower band, single solid line at 50** [8:15-8:47]; plus an added "floating moving average" line on the RSI that adapts per timeframe [8:47-9:07]
  - Engulfing-candle arrows (single arrow) and **three-line-strike** arrows (double arrow) [5:23-6:11]
  - A shaded **session cloud** with selectable timezone: New York / London / Tokyo session, default = American session; plus per-weekday checkboxes so you can exclude days [7:24-7:59]
  - A red/green cloud from price to the moving average showing up- vs down-trend [5:07-5:21]
  - Automatic bullish/bearish RSI **divergence** labels [9:26-10:03]
- Setup/context required: "if we are above the 200 period moving average we are looking for buys; if we are below the 200 period moving average we are looking for sells" [4:36-4:48]. After price breaks the 200, **wait for all moving averages to line up in order — 21, 50, 200** [6:14-6:22]. RSI must be on the correct side of 50: buys above 50, sells below 50 [8:20-8:31].
- Entry trigger: price pulls back to the **first moving average (the 21)** and rejects off it with a **bearish/bullish engulfing candle** (single arrow) — "this right here would have been your entry candle with a bearish engulfing"; a **three-line strike** (three consecutive candles then one big opposite engulfing candle) at the same location is "an even stronger entry point" [6:22-6:42]. Secondary/confirming trigger given: price crossing the RSI's floating moving average [9:07-9:19].
- Stop loss: **"you double the length of that bearish engulfing candle for your stop loss"** [6:42-6:48] — i.e. stop distance = 2x the entry candle's range, measured from the entry.
- Take profit: **fixed 2:1 risk-reward** — "you keep your risk to reward at a 2 to one" [6:48-6:54].
- Filters he adds: session cloud restricts you to your normal trading window [7:17-7:31]; weekday exclusion — "if you don't trade Monday or Friday because those are like trap days you can just untick these two boxes" [7:47-7:59]; mark up support/resistance manually first (per his naked-trading video) and prefer entries where a fat rejection off a prior level coincides with a three-line strike and RSI on the correct side of 50 [10:16-10:43].

## Vague / untestable / chart-pointed claims
- [0:23-1:15] Long framing section; the whole video is an indicator install walkthrough, so much of the "rule" content is restated rather than newly specified.
- [6:22-6:31] "price usually pulls back to the first moving average, the 21, and rejects off of it" — "usually", no tolerance band for what counts as a touch/rejection.
- [9:07-9:19] "at this point right here we crossed below that floating moving average and right here is going to be your entry point" — chart-pointed; the "floating moving average" on the RSI is a custom, undocumented calculation (no length/type given).
- [9:19-9:26] "you could have actually waited for this move to be 100% positive... either one of those two entries would have still got you in profit" — two different entries both declared correct after the fact.
- [9:43-10:03] Divergence definition given only for the bullish case ("lower lows on the price action and higher lows on the RSI"); no lookback window for what counts as a valid swing pair.
- [10:16-10:43] "a fat rejection off of a previous level of resistance creating a new support with a big three-line strike bullish engulfing high up on the RSI — you can take these positions to the next zone" — "next zone" is a hand-drawn S/R level, no numeric target.
- [4:24-4:34] Claims the shipped defaults are exactly his settings, but the numbers for the divergence detector and the floating RSI MA are never shown.

## Testability
- rating: MEDIUM (entry, stop = 2x candle, TP = 2R, and the MA/RSI filters are all fully specified; the "reject off the 21" tolerance and the custom RSI floating-MA are undefined)
- overlap: 5m-scalp(SMMA) + three-line-strike + candlestick-pattern + regular-divergence + session-filter
- notable quotes:
  - [6:14-6:31] "the price breaks below the 200 period moving average, we wait for all the moving averages to line up in order — the 21, the 50 and the 200 — price usually pulls back to the first moving average, the 21, and rejects off of it"
  - [6:42-6:54] "each one of these you double the length of that bearish engulfing candle for your stoploss and you keep your risk to reward at a 2 to one"
  - [8:20-8:31] "I like to be looking at buys when I'm above the 50 level on the RSI and sells when I'm below the 50 level on the RSI"
