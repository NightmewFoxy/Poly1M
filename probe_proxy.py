"""One-shot diagnostic for the cloud->IPRoyal tunnel path (CLAUDE.md #1).

Since 2026-07-02 ~12:50 UTC IPRoyal refuses tunnels whose SOURCE is a
hosting ASN (Railway et al): CONNECT is accepted, the upstream never
answers, every session. The same gateway+creds work from consumer-classified
sources (home PC). This script produces the evidence matrix for that
diagnosis — run it from BOTH vantages and diff:

  railway ssh -- python probe_proxy.py     # inside the Railway container
  python probe_proxy.py                    # home baseline

Tests: direct egress IP+ASN, gateway DNS, raw TCP connect to each gateway,
then a tunneled GET through each gateway (as-configured session + ONE fresh
session — deliberately few attempts; rotation spam is itself suspected of
tripping IPRoyal's abuse flag). If a tunnel works, verifies
clob.polymarket.com through it. Never prints credentials. Results also
append to DATA_DIR/proxy_probe.jsonl.
"""
from __future__ import annotations

import json
import os
import re
import socket
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

try:  # home: read .env; Railway: platform env, no .env file
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import httpx

TIMEOUT = 15.0
RESULTS: list[dict] = []


def red(url: str) -> str:
    return re.sub(r"//[^@]+@", "//***@", url)


def rec(test: str, ok: bool, detail: str) -> None:
    RESULTS.append({"test": test, "ok": ok, "detail": detail[:300]})
    print(f"{'PASS' if ok else 'FAIL'}  {test}: {detail[:200]}", flush=True)


def gateways() -> list[str]:
    base = (os.getenv("LP_VIA_PROXY") or os.getenv("OUTBOUND_PROXY") or "").strip()
    if not base:
        sys.exit("no LP_VIA_PROXY / OUTBOUND_PROXY in env — nothing to probe")
    urls = [base]
    for h in (x.strip() for x in os.getenv("LP_PROXY_ALT_HOSTS", "").split(",")):
        if h:
            alt = re.sub(r"@[^@:/]+(:\d+/?)$", f"@{h}\\1", base)
            if alt != base:
                urls.append(alt)
    return urls


def via(url: str) -> httpx.Client:
    try:
        return httpx.Client(proxy=url, timeout=TIMEOUT, trust_env=False)
    except TypeError:  # httpx < 0.26 spells it "proxies"
        return httpx.Client(proxies=url, timeout=TIMEOUT, trust_env=False)


def main() -> None:
    print(f"=== proxy probe {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} ===",
          flush=True)

    # 1. direct egress: who are we to the internet? (the thing IPRoyal judges)
    direct = httpx.Client(trust_env=False, timeout=TIMEOUT)
    try:
        ip = direct.get("https://api.ipify.org").text.strip()
        try:
            org = direct.get(f"https://ipinfo.io/{ip}/org").text.strip()
        except Exception:
            org = "?"
        rec("direct egress", True, f"{ip} ({org})")
    except Exception as exc:
        rec("direct egress", False, str(exc))

    # 2. gateway DNS as seen from here (GeoDNS gotcha: per-region answers)
    try:
        ips = sorted({a[4][0] for a in socket.getaddrinfo("geo.iproyal.com", None)})
        rec("dns geo.iproyal.com", True, ",".join(ips))
    except Exception as exc:
        rec("dns geo.iproyal.com", False, str(exc))

    # 3. per-gateway: TCP connect, tunneled GET (x2 sessions), then CLOB
    for gw in gateways():
        u = urlsplit(gw)
        host, port = u.hostname, u.port or 12321
        label = f"{host}:{port}"
        t0 = time.time()
        try:
            socket.create_connection((host, port), timeout=10).close()
            rec(f"tcp {label}", True, f"connected in {time.time() - t0:.2f}s")
        except Exception as exc:
            rec(f"tcp {label}", False, f"{exc} after {time.time() - t0:.2f}s")
            continue

        attempts = [("as-configured", gw)]
        if "_session-" in gw:
            attempts.append(
                ("fresh session",
                 re.sub(r"_session-[^_@]+", f"_session-probe{int(time.time()) % 100000}", gw)))
        tunnel_ok = None
        for name, url in attempts:
            t0 = time.time()
            try:
                with via(url) as c:
                    exit_ip = c.get("https://api.ipify.org").text.strip()
                rec(f"tunnel {label} ({name})", True,
                    f"exit {exit_ip} in {time.time() - t0:.2f}s")
                tunnel_ok = url
                break  # one working tunnel per gateway is enough
            except Exception as exc:
                rec(f"tunnel {label} ({name})", False,
                    f"{type(exc).__name__}: {exc} after {time.time() - t0:.2f}s")
            time.sleep(2)

        if tunnel_ok:
            t0 = time.time()
            try:
                with via(tunnel_ok) as c:
                    r = c.get("https://clob.polymarket.com/time")
                rec(f"clob via {label}", r.status_code == 200,
                    f"HTTP {r.status_code} in {time.time() - t0:.2f}s")
            except Exception as exc:
                rec(f"clob via {label}", False, str(exc))

    # summary + ledger
    fails = [r for r in RESULTS if not r["ok"]]
    print(f"=== {len(RESULTS) - len(fails)}/{len(RESULTS)} passed ===", flush=True)
    try:
        data_dir = Path(os.getenv("DATA_DIR", "./data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        with (data_dir / "proxy_probe.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time()), "results": RESULTS}) + "\n")
    except Exception as exc:
        print(f"(ledger write failed: {exc})", flush=True)


if __name__ == "__main__":
    main()
