"""Arty-style divergence detector (per VwVEVu0-JWQ / 3APFZa1AQNw / udwkldark34):
- Swings found on the RSI SERIES itself (fractal 3/3 on RSI), confirmed 3 bars
  late (no lookahead).
- Divergence = the two most recent ADJACENT RSI pivots (gap <= 60 bars).
- Price side read as the price extreme within +/-2 bars of each RSI pivot.
- regular bearish: price HH + RSI LH | hidden bearish: price LH + RSI HH
  (mirrored for lows).
- Optional 70/30 qualifier ("first divergence out of the range"): first RSI
  pivot outside 70/30, second back inside.
Emits (dir, confirm_bar, extreme) like gen_divs/gen_signals so the existing
simulators plug in.
"""
from engine import rsi, pivots

def rsi_pivots(r, lr=3):
    ph, pl = [], []
    for i in range(lr + 20, len(r) - lr):
        if r[i] is None: continue
        win = [x for x in r[i - lr:i + lr + 1] if x is not None]
        if len(win) < 2 * lr + 1: continue
        if r[i] == max(win): ph.append(i)
        if r[i] == min(win): pl.append(i)
    return ph, pl

def gen_divs_arty(d, kinds=("regular",), band=False, gap=60, lr=3):
    h, l, c = d["h"], d["l"], d["c"]
    r = rsi(c)
    ph, pl = rsi_pivots(r, lr)
    out = []
    def price_hi(j):
        a = max(0, j - 2); b = min(len(h), j + 3)
        return max(h[a:b])
    def price_lo(j):
        a = max(0, j - 2); b = min(len(l), j + 3)
        return min(l[a:b])
    for idx in range(1, len(ph)):
        p, j = ph[idx - 1], ph[idx]          # adjacent RSI swing highs
        if j - p > gap: continue
        confirm = j + lr
        if confirm >= len(c): continue
        hp, hj = price_hi(p), price_hi(j)
        reg = hj > hp and r[j] < r[p]
        hid = hj < hp and r[j] > r[p]
        if band:
            reg = reg and r[p] > 70 and r[j] < 70
            hid = hid and r[p] > 70 and r[j] < 70
        if (reg and "regular" in kinds) or (hid and "hidden" in kinds):
            out.append((-1, confirm, max(hp, hj)))
    for idx in range(1, len(pl)):
        p, j = pl[idx - 1], pl[idx]
        if j - p > gap: continue
        confirm = j + lr
        if confirm >= len(c): continue
        lp, lj = price_lo(p), price_lo(j)
        reg = lj < lp and r[j] > r[p]
        hid = lj > lp and r[j] < r[p]
        if band:
            reg = reg and r[p] < 30 and r[j] > 30
            hid = hid and r[p] < 30 and r[j] > 30
        if (reg and "regular" in kinds) or (hid and "hidden" in kinds):
            out.append((1, confirm, min(lp, lj)))
    out.sort(key=lambda x: x[1])
    return out
