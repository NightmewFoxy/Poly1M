# 1 Min Scalping Strategy
- id: Vo6nKAzqUGU | views: 116000 | length: 243s
- market(s) shown: unstated (chart shown, instrument never named)
- timeframe(s) taught: 1h for support/resistance context → 15m for mid-level zones → **1m entry**; the indicator's own "timeframe" input is set to "chart"

## Mechanical rules (only what the video actually states)
- Indicators + exact settings — "Stair Master" (his community's proprietary indicator, prints sneaker icons). **1-minute preset stated explicitly** [1:19–1:46]:
  - Allow signal repainting: **ON**
  - Time frame: **chart**
  - Stair sensitivity: **3** (unchanged from the 15m video)
  - TSV length: **13**
  - TSV MA filter: **7**
  - MA source: **close**
  - MA length: **75** (changed from the 15m video's value)
  - MA type: **smoothed** (i.e. SMMA)
  - "Everything else will remain the same from yesterday's video."
  - Cosmetic: he removes the ceiling/floor/MA plots from view, "just for convenience... and only look at every time the shoe prints a signal" [2:04–2:10].
- Setup/context required:
  - The signal's own internal condition, stated verbally: **"the signal must print while it's breaking above a ceiling or below a floor and above or below the moving average"** [1:56–2:02].
  - Draw **1-hour support and resistance** (support = price hit it and bounced up; resistance = price hit it and shot down) [2:20–2:30].
  - Mark a **mid-level** zone: old 1h resistance that broke and was then used as support twice; verify it on the **15-minute** chart and colour it blue [2:31–2:47].
  - Wait for an **active session** — "We are currently not in an active market session. This is pre-London session right now. So, we wait for London session to open. We wait for some movement" [2:57–3:05].
- Entry trigger: on the 1-minute chart, **a 1-minute candle print as it breaks the consolidation zone** (break above/below the marked level), with the Stair Master sneaker signal [2:48–3:10]. Base rule from the previous video: **take every single sneaker signal between London session and New York session** [3:18 of prior video, restated at 0:31–0:36 here].
- Stop loss: "stop loss below the swing low" (for the long example) [3:32].
- Take profit: **1 : 1.5 risk-to-reward is the strategy rule** — "if you're sticking to the rules of the strategy, a 1 to 1.5 is completely fine" [3:48–3:52]. Discretionary alternatives shown: target the 1-hour S/R or "previous structure to the left"; in his example the "safe level" gave **1 : 1.65** and the top of the zone gave **1 : 2.83** [3:36–3:47].
- Filters he adds:
  - Session window: **between London session open and New York session** (no clock times, no timezone).
  - Target selection logic: "Price will always go for the nearest available liquidity. There is liquidity living above this swing high" [3:19–3:25].
  - Use TradingView alerts so you don't have to watch charts; repainting-on gives "a couple of minutes to get on the charts and set up your trade entry" [0:36–0:49].

## Results claimed (15-minute version, referenced not re-derived)
- [0:49–1:15] From "the 28th to the 14th of August", **10 days**: **8 losses, 20 wins** at **1:1.5 RR** → "+30% ... minus 8% for your losses, giving you a net of 22% on your account". Month of the start date and the year are never stated; 28 trades in 10 days.

## Vague / untestable / chart-pointed claims
- [1:22] The whole entry engine is the paid closed-source "Stair Master" indicator — the settings are given but the algorithm (TSV, ceiling/floor construction, "stair sensitivity") is not, so it cannot be reimplemented.
- [2:20] "drawing up 1-hour support and resistance... this is a level of support because price hit it and bounced up" — discretionary, one-touch definition, no zone width rule.
- [2:31] "this right here is a mid-level" — chart-pointed zone; the rule (broken resistance reused twice as support) is stated but the tolerance is not.
- [2:48] "you're looking for either a break below this or a break above this using the stair master and consolidation zones" — "consolidation zones" is never defined numerically.
- [3:04] "We wait for some movement and then take a 1-minute candle print as it breaks these consolidation zones" — "some movement" is undefined.
- [3:14] "we're going to be targeting the 1-hour support and resistance or previous structure to the left" — three different targets demonstrated (1:1.5 rule, 1:1.65 safe, 1:2.83 max) with no rule for choosing.
- [0:31] "You take every single sneaker signal between London session and New York session" — no clock times, no timezone.
- [0:52] "from yesterday, the 28th to the 14th of August" — dates are internally inconsistent / month unstated; the backtest cannot be located.

## Testability
- rating: MEDIUM (numeric indicator settings are fully quoted and the RR is fixed, but the indicator itself is closed-source and the S/R + session filters are discretionary)
- overlap: 5m-scalp(SMMA)-family / proprietary-indicator-signal + S/R-retest + session-filter
- notable quotes:
  - [1:36] "The TSV length and the TSV MA filter is going to remain the same at 13 and seven. The MA source is going to be closed, and you are going to change the MA length to 75, and change the MA type to smoothed."
  - [1:58] "the signal must print while it's breaking above a ceiling or below a floor and above or below the moving average."
  - [3:48] "If you're sticking to the rules of the strategy, a 1 to 1.5 is completely fine."
- update relationship: explicitly the **1-minute variant of the previous day's 15-minute Stair Master video** ("using the same indicator as yesterday's video", "I'm going to show you the 1-minute settings for this same strategy") — only the MA length (75) and MA type (smoothed) change; also points to "a more in-depth video by Christie" [3:55].
