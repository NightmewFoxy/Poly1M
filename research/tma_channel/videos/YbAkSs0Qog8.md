# Ultimate Scalping Strategy   1 min 5 min Timeframe
- id: YbAkSs0Qog8 | views: 115000 | length: 410s
- market(s) shown: German 40 (DAX). Backtest list quoted: Bitcoin, NAS100, gold, GBPJPY, EURUSD, German 40, AUDUSD, US30, UK100, GBPUSD
- timeframe(s) taught: **5-minute for analysis/bias, 1-minute for entries**; a 15-minute variant is also referenced in the backtest sheet

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  1. **"ICT New York Midnight Open and Divider"** — used as a **visual day separator only**. Settings stated: **turn the horizontal line OFF**; shift the divider from New York midnight to his own session because he is in central Europe, **GMT+2** [0:53–1:24]. (He notes a *different* strategy of his does use the true NY-midnight line + horizontal line — "but that's a different video".)
  2. **"Fractal Frenzy"** (his community's indicator) — settings stated: **allow signal repainting = ON**; enable the **DR/IDR ranges for the Tokyo, London and New York sessions** ("this is Japan, Europe and New York"); **extend each one of them**; "the rest of the settings stay exactly the same" [1:30–1:57]. Signals: red tornado above a candle = sell, green tornado below a candle = buy [3:08–3:19]. The indicator also has a **sensitivity** setting used as a backtest variable [5:31].
- Setup/context required:
  - **Daily bias from the Tokyo/Asia session range: above the Tokyo session = bullish, below the Tokyo session = bearish** — applies for both London and New York [2:12–2:27].
  - **DR/IDR = the first hour of the session** ("defining range" and "implied defining range") [2:27–2:40].
  - Basic version: "if it goes above this box it's going to go up; if price breaks below the box it's going to go down" [2:40–2:47].
- Entry trigger (the 1-minute version) [4:01–4:33]:
  1. Confirm daily bias vs the Tokyo DR/IDR box.
  2. Wait for the session (London or NY) DR/IDR **breakout in the direction of that bias**.
  3. Drop to the **1-minute chart**, wait for a **pullback**.
  4. Take the **Fractal Frenzy tornado signal in the breakout direction** → enter.
- Stop loss: "we set our stoploss" [4:28] — placement **never stated**.
- Take profit: **1 : 1.5 risk to reward**, stated twice [3:24, 4:31].
- Filters he adds (worked examples at [3:20–3:48]):
  - Trade only when the session breakout agrees with the Tokyo bias — "with the New York session it broke out above, but because we are below the Tokyo session we're not taking the trade because we are bearish."
  - **No breakout, no trade** — "London session we did not break out, we do not trade."
- Statistical claim used as the edge: "over the last 20 years, statistically **80% of the time** when price breaks out from the upper or lower end of the DR/IDR range it will continue in that direction" [2:47–3:07].
- Results claimed: he passed a funded-account challenge using the simple (non-1m) version for the whole month of April [3:48–3:55]. Backtest sheet columns quoted: timeframe, indicator sensitivity, session, risk-to-reward, % gain, max drawdown, number of trades, win rate, for **2023 and 2024**; sessions broken out as late Asia / London / mixed / New York; headline number **"a 36% gain just by trading it on the 5 minute time frame between 2023 and 2024"** [6:13–6:19]; "Bitcoin was very profitable" [6:05].

## Vague / untestable / chart-pointed claims
- [1:30] "Fractal Frenzy" is a paid/closed-source indicator — the actual entry signal cannot be reproduced; only the surrounding session framework can.
- [2:03] "I'm drawing these boxes so that you can get a clear view of this session" — the Tokyo box is hand-drawn on top of the indicator; exact session clock times are **never given** (only "Tokyo / London / New York", "Japan, Europe and New York").
- [2:12] "if we are below the Tokyo session we are bearish, if we are above the Tokyo session we are bullish" — "above/below the Tokyo session" is not defined as above the range high vs the DR/IDR box high vs the session close.
- [2:47] "over the last 20 years statistically 80% of the time... it will continue in that direction" — no source, no instrument, no sample size; the load-bearing statistic of the strategy is unverified.
- [4:12] "we then take the price down to the one minute chart looking for our pullback" — "pullback" is never defined (no fib level, no % retrace, no bar count).
- [4:28] "we set our stoploss and we set our takeprofit for a 1 to 1.5" — **the stop-loss placement is never stated**, so the 1:1.5 target is unanchored. This is the single biggest hole in the video.
- [1:07] "since I live in central Europe... currently I'm GMT plus 2" — the divider offset is personal to him; a coder would have to guess which anchor matters.
- [3:48] "I was able to pass a funded account challenge just using this strategy" for "the entire month of April" — year unstated.
- [5:12] The backtest workbook is a gated resource; the numbers are read off screen, not derivable.

## Testability
- rating: MEDIUM (the session/DR-IDR framework, the Tokyo-bias filter, the breakout-then-pullback sequence and the 1:1.5 RR are all clearly stated — but the entry signal is a closed-source indicator and the stop-loss rule is entirely missing)
- overlap: session-filter (Asia-range bias + DR/IDR breakout, ICT-flavoured) + proprietary-indicator-signal; adjacent to market-structure/BOS
- notable quotes:
  - [2:18] "If we are below the Tokyo session we are bearish. If we are above the Tokyo session we are bullish."
  - [2:47] "Over the last 20 years, statistically 80% of the time when price breaks out from the upper or lower end of the DR/IDR range it will continue in that direction."
  - [4:39] "Once we have our breakout we wait for a pull back and then our signal on the one minute time frame in the direction of the breakout."
- update relationship: he explicitly carves out a *different* strategy that uses the true New York midnight line plus its horizontal line ("but that's a different video") [1:12–1:21], and points to an in-depth playlist for per-timeframe entries/biases.
