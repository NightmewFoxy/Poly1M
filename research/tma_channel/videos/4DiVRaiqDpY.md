# 15 Min Scalping Strategy Final
- id: 4DiVRaiqDpY | views: 130000 | length: 479s
- market(s) shown: NAS100 ("Nas"), US30 (backtest sheets for both); live walkthrough on NAS 100
- timeframe(s) taught: 15m (single timeframe — entry and context both 15m)

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: **StairMaster** (proprietary invite-only TradingView indicator from "the trading floor" / TTF) + a **"consolidation zones" indicator** (also proprietary) + **"Simple Sessions by TTF"** sessions indicator. No open-source settings given — he says "click this link… you will have the StairMaster indicator with the correct settings on there" [3:37–3:54]. Only tweaks stated: in Simple Sessions settings, **remove the Tokyo session** (leaving London / mixed / New York) [4:10–4:15]; in StairMaster settings, **change symbol size to small** (cosmetic only) [4:28–4:36].
- Setup/context required: A **consolidation zone** must be present, and the buy/sell "Seeker" signal must print **inside the consolidation zone** [2:22–2:26].
- Entry trigger: "receiving a buy or sell signal inside of the consolidation zone you get a **one candle grace period** for entry — if the next candle after the Seeker doesn't **break and close above or below the consolidation zone** then the setup is invalid" [2:22–2:34]. So: signal candle prints inside zone → the very next candle must close outside the zone in the signal direction → enter.
- Stop loss: "place your stop loss on the **high or low of the zone opposite the trade direction**, meaning the swing high or swing low looking left" [2:45–2:54]. Override: **"if the zone is greater than 120 pips then place your stop loss exactly half the length of it"** [2:54–2:58]. In the live markup he simplifies further: "on big candles what I've done is literally just put my stop loss **halfway through that candle**" [4:50–4:54].
- Take profit: Fixed **risk:reward 1:1.5** for the walkthrough ("on this it's strictly 1 to 1.5") [1:38–1:41]; backtest sheets also exist for **1:2 R** on NAS and US30 [1:55–1:59]. No trailing, no partials mentioned.
- Filters he adds: **Session filter — "I'm only trading from London open to New York close, this is the only time that I'm taking these signals"** [5:01–5:06]. Timezone for those session boundaries is never stated; the sessions indicator defines them. Tokyo session excluded. Soft discretionary filter mentioned but explicitly NOT applied in this video: "just because you're getting a buy signal on a clear downtrend doesn't mean you should be taking all of them" [3:18–3:23] — he says "I'm not going to do that for you guys in this video."

## Vague / untestable / chart-pointed claims
- [1:07–1:15] The whole rule set is gated behind a paid indicator (StairMaster, £20 GBP/month) — the **signal generation logic is never disclosed**, so the strategy is not independently reproducible. This is the single biggest blocker.
- [2:22] "consolidation zone" is defined only by the proprietary "consolidation zones live indicator" [3:09–3:13] — no algorithm for drawing the zone is given.
- [2:54–3:05] The 120-pip override: "if you are experienced you can play around with this rule because there are definitely outliers if you don't understand market structure" — discretionary escape hatch on the SL rule.
- [4:50–4:56] "on big candles… stop loss halfway through that candle" — "big" is undefined; this appears to substitute for the zone-based SL rule without stating when.
- [4:39–6:06] The entire 14-day tally (Aug 14–28) is chart-pointed: "we have a losing trade right here… winning trade here…" with no visible entry prices, times, or trade log. Unverifiable from audio.
- [6:07–6:22] Result claim: **8 losses, 20 wins over Aug 14–28** = "minus eight percent and… plus thirty percent" = "22% profit on the account minus fees and commissions and spreads." Implies fixed **1% risk per trade** but that is never stated as a rule, only inferred from the arithmetic (8 losses = -8%, 20 wins × 1.5 = +30%).
- [6:38–7:40] Rest of video is funded-account / prop-firm profit extrapolation and a membership pitch — no trading content.

## Testability
- rating: LOW (rules are crisply stated but the entry signal comes from a closed-source paid indicator; without StairMaster's logic nothing can be backtested)
- overlap: other (proprietary-indicator strategy) + session-filter + market-structure/BOS (consolidation-zone break-and-close) ; StairMaster family also appears in HNvw6Ut3BWY and Du81XPkPOHQ
- notable quotes:
  - [2:22–2:34] "receiving a buy or sell signal inside of the consolidation zone you get a one candle grace period for entry; if the next candle after the Seeker doesn't break and close above or below the consolidation zone then the setup is invalid"
  - [2:45–2:58] "place your stop loss on the high or low of the zone opposite the trade direction… if the zone is greater than 120 pips then place your stop loss exactly half the length of it"
  - [5:01–5:06] "I'm only trading from London open to New York close, this is the only time that I'm taking these signals"
