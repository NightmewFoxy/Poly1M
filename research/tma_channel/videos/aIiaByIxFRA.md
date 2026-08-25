# Make More Money on Every Trade
- id: aIiaByIxFRA | views: 54000 | length: 467s
- market(s) shown: AUDUSD (TradingView + MT4)
- timeframe(s) taught: 1-minute chart for the MT4 execution example; the TradingView markup timeframe is unstated

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **21 moving average** (type unstated) referenced as the rejection MA; he notes the shown entry "did not reject off of the 21 but maybe like the seven if we were to change that moving average" [1:03–1:10] → a **7 MA** also exists on his template. Tools: **"trading floor risk calculator"** (TTF) for TradingView and MT4.
- Setup/context required: an established **uptrend**; a **three-line strike** candle formation at/near the moving average.
- Entry trigger: **enter at the close of the three-line-strike candle** [1:14–1:17].
- Stop loss: **below the previous swing low**, or a fixed **10 pips** "if you want to stay nice and comfortable" [1:20–1:27].
- Take profit: example uses **20 pips = 1:2 R** on a 10-pip stop [1:28–1:42]. Also demonstrates a **1:2** setup on MT4 with stop below the swing low.
- Trade management (the core of the video — trailing stop):
  1. **At 1:1 R (i.e. +10 pips on a 10-pip stop), move stop to break-even** — "once you get to a one to one on your risk reward you should move your stop loss to break even ... then it's a zero risk trade" [1:44–2:02].
  2. After BE, trail the stop **to each new higher low** of market structure: when price breaks past a swing, makes a new low and turns up, that new low becomes the stop [2:41–2:59].
  3. Alternative, looser trail: **keep the stop along the 21 moving average** [3:15–3:21].
  4. MT4 built-in trailing stop: right-click active trade → "Trailing stop" → preset **15 / 20 / 25 / 30 / 35 / 40 / 45 / 50 points** or custom. **Points are not pips: 15 points = 1.5 pips; a 50-point setting keeps a 5-pip trail** [4:41–5:07].
  5. MT4 manual method: drag the active stop-loss line up to a previous swing (example: risk was $500 = 1% of a $50,000 account; after the drag the risk was ~$200) [5:11–5:53].
  6. TTF risk calculator "TS" button: **box 1 = how far price must move in your direction before the trail activates; box 2 = the trail distance behind price**. Example uses **10 pips / 10 pips** — once price is +10 pips, the stop stays 10 pips behind price [6:16–7:33].
- Filters he adds: none (no session, news or day filter). He does add a **use-case filter**: trailing is worth it for **swing trading** (multi-day/week holds); for **scalping with a pre-decided R:R he says just let it play out** [3:28–3:47].

## Vague / untestable / chart-pointed claims
- [1:00–1:10] "we had a little three line strike right here this did not reject off of the 21 but maybe like the seven" — the entry candle and the MA touch are chart-pointed; MA **type** (SMA/EMA/SMMA) never stated for either the 21 or the 7.
- [2:10–2:33] "you are essentially keeping track of Market structure ... looking at these low points and using those to judge your stop loss" — which swing lows qualify is eyeballed; no swing-definition (no N-bar pivot rule).
- [3:05–3:11] "if you keep your trailing stop loss too tight you will get closed out of a position like it did right here" — tightness threshold never quantified.
- [3:53–4:16] the MT4 vs TradingView discrepancy ("because of the price difference it did not pop up ... I got into this trade extremely late ... two candles later") — an anecdote about feed differences, not a rule.
- [7:00–7:08] "it's kind of getting a little bit of resistance which is also a previous high point" — discretionary reason for activating the trail at that moment.

## Testability
- rating: MEDIUM (the trailing/BE rules and the 10-pip / 1:2 numbers are fully mechanical; the entry depends on the three-line-strike + unspecified MA type, and structural trailing needs a swing definition)
- overlap: three-line-strike (entry), trade-management/trailing-stop (main topic), market-structure/BOS (the higher-lows trail), 5m-scalp(SMMA) family via the 21/7 MA reference
- notable quotes:
  - [1:44] "once you get to a one to one on your risk reward you should move your stop loss to break even ... because then it's a zero risk trade"
  - [4:49] "this 15 points is not 15 Pips it is 1.5 Pips so if you have a 50 point stop loss on a 4X pair it's going to keep your stop loss five Pips"
  - [3:15] "instead of every single one of these higher lows is essentially keep your stop loss along the 21 moving average"
