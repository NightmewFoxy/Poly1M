# 5 Minute Scalping Strategy Trade Breakdown
- id: wNb67k26x1k | views: 40000 | length: 229s
- market(s) shown: **German 40 (DAX)** — "that's just what I've seen on German 40" [1:47]-[1:50]; trade taken Friday 8 November
- timeframe(s) taught: **5-minute** (title and framing); not restated in the transcript

## Mechanical rules (only what the video actually states)
This is a single-trade post-mortem, not a rules video — he explicitly defers the rules ("if you want to learn the exact rules of this strategy check out this video right here" [3:35]-[3:38]). What it does contain is his **bias-forming stack**.

- Indicators + exact settings:
  - **Midnight New York line** — a vertical at midnight NY plus a horizontal at the price that printed at that moment: "this is midnight in New York, this is the price at which it opened midnight New York, this is called the midnight New York line" [0:53]-[1:02]. **This is the only session time given with a timezone in the whole video.**
  - **Happy Trail** (paid TTF indicator) — "currently I'm using the happy trail indicator for strategy wars in the whole month of November, I waited for a signal" [2:12]-[2:18].
  - **Fractal Frenzy** (a second TTF indicator) used as a doubling confluence: "luckily enough this one doubled up with fractal frenzy — really good strong entry" [2:18]-[2:23].
  - **Fibonacci retracement** — levels spoken: **0.5 and 0.382** [2:33]-[2:44].
  - No settings/parameters given for any of them.
- Setup/context required (the bias stack, in order):
  1. **Midnight-NY-line bias:** "if price moves dramatically above or below this blue line it usually tends to go that way all day... that's just a general rule of thumb and it's what I go by to form my bias" [1:02]-[1:19]; restated "most days when it stays above or below the range it stays there all day" [1:41]-[1:47], plus a DAX-specific version: "German 40 usually closes higher or lower than the open — it's a really stupid rule of thumb but it helps me form my bias" [1:47]-[1:57].
  2. **Wait for London open:** "I'm waiting for London open before I make any moves" [1:57]-[2:03].
  3. **First hour of London open defines the range:** "this section right here is the first hour of London open, and if we break out of London session we usually trend in that direction" [2:03]-[2:12].
- Entry trigger: **the Happy Trail signal after that London-open breakout**, ideally doubled with a Fractal Frenzy signal [2:12]-[2:23]. He notes the actual entry was late: "I got in a little bit later than I wanted to so I changed my risk percentage to less than 1%" [0:27]-[0:33].
- Stop loss: **not stated** anywhere in this video.
- Take profit: **goal was 1:2** — "the goal was to get a 1 to two risk to reward" [0:34]-[0:36]. Actual: closed manually at **1:1** for discretionary reasons: "I had stuff to do so I closed the trade, saw the volume dropping and didn't want to get stuck in something that was zigzagging" [0:36]-[0:45]; "I closed it at a 1:1" [3:16]-[3:18].
- Filters he adds (the trade-management rule — the only genuinely reusable rule in the video):
  - **Fib-based hold/exit test:** "if you're ever in a position where you don't know if you should stay in a trade or not, all you got to do is use Fibonacci retracements. So we had this move down and it retraced to the 50 and then broke structure. Once it breaks structure we move our fib tool from the top to the bottom; price retraced to the 382 and continued to reject down, so now this is our new start" [2:26]-[2:47]. I.e. **redraw the fib on each new structure break and require the retracement to hold shallower than the prior one.**
  - **Two hard preconditions for that continuation logic:** "**price must be trending for this to work; there must be high volume for the trend to continue strongly in one specific direction**" [2:51]-[2:57].
  - Risk sizing shown: "I risked a little bit less than 1%, which is about 1,500" [3:20]-[3:25] on the funded account; made ~$1,600; account up $854 overall [3:31]-[3:35].
  - Named "fake out candle": "this is what we call a fake out candle, big engulfing candle, and then price took off for the whole day" [1:32]-[1:38] — a bias-confirmation observation, not a rule (he says he did not take that trade).

## Vague / untestable / chart-pointed claims
- [1:02]-[1:19] "if price moves **dramatically** above or below this blue line it usually tends to go that way all day" — the whole bias rule hinges on "dramatically", which is never quantified (no point/ATR/% threshold). He hedges it twice himself as "a general rule of thumb" and "a really stupid rule of thumb".
- [2:03]-[2:12] "if we break out of London session we usually trend in that direction" — no London open time, no timezone, and no candle-close-vs-wick definition of the breakout. ("First hour of London open" is the range, but the clock time is never spoken.)
- [0:20]-[0:27] "I got my sell signal right here and we had really high volume to the cell side" — "really high volume" is unquantified and chart-pointed; the same is true of the [2:51] precondition "there must be high volume".
- [0:36]-[0:45] The exit was fully discretionary (had things to do, volume dropping, zigzagging) — the trade as shown does **not** follow a stated exit rule, so it cannot be used to validate one.
- [2:12]-[2:23] Both the entry signal (Happy Trail) and its confluence (Fractal Frenzy) are **paid closed-source indicators**; neither logic is disclosed.
- [2:26]-[2:47] The fib hold/exit test is narrated over the chart; "then broke structure" is not defined (no candle-close requirement given here, unlike uC_Iimhvwiw and uagC-2UjAO0).
- No stop-loss placement rule at all — which makes the "1:2 goal" unreconstructable.
- [1:20]-[1:32] "we opened up, little bit of grabbing liquidity, and then aggressive momentum down which is why I went to the sell side" — post-hoc narration; "grabbing liquidity" and "aggressive momentum" undefined.

## Testability
- rating: LOW (a single-trade recap that defers its own rules to another video; the bias trigger is "dramatically above/below", the entry is a paid black box, there is no stop rule, and the exit taken was admittedly discretionary)
- overlap: session-filter (midnight-NY open line + London-open first-hour range breakout) + proprietary-signal entry + fib-scalp (as a hold/exit test rather than an entry). Bias stack overlaps heavily with x1-InyOycus; the fib mechanics restate uC_Iimhvwiw.
- notable quotes:
  - [1:02] "if price moves dramatically above or below this blue line it usually tends to go that way all day... that's just a general rule of thumb and it's what I go by to form my bias"
  - [2:03] "this section right here is the first hour of London open, and if we break out of London session we usually trend in that direction"
  - [2:51] "price must be trending for this to work; there must be high volume for the trend to continue strongly in one specific direction"
