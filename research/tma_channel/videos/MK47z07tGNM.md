# Best Scalping Strategy Period
- id: MK47z07tGNM | views: 1300000 | length: 714s
- market(s) shown: EURUSD (setup walkthrough), GBPJPY (long and short worked examples); claims to work on any pair, plus ETH and US30 anecdotes
- timeframe(s) taught: works on 1m / 5m / 15m; the worked examples are on the **5 minute** chart [7:16-7:23]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings (exactly three, to fit the free TradingView tier) [1:20-3:44]:
  - **"Three smoothed moving averages" by Hamid Safi**, inputs **21 / 50 / 200**; styles white, green, red, all full colour, second thickness [1:42-2:54]
  - **RSI, length 14**, upper and lower band both changed from 70/30 to **50 and 50**, changed from dotted to **solid**, colour yellow, second line thickness [2:55-3:28]
  - **Williams Fractals**, **periods input = 2** (left at default), style green and red full colour [2:10-2:22, 3:28-3:42]
- Setup/context required: a **trending market** where all three moving averages point the same way **and** price is on the correct side of all of them — "if the price is trending up, all three moving averages going up, I want the price to be above it; if all the moving averages are down I want the price to be below it" [4:18-4:41]. He shows the sequence: price breaks the 200, retests it as support, then the 21 and 50 cross over and sit above the 200, i.e. **stack order 21 / 50 / 200** [5:04-5:26].
- Entry trigger: the **first Williams Fractal arrow printed after all three moving averages line up** — "I want you to try to get the first move and the first Williams fractal signal when it crosses over the 200... here is too late" [5:26-5:50]. **Wait for the candle to close**, because the fractal repaints [5:50-6:04]. Enter at the top or bottom of the signal candle [6:13-6:22]. Direction filter: longs only when price is above the MAs, shorts only when below [6:04-6:13].
- Stop loss: **below the lowest part of the candle that printed the fractal** for longs, **above the wick of that candle** for shorts [6:22-6:30, 9:07-9:11]. Worked example stop = **5.9 pips** [7:10-7:16].
- Take profit: **10 pips** is the recommended default — "you can either go for five pips, ten pips, twenty pips, whatever you feel most comfortable with... for this video I'm going to suggest you only get 10 pips out of each move" [6:30-6:51]. With a 5.9-pip stop that's roughly 1.7R. Scaling logic he offers instead of a bigger target: run 5-10 positions simultaneously and take 10 pips off each [6:56-7:10]. Worked result: 10 pips in 6 five-minute candles (30 minutes) [7:16-7:23].
- Runner variant: if holding longer, **close 75-80% at the 10-pip level and move the stop to +1 or +2 pips (in profit)** [7:35-8:10]. General trailing rule: **trail the stop on the 21 SMMA** [8:10-8:18]. Exit the runner on something like an RSI divergence [11:00-11:05].
- Filters he adds: **RSI must be above 50 for longs and below 50 for shorts** — stated as a mandatory confluence [7:23-7:44]; only take the first signal after MA alignment, not later ones [5:32-5:50]; if you use a wider stop, lower the position size [9:14-9:24].

## Vague / untestable / chart-pointed claims
- [4:00-4:12] "once you zoom out your chart you're going to get a lot of clutter, there are a lot of arrows all over the place but there are only certain ones that I want you to take" — the filtering of which fractals to take is then only partly specified ("the first one").
- [5:32-5:44] "here is too late, I want you to get here right when all of these three line up" — chart-pointed; no bar count defining how many candles after alignment a signal is still valid.
- [4:22-4:41] "I want all three moving averages to be moving in the same direction" — no slope threshold or lookback for "moving in the same direction".
- [8:18-8:29] The 21-trailing-stop example immediately shows itself failing ("you would have gotten stopped out here... honestly any normal person would have gotten out here") — the trail rule is stated and then walked back.
- [6:30-6:51] Take profit is offered as a menu (5 / 10 / 20 pips, "whatever you feel most comfortable with"), so R is not fixed by the rules.
- [8:53-8:59] "you would have gotten your 10 pips in this first 10 candles, but if you waited a little bit for this next candle to print you would have waited one hour" — two different valid entries on the same setup.
- [9:44-10:08] Performance anecdotes (≈50% of a $100 account on one ETH trade, "$1100 in like three minutes" on US30 on the 1m) with no trade log, entry, stop or size.
- [11:00-11:05] "monitor that trade until you get like an RSI divergence or something" — runner exit is undefined.

## Testability
- rating: HIGH (three named indicators with exact settings, an unambiguous entry signal, a mechanical stop, and a stated default target — the only real gaps are "how soon after alignment" and the menu-style TP)
- overlap: 5m-scalp(SMMA) + fractal-entry (Williams Fractals) + RSI-50 momentum filter
- notable quotes:
  - [4:18-4:41] "I want all three moving averages to be moving in the same direction and I want the price to be above those moving averages... if all the moving averages are down I want the price to be below it"
  - [5:26-6:04] "using the Williams fractals you are going to use these as your entry points — I want you to try to get the first move and the first Williams fractal signal when it crosses over the 200... you have to wait for the candle to close because it could repaint"
  - [6:22-6:35] "our stop loss is literally going to be below the lowest part of that candle that had the printed triangle on it... you can either go for five pips, ten pips, twenty pips"
