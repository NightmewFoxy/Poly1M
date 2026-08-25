"""Candidate 1: TMA fib golden-zone continuation ("golden pocket") strategy.

Canonical rules (union of uC_Iimhvwiw, h5SYMT4-wEQ, 2GAAK_JhNW0, _iM7tC5QHns,
AlsXNhTm4AA, CpSLTA9BXjc, H7qwIiO4YuE, nYKpik-o8zI):
  - Impulse leg that BREAKS STRUCTURE: candle CLOSE beyond the prior swing
    high (long) / swing low (short). Swings = fractal pivots (no lookahead).
  - Draw fib wick-to-wick on the impulse leg: anchor = the swing low the leg
    started from, to the highest high reached after the BOS (long case).
  - Limit entry in the golden zone 0.5-0.618 (variants: at 0.5, at 0.618,
    midway).
  - SL: halfway between 0.618 and 1.0 (variant: beyond 1.0).
  - TP: the impulse extreme (fib 0) (variants: -0.382 / -0.618 extensions).
  - The leg terminates when price starts retracing; we finalize the leg when
    a fractal pivot forms at its extreme (known lr bars later - no lookahead).

Implementation (long side; short mirrored):
  - detect BOS: close[i] > high[last confirmed pivot high]
  - after BOS, wait for the extreme pivot: the next confirmed pivot high ph2
    with high[ph2] >= BOS close. Fib low anchor = the last confirmed pivot low
    before the BOS leg started.
  - at bar ph2+lr (pivot confirmed), place limit at chosen fib level; expires
    after `fill_window` bars or if a new BOS occurs.
Entry is maker by construction (limit into a pullback). SL taker, TP maker.
"""
import sys, itertools
from engine import *


def signals_fib(d, lr=3, entry_lvl=0.618, sl_lvl=0.809, tp_lvl=0.0,
                min_leg_pct=0.004):
    h, l, c = d["h"], d["l"], d["c"]
    n = len(c)
    ph, pl = pivots(h, l, lr)
    phset, plset = set(ph), set(pl)
    sigs = []
    last_ph = None  # last confirmed pivot high idx
    last_pl = None
    # state for pending BOS legs: (dir, anchor_idx, bos_bar)
    pend = None
    for i in range(lr, n):
        j = i - lr
        if j in phset:
            if pend and pend[0] == 1 and h[j] > pend[3]:
                # impulse extreme pivot confirmed -> fire signal
                dr, anchor, bosbar, _ = pend
                lo, hi = l[anchor], h[j]
                leg = hi - lo
                if leg / c[i] >= min_leg_pct:
                    entry = hi - entry_lvl * leg
                    sl = hi - sl_lvl * leg
                    tp = hi - tp_lvl * leg
                    sigs.append({"bar": i, "dir": 1, "sl": sl, "tp": tp,
                                 "limit": entry})
                pend = None
            last_ph = j
        if j in plset:
            if pend and pend[0] == -1 and l[j] < pend[3]:
                dr, anchor, bosbar, _ = pend
                hi, lo = h[anchor], l[j]
                leg = hi - lo
                if leg / c[i] >= min_leg_pct:
                    entry = lo + entry_lvl * leg
                    sl = lo + sl_lvl * leg
                    tp = lo + tp_lvl * leg
                    sigs.append({"bar": i, "dir": -1, "sl": sl, "tp": tp,
                                 "limit": entry})
                pend = None
            last_pl = j
        # BOS detection on closes
        if last_ph is not None and c[i] > h[last_ph] and (pend is None or pend[0] != 1):
            if last_pl is not None:
                pend = (1, last_pl, i, c[i])
        elif last_pl is not None and c[i] < l[last_pl] and (pend is None or pend[0] != -1):
            if last_ph is not None:
                pend = (-1, last_ph, i, c[i])
    return sigs


class FibSim(Sim):
    """Entry at an explicit limit price from the signal (golden-zone)."""

    def run(self, signals, max_hold=None):
        d = self.d
        h, l, c, t = d["h"], d["l"], d["c"], d["t"]
        trades = []
        busy_until = -1
        for s in signals:
            i = s["bar"]
            if i <= busy_until:
                continue
            dr = s["dir"]
            lim = s["limit"]
            # price may already be below the limit at signal time (gap):
            # then limit is not a pullback entry; skip (his rule: wait for pullback)
            if dr > 0 and c[i] <= lim:
                continue
            if dr < 0 and c[i] >= lim:
                continue
            entry_bar = None
            sl = s["sl"]
            for jj in range(i + 1, min(i + 1 + self.fill_window, len(c))):
                if dr > 0 and l[jj] <= lim:
                    entry_bar = jj
                    break
                if dr < 0 and h[jj] >= lim:
                    entry_bar = jj
                    break
            if entry_bar is None:
                continue
            entry = lim
            tp = s["tp"]
            # same-bar SL check on fill bar (pessimistic: if fill bar also
            # trades through SL, we take the SL)
            exit_px = exit_fee = exit_bar = None
            for jj in range(entry_bar, len(c)):
                hit_sl = l[jj] <= sl if dr > 0 else h[jj] >= sl
                hit_tp = (h[jj] >= tp if dr > 0 else l[jj] <= tp) and jj > entry_bar
                if hit_sl:
                    exit_px, exit_fee, exit_bar = sl, TAKER, jj
                    break
                if hit_tp:
                    exit_px, exit_fee, exit_bar = tp, MAKER, jj
                    break
                if max_hold and jj - entry_bar >= max_hold:
                    exit_px, exit_fee, exit_bar = c[jj], TAKER, jj
                    break
            if exit_px is None:
                exit_px, exit_fee, exit_bar = c[-1], TAKER, len(c) - 1
            gross = dr * (exit_px - entry) / entry
            net = gross - MAKER - exit_fee
            trades.append({"i": i, "entry_bar": entry_bar, "exit_bar": exit_bar,
                           "dir": dr, "gross": gross, "net": net, "t": t[entry_bar]})
            busy_until = exit_bar
        return trades


def main():
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    for iv in ("15m", "30m", "1h"):
        d = load(sym, iv)
        for entry_lvl, sl_lvl, tp_lvl in (
            (0.618, 0.809, 0.0),      # canonical: entry .618, SL mid .618-1, TP 0
            (0.618, 1.05, 0.0),       # SL beyond the 1.0
            (0.5, 0.809, 0.0),        # entry at .5
            (0.618, 0.809, -0.382),   # extension target
        ):
            sigs = signals_fib(d, entry_lvl=entry_lvl, sl_lvl=sl_lvl, tp_lvl=tp_lvl)
            sim = FibSim(d, fill_window=30)
            trades = sim.run(sigs)
            lbl = f"{sym} {iv} e{entry_lvl} sl{sl_lvl} tp{tp_lvl}"
            print(report(trades, lbl))
            y1, y2 = split_years(trades)
            print("   " + report(y1, "  yr1") + "\n   " + report(y2, "  yr2"))


if __name__ == "__main__":
    main()
