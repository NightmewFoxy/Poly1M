# 20 PIPS a Day Forex Strategy
- id: tHPqhvN0gYU | views: 515000 | length: 450s
- market(s) shown: EURUSD
- timeframe(s) taught: **15-minute**, stated twice — "right now I am looking at euro usd on a 15 minute time frame" [0:56]-[1:01], and "you're still on a 15 minute time frame but you can see the nice ebb and flow" [4:45]-[4:50]

## Mechanical rules (only what the video actually states)
The video is ~70% position-sizing arithmetic and ~30% entry method. The sizing half is fully mechanical; the entry half is not.

- Indicators + exact settings: **"moving averages"** — plural, referred to throughout ([5:12], [5:57], [5:39]) but **no length and no type are ever named in this video.** He defers to his other MA videos: "if you've watched my videos on moving average trading, whether it's a crossover, whether it's the support and resistance, whether it's continuation of the momentum" [4:52]-[5:03]. One chart setting is given exactly: TradingView **chart settings -> Appearance (4th option down) -> "Session breaks" enabled** [4:04]-[4:16], used only to visualise daily ranges.
- Setup/context required: previous-day directional bias must agree with the trade. Worked example: he *skips* the first cross-down because "the previous day you see this swoop up so you're seeing bullish momentum, so why would you get in on a short position?" [1:22]-[5:30].
- Entry trigger: **price crossing back through the moving average(s) a second time, in the direction of the prevailing bias, with price then holding above them.** "so just be patient and wait and it crossed through it again and you're like, cool, that confirms the theory that I had that we're having bullish momentum, so we're above moving averages now creating support, get in on your trade and you got your 20 pips" [5:30]-[5:47]. He explicitly points to a separate video for "specific sniper entries" [5:47]-[6:02].
- Stop loss: **defined by money, not by chart level** — risk exactly **2% of account per trade**, cut there: "with your risk at two percent you're only willing to lose two hundred dollars per trade, twenty dollars, and two dollars depending on your account size" [1:26]-[1:38]; "you cut your losses at two hundred dollars because you're only risking two percent per trade" [2:59]-[3:04]. No structural/ATR stop placement rule is given.
- Take profit: **fixed 20 pips**, sized so that 20 pips = the 2:1 payoff. "with your profit goal being a minimum of two to one, so we're looking at a minimum of four percent" [1:38]-[1:46]. **Exactly one trade per day, then stop:** "it's better for you to get your 20 pips in one trade and walk away for the day, like you've had a successful day" [6:34]-[6:43].
- Position sizing (the most concrete content, [1:16]-[3:08]): risk 2% -> target 4%. Table given for three account sizes:
  | account | 2% risk | 4% (20-pip) target |
  |---|---|---|
  | $100 | $2 | $4 |
  | $1,000 | $20 | $40 |
  | $10,000 | $200 | $400 |
  Then use a **pip-value calculator (forextime.com)** — enter pip amount, pair, deposit currency — and adjust lot size until 20 pips equals the target. Worked answer: **$10,000 account, 20 pips, $400 target -> lot size 2.0** [2:43]-[2:53].
- Filters he adds:
  - **One trade per day maximum.** "over trading, doing 30, 40, 50 positions a day is completely reckless" [6:30]-[6:37].
  - Previous-day momentum must not contradict the trade [5:22]-[5:30].
  - Timeframe-appropriateness caveat: "every single one of them work if they are implemented at the correct time frame and not falling for the fake out" [7:02]-[7:13] (both deferred to other videos).
- Stated math of the approach: at 1:2, "you could afford to lose two days in a row and still be break even if you win the third day" [6:46]-[6:56].

## Vague / untestable / chart-pointed claims
- [5:12]-[5:14] "you don't really know where to get in unless you have moving averages on there" — **the MA lengths and type are never given in this video**, so the entry cannot be reproduced from this video alone.
- [5:30]-[5:43] "it crossed through it again and you're like, cool, that confirms the theory that I had... so we're above moving averages now creating support, get in on your trade" — the entry candle is pointed at on the chart; "creating support" has no definition (how many bars above? close-based? which MA?).
- [5:22]-[5:30] "because the previous day you see this swoop up so you're seeing bullish momentum" — "swoop up" is eyeballed, not measured.
- [3:11]-[3:24] "looking at euro usd you can see that there's 20 pip moves all over the place" and [4:24]-[4:31] "every single day has over a 20 pip movement" — true of a daily *range*, but a range existing is not the same as a rule capturing it; no data is shown for whether the entry rule catches it before the stop.
- [0:36]-[0:52] "your one trade a day is enough profit to keep you from being homeless, pays your bills, pays your car, your insurance, your gas, your food" — income claim with no win-rate assumption stated; the entire premise assumes the 20-pip target is hit daily, which is never evidenced.
- [5:47]-[6:09] "if you want specific sniper entries for your trades I have a strategy that I've made a video on right here... very very tight stop-loss trades with high profit ranges. It doesn't happen every day but it happens consistently" — the actual entry precision is deferred to another video; "consistently" is not quantified. (This is the video's own admission that its entry rule is incomplete.)
- [7:02] "I have a plethora of videos on moving average crossovers... every single one of them work if they are implemented at the correct time frame" — unfalsifiable as stated (any failure is attributed to wrong timeframe).
- Note on internal consistency: at [6:46] he calls it a "one to two risk to reward ratio" while the table is built on 2:1 reward:risk — the same thing described in the opposite order, not a contradiction in the numbers.

## Testability
- rating: MEDIUM — the **risk and sizing half is exactly specified** (2% risk, 2:1, 20-pip fixed target, one trade/day, 15m EURUSD, lot table with a worked 2.0-lot answer) and directly codeable. The **entry half is not**: the moving averages are unnamed, and the trigger ("crossed through it again... creating support") is chart-pointed and deferred to other videos. A backtest can implement the money-management wrapper but must import the entry from another TMA video.
- overlap: session-filter/day-structure (session breaks) is only cosmetic here; the real families are **risk-management/position-sizing** + **5m-scalp(SMMA)-style MA cross/retest** (unnamed MAs) + a one-trade-per-day overtrading filter
- notable quotes:
  - [1:26] "with your risk at two percent you're only willing to lose two hundred dollars per trade, twenty dollars, and two dollars depending on your account size, with your profit goal being a minimum of two to one"
  - [2:43] "for that trade on a 10,000 account for 20 pips you want a profit of 400, so your lot size needs to be two"
  - [6:34] "it's better for you to get your 20 pips in one trade and walk away for the day"
