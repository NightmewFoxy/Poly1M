# XAUUSD Scalping Strategy
- id: oDOCBTYgCQM | views: 1600000 | length: 593s
- market(s) shown: XAUUSD / gold (GOLDUSD)
- timeframe(s) taught: **5 minute**, explicitly rejecting the 1 minute — "one minute is far too noisy, it creates a lot of false signals and I do not recommend it, but the five minute is nice and quick" [2:30-2:41]

## Mechanical rules (only what the video actually states)
- Indicators + exact settings:
  - Three **smoothed moving averages: 21, 50, 200** [3:14-3:49]
  - **RSI** — used only to check "if the price is below or above the 50 level... not overbought and oversold", and to spot divergences for exits [3:49-4:00]. Length not restated in this video (14 in his other videos).
- Setup/context required:
  - Direction filter: **long only above the 200 SMMA, short only below the 200 SMMA** [3:00-3:20]
  - Hard no-trade filter: "you do not want to trade while moving averages are smashed together like this... if you see them smashed and flat, no touchy" — you must see the three MAs **fanned out at a nice slope** [3:23-3:45]. Restated at the end as an absolute: "we never ever ever ever ever trade gold when the moving averages are touching each other or flat" [8:47-8:55]
  - Preferred sequence: price crosses through the 200, then **comes back up to retest one of the subsequent moving averages** [4:04-4:17]
  - Trade duration cap: **maximum six 5-minute candles — less than an hour** on any gold trade [2:43-2:54]
- Entry trigger: a **three-line strike** at that retest — three consecutive candles in one direction followed by a big opposite engulfing candle that engulfs **at least fifty percent** of the preceding move [4:17-4:36, 6:52-7:04]. Enter at that point ("this is where you would get into your short position"). Worked entry: **1778** on gold [4:36-4:48].
- Stop loss: default rule = **double the size of the engulfing candle** [5:07-5:13, 7:04-7:09]. In the worked trade he tightened it because the 200 SMMA sat just above: entry **1778**, stop **1780** — "that is only a two dollar difference" [4:43-4:56]. Rationale: "this is why it's important to keep your stop losses tight because gold can move quickly and really never ever come back to your entry price" [4:50-5:03].
- Take profit: **no R multiple and no price target** — you exit on an **RSI divergence**, taken at the **close of the divergent candle** [5:21-5:52, 7:09-7:13]. Bearish-trade version: price makes a lower low while the RSI makes a higher low → get out [5:38-5:52, 7:34-7:47]. Worked results: a ~$3 move on the first trade [5:52-6:04] and **1776 → 1769, a $7 move**, on the second [7:44-7:55]. Secondary discretionary exit: get out on consolidation — "we rejected off of that 21 moving average and instead of continuing down we started to go back up; that's consolidation for me and I get out of a trade when I see consolidation" [6:26-6:46].
- Filters he adds: demo-first warning for anyone who has never traded gold [1:03-1:12]; don't force a trade — "don't force the trade unless you actually see like three subsequent candles in one direction and then an engulfing" [9:03-9:16]; write your rules on paper and only enter with all confluences present [9:25-9:30]; never trade counter-trend on gold ("it is physically impossible for you to win") [7:55-8:22]. He also notes he does **not** personally trade gold — this is back-tested, not live [0:20-0:34].

## Vague / untestable / chart-pointed claims
- [3:23-3:45] "moving averages smashed together like this... I want you to visually see these three moving averages fanned out at a nice slope" — the primary no-trade filter is purely visual; no MA-separation or slope threshold in dollars, ATR or percent.
- [4:36-4:43] "we got three nice decent bullish candles" — "nice decent" undefined; only the engulfing candle gets a numeric threshold (≥50%).
- [4:56-5:07] "usually I double the size of this engulfing candle for my stop loss, but because the 200 period moving average is right here I'm just going to leave it at that, maybe just a little bit above" — the stop rule is overridden by discretion in the very first example.
- [5:21-5:52] The exit divergence is picked by eye ("we created this low right here and this one didn't exceed it but this one did"); no swing-detection rule or lookback.
- [6:04-6:18] "if you're waiting for the RSI divergence, I mean technically you still would have gotten out at the same point" — the two exit rules are conflated after the fact.
- [6:26-6:46] "that's consolidation for me and I get out of a trade when I see consolidation" — explicitly personal and undefined.
- [7:13-7:31] "on the RSI [it] was about the 14 level showing a very very oversold market means that the momentum is very strong in that direction" — uses an RSI absolute level as a momentum read, without a stated threshold rule.
- [9:13-9:25] "do not get in on a trade like this — was not a good trade to get in on even though it went up and you would have made money" — the disqualifying feature is chart-pointed only.
- [2:43-2:54] The "maximum six 5-minute candles" cap is stated as a duration rule but never applied to either worked example.

## Testability
- rating: MEDIUM (entry is the most precisely specified three-line strike in the batch — the ≥50% engulf threshold plus the 2x-candle stop — but the exit is an eyeballed RSI divergence with no target, and the "fanned out" filter is visual)
- overlap: three-line-strike + 5m-scalp(SMMA) + regular-divergence (used as exit, not entry)
- notable quotes:
  - [4:17-4:36] "we got three nice decent bullish candles and then a big fat engulfing bearish candle, engulfing at least fifty percent of this move — at this point this is where you would get into your short position"
  - [3:27-3:45] "if you see them smashed and flat, no touchy... I want you to visually see these three moving averages fanned out at a nice slope; these moving averages are smoothed, they are the 21, the 50 and the 200"
  - [8:36-8:47] "we're trading three line strikes for sniper entries with extremely tight stop losses; we're looking for an RSI divergence to exit our trade"
