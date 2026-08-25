# Best Time of Day to Trade
- id: Qplxmh-YYU4 | views: 23000 | length: 255s
- market(s) shown: NAS100 (New York session example), AUDUSD (Tokyo session
  example); GBPJPY and EURJPY mentioned as Tokyo-session candidates
- timeframe(s) taught: 15m mentioned as the backtesting chart, 5m used to view the
  session boxes ([0:25]-[0:27], [2:05]-[2:07])

> NOTE: same title as ot0qFIhXylw but a completely different, much shorter video —
> this one is the actual "how to set your trading window" tutorial.

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - **"FX Market Sessions" indicator** (type it into the TradingView indicator
    box) ([1:04]-[1:12]).
  - Configuration: **untick all sessions except the first one; rename "London
    session" to "mine"; set its start/end to your own available trading hours and
    set the indicator's timezone accordingly** ([1:21]-[1:44]).
- Setup/context required: none — this video contains **no entry logic whatsoever**.
  It is purely about restricting *when* you backtest and trade.
- Entry trigger: none given.
- Stop loss: none given.
- Take profit: none given.
- Filters he adds — three concrete session presets:
  1. **His own London window: 11:00 → 13:00** (a 2-hour window) ([1:57]-[2:03]).
     Rationale: "I don't want to trade the opening session because there's a lot of
     whipsawing back and forth when the Market opens, so ... wait for about **an
     hour or two after the London open** and then get my entry" ([1:47]-[1:57]).
     Timezone of the 11–13 numbers is not stated for this preset; he says elsewhere
     his own zone is GMT+2.
  2. **New York window: set the indicator timezone to GMT−4, session 10:30 → 12:30**
     ([2:26]-[2:38]) — "about an hour after market open and then your Market session
     is going to be about two hours".
  3. **Tokyo / overnight window: roughly midnight → 05:00 in his own GMT+2 zone**
     ([2:57]-[3:10]).
- **Instrument-per-session rule** ([3:12]-[4:07]) — the most transferable rule here:
  - For the Tokyo session trade only currencies from that region: **AUD pairs, NZD
    pairs and JPY pairs** (he names AUDUSD, GBPJPY, EURJPY).
  - **"NAS 100, US-100 they do not move very well during the Tokyo session."**
- Governing principle ([4:07]-[4:14]): "figure out when you're going to be trading,
  put it on the charts, and **only test and only trade during those times**" —
  i.e. backtest statistics gathered outside your live window are worthless.

## Vague / untestable / chart-pointed claims
- [0:25]-[0:51] The whole opening argument ("you'd be backtesting signals firing at
  3am in your timezone") is illustrated on an unnamed 15m chart with an unnamed
  "buy sell indicator" — no indicator named, no stats shown.
- [1:57]-[2:03] The 11:00–13:00 London preset is given **without a timezone**. Given
  he later says "mine's GMT plus two" ([3:01]-[3:03]) and that this is "an hour or
  two after the London open", 11:00–13:00 GMT+2 = 09:00–11:00 UTC is the plausible
  reading, but it is never stated. **This conflicts with a-AuUHbTx-M**, which
  prescribes 11:00–14:00 *New York* time — the same clock numbers, a different zone.
- [2:20]-[2:24] "if you're scalping it's enough to make profit" (about London's
  smaller moves) — no pip threshold given.
- [2:38]-[2:48] "as you can see here you have much more movement during the New York
  session, for example on NAS it went from 15080 up to 15161 which is an 80 Point
  movement" — a single-day, single-instrument anecdote used as the evidence for
  preferring New York.
- [3:10]-[3:14] "there's some pretty decent movement on this" (AUDUSD overnight) —
  chart-pointed, no measurement.

## Notes on relation to other videos
- Companion to **a-AuUHbTx-M** ("STOP wasting your TIME"), which gives the harder
  rule of 11:00–14:00 New York (UTC−4) and to avoid the first 60–90 minutes of the
  NY open. Both agree on the principle "skip the market open's whipsaw, trade a
  2–3 hour window", but the specific clock windows differ (11–13 London-ish here vs
  10:30–12:30 GMT−4 here vs 11:00–14:00 UTC−4 there).
- Unlike a-AuUHbTx-M, this video explicitly accommodates traders who can **only**
  trade Tokyo hours, and gives the AUD/NZD/JPY instrument substitution.

## Testability
- rating: LOW as a strategy (no entry, stop or target at all); the individual
  session windows and the Tokyo instrument-selection rule are mechanical and
  directly usable as filters on top of another strategy
- overlap: session-filter (pure), plus an instrument-selection-by-session rule
- notable quotes:
  - [1:47]-[2:03] "I don't want to trade the opening session because there's a lot
    of whipsawing back and forth when the Market opens ... wait for about an hour or
    two after the London open ... adjust this first one to a 11AM and the second one
    to 1 pm so 11 to 1 that gives me a two hour trading window"
  - [2:26]-[2:38] "change the time zone to gmt-4 which is New York and you're going
    to change that to about 10 30 to 12 30, so an hour after market open"
  - [3:57]-[4:07] "Nas 100 us-100 they do not move very well during the Tokyo
    session this is why it's important to figure out when you're going to be
    trading put it on the charts and only test and only trade during those times"
