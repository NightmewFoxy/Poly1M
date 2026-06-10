# Bot history analysis & the only guaranteed-profit path (2026-06-10)

Full lifetime reconstruction from on-chain data (data-api `/trades`, `/activity`,
`/positions` for proxy `0x832D...64ac`): 78 trades, 70 redemptions.

## Lifetime P&L by strategy

| Strategy                  | Trades | Staked | P&L     | Record |
|---------------------------|--------|--------|---------|--------|
| Esports research bot      | 31     | $310   | -$69.47 | 10W / 18L / 3 flat |
| BTC 5-min sniper          | 29     | $150   | -$25.00 | 16W / 12L |
| Dead-market bug ($0.001)  | 4      | $40    | -$40.00 | 0W / 4L |
| Manual bets               | 2      | $101   | +$22.59 | 1W / 1 flat |
| **Bots combined**         | **64** | **$500** | **-$134.47** | |

## Why the esports strategy loses (and no parameter fixes it)

Win rate vs. price paid — a bettor with real edge wins *more* often than the
entry price implies. This bot wins *less*:

| Entry price | n | Win rate | Market-implied | P&L |
|------------|---|----------|----------------|------|
| 0.10-0.30  | 7 | 0%       | ~24%           | -$60.38 |
| 0.30-0.50  | 11| 45%      | ~39%           | +$20.45 |
| 0.50-0.70  | 13| 38%      | ~58%           | -$29.53 |

- Claude's `true_prob` estimates carry no information the market lacks. Esports
  odds on Polymarket mirror bookmaker lines set by sharps; 30 minutes of web
  search does not out-model them.
- The bot is a pure taker: it pays the spread on entry and 2% fee on wins.
  Zero-edge picks + costs = guaranteed negative expectancy.
- The cheap-underdog bets (<$0.30) went 0/7. Classic longshot bias.
- The last 12 open positions resolved 0/12. The MIN_GAP_PP=3 filter did not help
  (trades after it shipped went 0/7).

Conclusion: **there is no configuration of "predict and bet" that guarantees
profit.** Tweaking gap thresholds, price bands, or rotation changes the noise,
not the sign.

## What actually guarantees profit: arbitrage

Verified live on 2026-06-10 by scanning real order books (`arb_scanner.py`):

1. **Binary merge arb** — `ask(YES) + ask(NO) < $1.00`. Buy both, call CTF
   `mergePositions`, receive $1.00 USDC instantly. Found 6 live (edges
   1-3c/set, e.g. a tennis match at 0.970, BTC dailies at 0.990). Profit is
   locked the moment both legs fill — no resolution wait, no outcome risk.

2. **Neg-risk convert arb** — in a winner-take-all event, at most one outcome
   resolves YES, so a full NO set always pays >= N-1; NegRiskAdapter
   `convertPositions` redeems the set into N-1 USDC immediately. Found live:
   "How many Fed rate cuts in 2026?" +0.6c/set x 548 sets depth, "IEM Cologne
   Major 2026 Winner" +1.2c/set.

3. **NOT an arb (avoid):** buying all YES when the sum < $1. Checked: these
   events have no "Other" catch-all (Presidential 2028 = 36 named candidates
   only), so an unlisted winner zeroes the whole basket. That discount is
   risk premium, not free money.

### Reality check on scale

Edges are 0.1-3 cents per $1 set and depth-limited — single hits pay cents to
a few dollars. They recur constantly (the binary arbs seen at 17:10 were gone
by 17:32), so this is a volume game: scan fast, execute both legs FOK, merge,
repeat. It is the only strategy whose *worst case* is breakeven-minus-gas
rather than -100%.

Run it: `python arb_scanner.py --loop 60`
