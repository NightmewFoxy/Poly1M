# tsmom-daily — time-series momentum / trend on BTC+ETH+SOL (daily, perps)

**Verdict: MARGINAL. The trend edge on crypto majors decayed hard after 2023.
Net OOS +12.1%/yr with −38.5% max drawdown (Sharpe 0.49) — barely above the
funding-harvest baseline (+10.6%/yr, −2.4% worst-30d) while taking ~15× the pain.
Long-SHORT variants are mostly NEGATIVE OOS; only long-flat survives.**

## Mechanism tested
Daily signals on BTC/ETH/SOL, equal-weight portfolio, positions changed at close,
fees 0.07% per side of turnover. Families: trailing-return sign (tsmom N),
SMA cross (N), Donchian stop-and-reverse (N), and the pre-registered multi-horizon
Donchian ensemble (20/55/100 — SSRN 5209907 style); each in long/short + long/flat,
fixed-1x + vol-target 30% sizing. 50 combos.

## Verification
- Data: OKX spot daily candles 2019-01-01→2026-07-15 (2,753d BTC/ETH; SOL from
  2020-10), cached `data/daily_candles.json`, script `data/backtest_tsmom.py`.
  (Bybit rate-blocked us mid-fetch; OKX numbers are equivalent for majors.)
- Discipline: grid searched IN-SAMPLE ≤2023 only (best: tsmom-30 long-flat 1x,
  IS Sharpe 2.12, +170%/yr — the bull-era mirage). Frozen, then OOS 2024-01-01→
  2026-07-15 (927 days).

## Results (OOS, net)
| variant | ann | Sharpe | maxDD | worst 30d |
|---|---|---|---|---|
| IS-pick: tsmom-30 long-flat 1x | **+12.1%/yr** | 0.49 | −38.5% | −24.6% |
| Donchian ensemble, vol-target | +6.1%/yr | 0.38 | −25.2% | −13.3% |
| Donchian ensemble, 1x | −0.2%/yr | 0.23 | −44.3% | −33.5% |
| buy & hold (same portfolio) | +3.7%/yr | 0.36 | −64.3% | −49.5% |

- **$1k ⇒ ~$0.33/day; $5k ⇒ ~$1.66/day** (IS-pick, 1x). Leverage scales P&L and
  drawdown together (2x ⇒ ~24%/yr with ~−60% maxDD): no free lunch, Sharpe stays ~0.5.
- Param sensitivity OOS (long-short 1x): −10.7% to +12.6%/yr across neighboring
  horizons — the edge is FRAGILE; small param changes flip the sign.
- The SSRN "Sharpe >1.5 net" Donchian-ensemble claim does NOT reproduce on majors
  post-2024. Possible the top-20 alt ROTATION breadth is what carries that paper —
  that is exactly the queued `xsmom-alts` test (next).

## Caveats
- 2024→2026 contains a strong 2024 bull, then chop: a regime where long-flat trend
  keeps up with B&H only via drawdown avoidance. Shorting majors lost consistently.
- No intraday stops modeled (daily close-to-close); realistic stops would add
  slippage, not edge.

## Bottom line
Real but weak and regime-dependent: +12%/yr net OOS at 1x with −38% drawdowns is
not a "highest-profitability" candidate — it's a diversifier. Keep as reference;
hopes for the family now ride on cross-sectional alt momentum (`xsmom-alts`).

## Addendum (iter 14): vol-targeting check (external claim "Sharpe 1.12→1.42")
OOS 2024→now, vol-target 30%-ann sizing vs 1x (`data/tsmom_vt_check.py`):
tsmom30-vt +8.0%/yr Sh 0.50 maxDD −26.2%; sma50-vt +13.3%/yr Sh 0.75 maxDD
−20.1%; tsmom120-vt +14.5%/yr Sh 0.77 maxDD −18.3%. Vol-targeting halves the
drawdown but Sharpe stays 0.5–0.8 — the claimed 1.4 does NOT reproduce post-2024
on majors. Verdict unchanged (MARGINAL); xsmom remains strictly better.
