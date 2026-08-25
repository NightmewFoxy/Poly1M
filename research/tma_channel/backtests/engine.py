"""Shared backtest engine for the TMA-channel candidate strategies.

Conventions (locked in by prior sessions' methodology lessons):
- No lookahead: fractal pivots act PIVOT_LR bars after forming; all entries
  decided on bar-close data, filled on LATER bars only.
- Fees: Binance USDT-M futures, maker 0.018%, taker 0.045% per side.
  Two execution models:
    taker: enter at close of signal bar (taker), exit taker.        fee = 2*taker
    maker: limit order placed at signal close +/- offset_bp beyond, filled only
           when a LATER bar trades through the limit price; entry maker,
           SL exit taker, TP exit modeled maker (limit at TP).
- SL/TP touched same bar -> count as SL (pessimistic).
- Entry limit not filled within `fill_window` bars -> signal expires.
"""

from __future__ import annotations
import json, math, os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MAKER = 0.00018
TAKER = 0.00045


def load(sym, iv):
    kl = json.load(open(f"{DATA_DIR}/{sym}_{iv}.json"))
    return {
        "t": [k[0] for k in kl],
        "o": [float(k[1]) for k in kl],
        "h": [float(k[2]) for k in kl],
        "l": [float(k[3]) for k in kl],
        "c": [float(k[4]) for k in kl],
        "v": [float(k[5]) for k in kl],
    }


# ---------- indicators ----------

def rsi(c, n=14):
    vals = [None] * len(c)
    ag = al = 0.0
    g = l = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        up, dn = max(d, 0.0), max(-d, 0.0)
        if i <= n:
            g += up; l += dn
            if i == n:
                ag, al = g / n, l / n
                vals[i] = 100 - 100 / (1 + (ag / al if al else 1e9))
        else:
            ag = (ag * (n - 1) + up) / n
            al = (al * (n - 1) + dn) / n
            vals[i] = 100 - 100 / (1 + (ag / al if al else 1e9))
    return vals


def sma(x, n):
    vals = [None] * len(x)
    s = 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            vals[i] = s / n
    return vals


def ema(x, n, seed_sma=True):
    vals = [None] * len(x)
    k = 2 / (n + 1)
    e = None
    for i, v in enumerate(x):
        if e is None:
            if seed_sma and i == n - 1:
                e = sum(x[:n]) / n
                vals[i] = e
            continue
        e = v * k + e * (1 - k)
        vals[i] = e
    return vals


def smma(x, n):
    vals = [None] * len(x)
    s = sum(x[:n]) / n
    vals[n - 1] = s
    for i in range(n, len(x)):
        s = (s * (n - 1) + x[i]) / n
        vals[i] = s
    return vals


def atr(h, l, c, n=14):
    trs = [None] * len(c)
    for i in range(1, len(c)):
        trs[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return smma_from(trs, n)


def smma_from(x, n):
    vals = [None] * len(x)
    s = None
    cnt = 0
    acc = 0.0
    for i, v in enumerate(x):
        if v is None:
            continue
        if s is None:
            acc += v; cnt += 1
            if cnt == n:
                s = acc / n
                vals[i] = s
        else:
            s = (s * (n - 1) + v) / n
            vals[i] = s
    return vals


def stoch_rsi(c, rsi_n=14, stoch_n=14, k_n=3, d_n=3):
    r = rsi(c, rsi_n)
    raw = [None] * len(c)
    for i in range(len(c)):
        if r[i] is None or i < rsi_n + stoch_n:
            continue
        win = [x for x in r[i - stoch_n + 1:i + 1] if x is not None]
        if len(win) < stoch_n:
            continue
        lo, hi = min(win), max(win)
        raw[i] = 100 * (r[i] - lo) / (hi - lo) if hi > lo else 50.0
    k = sma_skipnone(raw, k_n)
    d = sma_skipnone(k, d_n)
    return k, d


def sma_skipnone(x, n):
    vals = [None] * len(x)
    for i in range(len(x)):
        win = x[max(0, i - n + 1):i + 1]
        if len(win) == n and all(v is not None for v in win):
            vals[i] = sum(win) / n
    return vals


def macd(c, fast=12, slow=26, sig=9):
    ef, es = ema(c, fast), ema(c, slow)
    line = [None if (a is None or b is None) else a - b for a, b in zip(ef, es)]
    # signal = EMA of line over its non-None region
    first = next(i for i, v in enumerate(line) if v is not None)
    sub = line[first:]
    k = 2 / (sig + 1)
    sig_vals = [None] * len(line)
    e = None
    for j, v in enumerate(sub):
        i = first + j
        if e is None:
            if j == sig - 1:
                e = sum(sub[:sig]) / sig
                sig_vals[i] = e
            continue
        e = v * k + e * (1 - k)
        sig_vals[i] = e
    return line, sig_vals


def pivots(h, l, lr):
    """Fractal pivot indices. A pivot at i is only KNOWN at i+lr."""
    ph, pl = [], []
    for i in range(lr, len(h) - lr):
        if h[i] == max(h[i - lr:i + lr + 1]):
            ph.append(i)
        if l[i] == min(l[i - lr:i + lr + 1]):
            pl.append(i)
    return ph, pl


def session_hour(ts_ms):
    return (ts_ms // 3600000) % 24  # UTC hour


def dow(ts_ms):
    return (ts_ms // 86400000 + 4) % 7  # 0=Mon ... 6=Sun (1970-01-01 was Thu)


# ---------- trade simulation ----------

class Sim:
    """Collects signals then simulates fills/exits honestly.

    signal = dict(bar=i, dir=+1/-1, sl=price, tp=price or None, tp_r=float or None)
    Entry models:
      taker: fill at close[i] on signal bar
      maker: limit at close[i] * (1 -/+ offset_bp/1e4) (beyond = better price),
             filled at first later bar whose low<=limit (long) / high>=limit,
             within fill_window bars, and only if SL not hit before fill bar's fill.
    """

    def __init__(self, d, exec_model="maker", offset_bp=10.0, fill_window=20,
                 tp_exit="maker"):
        self.d = d
        self.exec_model = exec_model
        self.offset_bp = offset_bp
        self.fill_window = fill_window
        self.tp_exit = tp_exit

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
            if self.exec_model == "taker":
                entry_bar, entry = i, c[i]
                entry_fee = TAKER
            else:
                lim = c[i] * (1 - dr * self.offset_bp / 1e4)
                entry_bar = entry = None
                for j in range(i + 1, min(i + 1 + self.fill_window, len(c))):
                    if dr > 0 and l[j] <= lim:
                        entry_bar, entry = j, lim
                        break
                    if dr < 0 and h[j] >= lim:
                        entry_bar, entry = j, lim
                        break
                if entry_bar is None:
                    continue
                entry_fee = MAKER
            sl = s["sl"]
            risk = abs(entry - sl)
            if risk / entry < 0.0008:
                continue
            tp = s.get("tp")
            if tp is None:
                tp = entry + dr * s["tp_r"] * risk
            # invalid geometry (fill gapped past SL)
            if (dr > 0 and entry <= sl) or (dr < 0 and entry >= sl):
                continue
            exit_px = None
            exit_bar = None
            for j in range(entry_bar if self.exec_model == "taker" else entry_bar,
                           len(c)):
                jj = j
                if jj == entry_bar and self.exec_model == "taker":
                    # same-bar exit not modeled for taker entry at close
                    continue
                hit_sl = l[jj] <= sl if dr > 0 else h[jj] >= sl
                hit_tp = h[jj] >= tp if dr > 0 else l[jj] <= tp
                if hit_sl:  # pessimistic: SL first
                    exit_px, exit_fee, exit_bar = sl, TAKER, jj
                    break
                if hit_tp:
                    exit_px = tp
                    exit_fee = MAKER if self.tp_exit == "maker" else TAKER
                    exit_bar = jj
                    break
                if max_hold and jj - entry_bar >= max_hold:
                    exit_px, exit_fee, exit_bar = c[jj], TAKER, jj
                    break
            if exit_px is None:
                exit_px, exit_fee, exit_bar = c[-1], TAKER, len(c) - 1
            gross = dr * (exit_px - entry) / entry
            net = gross - entry_fee - exit_fee
            trades.append({"i": i, "entry_bar": entry_bar, "exit_bar": exit_bar,
                           "dir": dr, "gross": gross, "net": net,
                           "t": t[entry_bar]})
            busy_until = exit_bar
        return trades


def report(trades, label="", years=2.0):
    n = len(trades)
    if n == 0:
        return f"{label:44s} n=0"
    nets = [tr["net"] for tr in trades]
    tot = sum(nets)
    avg = tot / n
    wins = sum(1 for x in nets if x > 0)
    var = sum((x - avg) ** 2 for x in nets) / max(n - 1, 1)
    sd = math.sqrt(var) if var > 0 else 1e-9
    tstat = avg / (sd / math.sqrt(n))
    gr = sum(tr["gross"] for tr in trades) / n
    return (f"{label:44s} n={n:4d} win={wins/n:5.1%} avg_gross={gr*100:+.3f}% "
            f"avg_net={avg*100:+.3f}% total_net={tot*100:+8.1f}% t={tstat:+.2f}")


def split_years(trades):
    if not trades:
        return [], []
    ts = [tr["t"] for tr in trades]
    mid = min(ts) + (max(ts) - min(ts)) / 2
    return [tr for tr in trades if tr["t"] < mid], [tr for tr in trades if tr["t"] >= mid]
