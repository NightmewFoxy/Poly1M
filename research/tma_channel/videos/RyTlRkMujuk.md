# Best Candle Formation for 5 Minute Scalping
- id: RyTlRkMujuk | views: 458000 | length: 414s
- market(s) shown: a forex pair on 5m (unnamed); he states his preferred pairs are **AUDUSD and GBPUSD** [5:58]
- timeframe(s) taught: 5-minute chart, with market structure watched on the same chart

## Mechanical rules (only what the video actually states)
The channel's flagship three-line-strike rules — this is the most fully mechanical version in this batch.

- Indicators + exact settings: **none**. Pure price action / candlestick.
- Setup/context required:
  - Establish trend direction from market structure (higher highs + higher lows = uptrend; lower highs + lower lows = downtrend).
  - **Only trade three-line strikes in the direction of the current trend** [3:37] "ignore three line strikes in the opposite direction of a trend you are only trading with the trend with this strategy".
  - When market structure breaks (fails to make the next HH/LL), stop trading that direction and start looking for the opposite trend [4:51–5:00, 6:22].
  - New trends typically start with a large momentum candle: [1:09] the example candle "was about 25 pips" and broke the prior uptrend's structure.
- Entry trigger: **three candles in one direction followed by one engulfing candle in the opposite direction; enter at the CLOSE of the engulfing (4th) candle.**
  - Bearish continuation (downtrend): three bullish candles + one bearish engulfing candle → sell at close [3:22].
  - Bullish continuation (uptrend): three bearish candles + one bullish engulfing → buy at close.
  - [3:45] "always wait for close of candle do not get in early don't force a trade".
- Stop loss: **10 pips** (fixed) [3:26].
- Take profit: **20 pips** (fixed) → a 1:2 R, stated as risking 1% for a 2% gain [2:22].
- Filters he adds:
  - **Session: London only.** [2:56] "I strictly trade london session london open starts at 9:00 a.m london time I'm on the charts around 6 a.m london time so from 6 a.m till 10 a.m that is my trading window" (timezone: London time).
  - **Candle-size filter:** skip the setup if the engulfing candle is too large to fit a 10-pip stop. [3:59] the rejected example's engulfing candle "was 11 pips which means my stop loss would have to be up here which is a 15 pip stop loss" → he'd then need 30 pips, "which I know is harder to get than a 20 pip move". So: **engulfing candle must fit within ~10 pips**.
  - Avoids Asian/Tokyo session moves as slow due to low liquidity [3:14].

Claimed results: 8 three-line strikes in 14h20m of trend, all 8 profitable at 10sl/20tp = **+16% on the account in under a day** at 1% risk [2:22]. Later he explicitly shows losers too [5:02–5:28]. Overall claim [5:38]: **"this consistently gets me a 70 to 75 win rate when I trade during my market hours."** He recommends backtesting 100 trades per session/pair to find the best combination [5:46].

## Vague / untestable / chart-pointed claims
- [1:09] "new trends usually start with a massive huge moving candle this candle right here was about 25 pips" — 25 pips is stated for the example only, not as a rule; no threshold for what counts as a momentum candle.
- [2:35] "during this entire thing you can see that market structure was never broken" — structure breaks are identified visually; no swing-detection rule (no fractal size / lookback) is given, which is the one real discretionary gap in an otherwise mechanical system.
- [1:41] The 8-winner count is read off the chart with no dates, prices or pair named — not reproducible.
- [3:59] "that engulfing candle is too big for my liking" — subjective phrasing, though he immediately quantifies it (11 pips → 15 pip stop → rejected), so the filter is usable at ~10 pips.
- [5:38] "70 to 75 win rate" — self-reported, no log.
- [6:04] "I talk about three line strikes in like 35 to 50 percent of my videos" — anecdotal.
- "Engulfing" is not formally defined here (body-only vs body+wicks); a companion video is referenced for candlestick definitions.

## Testability
- rating: HIGH (fully mechanical: pattern, entry timing, fixed 10-pip stop, fixed 20-pip target, session window, candle-size filter — only swing/structure detection needs a formal definition)
- overlap: three-line-strike (primary); market-structure/BOS as trend filter; session-filter (London 6–10am London time)
- notable quotes:
  - [3:22] "what you're looking for is three bullish candles and one bearish candle enter on close of candle 10 pip stop loss 20 pip take profit"
  - [2:56] "I strictly trade london session ... from 6 a.m till 10 a.m that is my trading window"
  - [3:59] "that engulfing candle is too big for my liking I like it to fit within 10 pips this one candle was 11 pips ... which is a 15 pip stop loss which I'm uncomfortable with"
