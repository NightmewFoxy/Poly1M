# Day Trading Strategy Wars - Which one is best?
- id: HNvw6Ut3BWY | views: 49000 | length: 560s
- market(s) shown: mentioned in backtest-sheet examples only — **NAS 100, GBPUSD, NZDCAD, JP225**; "all the different major currency pairs as well as indices and cryptocurrencies" [6:40–6:48]
- timeframe(s) taught: multi-timeframe **Confluence pairs** for the Happy Trail indicator: **5m chart / 15m HTF**, **1m / 5m**, **1m / 45m HTF**, and a 15m example — see below

## Mechanical rules (only what the video actually states)
This is primarily a **promo for "Strategy Wars season 4"** and a changelog for the revamped **Happy Trail** indicator. The tradeable content is thin but non-zero.

- Indicators + exact settings: **Five proprietary invite-only TradingView indicators**, all closed-source: **DeLorean, StairMaster, Happy Trail, Outback, Brute Force** [1:02–1:07], plus the **three-line strike** indicator which he says is "not a rules-based strategy" [2:18–2:24]. Only configuration steps disclosed for **Happy Trail**: remove the old version from charts, refresh, re-add under **Invite Only**, and **"allow signal repainting"** [4:56–5:05]. New settings expose **four "use cases"** — case 4 = the old behaviour; cases 1–3 are new [5:06–5:15]:
  - **Case 1:** "for seasoned veterans that know price action… this will give you your overall directional bias and allow you to filter out the false signals — and this is 100% reliant on you" [5:15–5:30] (i.e. fully discretionary).
  - **Case 2 (his favourite):** a **higher-timeframe Confluence setting** — change the HTF field from "chart" to e.g. 15m while trading the 5m; the 5m Happy Trail signal must agree with the HTF arrow [5:30–5:49].
- Setup/context required: **Higher-timeframe Confluence must agree with the signal** — "the higher time frame Confluence will be this **green arrow in an uptrend and a red arrow in a downtrend**" [5:49–5:53]. Stated tradeoff: **"the higher your higher time frame Confluence, the less entries you will get but the more directional bias you will get"** [6:17–6:23].
- Entry trigger: **Happy Trail prints a right-side-up smiley face for a bull move and an upside-down smiley face for a bear move** [5:53–5:59]; take every signal that is in confluence with the HTF trend [6:00–6:07]. In the demand-zone example: take the signal each time a demand level is created [8:12–8:23].
- Stop loss: **"stop loss below the swing"** [8:23–8:24] (the only SL statement in the video).
- Take profit: **1 : 1.5 risk-reward**, stated twice — "staying safe and looking for a smaller take profit with a 1 to 1.5 risk to reward ratio" [6:07–6:11] and "stop loss below the swing with a 1 to 1.5" [8:23–8:26].
- Filters he adds: HTF confluence (above). Backtest-sheet-driven selection: he says they tested "thousands of different combinations" and publish **the top 116** pair/timeframe/HTF combos sortable by **risk-to-reward, total percentage gain, maximum drawdown, win rate and standard deviation** [6:23–7:15]. Cited examples: **NZDCAD 1m with 5m confluence — +73% over 224 trades**; **JP225 — 65% win rate, 97 trades, +31R** [7:22–7:34], backtested "all the way back from January".

## Vague / untestable / chart-pointed claims
- **All five strategies are closed-source paid indicators.** Neither the signal logic nor any numeric setting (beyond the HTF field) is ever disclosed — nothing in this video is independently backtestable.
- [4:56–5:05] **"allow signal repainting"** — the indicator is explicitly permitted to repaint. Any backtest or claimed win rate from a repainting signal is unreliable by construction. This is the most important red flag in the video.
- [5:15–5:30] Case 1 is described as "100% reliant on you" — fully discretionary by design.
- [8:08–8:26] The demand-zone example is chart-pointed: "looking at these areas of demand… every time one of these demand levels were created you could have taken these signals" — how a demand level is defined is never stated; "four back-to-back wins right here within four days on a 15 minute time frame."
- [7:34–7:48] "over 10,000 data sets… over 10 million trades backtested" — unverifiable, and undermined by the repainting disclosure above.
- [2:31–2:56] "95% of day traders fail… of the total traders that we had competing in strategy wars, 17% of our traders using our strategies were profitable for this month, that's three times the normal statistic" — a survivorship-prone, self-reported community statistic (note: 17% profitable still means 83% were not).
- [2:56–3:03] "Christy had 100% profitability that month" — same unverified claim as Du81XPkPOHQ.
- No session filter, no timezone, no news filter, no position sizing given anywhere.
- The final third [8:26–end] is pure Strategy Wars season 4 signup promo (launching July 5th, Discord-gated).

## Testability
- rating: LOW (every entry signal comes from a closed-source, explicitly repainting paid indicator; only the SL-below-swing and 1:1.5 R rules are portable)
- overlap: other (proprietary-indicator suite: Happy Trail / StairMaster / DeLorean / Outback / Brute Force / three-line-strike) ; multi-timeframe confluence filter ; three-line-strike (named only)
- notable quotes:
  - [5:30–5:49] "say you're looking at NAS on the five minute chart and you want multi-time frame Confluence — in the settings you can select the higher time frame, instead of being at chart you can change it to the 15 minute; that means that whatever Happy Trail prints on the five minute chart needs to be in Confluence with the higher time frame on the 15 minute"
  - [8:23–8:26] "stop loss below the swing with a 1 to 1.5"
  - [4:59–5:05] "go to your indicators tab, under invite only click Happy Trail and allow signal repainting"
