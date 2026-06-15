"""Scan Polymarket for GUARANTEED-profit arbitrage (no prediction, no edge needed).

Two mechanisms, both instantly realizable (no waiting for resolution):

1. BINARY MERGE ARB
   best_ask(YES) + best_ask(NO) < $1.00 on the same binary market.
   Buy both legs, then CTF `mergePositions` fuses 1 YES + 1 NO back into
   $1.00 USDC on the spot. Profit = 1 - (yes_ask + no_ask) per set, locked
   in the moment both legs fill.

2. NEG-RISK CONVERT ARB
   In a neg-risk event (mutually exclusive outcomes, e.g. "IEM Cologne
   Winner"), at most ONE outcome can resolve YES. A full set of NO tokens
   (one per outcome) therefore always pays >= N-1 dollars — and the
   NegRiskAdapter `convertPositions` turns a full NO set into N-1 USDC
   immediately. If sum(best_ask(NO_i)) < N-1, buying every NO is free money.
   (Robust even if NO listed outcome wins: then every NO pays and you get N.)

NOT included on purpose: "buy all YES < $1" long arb. Most Polymarket
winner events have NO catch-all outcome (verified: Presidential 2028 lists
36 names, no "Other"), so all-YES can lose if an unlisted outcome wins.
That is a bet, not an arb.

Execution notes (this script only SCANS, it does not trade):
  - Edges are small (0.1c-3c per $1 set) and depth-limited. Profit per
    opportunity is typically cents to a few dollars. They recur constantly,
    especially on short-dated crypto/sports markets around volatility.
  - Both legs must fill: use FOK orders sized to min(depth) per leg, or
    accept legging risk. Books move; re-quote before sending.
  - mergePositions / convertPositions cost only Polygon gas (~cents).

Usage:
  python arb_scanner.py            # one scan, print table
  python arb_scanner.py --loop 60  # rescan every 60s, print only hits
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import httpx

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

# Treat an edge as actionable only above this, to leave room for slippage/gas.
MIN_EDGE_CENTS = 0.5

# CLOB rejects tiny orders; below ~5 shares a "hit" isn't placeable anyway.
MIN_DEPTH_SETS = 5.0

# Wait this long after the wide scan, then re-fetch a hit's legs in ONE
# request. The wide scan fetches books in chunks seconds apart, so a fast
# market can show a phantom edge (YES snapshotted before a price jump, NO
# after). Only edges that survive this near-simultaneous re-check are real.
CONFIRM_DELAY_S = 2.0

# Only count/return arbs on zero-taker-fee markets. Polymarket charges a taker
# fee on the liquid sports/Fed markets that exceeds a ~1c merge edge, turning the
# "arb" into a guaranteed loss; the fee-free markets (mostly politics) are where
# a real merge arb can exist. Default on; ARB_FEE_FREE_ONLY=0 disables (debug).
FEE_FREE_ONLY = os.getenv("ARB_FEE_FREE_ONLY", "1").lower() not in ("0", "false", "no")

# Market data is NOT geoblocked (only order placement is), so connect direct.
# trust_env=False ignores HTTPS_PROXY/OUTBOUND_PROXY left over from the
# trading bot's env — that proxy may be dead and isn't needed for reads.
_HTTP = httpx.Client(trust_env=False, timeout=30)


def _ascii(s: str) -> str:
    return (s or "").encode("ascii", "replace").decode("ascii")


def fetch_pages(path: str, params: dict, pages: int, page_size: int = 100) -> list[dict]:
    out: list[dict] = []
    for offset in range(0, pages * page_size, page_size):
        try:
            r = _HTTP.get(f"{GAMMA}{path}", params={**params, "limit": str(page_size),
                                                    "offset": str(offset)})
            r.raise_for_status()
            batch = r.json()
        except Exception as exc:
            print(f"  gamma {path} offset={offset} failed: {exc}", file=sys.stderr)
            continue
        if not batch:
            break
        out.extend(batch)
        time.sleep(0.15)
    return out


def get_books(token_ids: list[str]) -> dict[str, dict]:
    """Batch-fetch order books from CLOB POST /books."""
    out: dict[str, dict] = {}
    for i in range(0, len(token_ids), 50):
        chunk = token_ids[i:i + 50]
        try:
            r = _HTTP.post(f"{CLOB}/books", json=[{"token_id": t} for t in chunk])
            if r.status_code != 200:
                continue
            for b in r.json():
                out[str(b.get("asset_id"))] = b
        except Exception as exc:
            print(f"  books chunk failed: {exc}", file=sys.stderr)
        time.sleep(0.15)
    return out


_fee_cache: dict[str, float | None] = {}


def taker_fee(condition_id: str) -> float | None:
    """CLOB taker_base_fee for a market, cached. None if unknown/lookup fails.

    Uses the same credential-free REST path as the book fetches (market data
    isn't geoblocked). A nonzero fee invalidates a thin merge arb, and an
    unknown fee can't be trusted — callers treat both as "not fee-free".
    """
    if not condition_id:
        return None
    if condition_id in _fee_cache:
        return _fee_cache[condition_id]
    fee: float | None = None
    try:
        r = _HTTP.get(f"{CLOB}/markets/{condition_id}")
        if r.status_code == 200:
            raw = r.json().get("taker_base_fee")
            fee = float(raw) if raw is not None else None
    except Exception as exc:
        print(f"  fee lookup {condition_id[:10]} failed: {exc}", file=sys.stderr)
        fee = None
    _fee_cache[condition_id] = fee
    return fee


def best_ask(book: dict | None) -> tuple[float | None, float]:
    asks = (book or {}).get("asks") or []
    if not asks:
        return None, 0.0
    b = min(asks, key=lambda a: float(a["price"]))
    return float(b["price"]), float(b["size"])


def scan_binary_merge(pages: int = 6) -> list[dict]:
    """Find YES_ask + NO_ask < 1 on active binary markets, by 24h volume."""
    markets = fetch_pages("/markets", {
        "active": "true", "closed": "false", "archived": "false",
        "order": "volume24hr", "ascending": "false",
    }, pages)

    pairs = []
    for m in markets:
        # Paused markets (live sports around resolution) keep displaying their
        # last book — quotes you cannot hit. They look like persistent arbs.
        if m.get("acceptingOrders") is False:
            continue
        try:
            toks = json.loads(m.get("clobTokenIds") or "[]")
        except Exception:
            continue
        if len(toks) != 2:
            continue
        pairs.append({"q": _ascii((m.get("question") or "?")[:70]),
                      "yes": toks[0], "no": toks[1],
                      "cond": m.get("conditionId"),
                      "vol24": float(m.get("volume24hr") or 0)})

    books = get_books([p["yes"] for p in pairs] + [p["no"] for p in pairs])
    hits = []
    for p in pairs:
        ya, ysz = best_ask(books.get(p["yes"]))
        na, nsz = best_ask(books.get(p["no"]))
        if ya is None or na is None:
            continue
        cost = ya + na
        edge_c = (1.0 - cost) * 100
        if edge_c < MIN_EDGE_CENTS:
            continue
        depth = min(ysz, nsz)
        if depth < MIN_DEPTH_SETS:
            continue
        hits.append({"kind": "BINARY_MERGE", "edge_cents": round(edge_c, 2),
                     "cost": round(cost, 4), "depth_sets": round(depth, 1),
                     "max_profit_usd": round(edge_c / 100 * depth, 2),
                     "title": p["q"], "vol24": p["vol24"],
                     "tokens": [p["yes"], p["no"]],
                     "condition_id": p["cond"]})
    return hits


def scan_negrisk_convert(pages: int = 3, max_events: int = 60) -> list[dict]:
    """Find sum(NO asks) < N-1 across neg-risk events, by 24h volume."""
    events = fetch_pages("/events", {
        "active": "true", "closed": "false", "archived": "false",
        "order": "volume24hr", "ascending": "false",
    }, pages)
    neg = [e for e in events if e.get("negRisk") and len(e.get("markets") or []) >= 3]

    hits = []
    for e in neg[:max_events]:
        # Dropping paused/inactive outcomes is safe: converting a NO subset of
        # size k still pays k-1 cash (plus YES on the rest as a bonus).
        mkts = [m for m in (e.get("markets") or [])
                if m.get("active") and not m.get("closed")
                and m.get("acceptingOrders") is not False]
        no_tokens = []
        cond_ids = []
        ok = True
        for m in mkts:
            try:
                toks = json.loads(m.get("clobTokenIds") or "[]")
            except Exception:
                ok = False
                break
            if len(toks) != 2:
                ok = False
                break
            no_tokens.append(toks[1])
            cond_ids.append(m.get("conditionId"))
        n = len(no_tokens)
        if not ok or n < 3:
            continue
        books = get_books(no_tokens)
        asks = [best_ask(books.get(t)) for t in no_tokens]
        if any(a[0] is None for a in asks):
            continue
        cost = sum(a[0] for a in asks)
        edge_c = ((n - 1) - cost) * 100
        if edge_c < MIN_EDGE_CENTS:
            continue
        depth = min(a[1] for a in asks)
        if depth < MIN_DEPTH_SETS:
            continue
        hits.append({"kind": "NEGRISK_CONVERT", "edge_cents": round(edge_c, 2),
                     "cost": round(cost, 4), "n_outcomes": n,
                     "depth_sets": round(depth, 1),
                     "max_profit_usd": round(edge_c / 100 * depth, 2),
                     "title": _ascii((e.get("title") or "?")[:70]),
                     "vol24": float(e.get("volume24hr") or 0),
                     "tokens": no_tokens, "condition_ids": cond_ids})
    return hits


def confirm_hits(hits: list[dict]) -> list[dict]:
    """Re-verify every hit on a near-simultaneous snapshot before counting it.

    For each hit, wait CONFIRM_DELAY_S, then fetch ALL of its legs in a single
    /books request and recompute edge/depth from books that share one moment
    in time. Phantom edges from the wide scan's chunked fetches die here; the
    survivors are returned with the fresh (usually smaller) numbers.
    """
    confirmed = []
    for h in hits:
        time.sleep(CONFIRM_DELAY_S)
        books = get_books(h["tokens"])
        asks = [best_ask(books.get(t)) for t in h["tokens"]]
        if any(a[0] is None for a in asks):
            continue
        payout = 1.0 if h["kind"] == "BINARY_MERGE" else float(len(h["tokens"]) - 1)
        cost = sum(a[0] for a in asks)
        edge_c = (payout - cost) * 100
        depth = min(a[1] for a in asks)
        if edge_c < MIN_EDGE_CENTS or depth < MIN_DEPTH_SETS:
            continue
        fee: float | None = 0.0
        if FEE_FREE_ONLY:
            cids = ([h["condition_id"]] if h.get("condition_id")
                    else list(h.get("condition_ids") or []))
            fees = [taker_fee(c) for c in cids] if cids else [None]
            # A nonzero fee wipes the edge; an unverifiable fee can't be trusted.
            if any(f is None or f > 0 for f in fees):
                continue
            fee = max((f for f in fees if f is not None), default=0.0)
        confirmed.append({**h, "edge_cents": round(edge_c, 2),
                          "cost": round(cost, 4), "depth_sets": round(depth, 1),
                          "max_profit_usd": round(edge_c / 100 * depth, 2),
                          "taker_fee": fee})
    return confirmed


def run_once(verbose: bool = True) -> list[dict]:
    raw = scan_binary_merge() + scan_negrisk_convert()
    hits = confirm_hits(raw)
    hits.sort(key=lambda h: -h["max_profit_usd"])
    if verbose or hits:
        mode = "fee-free " if FEE_FREE_ONLY else ""
        print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} | {len(hits)} confirmed "
              f"{mode}arb hits ({len(raw)} raw, edge >= {MIN_EDGE_CENTS}c) ===")
        for h in hits:
            extra = f" n={h['n_outcomes']}" if "n_outcomes" in h else ""
            print(f"[{h['kind']:15}] edge={h['edge_cents']:5.2f}c/set "
                  f"depth={h['depth_sets']:8.1f} maxProfit=${h['max_profit_usd']:7.2f}"
                  f"{extra}  {h['title']}")
        if not hits:
            print("(none)")
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--loop", type=int, metavar="SECONDS", default=0,
                    help="rescan forever at this interval")
    args = ap.parse_args()
    if args.loop > 0:
        while True:
            try:
                run_once(verbose=False)
            except Exception as exc:
                print(f"scan failed: {exc}", file=sys.stderr)
            time.sleep(args.loop)
    else:
        run_once()


if __name__ == "__main__":
    main()
