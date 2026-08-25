# Per-video rule extraction spec (for subagent extractors)

For each assigned video, read its cleaned transcript
(`transcripts_clean/<id>.txt`, lines `[mm:ss] text`) and write
`research/tma_channel/videos/<id>.md` in EXACTLY this format:

```markdown
# <title>
- id: <id> | views: <views> | length: <duration>s
- market(s) shown: <e.g. US30, XAUUSD, BTC, NAS100 — as stated>
- timeframe(s) taught: <e.g. 5m entry / 15m context; "unstated" if never said>

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: <e.g. RSI(14); SMMA 21/50/200; "settings unstated">
- Setup/context required: <trend filter, session, structure state>
- Entry trigger: <exact condition; the candle/event that fires the trade>
- Stop loss: <exact placement rule>
- Take profit: <exact rule; R multiple / level / trail>
- Filters he adds: <sessions, days, news, confluences>

## Vague / untestable / chart-pointed claims
- [mm:ss] <claim> — why untestable (e.g. "points at chart: 'this level here'",
  discretionary zone drawing, no numeric setting given)

## Testability
- rating: HIGH (fully mechanical) / MEDIUM (1-2 discretionary gaps) / LOW (mostly discretionary)
- overlap: <which known TMA technique family: regular-divergence, hidden-divergence,
  fib-scalp, 5m-scalp(SMMA), market-structure/BOS, S/R-retest, three-line-strike,
  volume-profile, VWAP, session-filter, candlestick-pattern, other>
- notable quotes: 1-3 timestamped quotes that pin down the core rule
```

Rules:
- NEVER invent a rule the transcript doesn't state. If the presenter says "as you
  can see here" and the rule depends on the unseen chart, log it under
  vague/chart-pointed with the timestamp — the main session will frame-check it.
- If the video teaches no strategy at all (pure vlog/motivation that slipped
  triage), write the file with `## Mechanical rules` = "none — <one-line reason>"
  and testability LOW.
- Numeric settings matter most: MA lengths and type (SMA/EMA/SMMA), RSI length
  and levels, fib levels used, session times WITH timezone, R multiples, pip
  targets. Quote them exactly.
- Note when a video contradicts or updates another one (he has "Update"/"Final"/
  "Improved" versions of the same strategy) if the transcript references it.
