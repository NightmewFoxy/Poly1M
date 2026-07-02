"""Maker bot for Polymarket liquidity rewards ("boring basket" strategy).

Strategy (see memory/lp_rewards_path.md for the full 2026-07-02 validation):
Polymarket pays daily USDC to makers whose resting orders sit within
`rewardsMaxSpread` of the midpoint (scoring S(v,s) = ((v-s)/v)^2 * size,
sampled every minute, paid at midnight UTC). Every OUTSIZED pool we examined
was danger pay for a risk the naive math can't see (news jumps, in-play flow,
recount sniping), so this bot deliberately farms only BORING markets: calm,
deep, long-dated books where our quotes sit behind big walls that absorb the
toxic flow. Expected yield is small-but-real; the point of the first run is
to measure actual paid rewards against the model.

Both quotes are BUYS (a NO bid is economically a YES ask), so a full
two-sided fill leaves a complete $1 YES+NO set — hedged, not directional.
The real risk is a one-sided fill before a jump; rails below bound it.

Safety rails:
  - LP_LIVE=1 required to place orders; anything else = dry run (prints
    intended quotes, touches no auth endpoint).
  - kill switch: create data/STOP_LP -> cancel-all + clean exit.
  - dead-man: cancel-all on startup, shutdown, SIGINT and any crash. A
    resting order surviving a dead bot is the worst operational failure here.
  - volatility pull: mid moved > LP_PULL_CENTS since last cycle -> cancel the
    market's quotes and sit out LP_COOLDOWN_CYCLES.
  - inventory cap: naked (unmatched) exposure beyond LP_MAX_INV_USD stops
    quoting the growing side; only the balancing side stays.
  - after the first live post, asks the CLOB `are_orders_scoring` — direct
    confirmation the quotes are reward-eligible, no model faith required.
  - outage watchdog (added 2026-07-03 after 8h of silent post failures on
    Railway): 10 consecutive failed posts => Telegram alert, flatten the
    book, then probe with exponential backoff (2->15 min cap) instead of
    hammering the gateway once a minute — the rotation spam itself may be
    what gets the source flagged. Re-alerts hourly, notifies on recovery.
    LP_PROXY_ALT_HOSTS=<host,host> adds fallback proxy gateways; probes
    cycle through them.

Orders need a residential IP (403 from cloud IPs — CLAUDE.md #1): either run
on the home PC, or run anywhere with LP_VIA_PROXY=<residential proxy url>
(the pattern the old Railway trading era used; buy a FRESH static
residential proxy, the .env one is dead).

Usage:
  python lp_quoter.py            # dry run, loop (safe anywhere)
  python lp_quoter.py --once     # one cycle, then exit
  LP_LIVE=1 python lp_quoter.py  # real orders (home PC, funded account)
  LP_STOP=1                      # cancel-all + idle (remote kill for cloud)
Rails (env): LP_USD_PER_SIDE (25), LP_MAX_MARKETS (5), LP_DELTA_CENTS (1.0),
LP_PULL_CENTS (2.0), LP_MAX_INV_USD (2x per-side), LP_MARKETS (pin basket by
comma-separated condition_ids, skips the screen), LP_SHARES (0 = size each
side as USD_PER_SIDE/price; >0 = quote exactly this many shares per side —
the way to sit at rewardsMinSize on pools whose minimum exceeds the USD
budget, e.g. the 200-share Fed markets).
"""
from __future__ import annotations

import os

# Env fixes BEFORE importing config (same preamble as arb_executor.py, and for
# the same reasons): NO-side bids price near $0.9x, above the old MAX_PRICE
# cap. Egress depends on where we run:
#   - home PC (default): orders go DIRECT from the residential IP; every
#     inherited proxy var is blanked (the .env OUTBOUND_PROXY is stale).
#   - cloud (LP_VIA_PROXY=<url>): order traffic (py-clob-client / requests)
#     routes through a FRESH residential proxy via config.py's OUTBOUND_PROXY
#     export; market reads + Telegram (httpx trust_env=False) stay direct,
#     which also means the bot can still see books and scream on Telegram
#     even when the proxy itself is down.
os.environ["MAX_PRICE"] = "0.999"
_VIA_PROXY = os.getenv("LP_VIA_PROXY", "").strip()
if _VIA_PROXY:
    os.environ["OUTBOUND_PROXY"] = _VIA_PROXY
else:
    os.environ["OUTBOUND_PROXY"] = ""
    os.environ["POLYMARKET_PROXY_URL"] = ""
    for _k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        os.environ.pop(_k, None)

# py_clob_client_v2 sets no request timeout anywhere; through a residential
# proxy a wedged tunnel blocks forever (observed 2026-07-02: post_order hung
# >2.5 min while the order itself HAD reached the exchange). Bound every
# socket op that lacks an explicit timeout — httpx clients set their own.
import socket

socket.setdefaulttimeout(20)

import argparse
import atexit
import json
import time

import httpx

import config
from arb_scanner import _ascii, fetch_pages, get_books

LIVE = os.getenv("LP_LIVE", "0").lower() in ("1", "true", "yes")
USD_PER_SIDE = float(os.getenv("LP_USD_PER_SIDE", "25"))
MAX_MARKETS = int(os.getenv("LP_MAX_MARKETS", "5"))
DELTA = float(os.getenv("LP_DELTA_CENTS", "1.0")) / 100
PULL_CENTS = float(os.getenv("LP_PULL_CENTS", "2.0"))
COOLDOWN_CYCLES = int(os.getenv("LP_COOLDOWN_CYCLES", "5"))
MAX_INV_USD = float(os.getenv("LP_MAX_INV_USD", str(2 * USD_PER_SIDE)))
CYCLE_S = float(os.getenv("LP_CYCLE_S", "60"))
MIN_POOL = float(os.getenv("LP_MIN_POOL", "50"))
FIXED_SHARES = float(os.getenv("LP_SHARES", "0"))  # 0 = USD-based sizing
MAX_JUMPS_14D = int(os.getenv("LP_MAX_JUMPS_14D", "8"))  # hourly moves >= 2c
PIN_MARKETS = [c for c in os.getenv("LP_MARKETS", "").split(",") if c.strip()]

KILL_FILE = config.DATA_DIR / "STOP_LP"
LEDGER = config.DATA_DIR / "lp_quoter_log.jsonl"
CLOB = "https://clob.polymarket.com"

_HTTP = httpx.Client(trust_env=False, timeout=30)

# --- proxy session rotation (cloud mode only) -------------------------------
# Residential gateways hand out peers of varying quality (~1 in 4 IPRoyal
# sessions 504s, measured 2026-07-02). requests re-reads HTTPS_PROXY from the
# env on every call, so swapping the _session-XXX tag in the env is enough to
# move all subsequent order traffic to a fresh peer. Rotate after 2
# consecutive order-plumbing failures.
_net_fails = 0


def _rotate_proxy_session(reason: str) -> None:
    cur = os.environ.get("HTTPS_PROXY", "")
    if "_session-" not in cur:
        return
    import random
    import string
    sid = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    import re as _re
    new = _re.sub(r"_session-[^_@]+", f"_session-{sid}", cur)
    for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        if os.environ.get(k):
            os.environ[k] = new
    _say(f"proxy session rotated ({reason})")
    log_event({"ev": "proxy_rotate", "reason": reason})


def _net_fail() -> None:
    global _net_fails
    _net_fails += 1
    if _net_fails >= 2:
        _rotate_proxy_session(f"{_net_fails} consecutive request failures")
        _net_fails = 0


def _net_ok() -> None:
    global _net_fails
    _net_fails = 0


# --- outage watchdog + gateway failover --------------------------------------
# 2026-07-03 incident: the Railway->IPRoyal tunnel died at 12:50 UTC and the
# bot retried (and rotated sessions) once a minute for 8 hours without ever
# telling the owner — post failures were stdout-only. Track consecutive post
# failures; past DOWN_AFTER the main loop flattens the book, alerts, and backs
# off. Session-rotation spam is itself a suspect for tripping the provider's
# abuse flag, so backing off is part of the cure, not just politeness.
DOWN_AFTER = int(os.getenv("LP_DOWN_AFTER", "10"))
_post_fail_streak = 0
_down = {"active": False, "since": 0.0, "alerted": 0.0,
         "backoff": 120.0, "next_try": 0.0}

_GATEWAYS: list[str] | None = None
_gw_idx = 0
_last_balance_alert = 0.0


def _reject_alert() -> bool:
    """Throttle order-rejection Telegrams to one per 6h — these conditions
    (balance shortfall, geoblock) persist until the owner acts, and a
    per-cycle alert would be exactly the spam the notify policy forbids."""
    global _last_balance_alert
    if time.time() - _last_balance_alert >= 6 * 3600:
        _last_balance_alert = time.time()
        return True
    return False


def _build_gateways() -> list[str]:
    """Primary proxy URL as deployed, plus the same URL re-pointed at each
    LP_PROXY_ALT_HOSTS host (creds/port/session tag preserved)."""
    import re as _re
    base = os.environ.get("HTTPS_PROXY", "")
    if not base:
        return []
    urls = [base]
    for h in (x.strip() for x in os.getenv("LP_PROXY_ALT_HOSTS", "").split(",")):
        if not h:
            continue
        alt = _re.sub(r"@[^@:/]+(:\d+/?)$", f"@{h}\\1", base)
        if alt != base:
            urls.append(alt)
    return urls


def _switch_gateway(reason: str) -> None:
    global _GATEWAYS, _gw_idx
    if _GATEWAYS is None:
        _GATEWAYS = _build_gateways()
    if len(_GATEWAYS) < 2:
        return
    _gw_idx = (_gw_idx + 1) % len(_GATEWAYS)
    for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        if os.environ.get(k):
            os.environ[k] = _GATEWAYS[_gw_idx]
    host = _GATEWAYS[_gw_idx].rsplit("@", 1)[-1]
    _say(f"proxy gateway switched to {host} ({reason})")
    log_event({"ev": "gateway_switch", "host": host, "reason": reason})
    _rotate_proxy_session("gateway switch")  # fresh session on the new node


def _say(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def notify(text: str) -> None:
    try:
        _HTTP.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text[:4000],
                  "disable_web_page_preview": True},
        )
    except Exception as exc:
        _say(f"telegram failed: {exc}")


def log_event(ev: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": int(time.time()), **ev}) + "\n")


def S(v: float, s: float, size: float) -> float:
    return ((v - s) / v) ** 2 * size if 0 <= s < v else 0.0


def qmin(q1: float, q2: float, extreme: bool) -> float:
    return min(q1, q2) if extreme else max(min(q1, q2), max(q1, q2) / 3)


def clob_meta(cond: str) -> dict | None:
    """neg_risk + tick_size from the CLOB (canonical — CLAUDE.md gotcha #4)."""
    try:
        r = _HTTP.get(f"{CLOB}/markets/{cond}")
        if r.status_code != 200:
            return None
        j = r.json()
        return {"neg_risk": bool(j.get("neg_risk", False)),
                "tick": float(j.get("minimum_tick_size") or 0.01),
                "accepting": bool(j.get("accepting_orders", True))}
    except Exception:
        return None


def jumps_14d(token_id: str) -> int | None:
    """Hourly moves >= 2c in the last 14d. None = no usable history."""
    try:
        r = _HTTP.get(f"{CLOB}/prices-history",
                      params={"market": token_id, "interval": "max", "fidelity": 60})
        now = time.time()
        ps = [float(h["p"]) for h in (r.json().get("history") or [])
              if h["t"] >= now - 14 * 86400]
    except Exception:
        return None
    if len(ps) < 48:
        return None
    return sum(1 for i in range(1, len(ps)) if abs(ps[i] - ps[i - 1]) >= 0.02)


def select_basket() -> list[dict]:
    """Screen for calm reward markets, or use the LP_MARKETS pin list."""
    if PIN_MARKETS:
        # Pinned markets are fetched directly by conditionId. Scanning the
        # top-volume pages for them (the old way) silently lost the pin
        # whenever its 24h-volume rank slipped below the page window —
        # observed 2026-07-02 on Railway: booted fine at 07:56, "no markets
        # passed the screen" at 08:17, same pin.
        mkts = fetch_pages("/markets", {"condition_ids": PIN_MARKETS},
                           pages=1)
    else:
        mkts = fetch_pages("/markets", {"active": "true", "closed": "false",
                                        "archived": "false", "order": "volume24hr",
                                        "ascending": "false"}, pages=6)
    picked: list[dict] = []
    for m in mkts:
        cond = m.get("conditionId") or ""
        if PIN_MARKETS and cond not in PIN_MARKETS:
            continue
        if m.get("acceptingOrders") is False:
            continue
        pool = sum(float(r.get("rewardsDailyRate") or 0)
                   for r in (m.get("clobRewards") or []))
        if pool < MIN_POOL:
            continue
        try:
            toks = json.loads(m.get("clobTokenIds") or "[]")
            bb, ba = float(m.get("bestBid") or 0), float(m.get("bestAsk") or 0)
        except Exception:
            continue
        if len(toks) != 2 or not bb or not ba:
            continue
        mid = (bb + ba) / 2
        if not PIN_MARKETS and not 0.10 <= mid <= 0.90:
            continue  # extreme mids cluster near resolution events
        # a calm 14d history says nothing about a market that RESOLVES soon
        # (Wimbledon/World Cup futures are placid until the knockout rounds);
        # boring means long-dated too. Gamma endDates are sometimes wrong
        # (CLAUDE.md #9) — unparseable ones pass, the jump filter still applies.
        if not PIN_MARKETS:
            end_iso = m.get("endDateIso") or m.get("endDate") or ""
            try:
                from datetime import datetime, timezone
                end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                if (end - datetime.now(timezone.utc)).days < 21:
                    continue
            except ValueError:
                pass
        v = float(m.get("rewardsMaxSpread") or 3) / 100
        minsize = float(m.get("rewardsMinSize") or 0)
        # both sides must clear the reward min size at our budget
        yes_cap = FIXED_SHARES or USD_PER_SIDE / max(mid - DELTA, 0.01)
        no_cap = FIXED_SHARES or USD_PER_SIDE / max(1 - mid - DELTA, 0.01)
        if yes_cap < minsize or no_cap < minsize:
            continue
        if not PIN_MARKETS:
            j = jumps_14d(toks[0])
            if j is None or j > MAX_JUMPS_14D:
                continue
        picked.append({"cond": cond, "q": _ascii((m.get("question") or "")[:60]),
                       "yes": toks[0], "no": toks[1], "pool": pool,
                       "v": v, "minsize": minsize})
        if len(picked) >= (len(PIN_MARKETS) or MAX_MARKETS):
            break
        time.sleep(0.1)
    return picked


# ---------------------------------------------------------------------------
# Order plumbing (only touched when LIVE)
# ---------------------------------------------------------------------------

_pmc = None


def pmc():
    global _pmc
    if _pmc is None:
        import polymarket_client
        _pmc = polymarket_client
    return _pmc


def cancel_all(reason: str) -> bool:
    if not LIVE:
        return True
    for attempt in range(3):
        try:
            pmc().clob().cancel_all()
            _say(f"cancel_all ok ({reason})")
            log_event({"ev": "cancel_all", "reason": reason})
            _net_ok()
            return True
        except Exception as exc:
            _say(f"cancel_all attempt {attempt + 1} failed: {exc}")
            _rotate_proxy_session("cancel_all failure")  # rotate NOW: cancels are safety-critical
            time.sleep(2)
    notify("LP quoter: cancel_all FAILED 3x — check open orders in the UI NOW")
    return False


def post_buy(token_id: str, price: float, shares: float,
             neg_risk: bool, tick: float) -> str | None:
    """Sign+post a GTC BUY. Returns order id, or None on failure."""
    from py_clob_client_v2.clob_types import OrderArgs, OrderType, PartialCreateOrderOptions
    from py_clob_client_v2.order_builder.constants import BUY
    args = OrderArgs(token_id=token_id, price=round(price, 4),
                     size=round(shares, 2), side=BUY)
    opts = PartialCreateOrderOptions(
        neg_risk=neg_risk, tick_size=("0.001" if tick < 0.01 else "0.01"))
    global _post_fail_streak
    try:
        signed = pmc().clob().create_order(args, options=opts)
        resp = pmc().clob().post_order(signed, OrderType.GTC)
        oid = (resp or {}).get("orderID") or (resp or {}).get("orderId")
        _post_fail_streak = 0
        _net_ok()
        return str(oid) if oid else None
    except Exception as exc:
        _say(f"post_buy failed {token_id[:10]} @{price}: {exc}")
        log_event({"ev": "post_error", "token": token_id, "err": str(exc)[:200]})
        sc = getattr(exc, "status_code", None)
        if sc is not None and 400 <= int(sc) < 500 and int(sc) != 429:
            # definitive server rejection: the network path is UP, so this
            # must NOT feed the outage watchdog (a persistent 400 would
            # false-trigger DOWN alarms forever). But persistent rejections
            # are owner-actionable — alert, throttled to one per 6h.
            if _reject_alert():
                if "not enough balance" in str(exc):
                    notify(f"LP quoter: NOT ENOUGH BALANCE to post "
                           f"{shares:g}sh @{price} (${shares * price:.0f} "
                           "needed). Top up USDC or free held capital; "
                           "quoting continues on the sides that fit. "
                           "Repeats at most every 6h.")
                else:
                    notify(f"LP quoter: orders REJECTED by the exchange "
                           f"(HTTP {sc}): {str(exc)[:150]} — retrying, but "
                           "this usually needs your action (403 = geoblock; "
                           "on the home PC re-add the WARP split-tunnel: "
                           "warp-cli tunnel host add clob.polymarket.com). "
                           "Repeats at most every 6h.")
        else:
            _post_fail_streak += 1
            if _post_fail_streak % 6 == 0:
                _switch_gateway(f"{_post_fail_streak} consecutive post failures")
            _net_fail()
        return None


def order_matched(order_id: str) -> float:
    """Filled size of an order (0.0 if still resting or lookup fails)."""
    try:
        o = pmc().clob().get_order(order_id)
        _net_ok()
        return float((o or {}).get("size_matched") or 0)
    except Exception:
        _net_fail()
        return 0.0


def cancel_one(order_id: str) -> bool:
    """True = the exchange answered (order no longer needs tracking); False =
    network failure, the order may still rest — caller must keep its id."""
    from py_clob_client_v2.clob_types import OrderPayload
    try:
        resp = pmc().clob().cancel_order(OrderPayload(orderID=order_id))
        # CLOB reports per-order outcomes; "already canceled" is fine, anything
        # else in not_canceled deserves eyes. Status reads lag a few seconds
        # after a cancel, so never re-check via get_order immediately.
        nc = (resp or {}).get("not_canceled") or {}
        bad = {k: v for k, v in nc.items() if "already canceled" not in str(v)}
        if bad:
            _say(f"cancel_order {order_id[:12]} not canceled: {bad}")
            log_event({"ev": "cancel_refused", "order": order_id, "resp": str(bad)[:200]})
        _net_ok()
        return True
    except Exception as exc:
        _say(f"cancel_order {order_id[:12]} failed: {exc}")
        _rotate_proxy_session("cancel_order failure")  # cancels are safety-critical
        return False


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def snap(price: float, tick: float) -> float:
    return round(round(price / tick) * tick, 4)


def seed_inventory(basket: list[dict]) -> None:
    """Restart-amnesia fix (2026-07-03): inv_* meant "bought this run", so a
    restarted bot forgot it was already long 200 YES from a fill, kept
    bidding the long side and couldn't afford the balancer. Seed from the
    wallet's actual on-chain positions so the inventory cap sees the truth
    and quotes only the balancing side when already exposed."""
    try:
        r = _HTTP.get("https://data-api.polymarket.com/positions",
                      params={"user": config.POLYMARKET_FUNDER_ADDRESS,
                              "limit": 500})
        pos = {str(p.get("asset")): float(p.get("size") or 0) for p in r.json()}
    except Exception as exc:
        _say(f"inventory seed failed (starting flat): {exc}")
        return
    for b in basket:
        b["inv_yes"] = pos.get(str(b["yes"]), 0.0)
        b["inv_no"] = pos.get(str(b["no"]), 0.0)
        if b["inv_yes"] or b["inv_no"]:
            _say(f"  seeded inventory {b['inv_yes']:g}Y/{b['inv_no']:g}N"
                 f"  {b['q'][:38]}")
            log_event({"ev": "inventory_seed", "q": b["q"],
                       "yes": b["inv_yes"], "no": b["inv_no"]})


def report_payouts(state: dict) -> None:
    """Once daily, after the 00:10-00:17 UTC payout window: read our own
    wallet's REWARD activity from the public data-api and Telegram the
    number. This IS the pilot's deliverable (k = actually-paid / model), so
    the bot reports it itself — works the same on the home PC and Railway."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    boot = state.get("day") is None
    if (now.hour, now.minute) < (0, 20) and not boot:
        return
    if state.get("day") == today:
        return
    state["day"] = today
    try:
        r = _HTTP.get("https://data-api.polymarket.com/activity",
                      params={"user": config.POLYMARKET_FUNDER_ADDRESS,
                              "type": "REWARD", "limit": 100})
        rows = [a for a in r.json() if a.get("type") == "REWARD"]
        day_of = lambda a: datetime.fromtimestamp(
            a["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d")
        got = sum(float(a.get("usdcSize") or 0) for a in rows if day_of(a) == today)
        total = sum(float(a.get("usdcSize") or 0) for a in rows)
        log_event({"ev": "payout_report", "day": today, "usd": got, "total": total})
        # Telegram policy: money landing is always news; a $0 day is news only
        # at the once-daily scheduled check (that IS the pilot measurement) —
        # never on a mere process restart.
        if got > 0 or not boot:
            notify(f"LP payout for {today}: ${got:.2f} (all-time rewards ${total:.2f})")
        else:
            _say(f"payout report {today}: $0 (boot check, not notified)")
    except Exception as exc:
        _say(f"payout report failed: {exc}")


_LOCK_SOCK = None


def run(once: bool = False) -> None:
    # Single-instance lock: two quoters on one machine cancel each other's
    # resting orders forever (nearly happened 2026-07-03 via a second
    # launcher window). A bound localhost port is a cross-process mutex
    # that dies with the process — no stale lockfile to clean up.
    import socket as _socket
    global _LOCK_SOCK
    _LOCK_SOCK = _socket.socket()
    try:
        _LOCK_SOCK.bind(("127.0.0.1", int(os.getenv("LP_LOCK_PORT", "47391"))))
    except OSError:
        _say("another lp_quoter already runs on this machine — exiting")
        notify("LP quoter: second instance blocked — one is already running. "
               "(Use data/STOP_LP to stop the live one.)")
        return

    # Remote kill for cloud runs (no shell to create data/STOP_LP there):
    # set LP_STOP=1 in the platform's env and redeploy/restart — the new
    # process cancels everything and idles instead of quoting. Idle rather
    # than exit, so a restart-on-exit policy doesn't loop cancel/notify spam.
    if os.getenv("LP_STOP", "").lower() in ("1", "true", "yes"):
        cancel_all("LP_STOP env")
        notify("LP quoter: LP_STOP is set — all orders cancelled, idling. "
               "Unset LP_STOP and restart to resume.")
        _say("LP_STOP set — idling forever (Ctrl-C to exit)")
        while True:
            time.sleep(3600)
    mode = "LIVE" if LIVE else "DRY RUN"
    basket = select_basket()
    empty_screens = 0
    while not basket:
        # Exiting here killed unattended cloud runs: a clean exit(0) is not
        # restarted by Railway's ON_FAILURE policy, so one empty screen
        # (Gamma hiccup, rank jitter) silently ended the pilot. Retry, and
        # tell the owner once if it persists — a pinned market staying gone
        # means it resolved/delisted and needs a repin.
        empty_screens += 1
        _say(f"no markets passed the screen (try {empty_screens}) — "
             f"retrying in 5 min")
        log_event({"ev": "empty_screen", "try": empty_screens})
        if empty_screens == 6:
            notify("LP quoter: no markets have passed the screen for 30 min "
                   f"(pins: {','.join(PIN_MARKETS) or 'none'}). If a pinned "
                   "market resolved, repin LP_MARKETS and restart.")
        if once:
            return
        time.sleep(300)
        basket = select_basket()
    _say(f"LP quoter {mode}: {len(basket)} markets, ${USD_PER_SIDE}/side, "
         f"quotes at mid+/-{DELTA * 100:.1f}c, pull>{PULL_CENTS}c")
    for b in basket:
        meta = clob_meta(b["cond"]) or {}
        b["neg_risk"] = bool(meta.get("neg_risk", False))
        b["tick"] = float(meta.get("tick", 0.01))
        b["orders"] = {}        # side -> {id, px, shares, matched}
        b["inv_yes"] = 0.0      # shares bought this run
        b["inv_no"] = 0.0
        b["cooldown"] = 0
        b["last_mid"] = None
        _say(f"  [{b['pool']:>6,.0f}$/d] {b['q']}")
    seed_inventory(basket)
    if LIVE:
        cancel_all("startup clean slate")
        # startup is routine (Railway restarts alone would spam) — ledger only
        log_event({"ev": "startup", "markets": len(basket)})
    atexit.register(cancel_all, "atexit")
    scoring_checked = False
    scoring_cycles = 0
    payout_state: dict = {}

    try:
        while True:
            t0 = time.time()
            if KILL_FILE.exists():
                _say("STOP_LP found — shutting down")
                cancel_all("STOP_LP")
                notify("LP quoter stopped via STOP_LP. All orders cancelled.")
                return

            # outage watchdog: sustained post failures => alert once, flatten
            # the book, probe with exponential backoff instead of hammering
            # the proxy every cycle. STOP_LP above stays responsive.
            now = time.time()
            if LIVE and _post_fail_streak >= DOWN_AFTER:
                if not _down["active"]:
                    _down.update(active=True, since=now, alerted=now,
                                 backoff=120.0, next_try=0.0)
                    log_event({"ev": "proxy_down", "streak": _post_fail_streak})
                    notify("LP quoter DOWN: order posts failing repeatedly "
                           "(proxy path?). Flattening book; probing with "
                           "backoff, will re-alert hourly until recovered.")
                    if cancel_all("proxy outage — flatten while down"):
                        for b in basket:
                            b["orders"] = {}
                    # cancel_all failure already screams via Telegram; keep
                    # tracked ids in that case so fills are still accounted.
                if now - _down["alerted"] >= 3600:
                    _down["alerted"] = now
                    notify(f"LP quoter: still DOWN "
                           f"{(now - _down['since']) / 3600:.1f}h "
                           "(order posts failing via proxy).")
                if now < _down["next_try"]:
                    time.sleep(CYCLE_S)
                    continue
                _down["next_try"] = now + _down["backoff"]
                _down["backoff"] = min(900.0, _down["backoff"] * 2)
                _switch_gateway("down-state probe")
            elif _down["active"]:
                log_event({"ev": "proxy_recovered",
                           "down_h": round((now - _down["since"]) / 3600, 2)})
                notify("LP quoter RECOVERED: orders posting again after "
                       f"{(now - _down['since']) / 3600:.1f}h down.")
                _down.update(active=False, backoff=120.0, next_try=0.0)

            books = get_books([b["yes"] for b in basket])
            for b in basket:
                book = books.get(b["yes"]) or {}
                bids = [(float(x["price"]), float(x["size"])) for x in book.get("bids") or []]
                asks = [(float(x["price"]), float(x["size"])) for x in book.get("asks") or []]
                if not bids or not asks:
                    continue
                mid = (max(p for p, _ in bids) + min(p for p, _ in asks)) / 2

                # volatility pull
                if b["last_mid"] is not None and abs(mid - b["last_mid"]) * 100 > PULL_CENTS:
                    _say(f"  pull {b['q'][:34]}: mid {b['last_mid']:.3f}->{mid:.3f}")
                    log_event({"ev": "vol_pull", "q": b["q"], "from": b["last_mid"], "to": mid})
                    for side, o in list(b["orders"].items()):
                        if LIVE and o.get("id") and not cancel_one(o["id"]):
                            continue  # may still rest — keep id, retry next cycle
                        b["orders"].pop(side, None)
                    b["cooldown"] = COOLDOWN_CYCLES
                b["last_mid"] = mid
                if b["cooldown"] > 0:
                    b["cooldown"] -= 1
                    continue

                # fill accounting on resting orders
                for side, o in list(b["orders"].items()):
                    if not LIVE or not o.get("id"):
                        continue
                    matched = order_matched(o["id"])
                    if matched > o["matched"]:
                        got = matched - o["matched"]
                        o["matched"] = matched
                        if side == "yes":
                            b["inv_yes"] += got
                        else:
                            b["inv_no"] += got
                        sets = min(b["inv_yes"], b["inv_no"])
                        naked = abs(b["inv_yes"] - b["inv_no"])
                        log_event({"ev": "fill", "q": b["q"], "side": side,
                                   "shares": got, "px": o["px"]})
                        hint = ("  TIP: complete YES+NO sets can be merged "
                                "back to USDC on polymarket.com (position "
                                "-> Merge) to recycle capital."
                                if sets > 0 else "")
                        notify(f"LP fill: {side.upper()} {got:.1f}sh @{o['px']} "
                               f"{b['q'][:40]} | sets={sets:.0f} "
                               f"naked={naked:.0f}sh{hint}")

                # desired quotes (both are BUYS: YES bid + NO bid == YES ask)
                yes_px = snap(mid - DELTA, b["tick"])
                no_px = snap((1 - mid) - DELTA, b["tick"])
                yes_sh = round(FIXED_SHARES or USD_PER_SIDE / max(yes_px, 0.01), 2)
                no_sh = round(FIXED_SHARES or USD_PER_SIDE / max(no_px, 0.01), 2)
                if yes_sh < b["minsize"] or no_sh < b["minsize"]:
                    continue
                naked_usd = (b["inv_yes"] - b["inv_no"]) * mid
                want = {"yes": (b["yes"], yes_px, yes_sh),
                        "no": (b["no"], no_px, no_sh)}
                if naked_usd > MAX_INV_USD:
                    want.pop("yes")   # long YES already — only quote the balancer
                elif naked_usd < -MAX_INV_USD:
                    want.pop("no")

                for side, (tok, px, sh) in want.items():
                    o = b["orders"].get(side)
                    if o and abs(o["px"] - px) < b["tick"] / 2 and o.get("id"):
                        continue  # still correctly placed
                    if o and LIVE and o.get("id") and not cancel_one(o["id"]):
                        continue  # old order may still rest — keep tracking it
                    if LIVE:
                        oid = post_buy(tok, px, sh, b["neg_risk"], b["tick"])
                        if oid is None:
                            # old order (if any) is cancelled and the new post
                            # failed: nothing rests on this side — say so,
                            # rather than tracking a phantom id=None entry
                            # (the 2026-07-03 stale-order bug).
                            b["orders"].pop(side, None)
                            continue
                    else:
                        oid = None
                        _say(f"  dry: {side:>3} BUY {sh:>8.2f}sh @{px:.3f}  {b['q'][:38]}")
                    b["orders"][side] = {"id": oid, "px": px, "shares": sh, "matched": 0.0}
                for side in ("yes", "no"):
                    if side not in want and side in b["orders"]:
                        # stop quoting a side => pull its resting bid too
                        # (previously it was dropped from tracking but left
                        # live on the exchange — same stale-order family).
                        o = b["orders"][side]
                        if LIVE and o.get("id") and not cancel_one(o["id"]):
                            continue
                        b["orders"].pop(side, None)

            # one-time direct confirmation that live quotes actually score.
            # The scorer samples per-minute: a just-posted order reads false
            # (observed 2026-07-02: false at +5s, true at +8min) — so wait a
            # cycle after the first orders appear before asking.
            if LIVE and not scoring_checked:
                oids = [o["id"] for b in basket for o in b["orders"].values() if o.get("id")]
                if oids and (scoring_cycles := scoring_cycles + 1) >= 2:
                    scoring_checked = True
                    try:
                        from py_clob_client_v2.clob_types import OrdersScoringParams
                        sc = pmc().clob().are_orders_scoring(OrdersScoringParams(orderIds=oids))
                        log_event({"ev": "scoring_check", "resp": sc})
                        # need-to-know only: alert when quotes AREN'T earning
                        if not all((sc or {}).values()):
                            notify(f"LP quoter: quotes NOT scoring for rewards: {sc}")
                        else:
                            _say("scoring check: all quotes earning")
                    except Exception as exc:
                        _say(f"scoring check failed: {exc}")

            if LIVE:
                report_payouts(payout_state)
            log_event({"ev": "cycle",
                       "quotes": sum(len(b["orders"]) for b in basket),
                       "mids": {b["q"][:30]: b["last_mid"] for b in basket}})
            if once:
                _say("--once done")
                cancel_all("--once exit")
                return
            time.sleep(max(1.0, CYCLE_S - (time.time() - t0)))
    except KeyboardInterrupt:
        _say("interrupted")
    except Exception as exc:
        log_event({"ev": "crash", "err": str(exc)[:300]})
        notify(f"LP quoter CRASHED: {exc}. Cancelling all orders.")
        raise
    finally:
        cancel_all("shutdown")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", help="one cycle, then exit")
    args = ap.parse_args()
    run(once=args.once)


if __name__ == "__main__":
    main()
