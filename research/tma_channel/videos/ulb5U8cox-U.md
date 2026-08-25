# The Ultimate 5 Minute Scalping Strategy for Quick and Easy Profits - You Have to Try This!
- id: ulb5U8cox-U | views: 115000 | length: 361s
- market(s) shown: unnamed, but rules are given per asset class — "20 to 30 point range on indices or 10 to 12 pips on FX pairs" [2:48]-[2:54]; he closes by recommending it "on the one minute and five minute on indices" [5:16]. MT4 account shown.
- timeframe(s) taught: **5-minute (primary) and 1-minute (faster-entry variant, "the rules are exactly the same")** [3:45]-[3:50]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings (four, one optional):
  1. **FX Market Sessions by biotoki** (free, optional/visual) — draws dotted session boxes showing "the top and the bottom of the range" [0:33]-[0:46].
  2. **Brute Force version 2** (TTF, paid) — the signal. "**on Brute Force these are default settings, you don't have to adjust any settings, just upload it onto your chart**" [1:36]-[1:41]. Prints a "rocket ship" marker.
  3. **STC indicator by Shayan** [1:22]-[1:28].
  4. **Awesome Oscillator — TradingView built-in** [1:28]-[1:33]. No settings given for either oscillator.
- Setup/context required: **A breakout of the Tokyo session range.** "what you're waiting for is a break out of the Tokyo session" [2:25]. Trade direction is locked to the breakout side: "because we broke out to the downside of the Tokyo session, you are only taking short signals, you are not paying attention to these long ones" [3:57]-[4:06].
- Entry trigger: **at the CLOSE of the candle that prints the Brute Force rocket-ship signal**, in the breakout direction — "wait for this little rocket ship to print, then at the close of the candle enter in a short position" [2:27]-[2:34].
- Stop loss:
  - 5-minute: **not immediately above the signal candle — give it a candle of room, capped by a point/pip budget.** "I want you to not place your stop loss just above the candle but give it some wiggle room and give it to the next candle... you want to stay in that like **20 to 30 point range on indices or 10 to 12 Pips on 4X pairs**" [2:38]-[2:54].
  - 1-minute variant: **above the previous swing** — "I want your stop loss to be above the previous swing" [4:12]-[4:16]; repeated as "stop loss below the swing" for longs in five consecutive day examples [4:36]-[4:54].
- Take profit:
  - Default: **1 : 1.5 risk-to-reward** — "to stay safe and in accordance with all of the back tested results that we have for you guys in a downloadable file, you want to stick to a one to one point five risk to reward ratio" [2:54]-[3:05].
  - Upgrade to **1:2** only with a look-left structural level: "sometimes you can manage to get a one to two, but when you do that you want to look left on the charts to see if there are areas... where you know that price is most likely to go" [3:05]-[3:18].
  - 1-minute: "you can target a one to two much more comfortably than on the five minute, but again if you want to stay safe 1 to 1.5" [4:16]-[4:23].
- Filters he adds — **the four stated confluences** [3:25]-[3:41]:
  1. Breakout of the Tokyo session;
  2. Rocket ship **above** the candle for a short, **below** the candle for a long;
  3. **STC red**;
  4. **Awesome Oscillator red**.
  (Green presumably mirrors for longs but he only says "red" — the video's worked example is a short.)
  - **One trade per day:** "just take one trade, if it doesn't play out wait for the next day" [3:41]-[3:45]; restated up front, "one trade per day" [0:04].
  - Session-activity preference: "when you have specific confluences that you're looking for like activity during the London session or the New York session or the mixed session, the likelihood of it playing out is much higher" [1:11]-[1:20].
  - Alert setup (workflow, not a rule): add alert on Brute Force v2, condition = "any alert", no expiration, app notifications on [1:57]-[2:23].
  - Claimed track record: 5 consecutive days, "four winners and one loser, that's seven percent profit on your account in five days", stated as "not cherry picking" [4:52]-[5:08].

## Vague / untestable / chart-pointed claims
- [1:00]-[1:10] "with the Brute Force indicator it's like a pre-breakout strategy, so it knows when the momentum might be coming" — the **signal is a paid black box**; its logic is never disclosed. Primary testability blocker.
- Tokyo session range is used as the breakout reference but **no session times and no timezone are ever stated** in this video (contrast rBwdxv8CLQw, which does give UTC+1 and 22:00–09:00). It is also unstated whether the breakout needs a candle close outside the range.
- [2:38]-[2:48] The stop rule is internally loose: "give it to the next candle **if it's not like a hundred points or whatever**, you want to stay in that like 20 to 30 point range" — so the stop is "the next candle's extreme, unless that's too far, in which case 20–30 points". No tie-break rule; and a fixed 20–30 point stop with the 1:1.5 target is a materially different system from a structural stop.
- [3:05]-[3:24] "look left on the charts to see if there are areas like right here where you know that price is most likely to go... looking left I can see a hard rejection here, using this as support" — the 1:2 upgrade is entirely discretionary chart reading; "hard rejection" is unquantified.
- [1:11]-[1:20] "activity during the London session or the New York session or the mixed session" — "activity" is never defined (no volume or range threshold).
- [3:25]-[3:41] STC and AO are required to be "red" but **no settings are given for either**, and STC is third-party; AO "red" means a falling histogram bar, which is a convention he never spells out.
- [4:23]-[4:54] The five-day sample is narrated over the chart with no dates or instrument; the "7% in five days" figure implies ~1.75% risk per trade, which is never stated.
- [5:33]-[5:50] Closing stretch is sales copy ("it's going to change your life forever, you're not going to be broke anymore") — no content.

## Testability
- rating: MEDIUM (the confluence checklist, entry-on-candle-close, one-trade-per-day cap, per-asset-class stop budgets and 1:1.5 default R are all explicit and unusually crisp — but the entry signal is a paid black box, the Tokyo session is never time-defined, and the stop has an undefined escape clause)
- overlap: session-filter (Tokyo/Asia range breakout) + proprietary-signal entry + oscillator-confluence (STC, Awesome Oscillator) + S/R-retest (the look-left 1:2 upgrade). Shares the Asia/session-range-breakout skeleton with rBwdxv8CLQw and x1-InyOycus.
- notable quotes:
  - [3:25] "so the confluences that you want: breakout of the Tokyo session, you want the rocket ship above the candle for a short and below the candle for a long, you want the STC to be red and you also want the awesome oscillator to be red"
  - [2:38] "not place your stop loss just above the candle but give it some wiggle room and give it to the next candle... you want to stay in that like 20 to 30 point range on indices or 10 to 12 pips on FX pairs"
  - [2:54] "in accordance with all of the back tested results... you want to stick to a one to one point five risk to reward ratio"
