# event-drift — pre-FOMC announcement drift on BTC

**Verdict: DEAD. The pre-FOMC long drift is statistically indistinguishable from
noise (t≈1.1 over 36 events) and has the WRONG SIGN in the recent regime
(2024→now: −11.8bp gross / −25.8bp net per event). Even taking the full-period
point estimate at face value, 8 events/yr × +31bp net ≈ +2.5%/yr — irrelevant.**

## What was tested (pre-registered, no fitting)
Long BTC [t−24h → t) into the FOMC statement (14:00 ET, correct EST/EDT UTC
hours), exit at announcement; variant exiting 2h early; post-announcement window
for information. 36 statements 2022-01→2026-06 (2026 dates verified vs the Fed
calendar). Fees 0.14%/event. Data: cached OKX BTC 1H candles.
Script `data/backtest_fomc.py`.

## Results
| window | 2022→now (36 ev) | 2024→now (20 ev) |
|---|---|---|
| PRE24 long | +45.1bp gross (t=1.13), net ann +2.5%/yr | **−11.8bp gross (t=−0.23)** |
| PRE24 exit-2h-early | +18.4bp (t=0.47) | −37.4bp (t=−0.66) |
| POST24 (info) | −62.7bp (t=−1.00) | −79.6bp (t=−0.97) |

- The 2022–2023 events carried the entire effect (+174…+586bp prints); it
  decayed/reversed exactly when it got publicized.
- Post-announcement weakness (shorting it would gross ~+63–80bp/event) is also
  t≈1 noise and was not pre-registered — recording it as a non-finding, not a
  strategy.

## Bottom line
Event trading around FOMC on BTC has no verifiable edge at retail. Family closed
(CPI was already debunked by the sweep's sources).
