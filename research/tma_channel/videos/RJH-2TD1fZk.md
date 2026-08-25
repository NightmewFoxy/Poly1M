# RSI Divergence (GOLD) Trading Strategy
- id: RJH-2TD1fZk | views: 123000 | length: 441s
- market(s) shown: XAUUSD ("gold US dollar") [2:53]
- timeframe(s) taught: 15-minute [2:56]

## Mechanical rules (only what the video actually states)
This is the clearest statement on the channel of his "RSI leaves-and-returns" entry — and he explicitly says divergence itself is NOT the entry.

- Indicators + exact settings: **RSI, default TradingView settings, nothing changed** [3:07] — "these are default settings. Nothing has been changed" (i.e. RSI length 14). Levels used: **70 upper, 30 lower**. Optional bonus: the proprietary "easy exit indicator" [6:34].
- Setup/context required: RSI must first **leave** the 70/30 band (print above 70 or below 30). Divergence is treated as a warning only: [2:20] "This is a sign of trend weakness. It doesn't mean reversal yet, just caution. This is a great warning, but it is not your entry."
- Entry trigger: **RSI comes back inside the 70–30 range after having left it, and forms a small peak/top just inside the band** — [2:32] "I wait for the RSI to leave the 70/30 zone. Then I wait for it to come back inside that zone. That's the moment where the momentum flips and that's where I look for entries." Direction: RSI returning from above 70 → short; returning from below 30 → long.
  - Workflow he demonstrates: double-click the RSI pane to full-screen it, circle every leave-then-return point, drop a **vertical line** on each, then double-click back to price and take the position at that bar [4:03–5:17].
- Stop loss: **below the previous swing** — [6:12] "Look left for your market structure. Put your stop loss below the previous swing" (i.e. beyond the swing on the trade's adverse side).
- Take profit: **not stated.** He uses TradingView's position tool "not even adjusting these tools" [5:24] so the R multiple is whatever the default tool shows — never named.
- Filters he adds: none — no session, day or news filter. Explicitly says divergence is optional confluence ("You don't even have to look for divergences even though they were here 90% of the time" [5:38]).

Rationale given [4:41]: because RSI is an oscillator, once price stops being overbought and re-enters the normal range "it's likely to go to the other side".

Bonus exit tool [6:34]: the "easy exit indicator" prints coloured dots — **yellow = weak exit, orange = medium exit, red = "GTFO" exit**. A dot near your entry means it is safe to hold. Not required for the strategy.

Contradicts/updates: this reverses the standard overbought/oversold teaching — [0:01] "Everyone on the internet seems to be teaching the RSI wrong ... that's exactly how you lose every single trade". Consistent with his other RSI video (TQMayZS9o1U) in rejecting 70/30 as reversal levels, but that one uses a trend-line break as the trigger while this one uses the band re-entry.

## Vague / untestable / chart-pointed claims
- [5:28] The result count ("a win, a win, a win, a loss, but it went in our direction. A win, a loss, a win, a win, a win") is read off an unmarked chart with no prices, dates or R values — not reconstructable.
- [5:31] "a loss, but it went in our direction" — counting a stopped trade as a moral win.
- [6:16] "you will make money like 80% of the time" — no backtest, sample size or period given.
- [4:00] "I'm looking at these little peaks after it left the range" — what qualifies as a "little peak" (how many bars, how large) is never defined; this is the core discretionary gap.
- [6:12] "Look left for your market structure. Put your stop loss below the previous swing" — "previous swing" is not defined (no lookback, no fractal rule).
- [5:24] "I'm not even adjusting these tools. I'm just putting the position tool" — target is whatever the tool defaulted to; no TP rule exists.
- [6:34] Easy-exit indicator is proprietary (paid) — its dot logic is not disclosed.
- [1:14] "this does not mean that it is confined to these two ranges. it can go outside of them" — correct but no rule for how far outside counts.

## Testability
- rating: MEDIUM (entry condition is fully mechanical apart from the "little peak" definition; stop is semi-defined; **take profit is missing entirely**)
- overlap: regular-divergence / RSI-oscillator — his own variant is really "RSI band exit-and-re-entry", with divergence as optional confluence
- notable quotes:
  - [2:32] "I wait for the RSI to leave the 70/30 zone. Then I wait for it to come back inside that zone. That's the moment where the momentum flips and that's where I look for entries."
  - [2:20] "This is a sign of trend weakness. It doesn't mean reversal yet, just caution. This is a great warning, but it is not your entry."
  - [6:12] "Put your stop loss below the previous swing and you will make money like 80% of the time."
