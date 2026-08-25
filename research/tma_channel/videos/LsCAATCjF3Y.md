# 5 Minute Scalping Strategy (1 Trade Per Day)
- id: LsCAATCjF3Y | views: 28000 | length: 274s
- market(s) shown: unstated (instrument never named; backtest window starts February 29th, [0:57])
- timeframe(s) taught: 5-minute

## Mechanical rules (only what the video actually states)
- Indicators + exact settings (four, listed at [0:14]–[0:55]):
  1. **"TTF SMC toolkit"** by The Trade Floor — free. Provides the **New York open price** (a yellow horizontal line) and the **session boxes**. His settings: "I have it only showing me New York session and London session these are my settings" ([1:34]).
  2. **"Happy Trail"** by The Trade Floor — **paid** (his affiliate link). Used on **default settings** ([2:15] "for this indicator you will use the default settings"). This prints the **smiley-face** buy/sell markers.
  3. **Smoothed moving average (SMMA), length 200, coloured red** — "I like smoothed moving averages it's just my preference ... I have my moving average set to 200 and red" ([0:37]–[0:44]). Optional (he says the first two are "technically all you need" for TradingView free-tier users limited to two indicators).
  4. **ICT New York open midnight line** — "all it does is create a vertical line at midnight in New York time" ([0:51]). Also used to delimit one trading day.
- Setup/context required (long side; short side is the exact mirror):
  - Price **above the New York open price** (the yellow line).
  - Price **above the 200 SMMA**.
  - Time is **during or after the London session**.
  - Short side adds an explicit strictness: "I want the **entire candle** to be below the 200 smooth moving average I don't want it crossing over **I don't like crossovers** whole candle below the moving average" ([1:57]–[2:05]).
- Entry trigger: **A Happy Trail smiley face printing below the candle for a buy, or above the candle for a sell** ([1:14]–[1:21]), with all three context conditions met. Entry on that candle.
- Stop loss: **At the end / far side of the signal candle** — "stop loss at the end of the candle" ([1:41]), "stop loss below the candle" ([2:27]), "stop loss at the top of the candle" for the short ([3:12]).
- Take profit: **Fixed 1:2 risk-to-reward**, stated on every single trade ([1:43], [2:12], [2:29], [3:00], [3:13]). No trailing, no partials, no break-even move (unlike J8_iTzp2ty0 which mandates BE at 1R).
- Filters he adds:
  - **One trade per day maximum** — "each time you see this vertical line it's the next day so we are trading once per day" ([2:48]).
  - **No-trade day** whenever the two location conditions disagree: "price was trading below the New York open and above the 200 smooth moving average so this is a no trading day" ([1:48]); repeated at [3:01].
  - **No signal during London session = no trade** ([2:53]).
  - Risk stated as "**proper risk management 1% and 2%**" ([0:06]) — 1% risked to make 2%.
  - Explicit discipline rule: "because we are sticking to strict rules we are not having any other thoughts besides these rules" ([2:38]).

## His stated backtest result (as claimed, not verified)
- Window: **last 30 days**, starting Feb 29 ([0:03], [0:57]).
- **16 trades**, over ~20 trading days ("you only didn't trade four days", [4:00]).
- **Win rate 68.75%** (= 11 wins / 5 losses), **+18.24%** return ([3:44]–[3:50]).
- **Profit factor 4.4**, **max drawdown 2%**, max **3 consecutive wins**, max **2 consecutive losses** ([4:02]–[4:08]).
- Dollarised on a $200,000 account as ~$36,480 ([3:51]).

## Vague / untestable / chart-pointed claims
- The entry signal is a **closed-source paid indicator** (Happy Trail smiley faces) — its logic is never disclosed, so the strategy cannot be reproduced or backtested from the transcript. Everything around it is mechanical; the trigger itself is a black box behind an affiliate link ([4:10]–[4:26]).
- [1:12] "it needs to be **during or after** the London session" — "after London" is open-ended; he never says when the tradeable window closes (the NY session? midnight?). At [2:25] he takes an entry "just before the New York session started", which is consistent, but the end boundary is undefined.
- [0:37] The 200 SMMA is called "just my preference" and optional, yet at [1:07] it is a hard entry condition and at [1:57] the whole-candle-below rule depends on it. Contradiction about whether it is required.
- [2:36] "price was trading sideways as you can clearly see this one was a loss" — chart-pointed observation; no ranging filter is actually part of the rules.
- [3:36] "currently on today if a candle closes above this line with a smiley face below it I'm going to take a long position" — implies a **candle-close** requirement above the NY open line that is not in the stated rule list (which says only "you need to be above the New York open price").
- The 30-day / 16-trade sample is far too small for the quoted profit factor of 4.4 and 68.75% win rate to be meaningful; there is no out-of-sample period and the instrument is never named, so it cannot be replicated.
- The 1% risk / 2% reward framing at [0:06] conflates position risk with the 1:2 R multiple; the 18.24% figure only follows if every trade risked a fixed 1%.

## Testability
- rating: MEDIUM — the context filters (above/below NY midnight open price, above/below 200 SMMA with no crossover, London session or later, one trade per day) plus the exits (stop at the signal candle extreme, fixed 1:2 R) are all fully mechanical and numerically pinned. It is not HIGH only because the trigger itself sits inside a paid closed indicator. Strip the smiley face and the remaining shell is directly codeable as a filter set.
- overlap: 5m-scalp(SMMA) — uses the channel's signature **smoothed** moving average (200 SMMA) — plus session-filter (London/NY, ICT midnight open) and an "other" proprietary-indicator trigger. Shares the fixed-R + no-trade-day discipline of HeNqrn_JO8k and the paid-indicator format of J8_iTzp2ty0.
- notable quotes:
  - [0:59] "the rules for entry for a buy position you need to be above the New York open price ... you need to be above the 200 smooth moving average and it needs to be during or after the London session and all you're waiting for is a smiley face to print below the candle for a buy position or above the candle for a sell position"
  - [1:57] "I want the entire candle to be below the 200 smooth moving average I don't want it crossing over I don't like crossovers"
  - [3:14] "this goes on and on and on one trade per day some days are no trading days because your requirements are not met because you should be systematic with your trading"
