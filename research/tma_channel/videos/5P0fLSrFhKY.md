# What Indicator Should You Choose?
- id: 5P0fLSrFhKY | views: 30000 | length: 458s
- market(s) shown: unstated (generic TradingView chart; London-session example)
- timeframe(s) taught: unstated

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **RSI** (his favourite) — length unstated, but the **70/30 bands** are the operative levels.
  - **MACD**, **Stochastic RSI**, **Ultimate Oscillator / Awesome Oscillator** — all settings unstated. Stochastic RSI is "more fine-tuned for lower time frames ... that laser sniper scope entry" [2:23–2:32]; Awesome Oscillator "shows me Trend changes better" [2:39–2:41].
  - Free TTF **"Any Oscillator Underlay"** — bundles TSI, RSI, Stoch RSI, Ultimate Osc, Awesome Osc, MACD and "orsi" into one indicator slot (workaround for TradingView free tier's **3-indicator limit**) [3:03–3:25].
  - Free TTF **"Simple Sessions"** — shows London / mixed / New York / Tokyo sessions; you can toggle off the sessions you don't trade so backtests only take entries inside your session [3:52–4:16].
  - Free TTF **"SMC Toolkit"** — draws S/R zones, the session opening ranges, and the midnight line [4:29–4:47].
  - **Fibonacci retracement** — the level he uses in the example is **0.618** [5:47–5:55]; "here are my settings for my Fibonacci tool take a screenshot and copy that" [5:55–5:59] — **settings shown on screen only, never spoken**.
  - **Gann box** — used to frame a consolidation range; settings stripped to show only **top of range, bottom of range, and the 0.5 equilibrium** [6:04–6:20].
  - Paid TTF indicators named: **Happy Trail** (buy/sell smiley-face signals), Outback, Brute Force, DeLorean, StairMaster.
  - **TTF risk calculator** for MT4/MT5: enter risk %, it computes account balance, position size and a **1:2** take profit from wherever you drag the stop [7:06–7:31].
- Setup/context required (the one full setup in the video — the midnight-line / London-open play):
  - **Midnight line** = the candle at **midnight New York time** (server reset), drawn out horizontally [5:01–5:12].
  - Bias: **price above the midnight line → buy only; price below → sell only** [5:16–5:22].
  - **Do not trade the first hour of London session** — "as London opens the first hour of London session open I consider that a no Trading Zone" [4:41–4:47]. The first-hour range then defines direction: **break below the London first-hour range → look bearish; break above → look bullish** [4:52–5:01].
- Entry trigger: after the first London hour, **enter on the break of that opening range in the direction already permitted by the midnight line** [5:22–5:31]. Optional signal-candle confirmation: enter short on an **upside-down smiley face from the Happy Trail indicator** [6:41–6:49].
- Stop loss: **"halfway between the opening of the session"** — i.e. mid-point of the London first-hour range [5:31–5:34].
- Take profit: **1:2 risk to reward** [5:34–5:37]; repeated for the Happy Trail entry [6:49–6:51].
- Filters he adds: session filter (London only, skipping hour 1); midnight-line directional bias; divergence-quality filter (below); "all oscillators are Trend indicators" so he wants **two oscillators in confluence** (e.g. Stoch RSI + Awesome Oscillator) before acting [2:43–2:51, 3:26–3:36].
- Divergence rule (a real, numeric one): "**if the first Divergence is outside of that 70 30 range and the next one is still outside of that 70 30 range wait for the one to be within the 70 30 range and use that one as your reversal point**" [1:39–1:50].
- Chart hygiene rule: **change candle colours off red/green to neutral** (his are yellow and white) because red/green candles bias you psychologically while in a position [0:51–1:07].

## Vague / untestable / chart-pointed claims
- [1:21–1:27] "price was going up and yet that entire time RSI was going down so you know that price reversal is imminent" — the divergence is chart-pointed; no swing-selection rule for which highs to connect.
- [2:02–2:11] "if you have a small pullback in an uptrend and you can see that the macd is oversold as it crosses over you can take a long position" — "oversold MACD" has no defined threshold (MACD has no fixed OB/OS bands).
- [3:30–3:44] "those two together would be your Confluence of seeing a break of structure come up to retest and break down" — chart-pointed BOS, no definition.
- [5:12–5:16] "price usually respects this line" (midnight line) — asserted, never quantified.
- [5:55] "here are my settings for my Fibonacci tool take a screenshot" — settings never spoken; needs a frame-check.
- [6:12] "just simply change your settings to this" (Gann box) — same problem, visual only.
- [6:20–6:26] "when price rejects the equilibrium point and breaks out look for retracement in and then a continuation to the downside" — "rejects" undefined.
- [6:41–6:49] the Happy Trail entry is a closed-source paid signal; not reproducible.
- [3:52–4:16] session times are named (London/NY/Tokyo) but **no clock times or timezone are given** anywhere except "midnight New York time".

## Testability
- rating: MEDIUM (the midnight-line + London-opening-range setup has a complete entry/stop/target and the 70/30 divergence filter is numeric; but session clock times, MA/RSI/fib settings and the final entry signal are visual or proprietary)
- overlap: session-filter (London first-hour no-trade + opening-range break), regular-divergence (RSI 70/30 rule), fib-scalp (0.618), volume-profile/SMC-adjacent (TTF SMC toolkit zones), other (indicator survey / TradingView tooling)
- notable quotes:
  - [1:41] "if the first Divergence is outside of that 70 30 range and the next one is still outside of that 70 30 range wait for the one to be within the 70 30 range and use that one as your reversal point"
  - [5:16] "if price is above the midnight line you buy prices below the midnight line you sell you avoid the first hour of London open wait for a break above that range ... enter in here stop loss halfway between the opening of the session ... with a one to two risk to reward"
  - [4:41] "as London opens the first hour of London session open I consider that a no Trading Zone"
