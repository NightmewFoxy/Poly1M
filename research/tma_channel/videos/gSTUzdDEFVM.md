# How To Enter a Trade in 4 Seconds
- id: gSTUzdDEFVM | views: 28000 | length: 447s
- market(s) shown: German 40 / DAX ("currently German 40 is consolidating in this area" [4:29-4:33]) and US100 ("we're looking at us 100" [5:17-5:19])
- timeframe(s) taught: unstated for the demo trades; he references scalping "on the 1 minute or 5 minute chart" as the reason speed matters [3:31-3:33]

## Mechanical rules (only what the video actually states)
This is a TOOL video for the paid TTF MT4/MT5 "risk calculator" expert advisor, not a strategy video. The only trading rules present are risk-management defaults.

- Indicators + exact settings: none. The tool is an MT4/MT5 Expert Advisor (install: File → Open Data Folder → MQL4 → drag into the `experts` folder → Navigator → Expert Advisors → drag onto chart → Common tab → allow live trading [4:04-4:19]).
- Setup/context required: the demo short is justified as — "currently German 40 is consolidating in this area but we're showing some weakness in the price, it's failing to make higher highs, so we're looking for a sell position" [4:29-4:39].
- Entry trigger: none given (the tool assumes you already have a signal — "let's say you got a signal from some indicator that you have" [5:04-5:08]).
- Stop loss: placed by dragging above the signal candle's extreme with a buffer — "the highest wick of this candle is 18760 so I'd like get a nice comfortable distance above that, that's going to be my stop loss" [4:42-4:48]. Also offers a fixed-distance mode: "let's say you want to do 20 points on every single trade, you can set your stop-loss to how you want it" [6:01-6:06].
- Take profit: **tool default risk:reward is 1:1.5** — "it automatically adjusts your take profit and the default is set 1 to 1.5 risk to reward" [4:48-4:55]. Manual mode: drag TP to a swing high/low — "you know that you're targeting swing highs and swing lows" [2:31-2:41]. Earlier he also mentions building a "1 to 5 risk to reward" with the position tool [0:52-0:59].
- Filters he adds: risk sizing — "as default the risk is set at 1%" [2:18-2:21], adjustable per position; splitting one position into three so you can "automatically close one" at 1:1 in profit and leave the rest running [2:01-2:13]; breakeven management — "once your trade is in profit protect your capital ... modify the stop loss by just simply clicking and dragging it to either break even right at your entry point ... or a little bit in profit" [3:17-3:36 → 5:47-6:39 section].

## Vague / untestable / chart-pointed claims
- [4:33-4:39] "we're showing some weakness in the price, it's failing to make higher highs" — the only entry justification in the video; "weakness" undefined, no candle count for the failed highs.
- [4:42-4:48] "a nice comfortable distance above that" — the stop buffer is explicitly eyeballed, no pip/ATR value.
- [5:04-5:25] The US100 buy is entered with no stated reason at all ("you got a signal from some indicator that you have ... we click buy, we double click our stop loss, we drag it to where we want it").
- [7:03-7:11] "this trade hit take profit so I'm up 1,500 on the account ... even if this trade hits stop loss I'm up 500 bucks for the day" — single-session P&L anecdote, no account size given, so the 1% risk claim can't be reconciled.
- [6:39-6:52] Motivational voiceover ("accept the pain, smile at the pain...") — no content.
- Entire video funnels to the paid tool ("first link in the description" [7:23-7:24]).

## Testability
- rating: LOW (execution/tooling video — no entry rule, no market context rule; the only reusable content is the risk defaults: 1% risk, 1:1.5 default RR, partial close at 1:1, move to breakeven in profit)
- overlap: other (risk management / execution tooling). Its one cross-video value is confirming his default risk parameters — 1% per trade and a 1:1.5 RR default, which matches the 1:1.5 target in bCX4YgXUQYs.
- notable quotes:
  - [2:18-2:21] "as default the risk is set at 1%"
  - [4:48-4:55] "it automatically adjusts your take profit and the default is set 1 to 1.5 risk to reward"
  - [2:05-2:13] "when your trade gets to one to one risk to reward in profit you can automatically close one and leave the others open"
