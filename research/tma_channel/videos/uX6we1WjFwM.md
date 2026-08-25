# Best Day Trading Strategy
- id: uX6we1WjFwM | views: 16000 | length: 123s
- market(s) shown: unstated (symbol never named; MetaTrader mentioned only as the platform for a downloadable risk calculator)
- timeframe(s) taught: **30-minute chart** — "You get on a 30-minute chart" [0:11]

## Mechanical rules (only what the video actually states)
This is ~85% a Black Friday sales pitch for The Trading Floor package. Only the first ~30 seconds contains a rule set, and it is a compressed restatement of the Happy Trail signal strategy.

- Indicators + exact settings: **Happy Trail** (paid, unnamed here but described by its output) — "There are two types of smiley faces, right side up and upside down" [0:06]-[0:11]. Right-side-up = long, upside-down = short (direction not spelled out in this video; taken from his other videos, so treat as unstated here). **No case/parameter setting is given** (contrast rBwdxv8CLQw "case 4" and uagC-2UjAO0 "case 2").
- Setup/context required: none stated. No trend filter, no session filter, no structure requirement — the signal alone is the whole setup as presented here.
- Entry trigger: **"Once it prints, you enter your trade"** [0:11]-[0:16] — i.e. enter on the printed smiley face.
- Stop loss: **"Stop loss two ticks above the candle"** [0:11]-[0:16]. This is the most precise stop rule he gives anywhere in this batch (contrast uagC-2UjAO0's "a couple of ticks above the previous candle"). Note the phrasing is for a short; the long mirror (two ticks below) is not spoken.
- Take profit: **1:2 risk-to-reward** [0:16].
- Filters he adds: none. He does show a claimed sequence of results — "+2% ×7, then −1%, currently active trade" [0:16]-[0:26] — and mentions a swing-trade variant that "would have gotten you a 1 to 29" [0:26]-[0:33], but neither is a rule.

## Vague / untestable / chart-pointed claims
- [0:00]-[0:06] "I made this video three days ago, and the 18 people that took my advice are absolutely crushing it" — unverifiable social proof.
- [0:11] "two types of smiley faces" — the signal is a **closed-source paid indicator**; its logic is never disclosed, so the entry cannot be reproduced or backtested independently. This alone caps testability.
- [0:16]-[0:26] The result string (+2% seven times, −1% once) is narrated over a chart with no dates, no instrument, no trade list; a 7/8 win rate at 1:2 R is an extraordinary claim with zero supporting detail.
- [0:26]-[0:33] "if you wanted a swing trade, this one would have gotten you a 1 to 29" — cherry-picked single outcome, no rule for when to convert a scalp into a swing.
- [0:33] onward — pure offer copy (7 other indicators, MetaTrader risk calculator, Discord, "earn as you learn", Black Friday 50% off £220→£110). No trading content.
- "two ticks above the candle" — "tick" is instrument-dependent and the instrument is never named, so the stop distance is not actually determined.
- No session, no news filter, no trend filter, no maximum trades per day.

## Testability
- rating: LOW (the entry is entirely a paid black-box signal with no disclosed parameters, on an unnamed instrument; only the stop convention and R multiple are concrete, and both are meaningless without the signal)
- overlap: proprietary-signal / candlestick-pattern entry (Happy Trail); same family as rBwdxv8CLQw, x1-InyOycus, wNb67k26x1k and the tail of trx_M2Bss-c — but this is the *bare* version with no structure, session or divergence confluence, and is best treated as an advertisement rather than a strategy video
- notable quotes:
  - [0:06] "The strategy is super simple. There are two types of smiley faces, right side up and upside down."
  - [0:11] "You get on a 30-minute chart. Once it prints, you enter your trade. Stop loss two ticks above the candle with a 1:2 risk-to-reward ratio."
  - [0:33] "Yes, it's a paid indicator, but it is absolutely phenomenal."
