"""Line-of-sight divergence detector (owner's clarification of Arty's method):
a divergence is any two swing points whose connecting line is UNOBSTRUCTED -
no intermediate candle pokes through the price line (and optionally no RSI
value pokes through the RSI line). No swing-width parameter.

- candidate anchors: local highs/lows with minimal width lr=2 (5-bar window),
  confirmed 2 bars later (no lookahead).
- for each new confirmed anchor j, scan PREVIOUS anchors from most recent
  backwards (gap <= 100 bars); take the FIRST whose line is clean.
- price extreme uses the candle high/low at the anchor bars.
- hidden bearish: h[j] < h[p] and rsi[j] > rsi[p] (mirror for lows).
- signal fires at j+2 (anchor confirm). SL extreme = the higher/lower of the
  two price anchors.
"""
from engine import rsi

LR = 2

def _local_extremes(h, l):
    ph, pl = [], []
    for i in range(LR, len(h) - LR):
        if h[i] == max(h[i - LR:i + LR + 1]): ph.append(i)
        if l[i] == min(l[i - LR:i + LR + 1]): pl.append(i)
    return ph, pl

def _clear_above(series, p, j, vp, vj):
    """True if no series[k] pokes ABOVE the line from (p,vp) to (j,vj)."""
    if j <= p + 1: return True
    slope = (vj - vp) / (j - p)
    for k in range(p + 1, j):
        if series[k] > vp + slope * (k - p) + 1e-12:
            return False
    return True

def _clear_below(series, p, j, vp, vj):
    if j <= p + 1: return True
    slope = (vj - vp) / (j - p)
    for k in range(p + 1, j):
        if series[k] < vp + slope * (k - p) - 1e-12:
            return False
    return True

def gen_divs_los(d, kinds=("hidden",), check=("price",), gap=100):
    h, l, c = d["h"], d["l"], d["c"]
    r = rsi(c)
    ph, pl = _local_extremes(h, l)
    out = []
    for idx in range(1, len(ph)):
        j = ph[idx]
        if r[j] is None: continue
        for back in range(idx - 1, -1, -1):
            p = ph[back]
            if j - p > gap: break
            if r[p] is None: continue
            ok = True
            if "price" in check and not _clear_above(h, p, j, h[p], h[j]): ok = False
            if ok and "rsi" in check and not _clear_above(r, p, j, r[p], r[j]): ok = False
            if not ok: continue
            reg = h[j] > h[p] and r[j] < r[p]
            hid = h[j] < h[p] and r[j] > r[p]
            if (reg and "regular" in kinds) or (hid and "hidden" in kinds):
                out.append((-1, j + LR, max(h[p], h[j])))
            break   # first clean-line predecessor only (the drawn line)
    for idx in range(1, len(pl)):
        j = pl[idx]
        if r[j] is None: continue
        for back in range(idx - 1, -1, -1):
            p = pl[back]
            if j - p > gap: break
            if r[p] is None: continue
            ok = True
            if "price" in check and not _clear_below(l, p, j, l[p], l[j]): ok = False
            if ok and "rsi" in check and not _clear_below(r, p, j, r[p], r[j]): ok = False
            if not ok: continue
            reg = l[j] < l[p] and r[j] > r[p]
            hid = l[j] > l[p] and r[j] < r[p]
            if (reg and "regular" in kinds) or (hid and "hidden" in kinds):
                out.append((1, j + LR, min(l[p], l[j])))
            break
    out = [s for s in out if s[1] < len(c)]
    out.sort(key=lambda x: x[1])
    return out
