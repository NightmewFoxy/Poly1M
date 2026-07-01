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

Must run from a residential IP (orders 403 from cloud IPs — CLAUDE.md #1).

Usage:
  python lp_quoter.py            # dry run, loop (safe anywhere)
  python lp_quoter.py --once     # one cycle, then exit
  LP_LIVE=1 python lp_quoter.py  # real orders (home PC, funded account)
Rails (env): LP_USD_PER_SIDE (25), LP_MAX_MARKETS (5), LP_DELTA_CENTS (1.0),
LP_PULL_CENTS (2.0), LP_MAX_INV_USD (2x per-side), LP_MARKETS (pin basket by
comma-separated condition_ids, skips the screen).
"""
from __future__ import annotations

import os

# Env fixes BEFORE importing config (same preamble as arb_executor.py, and for
# the same reasons): NO-side bids price near $0.9x, above the old MAX_PRICE
# cap; orders must egress direct from the home IP, not the stale proxy.
os.environ["MAX_PRICE"] = "0.999"
os.environ["OUTBOUND_PROXY"] = ""
os.environ["POLYMARKET_PROXY_URL"] = ""
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
    os.environ.pop(_k, None)

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
MAX_JUMPS_14D = int(os.getenv("LP_MAX_JUMPS_14D", "8"))  # hourly moves >= 2c
PIN_MARKETS = [c for c in os.getenv("LP_MARKETS", "").split(",") if c.strip()]

KILL_FILE = config.DATA_DIR / "STOP_LP"
LEDGER = config.DATA_DIR / "lp_quoter_log.jsonl"
CLOB = "https://clob.polymarket.com"

_HTTP = httpx.Client(trust_env=False, timeout=30)


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
        if USD_PER_SIDE / max(mid - DELTA, 0.01) < minsize or \
           USD_PER_SIDE / max(1 - mid - DELTA, 0.01) < minsize:
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


def cancel_all(reason: str) -> None:
    if not LIVE:
        return
    for attempt in range(3):
        try:
            pmc().clob().cancel_all()
            _say(f"cancel_all ok ({reason})")
            log_event({"ev": "cancel_all", "reason": reason})
            return
        except Exception as exc:
            _say(f"cancel_all attempt {attempt + 1} failed: {exc}")
            time.sleep(2)
    notify("LP quoter: cancel_all FAILED 3x — check open orders in the UI NOW")


def post_buy(token_id: str, price: float, shares: float,
             neg_risk: bool, tick: float) -> str | None:
    """Sign+post a GTC BUY. Returns order id, or None on failure."""
    from py_clob_client_v2.clob_types import OrderArgs, OrderType, PartialCreateOrderOptions
    from py_clob_client_v2.order_builder.constants import BUY
    args = OrderArgs(token_id=token_id, price=round(price, 4),
                     size=round(shares, 2), side=BUY)
    opts = PartialCreateOrderOptions(
        neg_risk=neg_risk, tick_size=("0.001" if tick < 0.01 else "0.01"))
    try:
        signed = pmc().clob().create_order(args, options=opts)
        resp = pmc().clob().post_order(signed, OrderType.GTC)
        oid = (resp or {}).get("orderID") or (resp or {}).get("orderId")
        return str(oid) if oid else None
    except Exception as exc:
        _say(f"post_buy failed {token_id[:10]} @{price}: {exc}")
        log_event({"ev": "post_error", "token": token_id, "err": str(exc)[:200]})
        return None


def order_matched(order_id: str) -> float:
    """Filled size of an order (0.0 if still resting or lookup fails)."""
    try:
        o = pmc().clob().get_order(order_id)
        return float((o or {}).get("size_matched") or 0)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def snap(price: float, tick: float) -> float:
    return round(round(price / tick) * tick, 4)


def run(once: bool = False) -> None:
    mode = "LIVE" if LIVE else "DRY RUN"
    basket = select_basket()
    if not basket:
        _say("no markets passed the screen — nothing to quote")
        return
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
    if LIVE:
        cancel_all("startup clean slate")
        notify(f"LP quoter LIVE: {len(basket)} markets, ${USD_PER_SIDE}/side. "
               f"Kill: create data/STOP_LP.")
    atexit.register(cancel_all, "atexit")
    scoring_checked = False

    try:
        while True:
            t0 = time.time()
            if KILL_FILE.exists():
                _say("STOP_LP found — shutting down")
                cancel_all("STOP_LP")
                notify("LP quoter stopped via STOP_LP. All orders cancelled.")
                return
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
                        if LIVE and o.get("id"):
                            try:
                                pmc().clob().cancel_order(o["id"])
                            except Exception:
                                pass
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
                        notify(f"LP fill: {side.upper()} {got:.1f}sh @{o['px']} "
                               f"{b['q'][:40]} | sets={sets:.0f} naked={naked:.0f}sh")

                # desired quotes (both are BUYS: YES bid + NO bid == YES ask)
                yes_px = snap(mid - DELTA, b["tick"])
                no_px = snap((1 - mid) - DELTA, b["tick"])
                yes_sh = round(USD_PER_SIDE / max(yes_px, 0.01), 2)
                no_sh = round(USD_PER_SIDE / max(no_px, 0.01), 2)
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
                    if o and LIVE and o.get("id"):
                        try:
                            pmc().clob().cancel_order(o["id"])
                        except Exception:
                            pass
                    if LIVE:
                        oid = post_buy(tok, px, sh, b["neg_risk"], b["tick"])
                    else:
                        oid = None
                        _say(f"  dry: {side:>3} BUY {sh:>8.2f}sh @{px:.3f}  {b['q'][:38]}")
                    b["orders"][side] = {"id": oid, "px": px, "shares": sh, "matched": 0.0}
                for side in ("yes", "no"):
                    if side not in want and side in b["orders"]:
                        b["orders"].pop(side, None)

            # one-time direct confirmation that live quotes actually score
            if LIVE and not scoring_checked:
                oids = [o["id"] for b in basket for o in b["orders"].values() if o.get("id")]
                if oids:
                    scoring_checked = True
                    try:
                        sc = pmc().clob().are_orders_scoring({"orderIds": oids})
                        log_event({"ev": "scoring_check", "resp": sc})
                        notify(f"LP quoter scoring check: {sc}")
                    except Exception as exc:
                        _say(f"scoring check failed: {exc}")

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
