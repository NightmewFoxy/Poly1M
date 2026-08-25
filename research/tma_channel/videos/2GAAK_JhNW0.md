# 1 Minute Fibonacci Scalping Strategy Backtested 100 TIMES
- id: 2GAAK_JhNW0 | views: 364000 | length: 615s
- market(s) shown: EURUSD (the 100-trade backtest). Says it generalises to gold, indices, FX pairs, oil [9:00]-[9:06].
- timeframe(s) taught: title says 1-minute; the transcript itself never names the chart timeframe used in the walkthrough or backtest — treat "1m" as title-only, unconfirmed in the audio.

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **Fibonacci retracement tool only.** Exact TradingView config given [3:50]-[4:33]:
  - Six levels enabled: **0, 0.5, 1, 0.618, -0.5, -1**. Everything else turned off.
  - No trend line, no "extend lines left", background removed.
  - Levels/text displayed as **values**, positioned **right**.
  - The 0.5-0.618 zone recoloured **orange** (the "golden pocket" / "gold zone").
  - Tool location: left toolbar, third icon down -> first option is fib retracement; star it into favourites.
- Setup/context required (his own on-screen checklist, [1:04]-[1:43]):
  1. Identify the impulse move: **swing low -> swing high in an uptrend, swing high -> swing low in a downtrend**.
  2. **Confirm the break of structure** — and specifically, structure is only broken with a **candle CLOSE** beyond it ("this right here did not break the previous structure, there was no candle closure below it") [3:24]-[3:30].
  3. Include the **wicks** in the high/low points when reading market structure [3:16]-[3:21].
  4. Draw the fib from the start of the impulse move to the end of it.
  5. Wait for a **heavy retracement** into the 0.5-0.618 zone.
  6. Trend definition given for uptrend: higher highs and higher lows (downtrend: lower highs and lower lows) [6:00]-[6:06], [7:14]-[7:22].
- Entry trigger: two options, both stated —
  - **Preferred: a limit order resting at the 0.618** [1:36]-[1:43], [4:33]-[4:38]. "The best trades are going to be at the 0.618, because if you set it at the 0.5 you will get a worse risk-to-reward closer to a one to one" [5:49]-[5:58].
  - Or a discretionary trigger inside the zone: candle patterns, continuation wicks, engulfing setups [1:33]-[1:36].
- Stop loss: **just beyond the 1.0 fib level** — "a stop-loss just above the one" for shorts [4:38]-[4:40]; "a stop loss below the one level" for longs [5:45]-[5:47]. I.e. just beyond the origin of the impulse move.
- Take profit: **the previous structure point / previous high (or low)** — the swing that the impulse broke [4:40]-[4:43], [6:17]-[6:26]. Explicitly the "safest" target, chosen over letting it run: "if you want to be safe and consistent, this is the one you should be targeting."
  - Stated resulting R: **1:1.6** [4:43]-[4:47]; restated as **1:1.5 to 1:1.6** across the backtest [8:16]-[8:25].
  - The -0.5 and -1 fib extension levels are enabled in his settings but no rule for using them is given.
- Filters he adds:
  - **Session filter (hard rule): only trade Fibonacci during high-volume sessions — London open to New York close. "Anything outside of that, you're gambling, not trading"** [2:34]-[2:46]. No clock times or timezone are ever given, only session names.
  - **Never draw fibs in a choppy range** — "you need a clear impulse, a structure break, and an obvious trend; if you don't see it, skip the trade" [1:43]-[1:58]. Called the golden rule.
  - **Avoid high-impact news** — spikes ignore levels; he identifies news by a ~100-pip / "monstrous" candle [2:14]-[2:25], [5:03]-[5:20].
  - **Avoid low-volume times** — fakeouts are common outside London/NY [2:25]-[2:34].
- Backtest claim: 100 trades on EURUSD over the past week, London open to New York close [6:26]-[6:38]. He states most trades retraced to the 0.5 or 0.618 and that with 1:1.5-1:1.6 R "you're having substantially more wins than you are losses" — **no win rate, no net P&L, no drawdown, no per-trade table is ever given** [8:10]-[8:44].

## Vague / untestable / chart-pointed claims
- [1:28]-[1:33] / [3:35]-[3:41] "wait for price to pull back... you want a HEAVY retracement" — "heavy" is undefined; it is unclear whether this is a separate condition from simply reaching the 0.5-0.618 zone.
- [1:33]-[1:36] "look for entry triggers, candle patterns, continuation wicks, engulfing setups" — a list of names with no definitions; wholly discretionary alternative to the limit order.
- [1:50]-[1:58] "you need a clear impulse, a structure break, and an obvious trend" — "clear" and "obvious" unquantified; no impulse-size threshold (no ATR, no pip minimum, no candle count).
- [2:37]-[2:43] "London open to New York close" — no times, no timezone anywhere in the video. Needs external definition to code.
- [2:14]-[2:25] "you'll see this occasionally with a 100 pip candle" — the only quasi-numeric news filter, and it is retrospective (identify news AFTER the candle prints) rather than a calendar filter.
- [6:38]-[8:44] The 100-trade backtest is narrated over a chart ("as you can see, every single one of these trades") with **zero reported statistics** — no win rate, no expectancy, no losing streak, no equity curve. The video's headline claim is entirely un-auditable from the transcript.
- [8:33]-[8:46] "on some of these days we've had multiple trade entries, some were losers and some were winners, but overall we tend to end the day profitably. If not the day, then overall the week" — hedged, unquantified.
- [7:22]-[7:27] "these trends follow trend lines religiously" — assertion.
- [5:38]-[5:51] In the uptrend example he notes "you would have missed your entry here" — the limit at 0.618 not filling is acknowledged but no rule is given for what to do (chase? skip? move to 0.5?).
- Title says "1 Minute" but no timeframe is stated in the audio at any point.

## Testability
- rating: HIGH (fib levels, exact tool settings, close-based BOS confirmation, limit entry at 0.618, stop beyond 1.0, target = prior structure, stated R — the only real gaps are "obvious trend"/"heavy retracement" and the session times lacking a timezone)
- overlap: fib-scalp (golden pocket 0.5-0.618) + market-structure/BOS + session-filter; the flagship mechanical strategy of the channel
- notable quotes:
  - [1:36] "set a limit order at that 618 level... a stop-loss just above the one and a take profit at the previous structure. That will give you a 1:1.6 risk-to-reward ratio"
  - [1:43] "here is the golden rule: never draw fib setups in a choppy range. You need a clear impulse, a structure break, and an obvious trend. If you don't see it, skip the trade"
  - [2:34] "only trade Fibonacci during the high volume sessions, London open to New York close. Anything outside of that, you're gambling, not trading"
