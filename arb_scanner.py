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
import sys
import time

import httpx

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

# Treat an edge as actionable only above this, to leave room for slippage/gas.
MIN_EDGE_CENTS = 0.5

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
        try:
            toks = json.loads(m.get("clobTokenIds") or "[]")
        except Exception:
            continue
        if len(toks) != 2:
            continue
        pairs.append({"q": _ascii((m.get("question") or "?")[:70]),
                      "yes": toks[0], "no": toks[1],
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
        hits.append({"kind": "BINARY_MERGE", "edge_cents": round(edge_c, 2),
                     "cost": round(cost, 4), "depth_sets": round(depth, 1),
                     "max_profit_usd": round(edge_c / 100 * depth, 2),
                     "title": p["q"], "vol24": p["vol24"]})
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
        mkts = [m for m in (e.get("markets") or []) if m.get("active") and not m.get("closed")]
        no_tokens = []
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
        hits.append({"kind": "NEGRISK_CONVERT", "edge_cents": round(edge_c, 2),
                     "cost": round(cost, 4), "n_outcomes": n,
                     "depth_sets": round(depth, 1),
                     "max_profit_usd": round(edge_c / 100 * depth, 2),
                     "title": _ascii((e.get("title") or "?")[:70]),
                     "vol24": float(e.get("volume24hr") or 0)})
    return hits


def run_once(verbose: bool = True) -> list[dict]:
    hits = scan_binary_merge() + scan_negrisk_convert()
    hits.sort(key=lambda h: -h["max_profit_usd"])
    if verbose or hits:
        print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} | {len(hits)} arb hits "
              f"(edge >= {MIN_EDGE_CENTS}c) ===")
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
