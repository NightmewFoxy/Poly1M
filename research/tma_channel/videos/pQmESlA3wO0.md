# 5 Minute Scalping Strategy Consistent WIN RATE
- id: pQmESlA3wO0 | views: 36000 | length: 295s
- market(s) shown: **CADJPY** (the headline example); says backtests cover indices and forex pairs, and recommends forex pairs for small accounts because indices need larger capital
- timeframe(s) taught: **unstated** — the transcript never names a timeframe (the title says 5-minute; the video is really a product launch for the "Wave Rider" indicator)

## Mechanical rules (only what the video actually states)
Note: despite the title, this is a promo for a paid proprietary indicator ("**The Wave Rider**", released Sept 1) rather than a self-contained strategy. The indicator's logic and settings are deliberately withheld ("all of the settings of the indicator are listed right here for you" — shown on a spreadsheet, never spoken, [2:23]).

- Indicators + exact settings: **"Wave Rider"** — a proprietary Trade Floor indicator that **prints a marker above the candle for a short and below the candle for a long** ([1:41]). Plus **one moving average** used as the trend filter — "if you're getting signals below this moving average you're going to be taking short positions" ([1:38]). **The MA's period and type are never stated.** The indicator's own settings are never stated.
- Setup/context required: trend-following. Take signals **below the moving average for shorts, above it for longs** ([1:38]–[1:44]). Trend end rule: "**once price fails to make a lower low you know the trend is over and you should be anticipating an uptrend trading above that moving average**" ([1:47]).
- Entry trigger: **every indicator signal** in the allowed direction — the baseline result is described as "mindlessly taking every single indicator signal with these parameters with these settings" ([3:11]). Multiple entries per trend are expected ("this is a very trend-based strategy so you're going to be getting multiple entries as you're trading this trend", [1:26]).
- Stop loss: **never stated** (implied by the fixed R:R but no placement rule is given).
- Take profit: fixed **1:1.5 risk-to-reward** as the primary tested config; a **1:2** variant is also shown ([2:12], [3:05]).
- Filters he adds: the one optional filter is a **price-action bias filter** — "**just marking up the higher highs and higher lows for the last 24 hours you'll get a general direction and use that for your next signal bias**" ([3:33]). Only take signals agreeing with that 24-hour direction.

## Stated performance figures (his claims, unverified)
- Backtest window: **1 September 2023 → 20 August** (updated weekly on a public spreadsheet), CADJPY, 1:1.5 R:R.
- Without the price-action filter: **461 trades, 56.6% win rate, +144R** ([3:45]–[4:04]).
- With the 24-hour price-action bias filter: **329 trades, 62.61% win rate, +143R** ([3:45]–[4:07]).
- Monthly spread described as 12%, 15%, 1.5%, up to 40% gains, with at least two negative months ([2:37]–[2:53]).
- His stated profitability bar: "if you can get a strategy that works more than 50% of the time you are a profitable trader" ([0:52]).

## Vague / untestable / chart-pointed claims
- The entire signal engine is a **closed-source paid indicator** — "the indicator prints above the candles for a short and below the candle for a long" is the only description of its logic. Not reproducible.
- [2:23] "you also have the settings for this specific pair and this specific strategy so all of the settings of the indicator are listed right here for you" — settings shown on screen only, never spoken; and they are **per-pair fitted**, which is an overfitting flag.
- [1:38] "if you're getting signals below this moving average" — **MA period and type never stated**.
- [3:33] "just marking up the higher highs and higher lows for the last 24 hours you'll get a general direction" — no swing definition, no rule for resolving a mixed 24-hour structure.
- **No stop-loss placement rule anywhere** — the 1:1.5 R:R is meaningless without it.
- [0:52] "if you can get a strategy that works more than 50% of the time you are a profitable trader" — false as stated at any R:R below 1:1; here it happens to be paired with 1:1.5 but the claim is made unconditionally.
- The two headline results (**144R over 461 trades vs 143R over 329 trades**) are presented as equivalent, which conveniently makes the filter look free; no drawdown, no per-month equity, no out-of-sample split, and the backtest window starts at the indicator's development period.
- [2:12] Backtest is on a **single pair (CADJPY)** with pair-specific settings — the classic curve-fit signature.

## Testability
- rating: LOW (proprietary closed indicator, no MA spec, no stop rule — nothing here can be reconstructed or backtested independently)
- overlap: MA-trend-filter, proprietary-indicator promo, market-structure/BOS (as the optional bias filter); despite the title it is not the 21/50/200 5m-scalp family
- notable quotes:
  - [1:38] "if you're getting signals below this moving average you're going to be taking short positions — the indicator prints above the candles for a short and below the candle for a long position"
  - [3:33] "just marking up the higher highs and higher lows for the last 24 hours you'll get a general direction and use that for your next signal bias — you can increase the win rate from 56.6% to 62.61%"
  - [3:11] "the information that I just gave you is mindlessly taking every single indicator signal with these parameters with these settings"
