# Ultimate Fibonacci Trading Strategy + $1,000,000 Giveaway
- id: H7qwIiO4YuE | views: 99000 | length: 1372s
- market(s) shown: **US100 / NASDAQ** primary (recent price action around the DeepSeek news gap) [0:31–0:37, 1:13–1:16]; one **German 40 daily** example for the consolidation section [10:49–10:53]. He states "it doesn't really matter what you're trading, this works on absolutely everything" [0:37–0:40].
- timeframe(s) taught: unstated for the main walkthrough; the consolidation counter-example is explicitly **daily** on German 40 [10:49]

## Mechanical rules (only what the video actually states)
Longest and most complete Fib video in this batch (~12 min of teaching, then a sponsor giveaway from [12:03] to the end).

- Indicators + exact settings: **Fibonacci retracement tool only** (TradingView: left toolbar, third icon down, first option) [2:56–3:06]. His level list is spoken explicitly [4:00–4:25]:
  - Retracement: **0, 0.382, 0.5, 0.618, 0.705, 0.79, 1**
  - Extension: **-0.5, -1, and -0.618** (transcript renders these as "-.5 / 1 and 0.618" at [4:19–4:22]; combined with [6:54–7:26] the extension set is **half a standard deviation (-0.5 / -0.618) and one full standard deviation (-1)**)
  - Colours: **all white except the 0.5, which he makes red** [4:22–4:30]
- Setup/context required: **A visible trend — no trend lines needed.** "if price is trending up you don't have to draw trend lines, you just have to see that price is going up or price is going down" [1:39–1:43]. Explicit exclusion: **"if markets are consolidating or flat or trading within a boxed range this isn't going to work"** [2:12–2:20]. Then price must **break a previous high (uptrend) or previous low (downtrend)** and stop extending [2:44–2:56].
- Entry trigger: Anchor + confirmation:
  1. **Anchor the Fib on the move that broke the previous structure**, from the start of that non-stop momentum leg to its extreme — "it is the move that **non-stop** broke the previous high… draw it from the bottom **including the wick** to the top **including the wick**" [3:33–4:00]; restated as the #1 takeaway at [10:00–10:25].
  2. **Wait for the retracement into the 0.5–0.618 band = the "Fibonacci gold zone"** [4:43–5:01].
  3. **Confirmation in the zone from candle formations (or a buy/sell indicator).** Named examples: **long rejection wick + an inside bar** ("the next candle lives within the entire distance of the previous candle") [5:22–5:39]; **long wick + bullish candle, wait for the candle to close** [8:29–8:37]; **doji + a candle that engulfs the doji to the upside** [9:05–9:12]. "you can wait for a few candles of confirmation" [5:36–5:41].
- Stop loss: Default: **below the 0.618** [5:41–5:47, 8:34–8:40]. Risk-averse variant: **below the previous low — the origin of the swing that broke structure** [6:02–6:12], with the reasoning "if price goes down to there it's either going to consolidate or reverse". Universal rule: **"you never enter a trade without a stop loss"** [0:55–0:59].
- Take profit: Default and preferred: **the previous high (uptrend) / previous low (downtrend)** — "this is the safest and most logical method" [5:47–5:56], because "you are expecting a double top or a double bottom" [7:36–7:44]. Optional scale-out ladder using extensions [7:02–7:27]:
  - **Take profit on 80% of the trade at the previous high** (TP1)
  - **Take another 10% off at the half-standard-deviation extension (-0.5 / -0.618)**
  - **Close the trade entirely at the full standard deviation (-1)**
- Filters he adds:
  - **Two-consecutive-loss circuit breaker (fully mechanical):** "if you have two back-to-back losses like that, **stop trading and draw a box**… you are in a period of consolidation. All you got to do is remove all of your indicators and all of your drawings and literally just draw a rectangle, and **until it gets out of that rectangle you do not touch it**" [11:15–11:38].
  - **News-risk filter (soft):** big news events (the DeepSeek gap, a "6% out of the markets" drop) will stop you out — the answer is always having a stop, not avoiding the session [0:40–1:08, 9:16–9:33].

## Vague / untestable / chart-pointed claims
- [2:26–2:46] "identify the highs and the lows — you will be able to see these because they are **aggressive** points at which the price moves to and from; like this right here would not be an aggressive move" — swing identification taught by pointing, "aggressive" unquantified.
- [3:33–3:41] "it is the move that **non-stop** broke the previous high" — "non-stop" (no intra-leg pullback?) is never defined numerically; and at [3:28–3:38] he excludes an earlier start point "because you can see a little down slope right here". **Frame-check required to encode the anchor rule.**
- [4:00–4:25] The settings panel is on screen while he reads the levels; the transcript garbles some ("0.51", "-.5 / 1 and 0.618"). **Frame-check the exact enabled level list.**
- [5:01–5:13] "you are looking for candle formations **or your buy/sell indicator** to tell you that the price is rejecting" — the confirmation step allows an unspecified proprietary indicator, so the entry is not uniquely defined.
- [8:11–8:29] "we did not retrace into the Fibonacci gold zone so we keep our measuring tool up and wait for price to reverse… it went **substantially further past** and rejected up" — a trade taken beyond the 0.618 with no stated tolerance limit. This contradicts the "stop loss below the 618" rule and is unresolved.
- [10:25–10:47] "the reason why I don't always target the Fibonacci extension levels for my take profits is because…" — the choice between previous-high TP and extension TP is discretionary, no rule given.
- [7:28–7:33] "these are not guaranteed; this one usually is, I say usually because…" — hedged.
- No **timeframe**, **session**, **market filter**, **R multiple** or **position size** is stated anywhere for the main method.
- [12:03–end] The final ~9.5 minutes are a FunderPro prop-firm giveaway interview — zero trading content. Only generic advice: "risking less percent per trade", "0.1 / 0.2% risk" [15:37–15:45, 20:40–20:57].

## Testability
- rating: MEDIUM (level set, gold-zone entry band, both stop variants and the scale-out ladder are all explicitly numeric; blockers are the undefined "non-stop impulse" anchor, the candle-confirmation menu, and the absence of any timeframe/session)
- overlap: fib-scalp ; market-structure/BOS ; candlestick-pattern (inside bar, doji + engulf, rejection wick) ; fib-extension take-profit. Same family as CpSLTA9BXjc, AlsXNhTm4AA, BnYI4U2iDaI, EJDUexo_uSM — this is the most complete statement of it.
- notable quotes:
  - [3:49–4:00] "you're going to select your Fibonacci tool and you're going to draw it from the bottom including the wick to the top including the wick"
  - [5:41–5:53] "you can enter your long position with your stop loss below the point 618 and your profit target should be the previous high — this is the safest and most logical method"
  - [11:15–11:38] "if you have two back-to-back losses like that, stop trading and draw a box… until it gets out of that rectangle you do not touch it"
