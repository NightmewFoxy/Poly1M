# 15-Min ORB Strategy: Why Most Traders Lose (And How to Fix It)
- id: jlShztsY3oA | views: 419000 | length: 297s
- market(s) shown: XAUUSD (gold) — the walk-forward example; NAS100 and S&P 500 named as the assets the strategy is usually taught on
- timeframe(s) taught: 15-minute opening range; 15m or 1h used as the higher-timeframe bias filter

## Mechanical rules (only what the video actually states)
This video presents the standard 15m ORB, **shows it losing**, then adds discretionary fixes.

**The baseline ORB he tests (fully mechanical):**
- Indicators + exact settings: none — just the opening-range box.
- Setup/context required: Mark the high and the low of the **first 15-minute candle after the New York open, 9:30–9:45 Eastern Standard Time** ([0:31]). Draw a range across that candle.
- Entry trigger: **a candle must break out of the range AND close outside it** — "if a candle breaks out of this range and closes above this range, you go long. If it closes below, you go short" ([1:34]).
- Stop loss: the opposite side of the opening range — "you put your stop loss below the range" ([1:38]).
- Take profit: **1:1.5 risk-to-reward** ("I'm being very conservative here using a 1:1.5 risk-to-reward ratio", [1:33]).
- Filters he adds (baseline): one trade per morning; taught for high-volatility assets (NAS100, S&P 500, gold).

**Stated result of that baseline:** over the last 8 trading days on gold — **2 wins, 5 losses, 1 undecided; +4.5% gross profit vs 5% losses = −0.5% over 8 days** ([1:52]–[2:13]).

**The three "fixes" he proposes (not mechanically specified):**
1. Only trade ORB **in the direction of the higher-timeframe trend — "like the 15 minute or the 1 hour bias"** ([2:48]).
2. **Watch for fakeouts and trade the re-entry back inside the range** ([2:53]) instead of the initial breakout.
3. Add confirmation: **structure breaks, liquidity sweeps, or indicators** ([2:59]); specifically named — a trend line, plus **Fibonacci retracement levels** ([3:08]), on the logic that after a large move price pulls back to a fib level and rejects off it.

## Vague / untestable / chart-pointed claims
- [2:48] "only trade orb in the direction of the higher time frame trend like the 15minute or the 1 hour bias" — no rule for how the bias is determined (no MA, no structure definition, no lookback).
- [2:53] "watch for fakeouts and then trade the re-entry back inside the range" — no definition of a fakeout (no time limit, no close-back-inside rule, no entry/stop for the re-entry trade).
- [2:59] "add confirmation structure breaks, liquidity sweeps, or even tools and indicators" — a list of concepts, not conditions.
- [3:08] "drawing out a trend line and using tools like Fibonacci is going to keep you out of these useless trades… price is likely to pull back to a Fibonacci retracement level and also reject off of that" — no fib levels are named in this video, and the trend line is hand-drawn.
- [3:23]–[3:48] "which is why after we had the rejection, we had a winning trade using the Orb strategy… on this example we've broken the downtrend to the upside but the orb strategy is telling us to go short. We would know using extra confluences that that was not a good option" — chart-pointed post-hoc filtering of the losing trades; the filter is applied visually, after the outcome is visible.
- [1:52]–[2:13] The 8-day gold sample is stated verbally only (2W/5L/1 TBD, −0.5%) — the trades themselves are on the unseen chart, and n=8 days is far too small to be a result.
- [4:02] "learn about the key Fibonacci zones that price likes to retrace to based on supply and demand of that asset in that time frame" — asserts the fib zone is asset- and timeframe-dependent but gives no values.

## Testability
- rating: MEDIUM — the *baseline* ORB is fully mechanical and directly backtestable (9:30–9:45 EST range, close-outside entry, opposite-side stop, 1:1.5 RR); every proposed *fix* is discretionary
- overlap: session-filter (NY open 9:30–9:45 EST), breakout/ORB, market-structure/BOS, fib-scalp (as add-on), liquidity-sweep
- notable quotes:
  - [0:31] "Mark the high and the low of the first 15-minute candle after the New York open from 9:30 to 9:45 Eastern Standard Time. If the price breaks above, go long. If the price breaks below, go short."
  - [1:52] "of the last eight trading days on gold, you had two wins and five losses… we have 4.5% profits, but 5% losses, which means we're down half a percent in eight days."
  - [2:28] "Orb has no context, no trend, no structure, and no liquidity… If you enter a trade because price broke the box, you're basically trading blind."
