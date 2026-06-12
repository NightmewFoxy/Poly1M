"""Capture confirmed binary-merge arbs with real (tiny) orders.

v1 scope, deliberately narrow:
  - BINARY_MERGE only. Neg-risk converts need N simultaneous legs plus an
    on-chain convertPositions through the proxy wallet — not worth building
    for a $3 test bankroll.
  - Hold to resolution instead of CTF mergePositions: a filled YES+NO pair
    pays $1/set when the market resolves, no on-chain plumbing needed.
    Capital is locked until then; winnings are claimed in the Polymarket UI.
  - Legging is THE risk. Orders are FAK with the live ask as a hard price
    cap (zero slippage allowance): if the book moved, we get a $0 NoFill
    instead of a worse price. If leg 1 fills and leg 2 misses, we chase
    leg 2 up to breakeven, and failing that unwind leg 1 at the bid.

Must run from a residential IP — Polymarket 403s order placement from
cloud/datacenter IPs (scanner reads work anywhere). Ignores the old bot's
TRADING_ENABLED flag on purpose; this executor's kill switch is the
data/STOP_ARB file.

Usage:
  python arb_executor.py            # trade live, loop every 45s
  python arb_executor.py --once     # one cycle, then exit (plumbing check)
Rails (env): ARB_MAX_EXPOSURE (default 3 USD), ARB_MAX_PER_OPP (default 3),
ARB_MIN_EDGE_CENTS (default 1.0).
"""
from __future__ import annotations

import os

# Env fixes BEFORE importing config (it reads env once at import time):
# - the old sniper's MAX_PRICE=0.80 would block arb legs priced above 80c
#   (place_market_buy clamps its price cap to config.MAX_PRICE);
# - OUTBOUND_PROXY in .env routes orders through a stale datacenter proxy;
#   from the home IP we must connect direct. Setting "" wins over
#   load_dotenv, which never overrides keys that already exist.
os.environ["MAX_PRICE"] = "0.999"
os.environ["OUTBOUND_PROXY"] = ""
os.environ["POLYMARKET_PROXY_URL"] = ""
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
    os.environ.pop(_k, None)

import argparse
import asyncio
import json
import time

import httpx

import arb_scanner
import config
import polymarket_client as pmc
from arb_scanner import best_ask, get_books

SCAN_INTERVAL = 45
# Execution needs more edge than detection: the final snapshot, order
# latency, and dust all eat into it.
EXEC_MIN_EDGE_CENTS = float(os.getenv("ARB_MIN_EDGE_CENTS", "1.0"))
MAX_PER_OPP_USD = float(os.getenv("ARB_MAX_PER_OPP", "3.0"))
MAX_TOTAL_EXPOSURE_USD = float(os.getenv("ARB_MAX_EXPOSURE", "3.0"))
MIN_LEG_NOTIONAL_USD = 1.05  # CLOB rejects market orders under $1
KILL_FILE = config.DATA_DIR / "STOP_ARB"
STATE_FILE = config.DATA_DIR / "arb_positions.json"
LEDGER = config.DATA_DIR / "arb_executor_log.jsonl"

# Markets already telegram'd as "too small for the bankroll" this run,
# so a persistent opportunity doesn't ping the phone every 45s.
_skip_notified: set[str] = set()


def _say(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def notify(text: str) -> None:
    try:
        httpx.Client(trust_env=False, timeout=15).post(
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


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"open": [], "naked": []}


def save_state(st: dict) -> None:
    STATE_FILE.write_text(json.dumps(st, indent=2), encoding="utf-8")


def open_exposure(st: dict) -> float:
    return sum(p["cost_usd"] for p in st["open"]) + \
        sum(p.get("cost_usd", 0) for p in st["naked"])


def best_bid(book: dict | None) -> float | None:
    bids = (book or {}).get("bids") or []
    if not bids:
        return None
    return float(max(bids, key=lambda b: float(b["price"]))["price"])


async def sell_at_bid(token: str, shares: float, neg_risk: bool,
                      tick: float) -> dict | None:
    """Best-effort market sell; returns fill dict or None."""
    for attempt in range(3):
        bid = best_bid(get_books([token]).get(token))
        if bid is None:
            await asyncio.sleep(2)
            continue
        try:
            return await pmc.place_market_sell(
                token, shares, target_price=bid,
                neg_risk=neg_risk, tick_size=tick, max_slippage_ticks=2)
        except pmc.NoFillError:
            await asyncio.sleep(2)
    return None


async def retry_naked(st: dict) -> None:
    """Try again to dump legs we got stuck holding. While any exist, the
    executor takes no new positions."""
    for p in list(st["naked"]):
        r = await sell_at_bid(p["token"], p["shares"], p["neg_risk"], p["tick"])
        if r is None:
            continue
        pnl = r["usd_received"] - p["cost_usd"]
        st["naked"].remove(p)
        save_state(st)
        log_event({"ev": "naked_unwound", "title": p["title"],
                   "pnl_usd": round(pnl, 4)})
        notify(f"Naked leg unwound: {p['title'][:50]} — sold "
               f"{p['shares']:.2f} sh, P&L ${pnl:+.2f}. Trading resumes.")


async def try_capture(hit: dict, st: dict) -> None:
    yes_t, no_t = hit["tokens"]
    # Final snapshot, both legs in one request, immediately before firing.
    books = get_books(hit["tokens"])
    ya, ysz = best_ask(books.get(yes_t))
    na, nsz = best_ask(books.get(no_t))
    if ya is None or na is None:
        return
    cost = ya + na
    edge_c = (1.0 - cost) * 100
    if edge_c < EXEC_MIN_EDGE_CENTS:
        log_event({"ev": "faded", "title": hit["title"], "edge_c": round(edge_c, 2)})
        return

    budget = min(MAX_PER_OPP_USD, MAX_TOTAL_EXPOSURE_USD - open_exposure(st))
    sets = min(ysz, nsz, budget / cost)
    # Exchange minimum: every leg must be >= ~$1 notional.
    min_sets = max(MIN_LEG_NOTIONAL_USD / ya, MIN_LEG_NOTIONAL_USD / na)
    if sets < min_sets:
        if min_sets * cost <= budget and min_sets <= min(ysz, nsz):
            sets = min_sets
        else:
            if hit["title"] not in _skip_notified:
                _skip_notified.add(hit["title"])
                need = min_sets * cost
                notify(f"Arb seen but SKIPPED (bankroll): {hit['title'][:50]} "
                       f"edge={edge_c:.1f}c needs ${need:.2f} for the exchange "
                       f"minimum, budget left ${budget:.2f}. Top up to capture "
                       f"these.")
            log_event({"ev": "too_small", "title": hit["title"],
                       "edge_c": round(edge_c, 2), "budget": round(budget, 2)})
            return
    sets = int(sets * 100) / 100

    meta = await pmc.get_market_meta(hit.get("condition_id") or "") or {}
    if meta and not meta.get("accepting_orders", True):
        log_event({"ev": "paused", "title": hit["title"]})
        return
    neg_risk = bool(meta.get("neg_risk", False))
    tick = float(meta.get("tick_size", 0.01))

    # Thinner leg first: it's the one most likely to vanish.
    legs = sorted([(yes_t, ya, ysz), (no_t, na, nsz)], key=lambda l: l[2])
    (t1, p1, _), (t2, p2, _) = legs
    try:
        r1 = await pmc.place_market_buy(
            t1, target_price=p1, stake_usd=round(sets * p1, 2),
            neg_risk=neg_risk, tick_size=tick, max_slippage_ticks=0)
    except pmc.NoFillError:
        log_event({"ev": "miss_leg1", "title": hit["title"],
                   "edge_c": round(edge_c, 2)})
        _say(f"missed leg1 {hit['title'][:40]}")
        return
    s1, paid1 = r1["size_shares"], r1["limit_price"]

    # Leg 2: aim for s1 shares at the seen ask; if that fails, chase up to
    # breakeven (any price <= 1 - paid1 still can't lose at resolution).
    r2 = None
    try:
        r2 = await pmc.place_market_buy(
            t2, target_price=p2, stake_usd=max(round(s1 * p2, 2), 1.0),
            neg_risk=neg_risk, tick_size=tick, max_slippage_ticks=0)
    except pmc.NoFillError:
        chase = round(1.0 - paid1 - 0.002, 4)
        if chase > p2:
            try:
                r2 = await pmc.place_market_buy(
                    t2, target_price=chase, stake_usd=max(round(s1 * chase, 2), 1.0),
                    neg_risk=neg_risk, tick_size=tick, max_slippage_ticks=0)
            except pmc.NoFillError:
                pass

    if r2 is None:
        # Stuck with a one-sided position: unwind at the bid.
        sold = await sell_at_bid(t1, s1, neg_risk, tick)
        if sold is not None:
            pnl = sold["usd_received"] - r1["stake_usd"]
            log_event({"ev": "unwound", "title": hit["title"],
                       "pnl_usd": round(pnl, 4)})
            notify(f"Arb leg missed, unwound: {hit['title'][:50]} "
                   f"P&L ${pnl:+.2f} (cost of legging risk).")
        else:
            st["naked"].append({"token": t1, "shares": s1, "cost_usd":
                                r1["stake_usd"], "title": hit["title"],
                                "neg_risk": neg_risk, "tick": tick,
                                "ts": int(time.time())})
            save_state(st)
            log_event({"ev": "naked", "title": hit["title"],
                       "cost_usd": r1["stake_usd"]})
            notify(f"WARNING: holding a naked leg of {hit['title'][:50]} "
                   f"(${r1['stake_usd']:.2f}). Couldn't sell back — will keep "
                   f"retrying; no new trades until it's cleared.")
        return

    s2, paid2 = r2["size_shares"], r2["limit_price"]
    pairs = min(s1, s2)
    pair_cost = pairs * (paid1 + paid2)
    locked = pairs * 1.0 - pair_cost
    st["open"].append({"title": hit["title"], "sets": round(pairs, 4),
                       "cost_usd": round(pair_cost, 4),
                       "locked_profit_usd": round(locked, 4),
                       "tokens": hit["tokens"], "ts": int(time.time())})
    save_state(st)
    log_event({"ev": "captured", "title": hit["title"], "sets": round(pairs, 4),
               "cost_usd": round(pair_cost, 4), "locked_usd": round(locked, 4),
               "paid": [round(paid1, 4), round(paid2, 4)]})
    notify(f"ARB CAPTURED: {hit['title'][:50]}\n{pairs:.2f} sets at "
           f"{(paid1 + paid2):.4f} — locked profit ${locked:.2f} "
           f"({locked / pair_cost * 100:.1f}%). Pays $1/set at resolution; "
           f"claim in the Polymarket UI.")

    # FAK partials can leave one side with extra shares; sell the excess if
    # it's big enough to be an order, otherwise note the dust and move on.
    excess_t, excess, excess_paid = (
        (t1, s1 - pairs, paid1) if s1 > s2 else (t2, s2 - pairs, paid2))
    if excess * excess_paid >= MIN_LEG_NOTIONAL_USD:
        sold = await sell_at_bid(excess_t, excess, neg_risk, tick)
        log_event({"ev": "excess_sold" if sold else "excess_stuck",
                   "title": hit["title"], "shares": round(excess, 4)})
    elif excess > 0.01:
        log_event({"ev": "dust", "title": hit["title"],
                   "shares": round(excess, 4),
                   "usd": round(excess * excess_paid, 4)})


async def cycle(st: dict) -> None:
    if st["naked"]:
        await retry_naked(st)
        if st["naked"]:
            return  # still stuck — don't open new risk
    raw = await asyncio.to_thread(arb_scanner.scan_binary_merge)
    hits = await asyncio.to_thread(arb_scanner.confirm_hits, raw)
    if hits:
        _say(f"{len(hits)} confirmed binary hits ({len(raw)} raw)")
    for hit in sorted(hits, key=lambda h: -h["edge_cents"]):
        if MAX_TOTAL_EXPOSURE_USD - open_exposure(st) < 1.0:
            _say("exposure cap reached; watching only")
            break
        try:
            await try_capture(hit, st)
        except Exception as exc:
            log_event({"ev": "error", "title": hit["title"], "err": str(exc)[:300]})
            notify(f"Arb executor error on {hit['title'][:40]}: {exc}"[:500])


async def main_async(once: bool) -> None:
    st = load_state()
    bal = await pmc.get_usdc_balance()
    locked = sum(p["cost_usd"] for p in st["open"])
    notify(f"Arb executor LIVE on home IP. Balance ${bal if bal is not None else '?'}"
           f", already locked ${locked:.2f}. Rails: ${MAX_PER_OPP_USD:.0f}/opp, "
           f"${MAX_TOTAL_EXPOSURE_USD:.0f} total, edge>={EXEC_MIN_EDGE_CENTS}c, "
           f"binary-merge only. Kill switch: create data/STOP_ARB.")
    while True:
        if KILL_FILE.exists():
            notify("STOP_ARB found — arb executor shut down.")
            return
        t0 = time.time()
        try:
            await cycle(st)
        except Exception as exc:
            _say(f"cycle failed: {exc}")
            log_event({"ev": "cycle_error", "err": str(exc)[:300]})
        if once:
            _say("single cycle done")
            return
        await asyncio.sleep(max(5.0, SCAN_INTERVAL - (time.time() - t0)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", help="one cycle, then exit")
    args = ap.parse_args()
    asyncio.run(main_async(once=args.once))


if __name__ == "__main__":
    main()
