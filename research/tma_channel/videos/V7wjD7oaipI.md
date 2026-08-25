# How to Trade Volume (Forex)
- id: V7wjD7oaipI | views: 208000 | length: 420s
- market(s) shown: unstated (forex pair, never named on screen or spoken)
- timeframe(s) taught: unstated (one reference to "100 pips in five minutes" implies a 5m chart at that moment, [4:26])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: TradingView's **built-in Volume indicator, default settings** ([0:53]-[1:19] "the first indicator the only indicator that they put up on the screen for you is a volume indicator... this is the built-in one and this is pretty much all you need"). No moving-average-of-volume, no threshold, no other indicator is added.
- Setup/context required: Explicitly a **supplement, not a standalone strategy** — [5:58]-[6:12] "using the volume indicator is a nice tool but i wouldn't rely on it solely... stick to your strategy and use the volume indicator as like the reassuring click". Recommended for experienced traders only.
- Entry trigger: Three distinct uses, none fully specified:
  1. **Avoidance filter** — if volume is "extremely low" (consolidation), do not enter the pair at all ([1:52]-[1:56] "if you see extremely low volume do not get into that pair whatsoever").
  2. **Trap/reversal entry** — after a consolidation with low volume, two taller counter-direction volume bars bait retail in; wait for a **high-volume long engulfing candle in the opposite direction** and trade with it ([3:30]-[3:59]). Entry is on that candle's close ("even if you just waited for this one candle to close on this one move you could have gotten 31 pips", [4:01]).
  3. **Stop-hunt fade** — a **massive volume spike** far larger than surrounding bars marks a stop-loss hunt; if you are in a losing position at that point, close it and reverse to trade with the spike ([4:33]-[5:31]).
- Stop loss: **never stated.**
- Take profit: The only rule given is for the post-spike case: after a huge volume spike expect a **correction of about 50% of that spike**, scalp that 50% and exit ([5:40]-[5:56] "you will get a nice fat correction of about 50 of that spike so you can scalp that 50 call it quits"). No target rule for the other two uses.
- Filters he adds: None numeric. No session, day or news filter. The only filter is "don't trade consolidation / low volume".

## Vague / untestable / chart-pointed claims
- [1:19]-[1:24] "you don't really need to know the amount of volume that's going in you just need to see a clear growth in volume" — explicitly refuses to give a threshold. Every rule in the video inherits this.
- [1:52] "if you see extremely low volume do not get into that pair" — "extremely low" relative to what lookback is never stated.
- [2:33]-[3:08] "we have this right this consolidation area it's also clearly represented in the volume by extremely low volume... then we get a taller red candle right here and a taller red candle right here" — entirely chart-pointed; "taller" is relative and unmeasured.
- [3:30]-[3:41] "waited for the trap to be set and then a high high high volume long engulfing wick in the opposite direction" — the entry condition; conflates "engulfing candle" and "long wick", and "high high high volume" is unquantified.
- [4:33]-[4:39] "you can see these massive massive spikes on the volume and those are literally just stop hunts" — asserts causation with no test; spike size undefined.
- [5:02]-[5:07] "this is absurd amounts of volume compared to the rest of everything like you can see how huge this candle spike is" — chart-pointed, comparative, no multiple-of-average given.
- [5:22]-[5:31] "if you're in a position you can easily get out of it take the loss but then reverse your position and go with that stop hunt because you don't know when it's going to stop" — advises reversing into a move with no stop rule and no invalidation; a live-risk instruction with no risk parameter.
- [5:40] "after this huge huge spike in the volume meter you know that the price is going to correct down a little bit it's not going to reverse fully but you will get a nice fat correction of about 50 of that spike" — the one numeric claim (**50% retrace of the spike**), asserted with no evidence and with "the spike" (candle range? move range?) undefined.
- [4:01] "31 pips", [4:26] "100 pips in five minutes", [5:32] "150 170 pips in one day" — cherry-picked examples.
- Forex volume is broker tick-volume, not true volume; he never mentions this, so any test result is broker-dependent.

## Testability
- rating: LOW — no indicator threshold, no entry price rule, no stop loss, and a single vague target ("50% of the spike"). Every condition is a comparative visual judgement about bar height that he explicitly declines to quantify. He himself frames it as a confirmation overlay rather than a strategy.
- overlap: volume-profile (loosely — this is raw volume-bar reading, not a real volume profile), candlestick-pattern (engulfing entry, shared with the 1m scalping video), "trap"/stop-hunt liquidity narrative that recurs across the channel (see `-za-CIJbwxs`, `R3T1zRyZdMc`). Could serve as an add-on filter to test on top of a mechanical TMA setup rather than as a strategy in its own right.
- notable quotes:
  - [1:19] "you don't really need to know the amount of volume that's going in you just need to see a clear growth in volume"
  - [5:40] "you know that the price is going to correct down a little bit it's not going to reverse fully but you will get a nice fat correction of about 50 of that spike"
  - [6:09] "stick to your strategy and use the volume indicator as like the reassuring click"
