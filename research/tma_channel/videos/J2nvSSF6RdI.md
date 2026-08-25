# 1 Min Scalping Strategy
- id: J2nvSSF6RdI | views: 66000 | length: 527s
- market(s) shown: German 40 / DAX ("this is a trade that I took today on the one minute chart on German 40 also known as Dax", [0:01]); mentions NAS by comparison
- timeframe(s) taught: 1-minute for entries/exits, 15-minute for trend context ("on the higher time frame like the 15minute we were on an uptrend", [0:35])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **SuperTrend**, settings stated exactly: **10 and 2.5** ("the settings that you're going to use on that is going to be 10 and 2.5", [0:54]) — the most popular/top SuperTrend in the TradingView list.
  - **Two Volume Profile indicators** (he uses the ones "by kv4 coins", says they are all the same): one configured to **bearish volume only**, the other to **bullish volume only**, each recoloured to match his bearish/bullish candle colours, including the **POC line**. Row/width setting: default is 100, and he demos lowering it to **40** to bring the profile closer to price — "bring these to like 40 and that'll bring it closer to the price I like it at 100 cuz then it stays further away" ([3:29]).
  - **Trend lines**, hand-drawn.
  - **New York midnight open** marked as a horizontal level: "this is just a representation of where price opened up for the day 12 midnight New York time" ([4:35]).
- Setup/context required: Higher-timeframe (15m) trend must have broken — "on the higher time frame like the 15minute we were on an uptrend and price broke through this uptrend and then immediately came back down" ([0:35]). Then draw the 1-minute trend line and trade with the SuperTrend in that direction.
- Entry trigger: **SuperTrend flip** in the direction of the broken trend line, at/after a trend-line rejection: "it rejected off the trend line but like broke through it and then immediately came back and then using the super Trend we saw a sell indication right there so I got in on a trade right there" ([1:43]). The long-side version is the mirror: downtrend broken + "a new Buy Signal off of the super Trend" ([5:00]).
- Stop loss: "set your stop loss at the Buy Signal when it breaks and you create the super Trend" ([6:32]) — i.e. at the SuperTrend flip level. A secondary structural stop is used: the **New York midnight open** level ("this was my ultimate stop-loss area", [4:50]), and he ratchets the stop to the **volume-profile point of control** once price clears it ("that's where I moved my stop loss to because I was like cool if it goes above the point of control not going to like it", [4:20]).
- Take profit: Baseline mechanical version = **1:2 risk-to-reward** ("go for a one to two risk to reward ratio and you can get those pretty consistently", [6:36]). The trade he actually took was trailed and finished at **1:6** ([6:24]). Discretionary target used: the prior consolidation area / double bottom to the left ([5:29]–[5:43]). Volume-profile POCs act as intermediate targets — price runs to the large volume node, breaks the bullish POC, hits the bearish volume and continues ([3:42]–[4:20]).
- Filters he adds:
  - **Trend-line exit rule:** "I like to see a break out and a retest and rejection up before I actually get out of my trend line trade" ([2:49]) — a break alone is not an exit; it needs break + retest + rejection.
  - **Session/time-of-day filter for DAX:** "this is Dax we usually die down at about 3 pm ... Europe time ... the trading window is really just 9 to 5 London session time" ([5:46]–[6:02]). Contrasted with NAS which "goes for hours and hours".
  - Volume-context filter for stopping: "now it's just going to fall into this consolidation there's less volume in the markets" ([7:02]).

## Vague / untestable / chart-pointed claims
- [2:06] "I just created you could probably see it on the video this like 45 degree angle in the in the trend" — trend line drawn live by eye; angle is chart-scale dependent.
- [2:22] "I kept slowly moving my stop loss into profit ... I just played it safe and trailed this thing the whole time" — no trailing rule (no ATR, no candle-low step) is given; explicitly motivated by a prior losing trade that day, i.e. psychology not system.
- [2:41] "the thing that I was concerned about was like okay maybe it's just a trap" — discretionary judgement.
- [3:15] "we got this huge engulfing candle and then it just stopped it stopped dead" — chart-pointed.
- [3:42]–[4:20] The volume-profile read (which node price "wanted to go to", the mixture of bullish/bearish layers) is entirely visual; no threshold for what counts as "a large area of volume". The lookback range of the two volume profiles is never stated.
- [5:16] "I just let it hit my stop loss I could have closed it here I was thinking about it" — the exit was not by rule.
- [6:53] "it doesn't work for every one of them and you got to like overall look at the trend and have deeper analysis of price action or whatever" — explicit admission that the mechanical version needs discretionary overlay.
- [4:41] The NY-midnight-open level: he does not say whether it is drawn from the 00:00 New York open of the current day only, or carried forward.
- [7:14] onwards is sponsor/motivational content (Osprey/TradeLocker, funded-account talk, "trade every single day") — no rules.

## Testability
- rating: MEDIUM — SuperTrend(10, 2.5) is an exactly specified, fully mechanical signal generator, the stop (at the SuperTrend flip) and the 1:2 target are stated, and the DAX 9-to-5 London window is a hard filter. The discretionary gaps are the hand-drawn trend line, the 15m "uptrend broken" condition, and the volume-profile reading.
- overlap: other (SuperTrend) + volume-profile + trend-line-break/S-R-retest + session-filter; sits outside the channel's usual SMMA/divergence families.
- notable quotes:
  - [0:54] "the indicators that you're going to need are super Trend ... and the settings that you're going to use on that is going to be 10 and 2.5"
  - [6:28] "if you just want to get one to twos all you have to do is you know set your stop loss at the Buy Signal when it breaks and you create the super Trend and then go for a one to two risk to reward ratio"
  - [5:48] "this is Dax we usually die down at about 3 pm is Europe time ... the trading window is really just 9 to 5 London session time"
