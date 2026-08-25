"""Regdiv incumbent (exact live paper-bot config) + TMA-channel refinement
filters, on the shared engine data.

Incumbent (baseline, must reproduce prior findings ~BTC +0.55%/tr, ETH +1.19%):
  30m, tier-B: regular divergence (fractal pivots lr=3, gap<=60), then within
  40 bars RSI across 50 + close beyond BOS + close beyond SMMA21.
  Entry: maker limit 10bp BEYOND signal close, TTL 4 bars. SL at divergence
  extreme (taker). TP 2R (maker).

Filters from the channel corpus (each tested as a delta on the baseline):
  band     divergence pivots: first pivot RSI outside 70/30, second back inside
           ("first divergence out of the range" - udwkldark34, 3APFZa1AQNw)
  band1    only first pivot outside 70/30
  sess_LN  entry bar in London+NY hours (07:00-21:00 UTC)
  sess_NY  12:00-21:00 UTC only
  no_wknd  skip Saturday/Sunday (UTC)
  no_mon   skip Monday (his "Why I Don't Trade On Monday")
  trend200 longs only above SMMA200, shorts only below (trade with the trend)
  oppdiv_exit  exit early when an opposite regular divergence CONFIRMS
           (2_uOr3WXSyc: "exit on first RSI divergence")
"""
import sys
from engine import load, rsi, smma, pivots, report, split_years, MAKER, TAKER

PIVOT_LR = 3
MAX_PIVOT_GAP = 60
CONF_WINDOW = 40
OFFSET_BP = 10
ORDER_TTL = 4
TP_R = 2.0
MIN_RISK = 0.0008


def gen_signals(d, band=None):
    """Returns list of (dir, sig_bar, extreme) for tier-B confluence fires.
    band: None | 'both' (piv1 outside 70/30 & piv2 inside) | 'first' (piv1 outside)"""
    h, l, c = d["h"], d["l"], d["c"]
    r = rsi(c)
    ma21 = smma(c, 21)
    ph, pl = pivots(h, l, PIVOT_LR)
    phs, pls = set(ph), set(pl)
    pending, out = [], []
    last_ph, last_pl = [], []
    for i in range(50, len(c)):
        j = i - PIVOT_LR
        if j in phs:
            for p in [p for p in last_ph if j - p <= MAX_PIVOT_GAP]:
                if h[j] > h[p] and r[j] is not None and r[p] is not None and r[j] < r[p]:
                    ok = True
                    if band == 'both':
                        ok = r[p] > 70 and r[j] < 70
                    elif band == 'first':
                        ok = r[p] > 70
                    if ok:
                        pending.append((-1, i, max(h[j], h[p]), min(l[p:j + 1])))
                    break
            last_ph.append(j)
        if j in pls:
            for p in [p for p in last_pl if j - p <= MAX_PIVOT_GAP]:
                if l[j] < l[p] and r[j] is not None and r[p] is not None and r[j] > r[p]:
                    ok = True
                    if band == 'both':
                        ok = r[p] < 30 and r[j] > 30
                    elif band == 'first':
                        ok = r[p] < 30
                    if ok:
                        pending.append((1, i, min(l[j], l[p]), max(h[p:j + 1])))
                    break
            last_pl.append(j)
        last_ph = last_ph[-8:]
        last_pl = last_pl[-8:]
        keep, fired = [], None
        for (dd, sb, ext, bos) in pending:
            if i - sb > CONF_WINDOW:
                continue
            if dd < 0:
                ok = r[i] is not None and r[i] < 50 and c[i] < bos and c[i] < ma21[i]
            else:
                ok = r[i] is not None and r[i] > 50 and c[i] > bos and c[i] > ma21[i]
            if ok:
                fired = (dd, i, ext)
            else:
                keep.append((dd, sb, ext, bos))
        pending = keep
        if fired:
            pending = []
            out.append(fired)
    return out


def opp_div_bars(d):
    """bar index -> +1/-1 when a regular divergence CONFIRMS at that bar
    (pivot-confirmation bar, no confluences)."""
    h, l, c = d["h"], d["l"], d["c"]
    r = rsi(c)
    ph, pl = pivots(h, l, PIVOT_LR)
    phs, pls = set(ph), set(pl)
    out = {}
    last_ph, last_pl = [], []
    for i in range(50, len(c)):
        j = i - PIVOT_LR
        if j in phs:
            for p in [p for p in last_ph if j - p <= MAX_PIVOT_GAP]:
                if h[j] > h[p] and r[j] is not None and r[p] is not None and r[j] < r[p]:
                    out[i] = -1
                    break
            last_ph.append(j)
            last_ph = last_ph[-8:]
        if j in pls:
            for p in [p for p in last_pl if j - p <= MAX_PIVOT_GAP]:
                if l[j] < l[p] and r[j] is not None and r[p] is not None and r[j] > r[p]:
                    out[i] = 1
                    break
            last_pl.append(j)
            last_pl = last_pl[-8:]
    return out


def simulate(d, sigs, sess=None, no_days=None, trend=None, opp_exit=None):
    h, l, c, t = d["h"], d["l"], d["c"], d["t"]
    ma200 = smma(c, 200) if trend else None
    trades = []
    busy_until = -1
    for (dr, i, ext) in sigs:
        if i <= busy_until:
            continue
        hour = (t[i] // 3600000) % 24
        day = (t[i] // 86400000 + 4) % 7
        if sess and not (sess[0] <= hour < sess[1]):
            continue
        if no_days and day in no_days:
            continue
        if trend and ma200[i] is not None:
            if dr > 0 and c[i] < ma200[i]:
                continue
            if dr < 0 and c[i] > ma200[i]:
                continue
        lim = c[i] * (1 - dr * OFFSET_BP / 1e4)
        entry_bar = None
        for jj in range(i + 1, min(i + 1 + ORDER_TTL, len(c))):
            if (dr > 0 and l[jj] <= lim) or (dr < 0 and h[jj] >= lim):
                entry_bar = jj
                break
        if entry_bar is None:
            continue
        entry = lim
        sl = ext
        risk = abs(entry - sl)
        if risk / entry < MIN_RISK or (dr > 0) != (entry > sl):
            continue
        tp = entry + dr * TP_R * risk
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
            if opp_exit and jj > entry_bar and opp_exit.get(jj) == -dr:
                exit_px, exit_fee, exit_bar = c[jj], TAKER, jj
                break
        if exit_px is None:
            exit_px, exit_fee, exit_bar = c[-1], TAKER, len(c) - 1
        gross = dr * (exit_px - entry) / entry
        net = gross - MAKER - exit_fee
        trades.append({"i": i, "dir": dr, "gross": gross, "net": net,
                       "t": t[entry_bar], "exit_bar": exit_bar})
        busy_until = exit_bar
    return trades


def run_all(sym, iv="30m"):
    d = load(sym, iv)
    base_sigs = gen_signals(d)
    variants = [
        ("baseline (incumbent)", dict(), base_sigs),
        ("band both (out->in 70/30)", dict(), gen_signals(d, band='both')),
        ("band first (piv1 outside)", dict(), gen_signals(d, band='first')),
        ("sess 07-21 UTC", dict(sess=(7, 21)), base_sigs),
        ("sess 12-21 UTC", dict(sess=(12, 21)), base_sigs),
        ("no weekend", dict(no_days={5, 6}), base_sigs),
        ("no Monday", dict(no_days={0}), base_sigs),
        ("trend200 with-trend only", dict(trend=True), base_sigs),
        ("opp-div exit", dict(opp_exit=opp_div_bars(d)), base_sigs),
    ]
    print(f"=== {sym} {iv} ===")
    for name, kw, sigs in variants:
        tr = simulate(d, sigs, **kw)
        print(report(tr, name))
        y1, y2 = split_years(tr)
        print("   " + report(y1, " yr1"))
        print("   " + report(y2, " yr2"))


if __name__ == "__main__":
    for sym in (sys.argv[1:] or ["BTCUSDT", "ETHUSDT"]):
        run_all(sym)
