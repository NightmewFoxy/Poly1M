"""On-chain redemption of resolved-winning sniper positions.

After a Polymarket BTC 5m market resolves, the CTF (ERC-1155) tokens that
the bot bought have to be redeemed against the on-chain payout vault to
turn into USDC back in the user's Polymarket Cash balance. The "Redeem"
button in the Polymarket UI calls `redeemPositions` on either:

  - ConditionalTokens (binary, non-neg-risk markets), or
  - NegRiskAdapter (negative-risk markets — what BTC 5m markets use).

For sig_type=1 POLY_PROXY accounts the CTF tokens are held by the
Polymarket-deployed proxy wallet (= POLYMARKET_FUNDER_ADDRESS), NOT the
user's EOA. So the redeem call has to originate FROM the proxy. The
proxy contract exposes `proxy(ProxyCall[])` which lets the EOA owner
(POLYMARKET_WALLET_PRIVATE_KEY) forward arbitrary contract calls through
the proxy. We construct the inner redeemPositions calldata, wrap it in a
ProxyCall(typeCode=1, to=target, value=0, data=inner), and sign+submit
proxy([proxy_call]) from the EOA. Gas is paid in MATIC by the EOA.

Direct Polygon RPC — no Polymarket relayer, no geoblock concern. Works
from Railway as long as POLYGON_RPC_URL is set (free Alchemy/Infura/etc).

Returns the submitted tx_hash and the post-receipt status. Caller persists
the tx_hash in sniper_positions.json so a restart doesn't re-submit.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

from eth_account import Account as EthAccount
from web3 import Web3
from web3.exceptions import TransactionNotFound

import config as _shared
from logger_setup import get_logger

log = get_logger("sniper.redeem")


# Polygon mainnet, checksummed.
CONDITIONAL_TOKENS = Web3.to_checksum_address(
    "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
)
NEG_RISK_ADAPTER = Web3.to_checksum_address(
    "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
)
USDC_E = Web3.to_checksum_address(
    "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
)
ZERO_BYTES32 = b"\x00" * 32


# --- Minimal ABIs (only the methods we actually call) -----------------------

_PROXY_WALLET_ABI = [
    {
        "name": "proxy",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {
                "name": "calls",
                "type": "tuple[]",
                "components": [
                    {"name": "typeCode", "type": "uint8"},
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "data", "type": "bytes"},
                ],
            }
        ],
        "outputs": [{"name": "returnValues", "type": "bytes[]"}],
    }
]

_CTF_ABI = [
    {
        "name": "redeemPositions",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "collateralToken", "type": "address"},
            {"name": "parentCollectionId", "type": "bytes32"},
            {"name": "conditionId", "type": "bytes32"},
            {"name": "indexSets", "type": "uint256[]"},
        ],
        "outputs": [],
    }
]

_NEG_RISK_ADAPTER_ABI = [
    {
        "name": "redeemPositions",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "_conditionId", "type": "bytes32"},
            {"name": "_amounts", "type": "uint256[]"},
        ],
        "outputs": [],
    }
]


class RedeemerError(RuntimeError):
    """A redeem attempt failed in a way the caller should record."""


class Redeemer:
    """Builds and submits redeem transactions through the POLY_PROXY.

    One instance per process is fine — it caches the Web3 connection and
    contract handles. All RPC work happens on a thread (web3.py 6.x is
    sync); call sites should `await asyncio.to_thread(...)` when invoking.
    """

    def __init__(self) -> None:
        self.rpc_url = os.getenv("POLYGON_RPC_URL", "").strip()
        if not self.rpc_url:
            # Public Polygon RPC as a fallback. Rate-limited but works for
            # the occasional redeem tx; user should set POLYGON_RPC_URL to
            # an Alchemy/Infura/etc. URL for reliability.
            self.rpc_url = "https://polygon-rpc.com"
            log.warning(
                "POLYGON_RPC_URL not set; falling back to public polygon-rpc.com "
                "(rate-limited). Set POLYGON_RPC_URL to a private RPC for reliable "
                "redemption."
            )
        self._w3: Optional[Web3] = None
        self._account = EthAccount.from_key(_shared.POLYMARKET_WALLET_PRIVATE_KEY)
        self._proxy_address = Web3.to_checksum_address(
            _shared.POLYMARKET_FUNDER_ADDRESS
        )
        self._chain_id = _shared.POLYGON_CHAIN_ID

    # ----- lazy init ----------------------------------------------------

    def _web3(self) -> Web3:
        if self._w3 is None:
            # web3.py respects HTTPS_PROXY via requests; but Polygon RPCs aren't
            # geoblocked, so iproyal-routing is unnecessary noise. Bypass with
            # a fresh session that ignores env proxies.
            from web3.providers.rpc import HTTPProvider
            import requests
            session = requests.Session()
            session.trust_env = False  # ignore HTTPS_PROXY
            self._w3 = Web3(HTTPProvider(self.rpc_url, session=session))
            if not self._w3.is_connected():
                raise RedeemerError(f"Polygon RPC not reachable at {self.rpc_url}")
            log.info(
                "Redeemer initialized | proxy=%s | eoa=%s | rpc=%s",
                self._proxy_address, self._account.address, self.rpc_url,
            )
        return self._w3

    # ----- redeem -------------------------------------------------------

    def redeem_position(
        self,
        condition_id: str,
        neg_risk: bool,
        side: str,
        shares: float,
    ) -> str:
        """Submit a redeem tx for one resolved-won position. Returns tx_hash.

        Raises RedeemerError on RPC/encoding failures. Caller is responsible
        for persisting tx_hash and re-querying status (we don't wait for
        receipt here — the redeem_loop polls separately).
        """
        w3 = self._web3()

        # Inner calldata for the matching redeem target.
        if neg_risk:
            # NegRiskAdapter.redeemPositions(conditionId, [yes_amt, no_amt])
            # Amounts are in 1e6 (USDC decimals on Polymarket CTF tokens).
            scaled = int(round(shares * 1_000_000))
            # side == "UP" → YES, side == "DOWN" → NO. (Polymarket BTC 5m
            # outcomes are "Up"/"Down" which map to YES/NO indices 0/1.)
            if side == "UP":
                amounts = [scaled, 0]
            else:
                amounts = [0, scaled]
            adapter = w3.eth.contract(
                address=NEG_RISK_ADAPTER, abi=_NEG_RISK_ADAPTER_ABI
            )
            inner = adapter.encode_abi(
                "redeemPositions",
                args=[bytes.fromhex(condition_id.removeprefix("0x")), amounts],
            )
            target = NEG_RISK_ADAPTER
            log.info(
                "Building NegRisk redeem: cond=%s side=%s shares=%.4f amounts=%s",
                condition_id[:10], side, shares, amounts,
            )
        else:
            # ConditionalTokens.redeemPositions(USDC, ZERO_BYTES32, conditionId, [1, 2])
            # Pass both index sets — the contract burns whatever balance the
            # caller holds for each, and pays out collateral on the winner.
            ctf = w3.eth.contract(address=CONDITIONAL_TOKENS, abi=_CTF_ABI)
            inner = ctf.encode_abi(
                "redeemPositions",
                args=[
                    USDC_E,
                    ZERO_BYTES32,
                    bytes.fromhex(condition_id.removeprefix("0x")),
                    [1, 2],
                ],
            )
            target = CONDITIONAL_TOKENS
            log.info(
                "Building CTF redeem: cond=%s side=%s indexSets=[1,2]",
                condition_id[:10], side,
            )

        # Wrap in a single ProxyCall(typeCode=1 CALL, to=target, value=0, data=inner).
        inner_bytes = bytes.fromhex(inner.removeprefix("0x"))
        proxy = w3.eth.contract(
            address=self._proxy_address, abi=_PROXY_WALLET_ABI
        )
        proxy_call = (1, target, 0, inner_bytes)

        # Build tx. Gas estimate first; if it fails, the inner call would
        # revert — fail loud and let the caller mark redeem_status='failed'.
        tx_kwargs: dict[str, Any] = {
            "from": self._account.address,
            "chainId": self._chain_id,
            "nonce": w3.eth.get_transaction_count(self._account.address),
            "value": 0,
        }
        try:
            gas_estimate = proxy.functions.proxy([proxy_call]).estimate_gas(
                {"from": self._account.address}
            )
        except Exception as exc:
            raise RedeemerError(
                f"gas estimate failed (likely the inner redeemPositions would "
                f"revert — already redeemed?  conditionId={condition_id}): {exc}"
            ) from exc
        tx_kwargs["gas"] = int(gas_estimate * 1.2)  # 20% headroom

        # Use legacy gasPrice — Polygon supports EIP-1559 but type-0 txs are
        # simpler and cheaper to reason about at the cost of slightly higher
        # priority fee. gasPrice = base * 1.5 to ensure inclusion within a
        # few blocks. Cap at 500 gwei for safety (Polygon should never need
        # this much in practice).
        gas_price = int(w3.eth.gas_price * 3 // 2)
        gas_price = min(gas_price, 500 * 10**9)
        tx_kwargs["gasPrice"] = gas_price

        unsigned = proxy.functions.proxy([proxy_call]).build_transaction(tx_kwargs)
        signed = self._account.sign_transaction(unsigned)
        # eth_account 0.13+ renamed `rawTransaction` -> `raw_transaction`. Try both.
        raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
        tx_hash = w3.eth.send_raw_transaction(raw)
        tx_hash_hex = tx_hash.hex()
        log.info(
            "Redeem tx submitted: cond=%s side=%s tx=%s gas=%s gasPrice=%s gwei",
            condition_id[:10], side, tx_hash_hex, tx_kwargs["gas"],
            round(gas_price / 1e9, 2),
        )
        return tx_hash_hex

    def get_receipt_status(self, tx_hash: str) -> Optional[bool]:
        """Returns True if mined+success, False if mined+reverted, None if
        not mined yet.
        """
        w3 = self._web3()
        try:
            r = w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            return None
        if r is None:
            return None
        return int(r.get("status", 0)) == 1


# Top-level async wrappers so callers don't have to remember to_thread.

_redeemer: Optional[Redeemer] = None


def _get() -> Redeemer:
    global _redeemer
    if _redeemer is None:
        _redeemer = Redeemer()
    return _redeemer


async def redeem_position(
    condition_id: str, neg_risk: bool, side: str, shares: float
) -> str:
    return await asyncio.to_thread(
        _get().redeem_position, condition_id, neg_risk, side, shares
    )


async def get_receipt_status(tx_hash: str) -> Optional[bool]:
    return await asyncio.to_thread(_get().get_receipt_status, tx_hash)
