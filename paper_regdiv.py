"""Paper-trading bot for the RSI regular-divergence confluence strategy
(research 2026-08-24, STRATEGY_FINDINGS.md addendum 2): the only config from
the YouTube-research program that survived out-of-sample testing.

Config (fixed, from the grid winner):
  - BTCUSDT + ETHUSDT, 30m bars (Binance data-api, works from any IP)
  - Tier-B confluences: regular divergence (fractal pivots, 3 each side,
    max 60-bar pivot gap) then within 40 bars: RSI(14) across the 50 line,
    close beyond the break-of-structure level, close beyond SMMA(21)
  - Entry: MAKER limit 10bp beyond the signal close, good for 4 bars,
    filled when a later bar trades through it
  - SL at the divergence extreme (taker fee), TP at 2R (maker fee)
  - Fees: maker 0.018%, taker 0.045% (Binance USDT-perp), no leverage (1x)

Paper account: starts at 100 USDT, net profit tracked from $0.
Sizing: each symbol trades notional = equity / 2 (so max total exposure 1x).

Telegram (project bot): entry fills, closes (with running net), and a daily
summary at midnight MYT (16:00 UTC). Kill switch: data/STOP_PAPER.
State: data/paper_regdiv_state.json  Ledger: data/paper_regdiv_log.jsonl
Run:   nohup python3 paper_regdiv.py >> data/paper_regdiv.out 2>&1 &
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.parse

BASE = "https://data-api.binance.vision/api/v3/klines"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "30m"
BAR_MS = 30 * 60 * 1000
RSI_LEN = 14
PIVOT_LR = 3
MAX_PIVOT_GAP = 60
CONF_WINDOW = 40
OFFSET_BP = 10
ORDER_TTL_BARS = 4
TP_R = 2.0
MAKER = 0.00018
TAKER = 0.00045
MIN_RISK = 0.0008
START_EQUITY = 100.0
WINDOW_BARS = 600
POLL_SEC = 60

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
STATE_FILE = os.path.join(DATA_DIR, "paper_regdiv_state.json")
LOG_FILE = os.path.join(DATA_DIR, "paper_regdiv_log.jsonl")
STOP_FILE = os.path.join(DATA_DIR, "STOP_PAPER")
MYT_OFFSET = 8 * 3600


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


def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {
        "equity": START_EQUITY,
        "net": 0.0,
        "day_net": 0.0,
        "day_key": myt_day(),
        "trades": 0,
        "wins": 0,
        "sym": {s: {"pos": None, "order": None, "last_bar": 0} for s in SYMBOLS},
    }


def save_state(st):
    tmp = STATE_FILE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE_FILE)


def myt_day(ts=None):
    return time.strftime("%Y-%m-%d", time.gmtime((ts or time.time()) + MYT_OFFSET))


def fetch(symbol, limit=WINDOW_BARS):
    url = f"{BASE}?symbol={symbol}&interval={INTERVAL}&limit={limit}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


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


def smma(closes, n):
    vals = [None] * len(closes)
    s = sum(closes[:n]) / n
    vals[n - 1] = s
    for i in range(n, len(closes)):
        s = (s * (n - 1) + closes[i]) / n
        vals[i] = s
    return vals


def signal_at_last_bar(kl):
    """Run the tier-B state machine over the window; return (dir, extreme)
    if the confluence set fires exactly on the final (closed) bar."""
    h = [float(k[2]) for k in kl]
    l = [float(k[3]) for k in kl]
    c = [float(k[4]) for k in kl]
    r = rsi(c)
    ma21 = smma(c, 21)
    ph, pl = set(), set()
    for i in range(PIVOT_LR, len(h) - PIVOT_LR):
        if h[i] == max(h[i - PIVOT_LR:i + PIVOT_LR + 1]):
            ph.add(i)
        if l[i] == min(l[i - PIVOT_LR:i + PIVOT_LR + 1]):
            pl.add(i)
    pending = []
    last_ph, last_pl = [], []
    fired_last = None
    for i in range(50, len(kl)):
        j = i - PIVOT_LR
        if j in ph:
            for p in [p for p in last_ph if j - p <= MAX_PIVOT_GAP]:
                if h[j] > h[p] and r[j] is not None and r[p] is not None and r[j] < r[p]:
                    pending.append((-1, i, max(h[j], h[p]), min(l[p:j + 1])))
                    break
            last_ph.append(j)
        if j in pl:
            for p in [p for p in last_pl if j - p <= MAX_PIVOT_GAP]:
                if l[j] < l[p] and r[j] is not None and r[p] is not None and r[j] > r[p]:
                    pending.append((1, i, min(l[j], l[p]), max(h[p:j + 1])))
                    break
            last_pl.append(j)
        last_ph = last_ph[-8:]
        last_pl = last_pl[-8:]
        keep = []
        fired = None
        for (d, sb, ext, bos) in pending:
            if i - sb > CONF_WINDOW:
                continue
            if d < 0:
                ok = r[i] is not None and r[i] < 50 and c[i] < bos and c[i] < ma21[i]
            else:
                ok = r[i] is not None and r[i] > 50 and c[i] > bos and c[i] > ma21[i]
            if ok:
                fired = (d, ext)
            else:
                keep.append((d, sb, ext, bos))
        pending = keep
        if fired:
            pending = []
            if i == len(kl) - 1:
                fired_last = fired
    return fired_last


def close_trade(st, sym, px, reason, exit_fee):
    pos = st["sym"][sym]["pos"]
    d = pos["dir"]
    ret = d * (px - pos["entry"]) / pos["entry"] - pos["entry_fee"] - exit_fee
    pnl = pos["notional"] * ret
    st["equity"] += pnl
    st["net"] += pnl
    st["day_net"] += pnl
    st["trades"] += 1
    if pnl > 0:
        st["wins"] += 1
    st["sym"][sym]["pos"] = None
    side = "SHORT" if d < 0 else "LONG"
    emoji = "✅" if pnl > 0 else "❌"
    telegram(f"{emoji} PAPER CLOSE {sym} {side} @ {px:.2f} ({reason})\n"
             f"PnL: {pnl:+.2f} USDT ({ret*100:+.2f}%)\n"
             f"Net profit: {st['net']:+.2f} | Equity: {st['equity']:.2f} USDT\n"
             f"Record: {st['wins']}/{st['trades']} wins")
    log_event({"e": "close", "sym": sym, "px": px, "reason": reason,
               "pnl": pnl, "net": st["net"], "equity": st["equity"]})


def process_symbol(st, sym):
    kl = fetch(sym)
    # last element may be an unclosed bar: drop it if close_time in future
    now_ms = int(time.time() * 1000)
    while kl and kl[-1][6] > now_ms:
        kl.pop()
    if not kl:
        return
    last_ts = kl[-1][0]
    ss = st["sym"][sym]
    if last_ts <= ss["last_bar"]:
        return  # no new closed bar
    # find bars newer than last processed
    new_bars = [k for k in kl if k[0] > ss["last_bar"]] if ss["last_bar"] else [kl[-1]]
    for k in new_bars:
        hi, lo = float(k[2]), float(k[3])
        pos = ss["pos"]
        if pos:
            d = pos["dir"]
            hit_sl = hi >= pos["sl"] if d < 0 else lo <= pos["sl"]
            hit_tp = lo <= pos["tp"] if d < 0 else hi >= pos["tp"]
            if hit_sl:
                close_trade(st, sym, pos["sl"], "stop-loss", TAKER)
            elif hit_tp:
                close_trade(st, sym, pos["tp"], "take-profit", MAKER)
            continue
        order = ss["order"]
        if order:
            d = order["dir"]
            filled = hi >= order["px"] if d < 0 else lo <= order["px"]
            if filled:
                entry = order["px"]
                risk = abs(order["ext"] - entry) / entry
                ss["order"] = None
                if risk < MIN_RISK:
                    log_event({"e": "cancel_degenerate", "sym": sym})
                else:
                    notional = st["equity"] / len(SYMBOLS)
                    tp = entry + d * TP_R * abs(order["ext"] - entry)
                    ss["pos"] = {"dir": d, "entry": entry, "sl": order["ext"],
                                 "tp": tp, "notional": notional,
                                 "entry_fee": MAKER, "opened": int(time.time())}
                    side = "SHORT" if d < 0 else "LONG"
                    telegram(f"📥 PAPER FILL {sym} {side} @ {entry:.2f}\n"
                             f"SL {order['ext']:.2f} | TP {tp:.2f} (2R)\n"
                             f"Size: {notional:.2f} USDT (1x, maker)")
                    log_event({"e": "fill", "sym": sym, "dir": d, "entry": entry,
                               "sl": order["ext"], "tp": tp, "notional": notional})
                continue
            order["bars_left"] -= 1
            if order["bars_left"] <= 0:
                ss["order"] = None
                log_event({"e": "order_expired", "sym": sym})
    ss["last_bar"] = last_ts
    # look for a fresh signal on the newest closed bar (flat, no order)
    if ss["pos"] is None and ss["order"] is None:
        sig = signal_at_last_bar(kl)
        if sig:
            d, ext = sig
            close_px = float(kl[-1][4])
            px = close_px * (1 - d * OFFSET_BP / 10000)
            ss["order"] = {"dir": d, "px": px, "ext": ext,
                           "bars_left": ORDER_TTL_BARS}
            side = "SHORT" if d < 0 else "LONG"
            telegram(f"🕐 PAPER SIGNAL {sym} {side}\n"
                     f"Limit {px:.2f} (10bp off close {close_px:.2f}), "
                     f"good {ORDER_TTL_BARS} bars\nSL would be {ext:.2f}")
            log_event({"e": "signal", "sym": sym, "dir": d, "px": px, "ext": ext})


def maybe_daily_report(st):
    dk = myt_day()
    if dk != st["day_key"]:
        telegram(f"📊 PAPER DAILY ({st['day_key']} MYT)\n"
                 f"Day PnL: {st['day_net']:+.2f} USDT\n"
                 f"Net profit since start: {st['net']:+.2f} USDT\n"
                 f"Equity: {st['equity']:.2f} / started {START_EQUITY:.0f}\n"
                 f"Trades: {st['trades']} ({st['wins']} wins)")
        log_event({"e": "daily", "day": st["day_key"], "day_net": st["day_net"],
                   "net": st["net"], "equity": st["equity"]})
        st["day_net"] = 0.0
        st["day_key"] = dk


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    st = load_state()
    telegram("🤖 Paper regdiv bot started (BTC+ETH 30m, 2R, maker, 1x)\n"
             f"Equity {st['equity']:.2f} USDT | Net {st['net']:+.2f}")
    log_event({"e": "start"})
    errs = 0
    while True:
        if os.path.exists(STOP_FILE):
            telegram("🛑 Paper regdiv bot stopped (STOP_PAPER)")
            log_event({"e": "stop"})
            return
        try:
            for s in SYMBOLS:
                process_symbol(st, s)
            maybe_daily_report(st)
            save_state(st)
            errs = 0
        except Exception as e:
            errs += 1
            print("cycle error:", e)
            log_event({"e": "error", "msg": str(e)})
            if errs == 10:
                telegram(f"⚠️ Paper regdiv bot: 10 consecutive errors, last: {e}")
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
