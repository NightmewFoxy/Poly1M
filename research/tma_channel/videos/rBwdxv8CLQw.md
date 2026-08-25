# 5 minute Scalping Strategy (Sniper Entries)
- id: rBwdxv8CLQw | views: 18000 | length: 169s
- market(s) shown: unstated (chart symbol never named; "indices"/FX implied by "range" talk only — do NOT assume)
- timeframe(s) taught: unstated in transcript. Title says 5-minute; the only timeframe words spoken are session boundaries. He does say the overnight range is drawn as a box over a ~11h window.

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **Happy Trail** (paid, trdfloor.com) — "the settings for the happy trail, there are four different cases. I used case 4" [2:30]. No other parameter given.
  - **Simple Sessions by TTF** (free, visual only) — "unselect all of the sessions and make your own userdefined custom session... I have it from 9:00 a.m. till 10 p.m." [0:53]-[0:58], time zone set to his own. That red block leaves the black block = the overnight range.
  - Rectangle tool drawn "around the highs and lows and the width of that range" [0:38]-[0:43] (this is just the manual equivalent of the session block).
- Setup/context required: **Overnight range = 22:00 to 09:00 in his time zone, which he states explicitly as GMT+1 / UTC+1** [0:26]-[0:33]: "I'm at GMT+1 or UTC+1... from my time 1000 p.m. until my time 9:00 a.m. is what I deem the overnight session when New York session is over and London session starts." Strategy is run starting in London session.
- Entry trigger: Price must first **break out of the overnight range**, then take **the first Happy Trail signal in the breakout direction**. "If it breaks out below the range, we sell. If it breaks out above the range, we buy" [1:12]. "if price breaks out below this range, I'm looking for the first sell signal from Happy Trail. And I enter that" [1:17]. Counter-direction signals are explicitly ignored: "We ignore the buys because we broke out below" [1:58].
- Stop loss: **not stated** — only implied by the RR ("stop-loss, 2% take profit" [2:25]). No placement rule given anywhere in the video.
- Take profit: **1:2 risk-to-reward** [1:23], sized so each win is +2% of account ("if you get a 1 to 2 risk-to-reward and you make 2% profit on every trade four times in a month, you're up 8%" [1:33]-[1:37]) — i.e. 1% risk per trade.
- Filters he adds:
  - Only the **first** signal after the breakout.
  - Direction locked to the breakout side (ignore opposite signals).
  - Requires momentum: "This type of setup requires lots of momentum and does not happen every day" [1:23].
  - Frequency claim: 4 occurrences in the last 30 days, 4/4 winners [1:28]-[1:33].
  - Explicit caveat: "I have not back tested this for the entire year. That is my caveat" [1:44].

## Vague / untestable / chart-pointed claims
- [0:00] "I've been doing this overnight range breakout strategy starting in London session" — references a prior video's strategy that is not restated here; the London-session start is asserted but never given as a hard entry-window rule (no cut-off time for taking the signal).
- [1:12]-[1:17] The breakout definition is never made precise: no statement of whether a candle must CLOSE outside the range or a wick suffices, and no timeframe on which the breakout is judged.
- [1:48]-[2:30] Every worked example is pure chart narration ("this example right here... we have our overnight range") — the outcomes cannot be verified from the transcript.
- Entire entry hinges on a **proprietary paid indicator (Happy Trail, case 4)** whose logic is never disclosed → not reproducible without buying it. This is the single biggest testability blocker.
- Stop-loss placement is genuinely absent, so the "1:2" cannot be reconstructed.

## Testability
- rating: MEDIUM (session window and RR are exact and timezone-stamped; but the entry signal is a closed-source paid indicator and the stop rule is never stated)
- overlap: session-filter (overnight/Asia-range breakout) + proprietary-signal entry; adjacent to the London-breakout family he teaches in ulb5U8cox-U and x1-InyOycus
- notable quotes:
  - [0:26] "I'm at GMT+1 or UTC+1. That is my time zone. So basically from my time 1000 p.m. until my time 9:00 a.m. is what I deem the overnight session"
  - [1:17] "if price breaks out below this range, I'm looking for the first sell signal from Happy Trail. And I enter that. And I'm shooting for a 1:2 risk-to-reward ratio."
  - [2:30] "the settings for the happy trail, there are four different cases. I used case 4."
