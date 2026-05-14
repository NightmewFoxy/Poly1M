"""One-shot helper: derive Polymarket CLOB API key / secret / passphrase from your wallet.

Use this only if Settings -> API Keys in the Polymarket UI doesn't expose them.

Run once locally:
    python derive_api_creds.py

It prints the three values. Paste them into your Railway env vars (and your local .env)
and never run this again -- subsequent runs will return the same credentials, but there's
no need to call it after the first successful generation.
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from py_clob_client_v2.client import ClobClient

load_dotenv()

PK = os.getenv("POLYMARKET_WALLET_PRIVATE_KEY")
FUNDER = os.getenv("POLYMARKET_FUNDER_ADDRESS")
SIG_TYPE = int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "1"))

if not PK:
    print("ERROR: POLYMARKET_WALLET_PRIVATE_KEY missing in .env")
    sys.exit(1)
if not FUNDER:
    print("ERROR: POLYMARKET_FUNDER_ADDRESS missing in .env")
    sys.exit(1)

client = ClobClient(
    host="https://clob.polymarket.com",
    key=PK,
    chain_id=137,
    signature_type=SIG_TYPE,
    funder=FUNDER,
)
creds = client.create_or_derive_api_key()
print()
print("=== Polymarket CLOB API credentials ===")
print(f"POLYMARKET_API_KEY={creds.api_key}")
print(f"POLYMARKET_API_SECRET={creds.api_secret}")
print(f"POLYMARKET_API_PASSPHRASE={creds.api_passphrase}")
print()
print("Save these into Railway -> your service -> Variables. Do not commit them.")
