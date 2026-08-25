# Break and Retest Strategy in Forex Trading
- id: 444IwI9i6JA | views: 193000 | length: 276s
- market(s) shown: AUDUSD ([1:22] "i'm going to show you an example on aud usd")
- timeframe(s) taught: **1 hour** for the S/R example, **1 minute** for the moving-average example; he states the concept "works on any time frame" ([2:56])

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: For the 1m version, three moving averages — **21, 50, 200** ([3:07] "imagine if we put up the 21 to 50 and the 200"). Type not stated in this video (channel default elsewhere: smoothed/SMMA). For the 1h version, **hand-drawn horizontal support/resistance levels**, no indicator.
- Setup/context required: A **level that has been respected** — either a horizontal S/R level formed by prior rejections, or the moving-average band. Directional bias from the MAs: [3:22] "we are trading above the moving averages it's trending up we are trading below the moving averages we are trending down".
- Entry trigger: **Break, then retest, then continuation** — never on the break itself. [2:43] "clear movement below that price and a re-test... that's a comfortable entry for a trade". On the MA version: price breaks through the MA band, consolidates below it, then **comes back up and tests the MAs as resistance**, and that retest is the entry for a short ([3:36]-[4:05]). He explicitly notes a retest may **fail to reach the level exactly** and still count: [2:51] "tried to retest but couldn't get to that level and then continued down".
- Stop loss: **not stated anywhere in this video.**
- Take profit: **not stated anywhere in this video.**
- Filters he adds: Only patience — do not enter the moment the level breaks ([1:52] "most people get in on a trade the second that it breaks and that is a huge mistake"). He also says S/R levels should be treated as **zones, not exact prices**: [2:03]-[2:13] "they're being too literal with their levels of support and resistance you just kind of want a general area of it it doesn't have to be an exact number". On the 1m chart he prefers **moving averages over horizontal levels** ([3:04] "on a one minute it's better to use moving averages").

## Vague / untestable / chart-pointed claims
- [1:26]-[1:33] "i'm gonna put up some levels of support and resistance here we've got a level here we've got a level here and we've got a level here" — levels are drawn by hand with no rule for how they are chosen (touch count, lookback, swing size). Purely chart-pointed.
- [2:03] "you just kind of want a general area of it it doesn't have to be an exact number" — the zone width is explicitly left undefined, which makes both "break" and "retest" untestable without inventing a tolerance.
- [2:43] "clear movement below that price and a re-test" — "clear movement" is unquantified (no minimum break distance, no close-beyond-level requirement, no candle count).
- [2:48]-[2:54] "we broke we retested came down tried to retest but couldn't get to that level and then continued down" — a retest that never reaches the level still counts as a valid retest. With no tolerance given, this makes the condition nearly unfalsifiable.
- [3:36]-[4:05] "we've clearly broken through these moving averages starting to consolidate a little bit and now we're trading below them it's consolidating just a little bit and then it tests this finds a resistance and then continues down" — which of the three MAs must be broken/retested is never specified (the 21? all three? the band?). Chart-pointed.
- [3:56] "and then continues down" — the continuation appears to be part of the entry condition, which would mean entering after the move has already resumed; no trigger candle is defined.
- **No stop loss, no take profit, no risk:reward, no session filter, no pip figures anywhere.** The video is a concept explainer, not a complete system; he defers to two other videos (market structure, moving averages) at [4:12]-[4:19].

## Testability
- rating: LOW — the concept is clear and the entry *shape* is well described, but there is no stop, no target, no level-selection rule, and he explicitly refuses to define the level as a precise price ("just a general area"). Every parameter a backtest needs (break tolerance, retest tolerance, which MA, stop, target) is absent.
- overlap: S/R-retest (the canonical break-and-retest family) and market-structure/BOS; the 1m variant is MA-band break-and-retest, shared with the 5m/1m SMMA scalping family. This is the "confirmation" primitive that appears as one of the six confluences in `K7vFNn7fZ7Y` (RSI Divergence) and as the pre-entry requirement in `R3T1zRyZdMc` (backtesting), so it is best treated as a **filter module** rather than a standalone strategy.
- notable quotes:
  - [2:43] "clear movement below that price and a re-test... that's a comfortable entry for a trade"
  - [2:03] "you just kind of want a general area of it it doesn't have to be an exact number"
  - [3:28] "this is a break and a retest of the moving averages which is the strategy that i like to do every single day"
