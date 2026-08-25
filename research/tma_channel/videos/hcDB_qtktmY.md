# Forex Scalping Strategy Results
- id: hcDB_qtktmY | views: 88000 | length: 412s
- market(s) shown: primarily **US30**; also "some currency pairs occasionally" and **ETH** ("I also trade some crypto primarily ethereum because the spreads are actually better on my broker than they are with bitcoin" [2:52]-[3:00])
- timeframe(s) taught: unstated — the chart timeframe is never named. Only holding time is given: "most of these trades were no longer than 15 minutes, a majority were done in two or three minutes" [6:27]-[6:36]

## Mechanical rules (only what the video actually states)
This is a **results/proof video**, not a teaching video — he repeatedly defers the method to a separate scalping video ("if you want detailed information on how this scalping strategy works, watch this video I made yesterday on scalping" [1:39]-[1:45], and again at [5:53]). The rules he does restate in passing:
- Indicators + exact settings: **moving averages, specifically the 50 and the 200** (named at [1:33] and [1:50]). Lengths beyond those two are not named here, and **no MA type (SMA/EMA/SMMA) is given in this video.**
- Setup/context required: price interacting with a moving average. Two stated cases:
  1. **Bounce case:** "when it tests a moving average and then bounces off of it I get in on a long position" [1:43]-[1:31].
  2. **Break case:** "when it breaks through a moving average like the 50, I know that it's eventually going to go down to the 200" [1:29]-[1:37] — i.e. the next MA is the destination.
- Entry trigger: the MA test-and-bounce, or the MA break, as above. No candle-close confirmation, no trigger candle is described.
- Stop loss: **no stop-loss price rule.** He explicitly denies using a fixed R: "there's no specific risk-to-reward ratio, I just — I have a losing threshold, so if I lose a certain amount of money that's what I'm going to stick with" [4:10]-[4:20]. The dollar value of that threshold is never given.
- Take profit: **discretionary momentum exit** — "if I start getting into profit I will take that profit, especially if I see a loss of momentum; if I see a loss of momentum I'm out of the trade right away and I'm looking for my next entry" [4:20]-[4:29]. In practice the target is the next moving average ("it crossed through the 50, went to the 200, that's my scalp" [1:56]-[1:53]).
- Filters he adds: none stated (no session, no news, no day filter). He does add a **hedging/averaging behaviour**: "when I get in on a position and it's going the wrong way I'll take the opposite position until I get some profit and then it'll start going in the direction of my original trade so I'll close that one" [3:45]-[3:55].
- Position sizing / instrument note: **0.01 lot on US30 = $1 P&L per 1 point of index move** on his broker [1:37]-[1:23]; contrasted with 0.01 lot forex ≈ 10 cents/pip [1:03]-[1:06].

## Reported results (the actual content of the video)
- Account grew **$1,000 -> $1,581**, total profit **$710.78** since "last Thursday", recorded on a Tuesday [0:07]-[0:19], [4:02]-[4:07].
- **53 total trades, 48 winners, 5 losses = "over a 90% win rate"** [4:37]-[4:55].
- Individual outcomes cited: +$16, +$2, +$23, one **-$35** loser [3:05]-[3:37]; some winners as small as **23 cents**, some ~**$80** [4:29]-[4:34]. Drawdowns of "$30 or whatever" on trades he held through [3:18]-[3:24].
- Caveat he gives himself: "you always have to back test and forward test, so I've been testing this seeing how it goes" [5:01]-[5:07].

## Vague / untestable / chart-pointed claims
- [1:43] "when it tests a moving average and then bounces off of it I get in on a long position" — "tests" and "bounces off" are undefined (touch? wick through? close back above? how many bars?). This is the entire entry rule and it is qualitative.
- [1:47]-[2:12] "I'm just like taking a trade here... trade trade trade trade trade trade trade trade trade" — the demonstration is chart-pointed narration of many entries with no criteria attached to any of them.
- [4:10] "I have a losing threshold, so if I lose a certain amount of money that's what I'm going to stick with" — the threshold is never stated, so max loss per trade is unknown. Combined with a 90% win rate and single losers of -$35 against many sub-$1 winners, the reported edge cannot be evaluated from what is given.
- [4:22] "especially if I see a loss of momentum, if I see a loss of momentum I'm out of the trade right away" — "loss of momentum" is undefined and is the exit rule.
- [3:24] "I know that my analysis is correct, I was just like — the entry point was kind of wrong" — used to justify sitting through drawdown; not a rule and not falsifiable.
- [3:45] "I'll take the opposite position until I get some profit and then it'll start going in the direction of my original trade" — hedging/martingale-flavoured behaviour with no trigger, no size rule and no stop. This alone makes the reported win rate non-reproducible.
- [4:37]-[4:55] The 90% win-rate claim is computed over **53 trades in ~3 days** with unequal, undisclosed position outcomes and no stop rule — a win-rate statistic without an average-win/average-loss figure. He shows the count on a phone screen; the sizes are not tabulated.
- [5:16]-[5:22] "I know my US30 pair and I know which direction it's going to go because the more you trade a pair the more comfortable you get with it" — pure discretion.
- [5:39]-[5:51] "imagine if you have a $50,000 account and you're doing a 0.25 [lot]... that's thousands of dollars in one day" — extrapolation from a 3-day sample, shown as other people's screenshots.

## Testability
- rating: LOW — the video is a results showcase that explicitly defers the method elsewhere. The two entry ideas (MA bounce, MA break targeting the next MA) have no definitions, there is **no stop rule and no R multiple by his own statement**, the exit is a discretionary momentum read, and an undisclosed hedging behaviour sits on top of it.
- overlap: 5m-scalp(SMMA)-family MA scalping (the 50/200 pair, "trading between moving averages") + S/R-retest (MA-as-support/resistance); results/proof video rather than a strategy video
- notable quotes:
  - [1:43] "when it tests a moving average and then bounces off of it I get in on a long position; when it breaks through a moving average like the 50 I know that it's eventually going to go down to the 200"
  - [4:10] "there's no specific risk-to-reward ratio, I just — I have a losing threshold, so if I lose a certain amount of money that's what I'm going to stick with"
  - [4:41] "there are 53 trades... of those 53 trades 48 were winners and five were losses... that is over a 90% win rate"
