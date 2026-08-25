# Stochastic RSI Trading Strategy
- id: Hh3yBjZrOjg | views: 636000 | length: 464s
- market(s) shown: EURUSD (all chart examples); US30 referenced only in a testimonial anecdote
- timeframe(s) taught: **15 minute and above** for default settings (15m / 30m / 1h / 4h / daily); below 15m requires a settings change [3:18-3:34]

## Mechanical rules (only what the video actually states)
> Explicit disclaimer: **"this is not my strategy"** [3:53-3:54, 6:21-6:25] — Arty is relaying a Discord member's ("Christie") method in response to questions.

- Indicators + exact settings — **two indicators only** [2:22-2:49]:
  - **200 moving average**. "You can use smooth, you can use exponential — it depends on which currency pair; I prefer smoothed" [2:32-2:40]
  - **Stochastic RSI** (TradingView built-in). Defaults are correct for 15m and higher: **K% = 3, D% = 3, RSI length = 14, Stochastic length = 14** [3:04-3:18]. **Below the 15-minute timeframe, change the Stochastic length to 8** [3:26-3:34]
- Setup/context required: this is a **trend-continuation** method, not a reversal method — "we're looking for continuations of a downtrend or an uptrend depending on if it's above or below the 200 moving average" [4:18-4:31]. The setup he shows is price rallying into the 200, **finding resistance on the 200**, and continuing down [4:31-4:45].
- Entry trigger: a **crossover of the two Stochastic RSI lines** at the moment price is rejecting off the 200 — "if you had the stochastic RSI up you would actually see a crossover" [4:55-5:07]. He then adds a confirmation delay: "we wait to make sure that that's a solid signal — this right here is three candles in to the downside of the move" [5:35-5:42], i.e. the shown entry is roughly **three candles after the cross**.
- Stop loss: **not stated anywhere in the video.**
- Take profit: two options offered, neither with a level or an R multiple — exit on the **next opposite Stochastic cross** ("you could have gotten out on this first stochastic cross"), or **maintain a trailing stop loss** and ride the move [6:04-6:12]. No trail distance or anchor given.
- Filters he adds: the 200 MA side/rejection is the direction filter [4:18-4:45]; use a higher timeframe because it "means less false signals, keeping you more consistent" [3:44-3:51]; explicitly warns the indicator is not standalone — "using the stochastic RSI alone would be very very difficult in my opinion; you need to overlay this with multiple indicators" [6:12-6:21]. He mentions a paid "LMI" indicator that the original trader also uses for a confirming cross, but **refuses to explain it** [6:25-6:46].

## Vague / untestable / chart-pointed claims
- [5:12-5:28] "we had this last ditch effort momentum swing up and then a completely flat top starting the continuation down; this in itself is a very weak signal, it's not even an engulfing candle" — price-side context described but never turned into a condition.
- [5:35-5:42] "we wait to make sure that that's a solid signal — this right here is three candles in" — the confirmation is shown, not stated as a rule; unclear whether three candles is the rule or an artefact of the example.
- [5:42-5:53] "you can clearly see that this price is in the overbought territory of the stochastic RSI with the potential to continue to the downside" — no overbought/oversold threshold value is ever given (80/20 or otherwise), and the framing contradicts his usual "never use overbought/oversold" teaching.
- [5:53-6:04] "with the stochastic RSI maintaining this oversold market for quite some time, this is just a heavy momentum grab" — descriptive, not actionable.
- [6:04-6:12] "theoretically you could have just maintained a trailing stop loss on this and gotten a nice decent move out of it" — no trail rule.
- [4:31-4:45] "finding resistance on that 200, continuing down, finding resistance on the 200 again" — chart-pointed rejections, no tolerance for what counts as touching the 200.
- [2:32-2:40] MA type left as a choice (smoothed vs exponential, "depends on which currency pair") — so the trend filter itself is not fully specified.
- [0:00-0:07, 3:53-4:08, 6:46-7:02] Testimonial claim that a Discord member makes "$10,000 to $20,000 a day trading US30" — unverified marketing, no trade record.

## Testability
- rating: LOW (indicator settings are exact, but there is no stop-loss rule at all, no take-profit level, and the entry confirmation is only implied by an example; he also disowns the strategy)
- overlap: other (Stochastic-RSI crossover) + 200-MA trend/session filter
- notable quotes:
  - [3:04-3:34] "the K percentage is three, D percentage is three, RSI length is 14 and the stochastic length is 14 — these settings are completely fine if you are trading 15 minutes and above... if you are trading below the 15 minute time frame you want to change the stochastic length [to] eight"
  - [4:18-4:31] "we're looking for continuations of a downtrend or an uptrend depending on if it's above or below the 200 moving average... we're using the stochastic RSI to find our entry points"
  - [6:12-6:21] "using the stochastic RSI alone would be very very difficult in my opinion — you need to overlay this with multiple indicators"
