# Best SMC ICT Indicator
- id: eiKZ8eASWR0 | views: 112000 | length: 909s
- market(s) shown: unstated — presenter says it works on "indices, Forex pairs, Commodities" and NOT crypto ("as long as it's not crypto" [0:21-0:26]); the demo chart symbol is never named
- timeframe(s) taught: 4 hour for the higher-timeframe fractal range + equilibrium [7:26-8:03]; 5 minute candles are the basis of the DR/IDR ranges [9:12-9:17]; "lower time frame" (unspecified) for the entry [8:01-8:05]

## Mechanical rules (only what the video actually states)
This video is a walkthrough of the free "TTF SMC toolkit" TradingView indicator by The Trading Floor, mostly narrated by a guest ("Jinx"). Setup: indicators tab → type "ttf SMC" → add → three dots → visual order → bring to front [0:26-0:43].

- Indicators + exact settings (five tools, each with a stated definition):
  1. **New York midnight open + 8:30 a.m. New York price lines** — enabled via "display under the New York midnight open and display under the New York 8:30 open" [1:45-1:56]. Rationale: ICT's IPDA "resets at midnight New York time every day" [2:01-2:06].
  2. **Williams fractals** — Styles tab → check "filter top fractals" and "filtered bottom fractals" [2:58-3:07]. CRITICAL LAG RULE: "Williams fractals print late ... that fractal printed two candle closures after the candle being denoted by the fractal" [3:09-3:20].
  3. **Gann box** for equilibrium — "plot a gan box to denote the equilibrium which is just the 50 line of any given range" [7:45-7:52]; the 50% line splits the range into premium (above) and discount (below) [7:54-8:01].
  4. **DR / IDR** (developed by "the master"; presenter credits "Alex's streams"): three session boxes — "regular denotes the time during New York Stock Exchange trading hours; after denotes the time during the Tokyo and Asian trading session; and the overnight denotes the European or London trading session" [8:21-8:34].
  5. **Fractal Wyckoff accumulation/distribution** — from the "Triple M strategy ... developed by Mint FX" [10:45-10:51]; prints fractal springs / upthrusts (UTADs) off candle wicks, used as an ENTRY TRIGGER, not a level tool [10:34-11:09].

- **DR/IDR construction (fully mechanical, quoted):** during the session window, using 5-minute candles —
  - "The highest wick created by a five minute candle during the DR time frame is considered the range high or the high of the defining range. The low wick of that same time frame is considered the DR low" [9:17-9:31]
  - "The body closure high of that same time period is the IDR or implied defining range high and the lowest body close is considered the IDR low" [9:31-9:41]
  - "the midline is calculated using the IDR ... the equilibrium of the IDR serves as our midline" [9:42-9:49]
  - **Core DR/IDR thesis:** "once this range is formed and broken in one direction, price will not trade past the other extreme of that range" [9:49-9:57], claimed at "nearly 80% historical accuracy" [10:13-10:15].

- **Fractal range / BOS construction (mechanical, quoted):** put a horizontal ray on the fractal low = range low; "trace backwards to the fractal that caused this low candle" = range high [4:00-4:15]. "every time you have one of these ranges break you can consider that a break of structure" [4:22-4:27]. On a bullish BOS, move the range high, and "drag the range low to the fractal that caused that break of structure" [4:33-4:41]. If no new opposing fractal printed in the meantime, that side does not move [5:11-5:21, 5:58-6:03].

- Setup/context required (the worked example, [12:36-13:34]): 4h fractal range drawn → Gann box equilibrium → price is in the DISCOUNT half of the 4h range → drop to lower timeframe → price breaks OUT of the DR range (this "established that the bias is bullish for the rest of this trading session" [12:45-12:50]) → price RETRACES back to the DR range.
- Entry trigger: a Wyckoff spring wick inside that retracement — "it retraced to the DR range, it gave us a Wyckoff accumulation in the form of a spring and we're looking to go long here" [13:15-13:27]. Entry is on the CLOSE of that candle [13:27].
- Stop loss: "that close of candle we would cover the swing low, in this case being this candle itself" [13:27-13:32] — stop below the swing low of the signal candle.
- Take profit: "let's just target conservative 2R" [13:32-13:34]. **2R.**
- Filters he adds:
  - **Directional bias from the midnight line:** "you generally be looking for longs below it and shorts above it" [2:06-2:12].
  - **Premium/discount filter:** only long from discount, only short from premium, relative to the 4h range's 50% equilibrium [8:01-8:05].
  - **No first-hour trading:** "not trading during that first hour of each market session open" [14:13-14:18] — Arty's own bot rule, stated in the outro.
  - Kill zones mentioned as a confluence but never defined numerically [11:13-11:15].

## Vague / untestable / chart-pointed claims
- [4:44-8:03] The entire fractal-range drag sequence (~3.5 minutes) is silent chart manipulation — "we have another break here", "bring price to the most recent [fractal]" — with no verbal definition of what price level constitutes the break (wick vs close) or how a "minuscule break" [6:29-6:32] is judged ("there is a minuscule break here so we will cover it" — a discretionary override).
- [2:12-2:24] "you can also visualize these price lines as magnets ... and then eventually the magnets let go and price will take off in its true intended direction" — narrative, no measurable trigger.
- [2:28-2:52] "every time price came up it rejected the midnight line" then "please do your own back testing" — an admission the presented evidence is cherry-picked chart-pointing.
- [10:13-10:15] "nearly 80% historical accuracy" — no sample size, instrument, date range or definition of a hit. Unverifiable as stated.
- [11:03-11:15] Wyckoff spring/UTAD detection: "we can use scenarios highlighted by these wicks to denote the fractal spring or upthrust" — the wick geometry that qualifies is inside the indicator, never stated in words.
- [12:20-13:13] The two long silent gaps in the walkthrough are pure screen work; the "bias" formation shown there is not verbally specified.
- [13:41-13:47] Explicit disclaimer: "what I've presented to you today is not a formalized back-tested trade plan. This is an example of how you could combine these tools together" — the author himself says this is not a validated strategy.
- [14:13-14:40] Arty's bot claims ("trading very very well", "it's just golden") have no numbers attached.
- Whole video funnels to trdfloor.com courses [15:02-15:08].

## Testability
- rating: MEDIUM (the DR/IDR construction, the midnight-line bias, the 2R target, the swing-low stop and the no-first-hour filter are all precisely stated; but the entry trigger — Wyckoff spring wick — and the fractal range dragging are indicator-internal/discretionary. The DR/IDR *thesis alone* — "range broken one way won't trade past the other extreme" — is 100% mechanically backtestable from 5m data with zero indicator dependency, which makes this the highest-value video in the batch.)
- overlap: market-structure/BOS (Williams-fractal BOS), session-filter (DR/IDR session boxes, no-first-hour, midnight open), volume-profile-adjacent (premium/discount equilibrium), candlestick-pattern (Wyckoff spring wick). References external methods: Scott Taylor / Evolution Markets [7:30-7:36], Mint FX Triple M [10:45-10:51], ICT IPDA.
- notable quotes:
  - [9:17-9:41] "The highest wick created by a five minute candle during the DR time frame is considered the range high ... The body closure high of that same time period is the IDR or implied defining range high and the lowest body close is considered the IDR low."
  - [9:49-9:57] "once this range is formed and broken in one direction, price will not trade past the other extreme of that range."
  - [13:27-13:34] "that close of candle we would cover the swing low, in this case being this candle itself, and let's just target conservative 2R."
