# Poly1M -- Polymarket esports trading bot

Continuous bot that scans Polymarket for esports markets, researches each one with
Claude + web search, and auto-fires $10 trades on the highest-EV opportunities.

## Architecture

```
main.py               Loop, signal handling, orchestration
config.py             Env loading + strategy constants
logger_setup.py       Stdout + rotating file logging
polymarket_client.py  Gamma REST discovery + CLOB orders + resolution lookup
research.py           Claude (web_search tool) + EV math
positions.py          positions.json atomic persistence
telegram_notif.py     Telegram Bot API messages
derive_api_creds.py   One-shot helper to mint CLOB API creds from your wallet
```

## Local smoke test

1. `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
2. `pip install -r requirements.txt`
3. Copy `.env.example` -> `.env`, fill every value. (If you don't have Polymarket
   API credentials yet, fill only the wallet + funder + signature type, then run
   `python derive_api_creds.py` and copy its output back into `.env`.)
4. `python main.py`

The first cycle takes ~1-2 minutes because every candidate market gets a full
Claude+web-search research call. Watch `data/bot.log` and your Telegram chat.

## Deploying to Railway

1. **Create a Railway project.** From the dashboard: `New Project` -> `Deploy from
   GitHub repo` (push this folder up first) or `Deploy from CLI`.
   - `railway login`
   - `railway init` in this directory
   - `railway up` to push

2. **Set environment variables** in the service's `Variables` tab. Copy every
   line from `.env.example` and fill in real values. At minimum:
   - `POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`
   - `POLYMARKET_WALLET_PRIVATE_KEY`, `POLYMARKET_FUNDER_ADDRESS`
   - `POLYMARKET_SIGNATURE_TYPE` (1 for email/Magic.link signup)
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   - `DATA_DIR=/data`

3. **Add a persistent volume** so `positions.json` and `bot.log` survive
   redeploys. In the service: `Settings` -> `Volumes` -> `New Volume`,
   mount path `/data`, size 1 GB is plenty.

4. **Deploy.** Railway will detect `nixpacks.toml` + `requirements.txt`,
   install deps, and run `python main.py` per the `Procfile`. The service
   type should be **Worker** (no port to expose). The `restartPolicyType =
   "ON_FAILURE"` in `railway.toml` will auto-restart on crashes up to 10
   times before giving up.

5. **Verify.** You should get a `Bot started.` Telegram message within ~30s
   of deploy. The next cycle's discovery log will appear in Railway's `Logs`
   tab. First trade (if EV exists) lands within a few minutes.

## Polymarket geoblock workaround

Polymarket's **CLOB** (where orders are placed) blocks Railway and most
other cloud-provider IPs even though the **Gamma** discovery endpoint is
open. Symptom: discovery works, then `place_order` returns
`PolyApiException[status_code=403, ... Trading restricted in your region]`.

The bot detects this and exits the cycle cleanly instead of looping. To
actually trade from Railway you need a proxy whose egress IP is in a
permitted region. Set:

```
OUTBOUND_PROXY=http://user:pass@host:port
```

(or `POLYMARKET_PROXY_URL=...` — both are accepted). Anything you give it
is exported as `HTTPS_PROXY` at process start, which both `requests` (used
by `py-clob-client`) and `httpx` pick up automatically.

Reasonable proxy options:
- **Residential proxy** (Bright Data, Oxylabs, Smartproxy, IPRoyal) sticky
  session pinned to a permitted country. Cheapest if you only fire ~10
  trades per cycle.
- **Self-hosted VPS** in a non-blocked region running tinyproxy / dante /
  squid. Fixed monthly cost, fastest.
- **Tailscale / cloudflared tunnel back to your home network** — your home
  IP is already known to work. Set up a tinyproxy on your home machine
  and expose it over Tailscale.

Run `python preflight.py` from inside your Railway shell (or with the same
env vars locally) to print the egress IP + country before trading.

## Tuning the strategy

All numeric knobs are env vars (see `.env.example`):

| Var | Default | Notes |
| --- | --- | --- |
| `LOOP_INTERVAL_SECONDS` | 1800 | 30 min |
| `MAX_OPEN_POSITIONS` | 10 | Hard cap on concurrent positions |
| `STAKE_USD` | 10 | $ per trade |
| `MIN_VOLUME_USD` | 10000 | Skip thin markets |
| `MAX_PRICE` | 0.80 | Don't trade lopsided markets |
| `MIN_HOURS_TO_RESOLUTION` | 2 | Skip last-2-hour markets |
| `POLYMARKET_FEE` | 0.02 | 2% on winnings |

## Safety reminders

- The bot auto-trades real money with no human approval. The first time you
  deploy, watch the first 2-3 cycles before walking away.
- A single hallucinated probability estimate burns $10. Over time the
  variance is the variance, but a stack of correlated bad calls in one cycle
  can dent the bankroll faster than you'd think.
- Polymarket geoblocks the CLOB on cloud IPs even though Gamma works. If
  `place_order` returns a 403, see the "Polymarket geoblock workaround"
  section above — `OUTBOUND_PROXY` is the fix.
- `MAX_PRICE` is enforced both in candidate filtering and at the moment of
  order placement (live-price recheck). It cannot be exceeded.
