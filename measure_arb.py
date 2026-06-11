"""Measure real-world arb opportunity flow: how many $/day is actually there?

Loops arb_scanner's scans, re-verifies each hit via arb_scanner.confirm_hits
(simultaneous book re-fetch ~2s later — kills phantom edges from chunked
snapshots), and appends confirmed hits to <DATA_DIR>/arb_log_v2.jsonl with a
timestamp. Analysis dedupes by (kind, title) "episodes" — an opportunity that
persists across consecutive scans counts once per episode, because you'd
capture its depth once and then it's gone for you until it replenishes.

Run modes:
  python measure_arb.py                      # scan every 60s forever, log hits
  python measure_arb.py --hours 24 --notify  # Railway mode: measure 24h, then
                                             # Telegram the report + verdict
  python measure_arb.py --report             # summarize the log so far
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

import arb_scanner

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR") or "./data")
# v2 = confirmed methodology (per-hit simultaneous re-check, acceptingOrders
# filter, min depth). v1 data is contaminated by phantom edges — never mix.
LOG = DATA_DIR / "arb_log_v2.jsonl"
SCAN_INTERVAL = 60
# Working-capital tiers for reporting: an opportunity's capture is
# min(depth, capital/set_cost) sets — depth caps what extra money can buy.
CAPITAL_TIERS = (100.0, 1000.0, 10000.0)
# Verdict thresholds on PERSISTENT capturable $/day with $100 (episodes seen
# in >=2 consecutive scans — blips a 60s home-IP bot can't realistically hit
# are excluded from the decision).
VERDICT_GOOD_USD_DAY = 2.0
VERDICT_MARGINAL_USD_DAY = 0.5


def _say(msg: str) -> None:
    print(msg, flush=True)


def send_telegram(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        _say("Telegram env missing; cannot notify")
        return False
    try:
        r = httpx.Client(trust_env=False, timeout=15).post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text[:4000],
                  "disable_web_page_preview": True},
        )
        return r.status_code == 200
    except Exception as exc:
        _say(f"Telegram send failed: {exc}")
        return False


def measure(hours: float | None = None) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + hours * 3600 if hours else None
    _say(f"Logging arb hits to {LOG} every {SCAN_INTERVAL}s"
         + (f" for {hours}h" if hours else " until stopped"))
    while deadline is None or time.time() < deadline:
        t0 = time.time()
        try:
            raw = arb_scanner.scan_binary_merge() + arb_scanner.scan_negrisk_convert()
            hits = arb_scanner.confirm_hits(raw)
        except Exception as exc:
            print(f"scan failed: {exc}", file=sys.stderr, flush=True)
            raw, hits = [], []
        now = int(time.time())
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now, "scan": True, "n": len(hits),
                                "raw": len(raw)}) + "\n")
            for h in hits:
                f.write(json.dumps({"ts": now, **h}) + "\n")
        if hits:
            _say(f"{time.strftime('%H:%M:%S')} {len(hits)} hits: "
                 + ", ".join(f"{h['title'][:30]} ({h['edge_cents']}c x {h['depth_sets']})"
                             for h in hits))
        time.sleep(max(5.0, SCAN_INTERVAL - (time.time() - t0)))


def analyze() -> dict | None:
    """Parse the log into deduped opportunity episodes + summary stats."""
    if not LOG.exists():
        return None
    scans = 0
    raw_total = conf_total = 0
    prev_scan_ts = 0
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
            raw_total += r.get("raw", r.get("n", 0))
            conf_total += r.get("n", 0)
            # An episode stays open only if seen in CONSECUTIVE scans — a hit
            # that vanishes and reappears minutes later is two blips, not one
            # persistent opportunity.
            for k in list(open_eps):
                if open_eps[k]["last_seen"] < prev_scan_ts:
                    episodes.append(open_eps.pop(k))
            prev_scan_ts = ts
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
        return {"scans": scans, "hours": 0, "episodes": []}

    def capturable(e: dict, capital: float) -> float:
        affordable = capital / max(e["cost"], 0.01)
        return min(affordable, e["depth"]) * e["edge"] / 100

    hours = (last_ts - first_ts) / 3600
    persistent = [e for e in episodes if e["last_seen"] > e["first_seen"]]
    return {
        "scans": scans, "hours": hours, "episodes": episodes,
        "raw_total": raw_total, "conf_total": conf_total,
        "persistent": persistent,
        "theoretical": sum(e["max_profit"] for e in episodes),
        "tiers": {c: sum(capturable(e, c) for e in episodes) for c in CAPITAL_TIERS},
        "tiers_persistent": {c: sum(capturable(e, c) for e in persistent)
                             for c in CAPITAL_TIERS},
        "capturable": capturable,
    }


def build_report() -> str:
    s = analyze()
    if not s:
        return "No arb log found — measurement never started."
    if not s["episodes"]:
        return (f"Arb measurement: {s['scans']} scans, ZERO opportunities above "
                f"{arb_scanner.MIN_EDGE_CENTS}c edge. Verdict: NOT worth doing.")
    h = s["hours"]
    raw, conf = s.get("raw_total", 0), s.get("conf_total", 0)
    survive = f"{conf / raw * 100:.0f}%" if raw else "n/a"
    lines = [
        "ARB FLOW REPORT v2 (confirmed-edge methodology)",
        f"Window: {h:.1f}h | scans: {s['scans']} | opportunities: {len(s['episodes'])}"
        f" ({len(s['persistent'])} persistent, consecutive scans)",
        f"Re-check survival: {raw} raw -> {conf} confirmed ({survive}) — the gap "
        f"is what v1 wrongly counted as profit.",
        "",
        "Capturable, scaled to $/day (all | persistent-only):",
    ]
    for c in CAPITAL_TIERS:
        all_d = s["tiers"][c] / h * 24
        per_d = s["tiers_persistent"][c] / h * 24
        lines.append(f"  ${c:,.0f} capital: ${all_d:.2f}/day | ${per_d:.2f}/day")
    per100 = s["tiers_persistent"][100.0] / h * 24
    if per100 >= VERDICT_GOOD_USD_DAY:
        verdict = (f"VERDICT: PROVEN - ~${per100:.2f}/day persistent on $100, and "
                   f"these edges survived a simultaneous re-check, so they were "
                   f"really fillable. BUILD THE EXECUTOR AND RUN IT NOW. "
                   f"(It must trade from the home PC - cloud IPs are geoblocked. "
                   f"No profit happens until the executor exists; this was only "
                   f"the measurement.)")
    elif per100 >= VERDICT_MARGINAL_USD_DAY:
        verdict = (f"VERDICT: MARGINAL (~${per100:.2f}/day persistent on $100). "
                   f"Real but thin. Worth it only if you enjoy the build; "
                   f"expect beer money.")
    else:
        verdict = (f"VERDICT: NO (~${per100:.2f}/day persistent on $100). "
                   f"v1's $30.88/day was phantom edges - once re-checked on "
                   f"simultaneous books, the flow is too thin vs the "
                   f"competition. Skip the executor.")
    lines += ["", verdict, "", "Top opportunities seen:"]
    for e in sorted(s["episodes"], key=lambda e: -e["max_profit"])[:8]:
        dur = (e["last_seen"] - e["first_seen"]) / 60
        lines.append(f"  ${e['max_profit']:.2f} edge={e['edge']:.1f}c "
                     f"{dur:.0f}m {e['title'][:40]}")
    lines += ["", "Notes: every hit re-verified ~2s later on a single "
              "simultaneous book fetch; paused markets (acceptingOrders=false) "
              "and sub-5-share depths excluded; 'persistent' = survived in "
              "consecutive 60s scans. Still assumes 100% fill at displayed "
              "depth and zero trading fees - the executor must read each "
              "market's fee rate before trusting an edge."]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="summarize log and exit")
    ap.add_argument("--hours", type=float, default=0,
                    help="stop measuring after this many hours")
    ap.add_argument("--notify", action="store_true",
                    help="send the report to Telegram when measurement ends")
    args = ap.parse_args()

    if args.report:
        _say(build_report())
        return

    if args.notify:
        send_telegram(
            f"Arb-flow measurement v2 started ({args.hours or 'unbounded'}h, "
            f"scan every {SCAN_INTERVAL}s). v2 re-checks every hit on a "
            f"simultaneous book snapshot and skips paused markets, so this "
            f"number is trustworthy where v1's $30.88/day was not. Report + "
            f"verdict will arrive here when it finishes."
        )
    measure(hours=args.hours or None)
    report = build_report()
    _say(report)
    if args.notify:
        ok = send_telegram(report)
        _say(f"Telegram report sent: {ok}")


if __name__ == "__main__":
    main()
