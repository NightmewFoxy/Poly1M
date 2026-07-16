# cleanup verdicts — oi-extreme & stablecoin-depeg

## oi-extreme — open-interest spikes / positioning extremes as signal
**Verdict: UNVERIFIABLE-DATA (tonight).** Bybit (the only free deep OI history)
has rate-blocked this IP since ~19:10 UTC; OKX Rubik keeps just 180 days of
daily OI (2026-01→now — no room for an IS/OOS split); Binance fapi
`openInterestHist` keeps 30 days. What would settle it: Bybit
`/v5/market/open-interest` (1h interval, paginated) once the block ages out —
test OI-24h-change extremes × price context → next-24h returns, IS 2024 /
OOS 2025→now. Prior after tonight: LOW — OI extremes correlate with funding and
recent momentum, both already tested (funding rank carries no clean-universe
signal; momentum is already harvested by xsmom).

## stablecoin-depeg — buy the panic, sell the repeg
**Verdict: NOT-A-STRATEGY (opportunistic playbook, kept for reference).**
Episodic with ~1 major event per 2–3 years (USDC @ $0.88 Mar-2023 repaid ~13%
in 3 days; USDR/USTC never repaid — the tail is fatal if you pick the wrong
peg). No backtest can be meaningful at n≈3-5 heterogeneous events, and the
opportunity requires being awake, funded, and on-venue during a systemic panic.
Keep as a standing playbook rule — "major reserve-backed stablecoin (USDC/USDT)
trading <0.95 on a solvency RUMOR (not confirmed insolvency) = consider buying
with ≤20% of stack" — not as a strategy with an expected $/day.
