# Best Volume Indicator for Day Trading
- id: SKb_LKNGhSY | views: 170000 | length: 367s
- market(s) shown: unnamed FX pair (Frankfurt session referenced [4:04])
- timeframe(s) taught: 15-minute for entries/stops; 1-hour / 4-hour / daily for targets [4:09]

## Mechanical rules (only what the video actually states)
This is an indicator setup + zone-reading tutorial rather than a full entry system.

- Indicators + exact settings:
  - **"Volume Profile" from TradingView community scripts, author "KV for coins"** [1:23–1:33]. Add it **twice** to the chart [1:39].
  - **Copy 1 — bullish:** Delta Type = **Bullish**; **Bar Horizontal Offset = 100** (so the profile sits right of price and doesn't overlap it) [2:41]; bar colour = yellow (to match his bullish candles); **POC colour = orange** [3:01].
  - **Copy 2 — bearish:** Delta Type = **Bearish**; **Bar Horizontal Offset = 100**; bar colour left greyed out; **POC colour = white** (matching his bearish candles) [3:19–3:35].
  - All other settings left at default [2:39] "all of these stay the same except for the bar horizontal offset".
  - He also keeps the standard TradingView volume histogram on the chart to see which candles/zones carry volume [1:50], while saying the default volume pane alone is useless [1:31] "you would think at a lot a bit of volume the price would do something more than consolidate which is why I hate this".
  - Chart colours: bullish = yellow, bearish = white (says it is psychological, better than red/green) [0:54].
- Setup/context required: identify the **POC (point of control, the highest-volume price)** separately for buying and selling volume. Read rejection at the POC: [2:18] "if price is rejecting the highest volume area that means that currently the price will probably continue down" — described as a trap: big volume, down wick up into the high-volume area, then down.
- Entry trigger: **not mechanically defined.** The demonstrated case is a short after price leaves the high-volume zone [4:41] "if you were to enter in a short position after it left that zone".
- Stop loss: **above the wick where everybody got trapped** [4:55] — i.e. beyond the high-volume rejection wick, set from the 15-minute chart.
- Take profit: **the next high-volume level on a higher timeframe** (1h/4h/daily) — where the opposing (buying) volume sits [4:09–4:38]. In the example this produced **a 1:3 risk-to-reward** [5:02].
- Filters he adds:
  - **Low-volume zones invalidate S/R.** [5:16] a support zone revisited on very low volume "is most likely going to disrespect this Zone" — it broke, retested and continued down. Rule stated: [5:38] "when trading smart money concepts of double bottoms and areas of support and resistance you will know that due to low volume this is not a viable option to set up an order to buy at this Zone."
  - Use in confluence with higher-timeframe support/resistance markup [5:07].

## Vague / untestable / chart-pointed claims
- [2:18] "if price is rejecting the highest volume area" — "rejecting" is never defined (no candle pattern, no close-beyond rule).
- [2:23] "a little bit of a trap big volume down Wick up into the high ball volume and down" — narrated off the chart.
- [4:14] "just go up to a higher time frame like the one hour the four hour or the daily" — which one to use is left open.
- [4:28] "right now we are in this dead zone of volume so it is most likely to continue down" — "dead zone" has no numeric threshold (no % of POC volume).
- [5:22] "there was very low volume it's most likely going to disrespect this Zone" — "very low" undefined.
- [4:55] "adjust your stop loss to above that Wick where everybody got trapped" — chart-pointed wick.
- [5:02] "now you're looking at a one to three risk to reward" — outcome of that one example, not a rule.
- [3:04] "I don't know what POC stands for maybe point of control" — he is not certain of the indicator's own terminology.
- No entry candle/trigger and no session filter given, so this cannot be backtested as a standalone strategy.

## Testability
- rating: LOW (indicator configuration is fully specified and reproducible, but entry, "rejection" and "low volume" are all undefined)
- overlap: volume-profile (primary); S/R-retest as confluence
- notable quotes:
  - [1:23] "click on the indicators tab type in volume profile it's going to be in the community scripts and the author of this indicator is KV for coins ... click the volume indicator twice that way you have two on your chart"
  - [2:41] "all of these stay the same except for the bar horizontal offset I like to set this at 100 ... the next thing that you're gonna do is change the delta type to bullish"
  - [5:38] "you will know that due to low volume this is not a viable option to set up an order to buy at this Zone"
