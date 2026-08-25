# Proposed paper_regdiv.py change (NOT applied — owner approval pending)

From the 2026-08-26 full-channel study + more-trades follow-up. The running
paper bot is untouched; this is the exact change to apply on approval.

## Change 1 — session gate (validated, recommend unconditionally)

Only accept NEW signals when the signal bar's open hour is 07:00–21:00 UTC.
Open positions/orders are managed unchanged.

In `check_symbol()` (or equivalent), before creating a fresh order from
`signal_at_last_bar`:

```python
SESS_UTC = (7, 21)   # entry window, from TMA "London open -> NY close"
...
sig = signal_at_last_bar(kl)
if sig:
    bar_open_ms = kl[-1][0]
    hour = (bar_open_ms // 3600000) % 24
    if not (SESS_UTC[0] <= hour < SESS_UTC[1]):
        sig = None   # outside London/NY window - skip signal
```

Backtest effect (2y): BTC +0.07% → +0.25%/trade net, positive both years;
ETH +0.59% → +0.50%; portfolio maxDD 24.4% → 16.9%.

## Change 2 — concurrency + fixed-risk sizing (optional, activity ~2x)

- Allow up to `MAX_CONC = 2` open positions per symbol (list instead of a
  single `pos`; each position tracks its own SL/TP).
- Size each trade by risk: `notional = equity * RISK_PCT / risk_frac`,
  capped at `equity * 0.5`, with `RISK_PCT = 0.005` (0.5%).

Backtest effect: ~14 → ~24-27 trades/month; per-trade edge intact on BTC
(+0.31% on the overlap set), diluted on ETH (+0.12%); at constant risk% the
RETURN does not improve (extra trades add turnover, not edge-per-risk) —
this change is for activity/signal-collection, not profit. Peak notional
~2x at conc2 — still fine at 1x-per-position paper sizing.

## Rollout

1. Apply change 1 (and 2 if wanted) to `paper_regdiv.py`.
2. Restart the paper bot process (it runs under nohup; old code keeps
   running until restarted). State file is compatible for change 1;
   change 2 needs `pos` -> `positions[]` migration (write fresh state or
   migrate the single open position into a one-element list).
3. Telegram continues as-is; add "(sess)" to the entry message for
   post-hoc filtering of pre/post-change trades.
