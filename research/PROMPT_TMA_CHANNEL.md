# Prompt: mine The Moving Average channel for a tradeable strategy

Analyse the entire YouTube channel https://www.youtube.com/@TheMovingAverage
("The Moving Average", host Arty, day-trading content) and produce the best
possible tradeable strategy from it, backtested honestly on crypto.

## Context from prior research (this repo, STRATEGY_FINDINGS.md + git log)

Two of this channel's videos have already been tested — read the findings
before re-testing anything:

1. **trx_M2Bss-c** (RSI *hidden*-divergence, 1h): backtested on crypto 1h —
   no edge. Logged 2026-08-21.
2. **K7vFNn7fZ7Y** (RSI *regular*-divergence + confluence stack, 15m):
   backtested on BTC (`backtest_regdiv15m.py`). Naive divergence loses.
   With his confluences (RSI across the 50 line, break of structure, close
   beyond SMMA21) the edge is real: the best config found is **30m, TP 2R,
   maker limit entry 10bp beyond signal close, SL at divergence extreme, no
   breakeven-move** — net of Binance futures fees: BTC +0.55%/trade
   (+107%/2y, t=2.3), ETH out-of-sample +1.19%/trade (t=3.3), positive both
   years on both, but decaying ~50%/yr and SOL firmly negative. A paper
   bot (`paper_regdiv.py`) is live on this config: BTC+ETH 30m, 100 USDT,
   1x, Telegram alerts. 20x leverage was simulated: guaranteed liquidation
   (worst trades -4.8%/-8.9% at 1x). Fixed-risk sizing beats fixed leverage.

Key methodology lessons already paid for — do not relearn:
- Fractal pivots (3 bars each side), signal only PIVOT_LR bars after the
  pivot forms — NO lookahead.
- Always report gross AND net of realistic fees (spot taker 0.075%/side kills
  ~0.1%-gross edges; futures maker 0.018% / taker 0.045% is the cheap path).
- Maker fills must be simulated with fill risk (limit fills only when a later
  bar trades through it), not just a lower fee.
- Robustness gates before believing anything: long/short split, year-by-year
  split, parameter sensitivity, neighbouring timeframes, and a second asset
  as out-of-sample. A spike on one timeframe with negative neighbours is
  suspect. Breakeven-stop "risk-free" tricks destroyed every config tested.

## Task

1. Enumerate every video on the channel (yt-dlp can list the uploads
   playlist). For EACH video, use **/watch** to get the transcript
   (`--detail transcript` first — cheap). When the captions are unclear,
   ambiguous, or the presenter says "look here / as you can see" about
   something on-chart, re-run /watch on that section with frames
   (`--start/--end`, or `--timestamps` for the flagged moments, `--detail
   balanced`) and read the frames — watch it frame by frame until the rule
   is unambiguous. Do not guess a rule the video didn't state.
2. For each video, write down the strategy/technique taught as EXACT
   mechanical rules (indicator, settings, entry trigger, SL, TP, timeframe),
   plus which claims are vague/untestable. Keep a per-video log file.
3. Synthesize: the channel's ideas overlap (divergences, market structure,
   moving averages, three-line strike, confluence stacking). Build candidate
   strategies from the UNION of his techniques — including combinations he
   implies but never fully specifies — and backtest them on BTC (build/tune)
   with ETH held out as out-of-sample, 30m/15m first (that's where his edge
   lived), 2 years of Binance data (data-api.binance.vision, pattern in
   `backtest_regdiv15m.py`).
4. Apply the full robustness gauntlet above to anything that looks positive.
   Charge futures fees with honest maker-fill simulation.
5. Deliverable: append findings to STRATEGY_FINDINGS.md, commit+push each
   cohesive step (repo auto-push convention), and give a final verdict —
   either "best strategy = X with these exact rules and these net numbers"
   or "nothing beats the already-live regdiv 30m config". If something DOES
   beat it, propose (don't launch) a change to the paper bot.

Use Opus subagents for the mechanical per-video transcript extraction and
rule write-ups (one per video or batched); keep synthesis and backtest
design in the main session. Never use a metered LLM API for any of this.
