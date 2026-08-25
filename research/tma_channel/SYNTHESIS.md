# TMA channel synthesis + backtest results (2026-08-26)

Full-channel mining of https://www.youtube.com/@TheMovingAverage (407 videos
enumerated, 166 strategy-relevant transcribed and rule-extracted by Opus
subagents — see `videos/`, `TRIAGE.md`, `EXTRACTION_SPEC.md`). Every
mechanically-specifiable technique family was translated to crypto and
backtested on 2y Binance data (BTC = build, ETH = out-of-sample, SOL = third
asset), Binance USDT-perp fees (maker 0.018% / taker 0.045%), no-lookahead
fractal pivots, pessimistic same-bar SL. Scripts in `backtests/`.

## What the channel actually teaches (12 families)

1. **Regular-divergence + confluence stack** (K7vFNn7fZ7Y + VwVEVu0-JWQ +
   udwkldark34 …) — the incumbent live paper-bot strategy.
2. **Fib "golden zone" 0.5–0.618 continuation** (uC_Iimhvwiw, 2GAAK_JhNW0,
   H7qwIiO4YuE, _iM7tC5QHns, nYKpik-o8zI…) — his most-repeated family.
3. **5m SMMA 21/50/200 stack scalp** with engulfing / three-line-strike entry,
   RSI>50, stop 2× entry candle, TP 2R (wbfXaqjIrJ0 2.7M views, Z__54ssczD0,
   6mr-XMcYU5c, ot0qFIhXylw) — the flagship.
4. **Three-line strike** standalone (RyTlRkMujuk, _Ek9NZNM-3c, XMOo4_r5qlA).
5. **Heikin-Ashi no-wick entry** after pullback (HeNqrn_JO8k, JFLroByoC5s,
   JvwTuiWdJ3c, MKJz4yURCEs, ITi9HRzS__E).
6. **Hidden divergence** trend continuation (trx_M2Bss-c, YqHTDBJlkb0).
7. **Market structure / BOS / liquidity sweeps / S-R retest** (mostly
   discretionary; the codeable parts are inside families 1–2).
8. **Session filters** — "London open → NY close", "never the first hour",
   no-Monday, Tue/Wed/Thu-only, no-December (ot0qFIhXylw, a-AuUHbTx-M,
   YtkgdPZ9VE4, 10SNAXJkgbg, QM0yROyc2Sc).
9. **Session opening-range / DR-IDR breakout** (jlShztsY3oA 15m ORB,
   KYZ3gFl6GW0, YbAkSs0Qog8, eiKZ8eASWR0).
10. **His actual trading bots** (MJ2WL4ld3Fo/hr-ejTXEFPE/axcP2CeIYe8):
    two-line-strike engulfing entry → later momentum entry (high>prev high
    + 21 EMA), SL at candle extreme, TP 2R–3.3R, morning session only.
11. **Tokyo-range failed-breakout fade** (HCiMznnYMiI, "I Gave AI 6 Years of
    Data") — tight Asia range + rel-volume ≥1.6×, fade the false break to the
    range midpoint. His only cost-aware, OOS-tested video.
12. **Indicator one-offs**: SuperTrend(10,2.5) (J2nvSSF6RdI), StochRSI
    (Hh3yBjZrOjg), MACD (RhYVHOs2IZU), Ichimoku, VWAP, volume profile, ATR
    stops (dfijk5dkito) — mostly without full rules; closed-source paid
    indicators (Happy Trail, Wave Rider, Outback, Brute Force, StairMaster)
    gate ~25 videos and are untestable by construction.

## Backtest verdicts (all net of futures fees, honest fills)

| Family (crypto translation) | Result | Verdict |
|---|---|---|
| Fib golden zone (4 param sets × 15m/30m/1h) | gross ≈ +0.02..0.06%, net −0.04..0.00%/tr, no year consistency | DEAD |
| SMMA-stack scalp (engulf + 3LS, 5m/15m/30m/1h, day filters) | net −0.02..−0.15%/tr everywhere | DEAD |
| Three-line strike (raw / trend / at-21SMMA) | net −0.04..−0.14%/tr, t≤−1.7 | DEAD |
| HA no-wick pullback | net −0.06..−0.09%/tr | DEAD |
| Hidden divergence + trend filter (2R/3R) | net −0.03..−0.14%/tr | DEAD (confirms 2026-08-21) |
| SuperTrend 2R | BTC 1h +0.40%/tr but yr1-only spike; ETH negative both TFs | DEAD (fails OOS) |
| StochRSI cross + 200 filter | noise/negative | DEAD |
| RSI 70/30 band-rejoin | negative | DEAD |
| SMMA200 retest-reject | negative | DEAD |
| Session ORB (London/NY open, 15m/30m/1h) | net −0.06..−0.14%/tr, t≈−3 | DEAD |
| His bot entries (engulf-2 and momentum+21EMA, session-gated) | net −0.03..−0.10%/tr, t≤−0.9 | DEAD |
| Tokyo-range fade | his exact conditions fire ~0–12×/2y on crypto (Asia session isn't quiet); unfiltered n=234: net −0.05% | DEAD (forex-microstructure edge, doesn't port) |
| **Regdiv 30m confluence (incumbent) + HIS session filter** | see below | **ONLY SURVIVOR** |

70/30-band divergence filter ("first divergence out of the band",
udwkldark34): cuts n to ~65, year-inconsistent on both assets → rejected.
Opposite-divergence exit: worse than 2R target → rejected. No-Monday filter:
looked strong (BTC +0.28%, ETH +0.95%) but **failed the placebo test** —
excluding Tuesday works as well on ETH, so it's day-noise → rejected honestly.
Tue/Wed/Thu-only (his 10SNAXJkgbg): worse than baseline → rejected.

## The one finding: London→NY session filter on the incumbent

His rule (stated in ≥5 videos): only trade London open → NY close; avoid the
Asia session. Crypto translation: **entry signals only 07:00–21:00 UTC**
(no change to exits).

Regdiv 30m incumbent config + session filter, 2y:

| | n | net/trade | yr1 | yr2 | long/short |
|---|---|---|---|---|---|
| BTC baseline | 197 | +0.07% | +0.36% | **−0.20%** | — |
| BTC + sess 07–21 | 159 | **+0.25%** | +0.245% | **+0.26%** | +0.15% / +0.35% |
| ETH baseline | 196 | +0.59% | +1.05% | +0.18% | — |
| ETH + sess 07–21 | 175 | +0.50% | +0.86% | +0.19% | +0.71% / +0.34% |

Robustness: positive on both assets in BOTH years; window neighbours
(05–21, 06–20, 08–22, 09–21) all positive on BTC (+0.19..+0.32) — a plateau,
not a spike; maker offset 0/5/10/20bp all positive; TP 1.5/2/2.5/3R all
positive; long and short sides positive on both assets. SOL remains firmly
negative under every variant (majors-only, unchanged). 1h remains dead; the
edge still lives only in the 15m/30m band.

Portfolio sim (BTC+ETH, 50% notional per trade, 1x, compounding):
- 2y: 1000 → 1767 USDT (+77%), max drawdown 16.9% (baseline: 1751, DD 24.4%
  — the filter's main effect is cutting drawdown, mostly on BTC yr2)
- yr1: +49.8% | yr2: +17.9% (edge decaying, consistent with prior finding)
- worst single trades: −7.4% at 1x (leverage >3–4x on 100% notional would
  have been liquidation-adjacent; 20x remains guaranteed death)

## Caveats (unchanged from the incumbent's file)

- **The honest re-implementation of the incumbent is weaker than the numbers
  logged on 2026-08-24** (BTC +0.55%/tr then; +0.07%/tr now on the same
  paper-bot logic). The prior grid script was scratchpad-only and can't be
  diffed; this implementation matches `paper_regdiv.py` exactly and is the
  one to trust. ETH remains the carrier of the edge.
- Maker-fill model still ignores queue position; funding rates (~±0.01%/8h)
  not modeled; 30m-band exclusivity and ~50%/yr decay still stand.
- Ambiguous chart-pointed rules in DEAD families (fib tool level sets, MA
  types where unspoken, "rejection" thresholds) were resolved by parameter
  sweeps rather than frame-checks — every swept variant died, so no frame
  reading could change those verdicts. The survivor's rules come from the
  already-frame-verified K7vFNn7fZ7Y test plus a session window that was
  swept ±2h.
