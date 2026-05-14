"""One-shot helper: register a new CLOB API key against your DEPOSIT WALLET
(not the relayer EOA), so POLY_1271 / sigType=3 orders pass the
"signer must = API KEY address" check.

The standard `derive_api_creds.py` flow signs the L1 ClobAuth message and sends
POLY_ADDRESS=<relayer EOA>. The CLOB registers the resulting API key under the
relayer EOA. But for sigType=3 orders, the CLOB requires the order's `signer`
field (= deposit wallet) to match the API key's registered address. Mismatch
→ 400 "the order signer address has to be the address of the API KEY".

This script does it the other way around:
  - POLY_ADDRESS header = deposit wallet (0x54C8...)
  - POLY_SIGNATURE     = ECDSA over the ClobAuth hash, signed by the relayer PK
  - The CLOB calls isValidSignature on the deposit wallet (since POLY_ADDRESS
    has bytecode), the wallet's EIP-1271 implementation accepts the relayer's
    signature, and the new API key is registered against the deposit wallet.

Run from your home machine (the deposit wallet's EIP-1271 read is on-chain, so
no Polymarket geoblock applies):

    python register_deposit_wallet_key.py

Outputs new API_KEY / SECRET / PASSPHRASE. Paste them into .env (and Railway
Variables) replacing the old ones, then re-run local_test_arbitrary.py.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

import httpx
from dotenv import load_dotenv
from eth_abi import encode as abi_encode
from eth_account import Account as EthAccount
from eth_utils import keccak
from py_clob_client_v2.signer import Signer
from py_clob_client_v2.signing.eip712 import (
    CLOB_DOMAIN_NAME,
    CLOB_VERSION,
    MSG_TO_SIGN,
    sign_clob_auth_message,
)
from py_clob_client_v2.signing.model import ClobAuth
from poly_eip712_structs import make_domain

# Skip the local IPRoyal proxy for this admin call — home IP works fine.
os.environ.pop("OUTBOUND_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("HTTP_PROXY", None)

load_dotenv(override=False)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("HTTP_PROXY", None)

PK = os.getenv("POLYMARKET_WALLET_PRIVATE_KEY")
FUNDER = os.getenv("POLYMARKET_FUNDER_ADDRESS")

if not PK:
    print("ERROR: POLYMARKET_WALLET_PRIVATE_KEY missing in .env")
    sys.exit(1)
if not FUNDER:
    print("ERROR: POLYMARKET_FUNDER_ADDRESS missing in .env")
    sys.exit(1)

CHAIN_ID = 137
HOST = "https://clob.polymarket.com"


# ERC-7739 / Solady nested-EIP-712 wrap of a ClobAuth message.
# Mirrors py_clob_client_v2.order_utils.exchange_order_builder_v2._build_poly_1271_order_signature
# but for the ClobAuth struct instead of the Order struct.
CLOB_AUTH_TYPE_STRING = "ClobAuth(address address,string timestamp,uint256 nonce,string message)"
SOLADY_TYPE_STRING_AUTH = (
    "TypedDataSign(ClobAuth contents,string name,string version,uint256 chainId,"
    "address verifyingContract,bytes32 salt)" + CLOB_AUTH_TYPE_STRING
)
DOMAIN_TYPE_STRING = (
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
)
CLOB_AUTH_TYPE_HASH = keccak(text=CLOB_AUTH_TYPE_STRING)
SOLADY_TYPE_HASH_AUTH = keccak(text=SOLADY_TYPE_STRING_AUTH)
DOMAIN_TYPE_HASH = keccak(text=DOMAIN_TYPE_STRING)
DEPOSIT_NAME_HASH = keccak(text="DepositWallet")
DEPOSIT_VERSION_HASH = keccak(text="1")
DEPOSIT_SALT = b"\x00" * 32


def _solady_wrap_clob_auth(signer: Signer, deposit_wallet: str, ts: int, nonce: int) -> str:
    """Produce an ERC-7739-wrapped POLY_1271 signature over a ClobAuth message."""
    addr_bytes = bytes.fromhex(signer.address()[2:])
    msg_hash = keccak(text=MSG_TO_SIGN)
    # contents_hash = keccak(ClobAuth typeHash || addr || keccak(ts) || nonce || keccak(message))
    contents_hash = keccak(
        primitive=abi_encode(
            ["bytes32", "address", "bytes32", "uint256", "bytes32"],
            [
                CLOB_AUTH_TYPE_HASH,
                signer.address(),
                keccak(text=str(ts)),
                nonce,
                msg_hash,
            ],
        )
    )
    # CLOB app domain separator (ClobAuthDomain)
    app_domain = keccak(
        primitive=abi_encode(
            ["bytes32", "bytes32", "bytes32", "uint256"],
            [
                keccak(text="EIP712Domain(string name,string version,uint256 chainId)"),
                keccak(text=CLOB_DOMAIN_NAME),
                keccak(text=CLOB_VERSION),
                CHAIN_ID,
            ],
        )
    )
    # Inner Solady TypedDataSign struct hash
    typed_data_sign_hash = keccak(
        primitive=abi_encode(
            ["bytes32", "bytes32", "bytes32", "bytes32", "uint256", "address", "bytes32"],
            [
                SOLADY_TYPE_HASH_AUTH,
                contents_hash,
                DEPOSIT_NAME_HASH,
                DEPOSIT_VERSION_HASH,
                CHAIN_ID,
                deposit_wallet,
                DEPOSIT_SALT,
            ],
        )
    )
    digest = keccak(primitive=b"\x19\x01" + app_domain + typed_data_sign_hash)
    signed = EthAccount._sign_hash(digest, private_key=signer.private_key)
    inner = signed.signature.hex()
    if inner.startswith("0x"):
        inner = inner[2:]
    contents_type = CLOB_AUTH_TYPE_STRING.encode("utf-8").hex()
    contents_type_len = len(CLOB_AUTH_TYPE_STRING).to_bytes(2, "big").hex()
    return "0x" + inner + app_domain.hex() + contents_hash.hex() + contents_type + contents_type_len


def _try(headers: dict, ts: int) -> httpx.Response | None:
    print(f"  Trying POST /auth/api-key  POLY_ADDRESS={headers['POLY_ADDRESS'][:10]}...")
    r = httpx.post(f"{HOST}/auth/api-key", headers=headers, timeout=30)
    print(f"    status {r.status_code}  body {r.text[:200]}")
    if r.status_code == 200:
        return r
    if r.status_code == 400 and "exist" in r.text.lower():
        print("  Falling back to GET /auth/derive-api-key with same headers...")
        r = httpx.get(f"{HOST}/auth/derive-api-key", headers=headers, timeout=30)
        print(f"    status {r.status_code}  body {r.text[:200]}")
        return r if r.status_code == 200 else None
    return None


def main() -> None:
    signer = Signer(PK, CHAIN_ID)
    print(f"Relayer EOA: {signer.address()}")
    print(f"Funder:      {FUNDER}")
    print()

    ts = int(datetime.now().timestamp())
    nonce = 0

    # Attempt A: plain ECDSA signature over ClobAuth, POLY_ADDRESS=deposit wallet.
    sig_plain = sign_clob_auth_message(signer, ts, nonce)
    print("Attempt A: POLY_ADDRESS=deposit wallet, plain ECDSA sig")
    resp = _try(
        {"POLY_ADDRESS": FUNDER, "POLY_SIGNATURE": sig_plain,
         "POLY_TIMESTAMP": str(ts), "POLY_NONCE": str(nonce)},
        ts,
    )
    print()

    if resp is None:
        # Attempt B: Solady/ERC-7739 wrapped signature, POLY_ADDRESS=deposit wallet.
        ts = int(datetime.now().timestamp())  # refresh ts
        sig_wrapped = _solady_wrap_clob_auth(signer, FUNDER, ts, nonce)
        print("Attempt B: POLY_ADDRESS=deposit wallet, ERC-7739 wrapped sig")
        resp = _try(
            {"POLY_ADDRESS": FUNDER, "POLY_SIGNATURE": sig_wrapped,
             "POLY_TIMESTAMP": str(ts), "POLY_NONCE": str(nonce)},
            ts,
        )
        print()

    if resp is None:
        print("Both attempts failed. The CLOB does not accept either signature scheme")
        print("for registering an API key under the deposit wallet address.")
        sys.exit(2)

    data = resp.json()
    print("=== API credentials registered to deposit wallet ===")
    print(f"POLYMARKET_API_KEY={data.get('apiKey')}")
    print(f"POLYMARKET_API_SECRET={data.get('secret')}")
    print(f"POLYMARKET_API_PASSPHRASE={data.get('passphrase')}")
    print()
    print("Paste these into .env (replacing the existing creds) and re-run local_test_arbitrary.py.")


if __name__ == "__main__":
    main()
