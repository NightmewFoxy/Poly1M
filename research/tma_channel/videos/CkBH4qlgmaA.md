# Heikin Ashi Strategy **Best for Swing Trading**
- id: CkBH4qlgmaA | views: 390000 | length: 682s
- market(s) shown: US30
- timeframe(s) taught: **1h minimum** — [10:40] "I only want you guys to do this on a high time frame, nothing less than the one hour chart. The one hour chart is very ideal for US30." Explicitly NOT for scalping.

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **Heikin Ashi candles only.** No moving average, no oscillator, no numeric setting. (He defines the candle type: it shows the *average pace* of price movement and the candles overlap rather than open at the prior close.)
- Setup/context required: A mature trend that is losing momentum. Diagnostic sequence he states:
  - Strong downtrend HA candles have **no wick on the upper side, only on the lower side**; strong uptrend HA candles have **no wick on the bottom, only on the top** ([3:44]–[4:02]).
  - Trend exhaustion = candle **bodies shrink** and wicks appear on **both** top and bottom, ending in a **doji-style HA candle** ([4:38]–[4:48], [5:02]–[5:24]).
- Entry trigger: **The first HA candle after the doji that has no wick on the side facing the new trend.** For a long: after the doji, the first HA candle with **no wick on the bottom** → enter **at the close of that candle** ([4:56]–[6:12] "waiting for this first candle to form without a wick on the bottom, you can place a trade at the close of that candle"). Mirror for a short: after the doji, the first HA candle with **no wick on the top** → enter at that candle's close ([5:32]–[5:36], [7:13]–[7:29]).
- Stop loss: **Below the swing low** for longs; **just above the swing high** for shorts ([6:12], [7:24] "you set your stop-loss just above the swing high"). Restated at [10:04] "keeping your stop-loss below that swing high or swing low."
- Take profit: **1:2 risk-to-reward** as the default ([6:13] "I want you guys to be going for [2:]1 risk-to-reward ratio with this strategy"; restated [7:29], [8:57]). Alternative hold-for-the-trend management: hold the whole move until the HA candles shrink with wicks on both sides again, targeting marked S/R zones — his cited examples: a **477-point move with a 150-point stop (~1:3)**, one that ended ~1:2, and a **234-point move with a 91-point stop** ([9:19]–[9:40]).
- Filters he adds:
  - **Do not use Heikin Ashi for scalping** — the whole thesis of the video. Reason given with numbers: entering at an HA close of **34417** on US30, the very next candle ranged to **34388** — "nearly a 40-point move" of hidden drawdown ([6:33]–[6:57]).
  - Avoid the setup when the candles after the doji are **very small** — "these are not momentum moving candles and can actually keep you in a period of consolidation" ([8:11]–[8:25]).
  - The first momentum candle should be **substantially larger than the doji** ([7:55]–[8:08]).
  - Practise on **demo** first; set the trade and close the trading app so the HA drawdown doesn't shake you out ([6:20]–[6:27], [8:25]–[8:31]).

## Vague / untestable / chart-pointed claims
- [4:38]–[4:53] "these heiken Ashi candles are much smaller with wicks on the top and the bottom. This doji style candle is where the trend is likely to go the opposite direction" — "much smaller" and "doji style" have no numeric body/range threshold.
- [7:33]–[7:42] He concedes an example doesn't fit: "This one is a little bit [iffy] because the candle body is a lot bigger than I would expect with these types of doji candlestick but you could have still gotten in on this one" — the doji criterion is applied by eye.
- [7:55] "look at the size of this first candle... It is substantially larger than that doji candle" — no ratio given.
- [8:11]–[8:22] The avoid-condition ("subsequent candles are very, very small") is also unquantified.
- [9:08]–[9:19] The hold-for-the-whole-trend variant depends on S/R zones marked by hand and on judging when the HA candles are "getting smaller and smaller and smaller" — fully discretionary exit.
- [10:08]–[10:24] "Do you guys think that I'm cherry-picking some random examples? Look doji candle swing low, doji candle swing high..." — the robustness claim is a visual eyeball over one US30 chart; no sample, no win rate.
- [10:49] "I've been back testing this throughout the last few hours and it's absolutely nuts" — no numbers, no sample size.
- Swing low/high used for the stop is not defined (lookback unspecified).

## Testability
- rating: MEDIUM (the wick-presence rules are objectively codable — HA candle with no lower wick after a two-sided-wick small-body candle, entry at close, stop at swing low, 2R target — but "doji-style / much smaller / substantially larger" carry no thresholds and the swing lookback is undefined)
- overlap: candlestick-pattern (Heikin Ashi wick structure); adjacent to market-structure/BOS as the claimed earlier-entry alternative to waiting for structure to break
- notable quotes:
  - [4:56] "two candles after that, we get our first heikin ashi candle where there is absolutely no wick on the bottom. This candle right here is the entry point for the new trend direction"
  - [6:02] "waiting for this first candle to form without a wick on the bottom, you can place a trade at the close of that candle with a stop loss below that swing low and I want you guys to be going for [2]:1 risk-to-reward ratio"
  - [10:40] "I only want you guys to do this on a high time frame, nothing less than the one hour chart"
- relation to other videos: positioned as the swing-trading counterpart to his 5-minute Japanese-candlestick scalping system (he closes by pointing viewers to that scalping video); explicitly warns the HA method contradicts scalping use.
