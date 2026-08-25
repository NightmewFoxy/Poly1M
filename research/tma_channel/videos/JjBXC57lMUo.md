# Fibonacci Trading Strategy
- id: JjBXC57lMUo | views: 313000 | length: 747s
- market(s) shown: AUDUSD (5m), BTCUSD (1h and daily)
- timeframe(s) taught: 5m chart for forex intraday (positions held 12-17h); 1h/daily for crypto "buy the dip"

## Mechanical rules (only what the video actually states)
- Indicators + exact settings: three **smoothed** moving averages — 21, 50, 200 SMMA (stated "the 21 50 and 200 smoothed moving averages", [1:30]); RSI with a single line drawn at the **50** level (he references his separate RSI video). Fib retracement tool configured with **10 levels: 0, 0.382, 0.5, 0.618, 0.764, 0.88 "and so on"** ([3:05]-[3:23]) — the remaining levels are only shown on screen, not spoken.
- Setup/context required: one "big fat" **non-stop directional move** (an impulse leg in one direction with no meaningful counter-move), followed by the price stalling/consolidating and beginning to retrace ([4:03]-[4:48]). Explicitly *not* a scalping strategy — intraday, position usually closed by end of trading day.
- Entry trigger: **on forex only, a 50% retracement of the impulse leg** ([5:14] "on forex only with forex you're looking for a 50 level retracement"). Draw fib from the extreme of the move (top→bottom for a short, bottom→top for a long); precision not required ("it does not have to be precise... bodies or the wicks", [4:54]). Refinement given at [6:31]-[7:05]: do **not** enter as price is travelling toward the 50; **place a resting limit order at the 50 in advance** so that if price pushes past the 50 (e.g. up to 0.618/0.764) and then comes back through it, the order executes on the way through.
- Stop loss: **the 0.764 fib level** ([5:51] and again [7:26] "if you're getting it at the 50 your stop loss is the 764"). Explicitly conditioned on entering at the 50 level.
- Take profit: **"take profit 1"** = the origin of the impulse leg, i.e. the low the move came from (for a short) / the high it came from (for a long) — "you're going to place your take profit at the low point that it was at and you walk away" ([6:06]). He says his fib template has TP1/TP2/TP3 but instructs using **only TP1** because "it is the easiest to get every single time" ([5:42]).
- Filters he adds: For **crypto**, use a higher timeframe (1h/daily) rather than intraday, and treat it as a long-term "buy the dip" position strategy, not intraday ([10:52]-[11:03]). Warning at [6:37]: a 50-level retracement on your timeframe may itself be a retracement on a higher timeframe — hence the "wait for it to pass the 50 and come back" entry mechanic.

## Vague / untestable / chart-pointed claims
- [3:05]-[3:23] "change your settings to what i have here the colors the numbers everything... 10 fibonacci levels the 0 the 0.382 0.5 0.618 0.764 0.88 and so on and so forth" — the full 10-level set is only fully visible on screen; four levels beyond 0.88 are never spoken. Needs a frame check.
- [4:03]-[4:22] "one big fat movement... this is a non-stop movement yes there was a little bit of shakiness but it literally in one direction non-stop" — no numeric definition of impulse size, candle count, or how much "shakiness" is tolerated. Fully discretionary leg selection.
- [4:52]-[5:04] "you take your tool from the top to the bottom it does not have to be precise... we're going to drag that out a little bit" — anchoring is explicitly imprecise; a backtest must pick a deterministic swing-detection rule he never gives.
- [4:46] "once you've seen one of these huge bear runs right here and then it starts consolidating" — "consolidating" is chart-pointed, undefined.
- [5:56]/[7:44] "56 pips... in 17 hours", "57 pips" in "12 hours" — cited results from two hand-picked chart examples, no sample.
- [8:07]-[8:15] "these are about one to two risk to reward ratio trades so for every time you win you can afford to lose twice and still be break even" — the stated R (SL at 0.764, entry at 0.50, TP at fib 0) is actually ~1:1.9 by construction, but he asserts the ratio rather than deriving it per-trade; also his break-even math is wrong (1:2 R needs a >33% win rate, not "lose twice per win to break even" — that IS break-even, so the claim is trivially restated, not a filter).
- [9:19]-[10:41] The BTC daily/1h examples: "we got a 50 level retracement right here... a 618 level retracement right here... this one stopped out" — for crypto he accepts BOTH the 0.5 and the 0.618 as entries, contradicting the forex-only 0.5 rule, but never states which to use in advance. Chart-pointed.
- [10:45] "out of all of these you would have gotten stopped out once on every single buy the dip" — unverifiable claim over an unspecified sample.
- The RSI is loaded on the chart at [1:36] but is **never used in a single rule** in this video.

## Testability
- rating: MEDIUM — entry (0.50 fib), stop (0.764 fib) and target (fib 0 / origin of leg) are exact and fully numeric; the single discretionary gap is impulse-leg identification (what counts as "one big fat non-stop movement" and where to anchor the fib), plus the ambiguous "place the order in advance and let price pass through the 50" execution nuance.
- overlap: fib-scalp (fib-retracement family); 5m-scalp(SMMA) chart template shared (21/50/200 SMMA + RSI-50), though the MAs/RSI are decorative here. Explicitly framed as an **upgrade/replacement** of an earlier fibonacci retracement video ([0:44]-[0:52], "i'm going to make a new upgraded fibonacci retracement video"), and he twice defers detail to that older video ([7:31], [2:38] region) — so this file may not be the complete ruleset.
- notable quotes:
  - [5:14] "on forex only with forex you're looking for a 50 level retracement"
  - [5:48] "you place your short position right here stop loss to the 764 and targeting take profit one"
  - [7:02] "you should have an order placed in advance if it goes past that price and then comes down that's when your order should execute as it's passing through it"
