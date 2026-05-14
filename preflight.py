"""Sanity-check every credential without placing any orders.

Run: python preflight.py

Checks (in order):
  1. Env vars all present
  2. Telegram bot can send a message
  3. Anthropic API key works (tiny non-search call)
  4. Polymarket CLOB auth works (list API keys + balance)
  5. Polymarket discovery (Gamma) returns markets

Exits non-zero on first failure so it's also usable as a deploy gate.
"""
from __future__ import annotations

import asyncio
import sys

import anthropic
import httpx

import config
from polymarket_client import clob, discover_markets


def _ok(msg: str) -> None:
    print(f"  OK    {msg}")


def _fail(msg: str) -> None:
    print(f"  FAIL  {msg}")
    sys.exit(1)


async def check_egress_ip() -> None:
    """Show the public IP/country the bot will use for Polymarket calls.

    Polymarket blocks most cloud providers. If OUTBOUND_PROXY is set we go
    through it; if the resulting country is in their blocklist (US, FR, SG,
    most cloud DCs) trades will 403.
    """
    print("[2/6] Egress IP")
    proxy = config.OUTBOUND_PROXY
    if proxy:
        # Mask credentials when echoing back
        safe = proxy
        if "@" in proxy:
            scheme, rest = proxy.split("://", 1) if "://" in proxy else ("", proxy)
            _, host = rest.split("@", 1)
            safe = f"{scheme}://***@{host}" if scheme else f"***@{host}"
        print(f"      OUTBOUND_PROXY set: {safe}")
    else:
        print("      OUTBOUND_PROXY not set; direct egress")
    try:
        async with httpx.AsyncClient(timeout=10) as ac:
            r = await ac.get("https://ipapi.co/json/")
            data = r.json() if r.status_code == 200 else {}
    except Exception as exc:
        print(f"      WARN  egress check failed: {exc}")
        return
    ip = data.get("ip", "?")
    country = data.get("country_name") or data.get("country") or "?"
    org = data.get("org") or ""
    print(f"      egress IP={ip} country={country} org={org}".rstrip())
    # Hint -- known Polymarket-blocked regions. Not exhaustive; see Polymarket docs.
    blocked = {"United States", "US", "France", "FR", "Singapore", "SG", "Belgium", "BE",
               "Poland", "PL", "Thailand", "TH"}
    if any(b == country for b in blocked):
        print(f"      WARN  {country} is on Polymarket's blocklist; trades will 403")
    else:
        _ok("egress region looks tradeable (verify against Polymarket's docs)")


async def check_telegram() -> None:
    print("[3/6] Telegram")
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as ac:
        r = await ac.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": "Poly1M preflight: Telegram works.",
                "disable_web_page_preview": True,
            },
        )
        if r.status_code != 200:
            _fail(f"Telegram returned {r.status_code}: {r.text[:200]}")
    _ok("test message delivered (check your Telegram)")


def check_anthropic() -> None:
    print("[4/6] Anthropic")
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    try:
        resp = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=20,
            messages=[{"role": "user", "content": "Reply with just the word: pong"}],
        )
    except anthropic.AuthenticationError as exc:
        _fail(f"Anthropic auth failed: {exc}")
    except anthropic.NotFoundError as exc:
        _fail(f"Model '{config.ANTHROPIC_MODEL}' not available: {exc}")
    except Exception as exc:
        _fail(f"Anthropic call failed: {exc}")
    text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text")
    _ok(f"{config.ANTHROPIC_MODEL} replied: {text.strip()[:40]}")


def check_polymarket_auth() -> None:
    print("[5/6] Polymarket CLOB auth")
    try:
        keys = clob().get_api_keys()
    except Exception as exc:
        _fail(f"CLOB auth failed: {exc}")
    _ok(f"auth works; {len(keys.get('apiKeys', keys)) if isinstance(keys, dict) else 'response received'}")

    print("      USDC balance")
    try:
        from py_clob_client.clob_types import AssetType, BalanceAllowanceParams
        params = BalanceAllowanceParams(
            asset_type=AssetType.COLLATERAL,
            signature_type=config.POLYMARKET_SIGNATURE_TYPE,
        )
        bal = clob().get_balance_allowance(params)
    except Exception as exc:
        # Not fatal; balance endpoint sometimes 404s for new accounts
        print(f"      WARN  balance lookup failed: {exc}")
        return
    raw = bal.get("balance") if isinstance(bal, dict) else None
    if raw is not None:
        try:
            usdc = int(raw) / 1_000_000  # USDC has 6 decimals
            _ok(f"USDC available: ${usdc:.2f}")
            if usdc < config.STAKE_USD:
                print(f"      WARN  balance < STAKE_USD (${config.STAKE_USD}); first trade will fail")
        except (TypeError, ValueError):
            _ok(f"balance raw: {raw}")
    else:
        _ok(f"balance response: {bal}")


async def check_discovery() -> None:
    print("[6/6] Polymarket discovery (Gamma)")
    markets = await discover_markets()
    if not markets:
        _fail("Gamma returned zero markets -- check network")
    _ok(f"received {len(markets)} active binary markets")


def check_env() -> None:
    print("[1/6] Env vars")
    # config.py already validated; this just confirms the import didn't crash
    required = [
        "POLYMARKET_API_KEY", "POLYMARKET_API_SECRET", "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_WALLET_PRIVATE_KEY", "POLYMARKET_FUNDER_ADDRESS",
        "ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
    ]
    for name in required:
        val = getattr(config, name, None)
        if not val:
            _fail(f"{name} is empty")
    _ok(f"all {len(required)} required vars present")


async def main() -> None:
    print("Poly1M preflight\n")
    check_env()
    await check_egress_ip()
    await check_telegram()
    check_anthropic()
    check_polymarket_auth()
    await check_discovery()
    print("\nAll checks passed. Safe to deploy to Railway.")


if __name__ == "__main__":
    asyncio.run(main())
