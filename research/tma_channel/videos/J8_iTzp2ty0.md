# Highest Win Rate Strategy I Have Ever Tested Period!
- id: J8_iTzp2ty0 | views: 48000 | length: 420s
- market(s) shown: German 40 / DAX only — "this is only for German 40 on the 5 minute chart if you're going to ask me about crypto or something else I don't know" ([0:31]). Gold is used only as a re-tuning example.
- timeframe(s) taught: 5-minute

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: ONE indicator, a paid/gated TradingView indicator called **"The Wave Rider"** (his affiliate link). Full settings dictated at [0:53]–[1:17]:
  - Short EMA = **100**
  - Long EMA = **200**
  - "use short EMA" box = **unchecked**
  - RSI source = **close**
  - RSI length = **3**
  - Overbought = **80**, Oversold = **20**
  - (an unnamed box at [1:07]) = **unticked**
  - ATR period = **10**
  - ATR multiplier = **3**
  - (the following box at [1:11]) = **ticked**
  - Style tab: **uncheck the short EMA** (display only)
  - He tells viewers to screenshot the settings panel.
- Setup/context required: None beyond the indicator's own signal. "the rules for entry if you get a Buy Signal you enter if you get a sell signal you enter" ([1:18]).
- Entry trigger: The Wave Rider **buy/sell signal print**. Entry is at the signal, no confirmation candle required.
- Stop loss: "your stop loss is set to the previous swing high[/]low or if that is too close to where the entry price is set the stop loss to the floating moving average" ([1:26]). Worked example: "the swing high right here is a 70 point stop loss" ([2:05]) on German 40.
- Take profit: Fixed **1:4 risk-to-reward** — "your risk reward ratio is 1 to 4 that means for every 1% you risk you aim to gain 4% in profit" ([1:35]). **Break-even management is mandatory**: "as the trade is going into profit you will move your stop-loss to break even once you are at a one:1 risk to reward ratio this is very important" ([1:42]). He asks that "break even" actually be set slightly into profit — "just get at least five bucks out of the trade" — to cover commissions ([3:10]–[3:22]).
- Filters he adds: None — no session, day-of-week or news filter is stated. Trade frequency is naturally low: "you will not be trading every day and who knows sometimes you might not even trade that week the signals are few and far between" ([2:16]).
- **Tuning procedure for other instruments** (stated as a rule, [5:56]–[6:40]): open Wave Rider settings, set ATR multiplier to its **lowest value 0.5**, then step it **up in 0.5 increments** until signal count drops to a small number of high-quality signals. On gold he judges 2.5 too high and **2** better. Then optionally reduce the ATR period.

## His stated backtest result (as claimed, not verified)
- Period: **August 1 to September 5** on German 40 5m ([4:46]).
- **11 trades: 7 winners, 4 break-even, 0 losers**, = **28R** at 1:4 ([4:49]–[5:00]).
- Individual trades he narrates with dates/times: Aug 1 signal at **4:00 p.m. UTC+2** ("I live in Europe that's my time zone", [2:00]) — 70-point stop, win; a sell signal (win); **Aug 8 ~2 p.m.** buy (win); **Aug 9** buy (reached 1:1 then stopped at BE); **Aug 15** buy (win); **Fri Aug 16** long (BE after 1:1); **Mon Aug 19** (win); **Aug 27** buy (win); **Aug 28** buy (win); one more buy (BE); **Sept 3** buy (BE).

## Vague / untestable / chart-pointed claims
- The core signal is a **closed-source paid indicator** ("if you want access to this indicator it's going to be the first link in the description", [6:52]) — the buy/sell logic is not disclosed, so the strategy cannot be reproduced from the transcript alone. The named settings (EMA 100/200, RSI(3) 80/20, ATR 10 x 3) suggest the internals but do not define the signal.
- [1:07] and [1:11] Two settings checkboxes are referred to only as "this box" while pointing at the panel — their names are never spoken. Frame-check required to get a complete settings list.
- [1:28] "or if that is too close to where the entry price is" — "too close" has no threshold (no minimum stop distance in points or ATR).
- [1:32] "set the stop loss to the floating moving average" — which of the two EMAs (100 or 200), or a third plotted line, is never said; the short EMA is explicitly hidden in the style tab, which muddies this further.
- [4:24] / [4:33] Some stop placements deviate: on one trade he sets the stop "to this one of the entry of the previous one" ([4:36]) rather than to a swing — an undocumented exception to the stated stop rule.
- [6:09] "just go up by 0.5 and get it to the point where you're only getting a smaller amount of signals but the likelihood that they're going to play out is much higher" — this is explicit **in-sample curve fitting** with no out-of-sample step; the 28R headline result comes from the same 5 weeks used to pick the settings.
- The 11-trade / 5-week sample is far too small to support the "highest win rate ever tested" title; no losers in the sample is itself a red flag for the fitting above.
- [5:06]–[5:31] The account-size income table ($100 -> $28 ... $200,000 -> $56,000/month) assumes 1%/trade compounding-free risk and is promotional, not a rule.

## Testability
- rating: MEDIUM — everything except the signal itself is fully mechanical and numerically pinned (1:4 R, BE at 1R, swing stop, 5m German 40, exact indicator parameters). It drops to LOW-in-practice because the entry signal lives inside a closed paid indicator, and the "floating moving average" fallback stop is ambiguous.
- overlap: other (proprietary indicator signal) — closest in spirit to the channel's trend + RSI-momentum family (EMA 100/200 trend filter with a fast RSI(3) 80/20 trigger and an ATR-3 stop rail, which is what the exposed settings describe); fixed-R money management shared with the rest of the channel.
- notable quotes:
  - [0:53] "you want the short EMA to be 100 the long EMA to be 200 ... the RSI source to close the RSI length to three overbought 80 oversold 20 ... ATR period 10 ATR multiplier 3"
  - [1:26] "your stop loss is set to the previous swing high[/]low or if that is too close to where the entry price is set the stop loss to the floating moving average your risk reward ratio is 1 to 4"
  - [1:42] "as the trade is going into profit you will move your stop-loss to break even once you are at a one:1 risk to reward ratio this is very important"
