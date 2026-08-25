# The Only Video You Will Ever Need To Day Trade Divergences
- id: trx_M2Bss-c | views: 55000 | length: 780s
- market(s) shown: German 40 (DAX) — "right now, I'm on German 40 on the 1-hour timeframe" [0:52]
- timeframe(s) taught: 1-hour (the only chart timeframe named); rules are presented as timeframe-agnostic

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **RSI — "just the standard TradingView built-in RSI"** [2:35], levels **70 (upper) and 30 (lower)**: "On the standard RSI, this top line is at 70 and the bottom line is at 30" [7:22]. Length never spoken (defaults to 14 by implication of "standard/built-in", but he does not say 14).
  - **Gann box** (TradingView left toolbar, "third box down... Gann and Fibonacci tools. Scroll down to Gann box") used as a **PD array / premium-discount zone**; settings shown only as an on-screen screenshot [8:59] "These are my settings for this. Take a screenshot if you'd like."
  - **Happy Trail** (paid TTF indicator) — optional entry-timing confirmation.
- Setup/context required:
  - Classify trend by market structure: uptrend = higher highs + higher lows; downtrend = lower highs + lower lows [2:16], [4:05].
  - Draw a trend line; the divergence must be "in confluence with the trend line" [2:30].
  - **Four divergence types, with the exact drawing rule for each:**
    - Hidden bullish (uptrend, continuation): compare the **higher lows** on price vs RSI — price low higher, RSI low lower [2:09]-[2:44].
    - Hidden bearish (downtrend, continuation): compare the **lower highs** — price high lower, RSI high higher [4:11]-[4:29].
    - Regular bearish (reversal): "the lines are drawn on the **tops of the higher highs**" [5:13] — price higher high, RSI lower high.
    - Regular bullish (reversal): "drawn on the **lows of the lower lows**" [5:17] — price lower low, RSI higher low.
  - Hidden = continuation, regular = reversal: "Hidden divergences are continuation divergences... Regular divergences usually mean that price is likely to reverse" [0:29]-[0:40].
- Entry trigger (the full "secret sauce" stack, all four conditions):
  1. Price **breaks previous market structure** [8:37].
  2. Price **pulls back to the trend line** and forms a **hidden divergence** [9:23]-[9:28].
  3. Gann box / PD array drawn over **the entire move that broke previous structure**, bottom-to-top for longs, **top-to-bottom for shorts** [8:54], [9:43]-[9:52]; the divergence point must sit **in the lower half of the PD array for a buy** ("within the lower half of your PD array, your discounted price" [9:30]) or **the top half for a sell** ("Once price comes back up into the top half of the PD array, this is now an area of premium" [9:55]).
  4. **RSI filter:** "don't take these divergences unless one of the divergences is above the 70-30 range" [7:15]-[7:22]; the setup he wants is "the one that was above the range and then the higher high that was below the range" [7:33]-[7:38].
  - Optional concrete trigger: Happy Trail smiley — "For a buy signal, you get a happy face underneath the price. Enter your trade" [11:08]; sell = "an upside down smiley face" printing above price [11:21].
- Stop loss: For the trailing/holding version the rule is explicit — "**every time price breaks the PD array, you want to draw a new one, and you want your stop loss to always be above the top of the PD array**" [11:54]-[12:10]. Initial stop placement for the entry itself is **not stated numerically** (it is implied by the R multiple only).
- Take profit:
  - Structural target: **the previous high point** for longs ("this would be take profit one, which is the previous high point that it created" [3:40]-[3:44]); **the previous low point** for shorts [10:17].
  - R-multiple version: "**shoot for a 1 to 1.5, or you can go for a 1 to 2**" [11:12]-[11:15], with the stated preference "**1 to 1.5s play out more often than one to two's**" [11:30].
  - Trail: at 1:1.5 in profit → move stop to break even ("making it a risk-free trade"); at 1:2 → move again [11:43]-[11:52], then keep stops above each newly drawn PD array.
- Filters he adds:
  - "I usually don't recommend taking regular divergences **unless a trend line is broken**" [6:27]-[6:30] — regular divergences are counter-trend and "more dangerous".
  - "Do I recommend taking a vast majority of hidden divergences? Absolutely. They are the best trades that you can take" [8:21].
  - Break of structure requires the move itself, not the wick (see contrast with uagC-2UjAO0 where he states the candle-close requirement explicitly).

## Vague / untestable / chart-pointed claims
- [1:11]-[1:25] "we have a hidden bullish divergence, a regular bearish divergence, a hidden bearish divergence, and a regular bullish divergence... take a screenshot of this" — the entire reference taxonomy is delivered as an image; the transcript alone does not fix which swings he selected.
- [2:35] "just the standard TradingView built-in RSI" — **length never spoken**. Must be frame-checked to confirm 14.
- [8:59] and [9:36] Gann box **settings are shown, never spoken** ("These are my settings... Take a screenshot") — the PD-array subdivision (does the 50% line come from a 0/0.5/1 Gann grid?) is only inferable as "lower half / upper half / 50%".
- [7:15]-[7:38] The 70/30 filter wording is self-contradictory in the transcript: he says "unless one of the divergences is above the 70-30 range" then "all of these divergences that happen above this range, I'm not interested in". The intended rule is almost certainly *one leg outside 70/30 and the second leg back inside*, matching udwkldark34 — but as spoken it is ambiguous and needs a frame-check.
- [6:07]-[6:28] "why didn't that divergence get respected? It did. Price pulled back a little bit" — post-hoc chart narration; no forward rule.
- [7:01]-[7:09] "This one is also a slight divergence... just barely lower on the RSI. Still a divergence." — no minimum RSI delta given; "slight" divergences count, which makes divergence detection threshold-free and therefore fitting-prone.
- Which swing points qualify as the two comparison legs is never defined mechanically (no fractal/pivot lookback N).
- Entry precision leans on **Happy Trail**, a closed-source paid indicator; without it the entry is "enter at the divergence", i.e. discretionary.

## Testability
- rating: MEDIUM (divergence class definitions, the 70/30 filter, the PD-array half rule, structural targets and R multiples are all explicit; but swing-point selection, RSI length, Gann settings and initial stop placement are not)
- overlap: hidden-divergence (primary) + regular-divergence + market-structure/BOS + PD-array/premium-discount (Gann box) + trend-line; this is the channel's most complete single statement of the divergence system
- notable quotes:
  - [7:15] "don't take these divergences unless one of the divergences is above the 70-30 range. On the standard RSI, this top line is at 70 and the bottom line is at 30."
  - [9:23] "if price breaks previous structure, then pulls back to your trend line, creates a hidden divergence, and this point right here is within the lower half of your PD array, your discounted price. You can set a buy position right here and target the previous high point."
  - [11:54] "every time price breaks the PD array, you want to draw a new one, and you want your stop loss to always be above the top of the PD array."
