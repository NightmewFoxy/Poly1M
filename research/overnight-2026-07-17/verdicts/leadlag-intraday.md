# btc-leads-alts + intraday-tsmom — hourly lead-lag and intraday momentum

**Verdict: BOTH DEAD.**

## A) BTC → ETH/SOL lead-lag
- Mechanism: BTC trailing k-hour impulse (k∈{4,24}, thresholds 1–4%) → position
  ETH+SOL for next h∈{4,12,24} hours, follow AND fade. Fees 0.14%/event.
- IS 2022-2024: **every FOLLOW cell negative** (down to −31bp/event, t=−6.1) —
  by the time BTC's hourly move is observable, ETH/SOL have already moved (the
  real lag is sub-minute, an HFT game). Fade cells also negative or noise.
- IS-pick (least bad: fade k=4/thr=2%/h=4) → OOS 2025→now: **−28.9bp/event,
  t=−3.2, n=606.** No retail-latency lead-lag exists on majors.
- LIMITATION: majors-only (cached hourly). A small-cap alt version is where any
  residual lag would live, but that needs breadth of hourly alt data + the
  survivorship problem returns. Prior after tonight: low.

## B) Intraday time-series momentum (first hours → rest of day)
- Mechanism: sign of BTC's first F∈{1,2} UTC hours → hold rest of day; variants
  gated on high trailing 24h realized vol (adaptation of Shen/Urquhart/Wang's
  30-min effect). Fees 0.14%/traded day.
- ALL cells negative in BOTH periods (IS: −12 to −33bp/day t≤−1.3; OOS: −9 to
  −23bp/day). The paper's 30-min granularity does not transfer to hourly, and
  daily fee drag buries whatever is left.

## Verification
Data: cached OKX 1H candles 2021-10→2026-07; script `data/backtest_leadlag.py`.

## Bottom line
Intraday continuation/lead-lag on majors is not harvestable at retail latency
and taker fees. Consistent with the cost-aware ML paper (hourly signals ⇒ no net
edge). Families closed.
