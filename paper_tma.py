"""Paper-trading bot for the two TMA divergence B-strategies
(research 2026-08-26, STRATEGY_FINDINGS.md follow-ups 4-7).

Both strategies: HIDDEN divergence sets direction; entry ONLY when price
touches the previous bar's SMMA(21) (owner's touch rule) within 40 bars of
signal confirm (or next-bar open if price is already beyond the MA);
SL = the far price anchor of the divergence; TP = 2R; no breakeven move.

  LOS-15m    line-of-sight divergences (owner's rule: any two 2/2 local
             extremes whose connecting line is unpierced on BOTH price and
             RSI), BTCUSDT + ETHUSDT, 15m bars.
  SWING-30m  prominent adjacent swings (fractal 8/8 on the RSI series,
             adjacent pairs, price extreme +/-2 bars), 30m bars.

Paper account: 1000 USDT, notional = equity/4 per trade (4 slots =
2 strategies x 2 symbols), 1x. Entry fee: maker 0.018% when filled at the
resting MA limit, taker 0.045% for immediate next-bar-open entries.
SL exit taker, TP exit maker.

Telegram (project bot): every FILL and CLOSE, tagged, WITH the divergence
anchor bars/prices/RSI so trades can be redrawn on TradingView for audit.
Daily summary at midnight MYT (16:00 UTC). Kill switch: data/STOP_TMA.
State: data/paper_tma_state.json   Ledger: data/paper_tma_log.jsonl
Run:   nohup python3 paper_tma.py >> data/paper_tma.out 2>&1 &
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://data-api.binance.vision/api/v3/klines"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
RSI_LEN = 14
GAP = 100
ENTRY_WIN = 40
TP_R = 2.0
MAKER = 0.00018
TAKER = 0.00045
MIN_RISK = 0.0008
START_EQUITY = 1000.0
WINDOW_BARS = 700
POLL_SEC = 60
MYT_OFFSET = 8 * 3600

STRATS = {
    "LOS-15m": {"interval": "15m", "bar_ms": 15 * 60 * 1000, "tv_iv": "15"},
    "SWING-30m": {"interval": "30m", "bar_ms": 30 * 60 * 1000, "tv_iv": "30"},
}
TV_LAYOUT = "https://www.tradingview.com/chart/nhgPREcq/"


def tv_link(strat, sym):
    return f"{TV_LAYOUT}?symbol=BINANCE%3A{sym}&interval={STRATS[strat]['tv_iv']}"

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
STATE_FILE = os.path.join(DATA_DIR, "paper_tma_state.json")
LOG_FILE = os.path.join(DATA_DIR, "paper_tma_log.jsonl")
STOP_FILE = os.path.join(DATA_DIR, "STOP_TMA")


def load_env():
    env = {}
    p = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
TG_TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = ENV.get("TELEGRAM_CHAT_ID", "")


def telegram(msg: str):
    if not TG_TOKEN or not TG_CHAT:
        print("TG (no creds):", msg)
        return
    try:
        data = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data)
        urllib.request.urlopen(req, timeout=15).read()
    except Exception as e:
        print("telegram failed:", e)


def log_event(ev: dict):
    ev["ts"] = int(time.time())
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(ev) + "\n")


def ts_str(ms):
    return time.strftime("%m-%d %H:%M", time.gmtime(ms / 1000)) + " UTC"


def fetch(symbol, interval, limit=WINDOW_BARS):
    url = f"{BASE}?symbol={symbol}&interval={interval}&limit={limit}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


# ---------- indicators ----------

def rsi(closes, n=RSI_LEN):
    vals = [None] * len(closes)
    ag = al = None
    g = l = 0.0
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        up, dn = max(d, 0), max(-d, 0)
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


def smma(closes, n=21):
    vals = [None] * len(closes)
    s = sum(closes[:n]) / n
    vals[n - 1] = s
    for i in range(n, len(closes)):
        s = (s * (n - 1) + closes[i]) / n
        vals[i] = s
    return vals


# ---------- divergence detectors (hidden only) ----------

def _clear(series, p, j, vp, vj, above):
    if j <= p + 1:
        return True
    slope = (vj - vp) / (j - p)
    for k in range(p + 1, j):
        line = vp + slope * (k - p)
        if above and series[k] > line + 1e-12:
            return False
        if not above and series[k] < line - 1e-12:
            return False
    return True


def sig_los_last(kl):
    """LOS hidden divergence confirming on the LAST closed bar.
    Anchors: 2/2 local extremes; both price and RSI lines unpierced.
    Returns (dir, sl_extreme, anchors) or None."""
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    t = [k[0] for k in kl]
    r = rsi(c)
    LR = 2
    last = len(kl) - 1
    j = last - LR   # extreme confirmed exactly now
    if j < LR:
        return None
    # pivot high at j?
    if h[j] == max(h[j - LR:j + LR + 1]):
        for p in range(j - 1, max(j - GAP, LR) - 1, -1):
            if h[p] != max(h[p - LR:p + LR + 1]):
                continue
            if r[p] is None or r[j] is None:
                continue
            if not _clear(h, p, j, h[p], h[j], True):
                continue
            if not _clear(r, p, j, r[p], r[j], True):
                continue
            if h[j] < h[p] and r[j] > r[p]:   # hidden bearish
                return (-1, max(h[p], h[j]),
                        {"t1": t[p], "p1": h[p], "r1": r[p],
                         "t2": t[j], "p2": h[j], "r2": r[j]})
            break
    if l[j] == min(l[j - LR:j + LR + 1]):
        for p in range(j - 1, max(j - GAP, LR) - 1, -1):
            if l[p] != min(l[p - LR:p + LR + 1]):
                continue
            if r[p] is None or r[j] is None:
                continue
            if not _clear(l, p, j, l[p], l[j], False):
                continue
            if not _clear(r, p, j, r[p], r[j], False):
                continue
            if l[j] > l[p] and r[j] < r[p]:   # hidden bullish
                return (1, min(l[p], l[j]),
                        {"t1": t[p], "p1": l[p], "r1": r[p],
                         "t2": t[j], "p2": l[j], "r2": r[j]})
            break
    return None


def sig_swing_last(kl):
    """Prominent-swing (RSI fractal 8/8, adjacent pairs) hidden divergence
    confirming on the LAST closed bar."""
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    t = [k[0] for k in kl]
    r = rsi(c)
    LR = 8
    last = len(kl) - 1
    j = last - LR
    if j < LR + 20:
        return None

    def rsi_piv_high(i):
        win = [x for x in r[i - LR:i + LR + 1] if x is not None]
        return r[i] is not None and len(win) == 2 * LR + 1 and r[i] == max(win)

    def rsi_piv_low(i):
        win = [x for x in r[i - LR:i + LR + 1] if x is not None]
        return r[i] is not None and len(win) == 2 * LR + 1 and r[i] == min(win)

    def price_hi(i):
        a = max(0, i - 2); b = min(len(h), i + 3)
        return max(h[a:b])

    def price_lo(i):
        a = max(0, i - 2); b = min(len(l), i + 3)
        return min(l[a:b])

    if rsi_piv_high(j):
        for p in range(j - 1, max(j - GAP, LR + 20) - 1, -1):
            if not rsi_piv_high(p):
                continue
            hp, hj = price_hi(p), price_hi(j)
            if hj < hp and r[j] > r[p]:   # hidden bearish
                return (-1, max(hp, hj),
                        {"t1": t[p], "p1": hp, "r1": r[p],
                         "t2": t[j], "p2": hj, "r2": r[j]})
            break   # adjacent pair only
    if rsi_piv_low(j):
        for p in range(j - 1, max(j - GAP, LR + 20) - 1, -1):
            if not rsi_piv_low(p):
                continue
            lp, lj = price_lo(p), price_lo(j)
            if lj > lp and r[j] < r[p]:   # hidden bullish
                return (1, min(lp, lj),
                        {"t1": t[p], "p1": lp, "r1": r[p],
                         "t2": t[j], "p2": lj, "r2": r[j]})
            break
    return None


DETECTORS = {"LOS-15m": sig_los_last, "SWING-30m": sig_swing_last}


# ---------- state ----------

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    slots = {}
    for st in STRATS:
        for sym in SYMBOLS:
            slots[f"{st}|{sym}"] = {"pos": None, "pending": None, "last_bar": 0}
    return {"equity": START_EQUITY, "net": 0.0, "day_net": 0.0,
            "day_key": myt_day(), "trades": 0, "wins": 0, "slots": slots}


def save_state(st):
    tmp = STATE_FILE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE_FILE)


def myt_day(ts=None):
    return time.strftime("%Y-%m-%d", time.gmtime((ts or time.time()) + MYT_OFFSET))


def anchors_str(a):
    return (f"div anchors: {ts_str(a['t1'])} px {a['p1']:.2f} RSI {a['r1']:.1f}"
            f"  ->  {ts_str(a['t2'])} px {a['p2']:.2f} RSI {a['r2']:.1f}")


def close_trade(st, key, px, reason, exit_fee):
    slot = st["slots"][key]
    pos = slot["pos"]
    d = pos["dir"]
    ret = d * (px - pos["entry"]) / pos["entry"] - pos["entry_fee"] - exit_fee
    pnl = pos["notional"] * ret
    st["equity"] += pnl
    st["net"] += pnl
    st["day_net"] += pnl
    st["trades"] += 1
    if pnl > 0:
        st["wins"] += 1
    slot["pos"] = None
    side = "SHORT" if d < 0 else "LONG"
    emoji = "✅" if pnl > 0 else "❌"
    strat_name, sym_name = key.split("|")
    telegram(f"{emoji} TMA CLOSE [{key}] {side} @ {px:.2f} ({reason})\n"
             f"PnL {pnl:+.2f} USDT ({ret * 100:+.2f}%) | equity {st['equity']:.2f}\n"
             f"{anchors_str(pos['anchors'])}\n"
             f"📈 chart: {tv_link(strat_name, sym_name)}")
    log_event({"e": "close", "key": key, "px": px, "reason": reason,
               "pnl": pnl, "ret": ret, "equity": st["equity"]})


def process_slot(st, strat, sym):
    key = f"{strat}|{sym}"
    slot = st["slots"][key]
    cfg = STRATS[strat]
    kl = fetch(sym, cfg["interval"])
    if not kl:
        return
    # drop unfinished bar
    now_ms = int(time.time() * 1000)
    if kl[-1][6] > now_ms:
        kl = kl[:-1]
    if not kl:
        return
    last_open = kl[-1][0]
    if last_open <= slot["last_bar"]:
        return                     # no new closed bar
    slot["last_bar"] = last_open

    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    o = [float(k[1]) for k in kl]
    ma = smma(c, 21)
    hi, lo, cl, op = h[-1], l[-1], c[-1], o[-1]
    prev_ma = ma[-2] if len(ma) >= 2 else None

    # 1. manage open position on this new bar
    if slot["pos"]:
        pos = slot["pos"]
        d = pos["dir"]
        hit_sl = lo <= pos["sl"] if d > 0 else hi >= pos["sl"]
        hit_tp = hi >= pos["tp"] if d > 0 else lo <= pos["tp"]
        if hit_sl:
            close_trade(st, key, pos["sl"], "SL", TAKER)
        elif hit_tp:
            close_trade(st, key, pos["tp"], "TP 2R", MAKER)

    # 2. try to fill pending entry
    if slot["pos"] is None and slot["pending"]:
        pd = slot["pending"]
        d = pd["dir"]
        entry = entry_fee = None
        if pd.get("imm"):
            entry, entry_fee = op, TAKER
        elif prev_ma is not None:
            lvl = prev_ma
            if d < 0 and hi >= lvl >= lo:
                entry = op if op > lvl else lvl
                entry_fee = MAKER
            elif d > 0 and lo <= lvl <= hi:
                entry = op if op < lvl else lvl
                entry_fee = MAKER
        pd["bars_left"] = pd.get("bars_left", ENTRY_WIN) - 1
        if entry is not None:
            risk = abs(entry - pd["sl"])
            ok = risk / entry >= MIN_RISK and ((d > 0) == (entry > pd["sl"]))
            slot["pending"] = None
            if ok:
                notional = st["equity"] / 4.0
                tp = entry + d * TP_R * risk
                slot["pos"] = {"dir": d, "entry": entry, "sl": pd["sl"],
                               "tp": tp, "notional": notional,
                               "entry_fee": entry_fee, "anchors": pd["anchors"],
                               "opened": int(time.time())}
                side = "SHORT" if d < 0 else "LONG"
                fee_kind = "maker@21SMMA" if entry_fee == MAKER else "taker@open"
                telegram(f"🎯 TMA FILL [{key}] {side} @ {entry:.2f} ({fee_kind})\n"
                         f"SL {pd['sl']:.2f} | TP {tp:.2f} (2R) | "
                         f"notional {notional:.0f} USDT\n"
                         f"{anchors_str(pd['anchors'])}\n"
                         f"📈 chart: {tv_link(strat, sym)}")
                log_event({"e": "fill", "key": key, "dir": d, "entry": entry,
                           "sl": pd["sl"], "tp": tp, "notional": notional,
                           "anchors": pd["anchors"]})
            else:
                log_event({"e": "degenerate_skip", "key": key})
        elif pd["bars_left"] <= 0:
            slot["pending"] = None
            log_event({"e": "pending_expired", "key": key})

    # 3. fresh signal on this closed bar (only when flat and no pending)
    if slot["pos"] is None and slot["pending"] is None:
        sig = DETECTORS[strat](kl)
        if sig:
            d, ext, anchors = sig
            imm = (d < 0 and cl < ma[-1]) or (d > 0 and cl > ma[-1])
            slot["pending"] = {"dir": d, "sl": ext, "anchors": anchors,
                               "imm": bool(imm), "bars_left": ENTRY_WIN}
            log_event({"e": "signal", "key": key, "dir": d, "sl": ext,
                       "imm": bool(imm), "anchors": anchors})


def daily_summary(st):
    day = myt_day()
    if day != st["day_key"]:
        wr = st["wins"] / st["trades"] * 100 if st["trades"] else 0.0
        telegram(f"📊 TMA PAPER daily ({st['day_key']} MYT)\n"
                 f"day PnL {st['day_net']:+.2f} USDT | equity {st['equity']:.2f} "
                 f"(net {st['net']:+.2f})\n"
                 f"lifetime: {st['trades']} trades, win {wr:.0f}%")
        st["day_net"] = 0.0
        st["day_key"] = day


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    st = load_state()
    telegram("🤖 TMA paper bot started: LOS-15m + SWING-30m, BTC+ETH, "
             f"equity {st['equity']:.2f} USDT (hidden div + touch-21SMMA, 2R)")
    log_event({"e": "start", "equity": st["equity"]})
    while True:
        if os.path.exists(STOP_FILE):
            telegram("🛑 TMA paper bot stopped (STOP_TMA)")
            log_event({"e": "stop"})
            return
        for strat in STRATS:
            for sym in SYMBOLS:
                try:
                    process_slot(st, strat, sym)
                except Exception as e:
                    log_event({"e": "error", "key": f"{strat}|{sym}", "err": str(e)})
        daily_summary(st)
        save_state(st)
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
