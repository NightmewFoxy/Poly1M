# 1 Minute Scalping Strategy - Easy and Fast
- id: 1XQKJ_MoFr4 | views: 125000 | length: 367s
- market(s) shown: Forex — "you can trade any forex pair with this" [5:38]-[5:41]; JPY/AUD/NZD pairs specifically for the Asian session
- timeframe(s) taught: 1-minute chart (entries), explicitly

## Mechanical rules (only what the video actually states)
This is a paid-indicator video. He states it up front: "this is not a free strategy, it is using paid indicators which cost 20 pounds a month" [0:26]-[0:33].
- Indicators + exact settings (three, none with disclosed settings):
  1. **"The Outback"** — his team's proprietary TradingView indicator. Prints little kangaroos below candles (buy) or above candles (sell). These ARE the entry signals. No internal settings given.
  2. **ATR bands** — two bands plotted outside price, "the average true range of where the price is capable of going". **These are the stop loss.** ATR length/multiplier NEVER stated [0:54]-[1:07].
  3. A **sessions indicator** to show London / New York / Asian session.
- Setup/context required: a signal must print DURING a live session — "make sure that it's during a live session, you don't want to be entering a trade when markets are basically closed and things are consolidating" [2:17]-[2:28].
- Entry trigger: a kangaroo prints -> **enter on the CLOSE of that candle** [2:25]-[2:28].
- Stop loss: **on the ATR bands** [2:28]-[2:30].
- Take profit: **1 : 1.5 risk-to-reward** — "you risk one percent, you make 1.5" [2:28]-[2:44]. (Risk 1% of account per trade.)
- Filters he adds:
  - **Asian session pair filter (the most concrete rule in the video): when trading the Asian session, only trade pairs that are JPY, AUD or NZD** — "like that side of the planet, they move more" [1:17]-[1:29].
  - All three sessions are tradeable: "you can trade london session, you can trade new york session, you can trade asian session" [5:32]-[5:38].
  - Alert setup (the "mindless" version) [1:47]-[2:12]: hover the indicator -> More -> "Add alert on Outback" -> condition "Outback / Any alert() function call" -> expiration open-ended -> notify on mobile app / pop-up / desktop -> Create. Then trade only when it pings; ~15 minutes of work per day.
- Two explicitly different modes:
  - **Mindless/automated mode** (taught here): take EVERY signal from the alert, no chart reading. He states this has a "substantially lower win rate" [1:29]-[1:47] and calls it "the most mindless easy strategy I've ever seen".
  - **Manual mode** (NOT taught here, deferred to Jay's/Christy's videos): filter signals discretionarily, "not going with every single signal" — higher win rate, better trades [3:15]-[3:52].

## Vague / untestable / chart-pointed claims
- [0:44]-[0:54] The entry signal is a proprietary paid indicator ("The Outback"). Its logic is never disclosed, so the strategy is **not reproducible at all** without a 20 GBP/month subscription. This alone caps testability.
- [0:54]-[1:07] "these two bands outside of the price is the atr bands" — no ATR length, no multiplier, no whether the stop sits on the near or far band. The stop is therefore unspecified.
- [1:29]-[1:38] "you are going to have a substantially lower win rate" — unquantified; no win rate is ever given for either mode.
- [2:17]-[2:25] "make sure that it's during a live session" — no session TIMES and no timezone given anywhere in the video; only session names.
- [4:08]-[4:25] The performance claim — "$4,000 profit, so four percent... in two and a half hours trading this manually across multiple pairs" — is a clip of someone else (Jay) on a $100,000 FTMO DEMO account, single session, no trade count, no losing-session context. Cherry-picked and un-auditable.
- [3:52]-[4:08] Backtested results are said to exist but only behind the paywall ("back tested results for all of those strategies") — none shown in this video.
- No definition of trend, structure, S/R or any context filter — the mindless mode deliberately has none.

## Testability
- rating: LOW (entry trigger is a closed-source paid indicator and the ATR stop has no stated length or multiplier; only the 1:1.5 R, 1% risk, enter-on-close and the Asian-session pair filter are reproducible)
- overlap: 1m-scalp via proprietary signal indicator + session-filter (Asian-session JPY/AUD/NZD restriction); ATR-band stop
- notable quotes:
  - [0:26] "this is not a free strategy, it is using paid indicators which cost 20 pounds a month"
  - [1:17] "when you are trading asian session you only want to trade pairs that are either jpy or aud or nzd... they move more"
  - [2:25] "you enter on close, stop loss on the atr bands, 1 to 1.5 risk to reward ratio"
