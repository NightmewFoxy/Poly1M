"""Measure real-world arb opportunity flow: how many $/day is actually there?

Loops arb_scanner's scans and appends every hit to data/arb_log.jsonl with a
timestamp. Analysis dedupes by (kind, title) "episodes" — an opportunity that
persists across consecutive scans counts once per episode, because you'd
capture its depth once and then it's gone for you until it replenishes.

Run:    python measure_arb.py              # scan every 60s forever, log hits
Report: python measure_arb.py --report     # summarize the log into $/day
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import arb_scanner

LOG = Path("data/arb_log.jsonl")
SCAN_INTERVAL = 60
# Working-capital tiers for --report: an opportunity's capture is
# min(depth, capital/set_cost) sets — depth caps what extra money can buy.
CAPITAL_TIERS = (100.0, 1000.0, 10000.0)


def measure() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    print(f"Logging arb hits to {LOG} every {SCAN_INTERVAL}s. Ctrl+C to stop.")
    while True:
        t0 = time.time()
        try:
            hits = arb_scanner.scan_binary_merge() + arb_scanner.scan_negrisk_convert()
        except Exception as exc:
            print(f"scan failed: {exc}", file=sys.stderr)
            hits = []
        now = int(time.time())
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now, "scan": True, "n": len(hits)}) + "\n")
            for h in hits:
                f.write(json.dumps({"ts": now, **h}) + "\n")
        if hits:
            print(f"{time.strftime('%H:%M:%S')} {len(hits)} hits: "
                  + ", ".join(f"{h['title'][:30]} ({h['edge_cents']}c x {h['depth_sets']})"
                              for h in hits))
        time.sleep(max(5.0, SCAN_INTERVAL - (time.time() - t0)))


def report() -> None:
    if not LOG.exists():
        print("No log yet."); return
    scans = 0
    first_ts = last_ts = None
    episodes: list[dict] = []
    open_eps: dict[tuple, dict] = {}  # (kind,title) -> episode
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = r.get("ts", 0)
        first_ts = ts if first_ts is None else min(first_ts, ts)
        last_ts = ts if last_ts is None else max(last_ts, ts)
        if r.get("scan"):
            scans += 1
            # close episodes not seen for > 3 scan intervals
            for k in list(open_eps):
                if ts - open_eps[k]["last_seen"] > 3 * SCAN_INTERVAL:
                    episodes.append(open_eps.pop(k))
            continue
        key = (r.get("kind"), r.get("title"))
        ep = open_eps.get(key)
        if ep is None:
            open_eps[key] = {"kind": r["kind"], "title": r["title"],
                             "max_profit": r["max_profit_usd"],
                             "edge": r["edge_cents"], "depth": r["depth_sets"],
                             "cost": r.get("cost", 1.0),
                             "first_seen": ts, "last_seen": ts}
        else:
            ep["last_seen"] = ts
            ep["max_profit"] = max(ep["max_profit"], r["max_profit_usd"])
    episodes.extend(open_eps.values())

    if not episodes or not first_ts or last_ts <= first_ts:
        print(f"{scans} scans, no episodes yet."); return

    hours = (last_ts - first_ts) / 3600
    total = sum(e["max_profit"] for e in episodes)

    def capturable(e: dict, capital: float) -> float:
        # sets you can afford at this capital, capped by displayed depth
        affordable = capital / max(e["cost"], 0.01)
        return min(affordable, e["depth"]) * e["edge"] / 100

    print(f"Window: {hours:.1f}h | scans: {scans} | episodes: {len(episodes)}")
    print(f"Theoretical extractable:   ${total:.2f}  (${total / hours * 24:.2f}/day)")
    for capital in CAPITAL_TIERS:
        cap_total = sum(capturable(e, capital) for e in episodes)
        print(f"Capturable with ${capital:>6.0f}:   ${cap_total:.2f}  "
              f"(${cap_total / hours * 24:.2f}/day, "
              f"{cap_total / hours * 24 / capital * 100:.2f}%/day on capital)")
    print()
    big = CAPITAL_TIERS[-1]
    for e in sorted(episodes, key=lambda e: -e["max_profit"])[:20]:
        dur = (e["last_seen"] - e["first_seen"]) / 60
        caps = " ".join(f"${capturable(e, c):.2f}" for c in CAPITAL_TIERS)
        print(f"  {e['kind']:15} ${e['max_profit']:6.2f} (cap {caps}) "
              f"edge={e['edge']:.1f}c lasted {dur:5.1f}m  {e['title'][:50]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    report() if args.report else measure()
