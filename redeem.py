"""On-chain redemption of resolved-winning esports positions.

After a Polymarket market resolves, the CTF (ERC-1155) tokens that the bot
bought have to be redeemed against the on-chain payout vault to turn into
USDC back in the user's Polymarket Cash balance. The "Redeem" button in
the Polymarket UI calls `redeemPositions` on either:

  - ConditionalTokens (binary, non-neg-risk markets), or
  - NegRiskAdapter (negative-risk markets).

For sig_type=1 POLY_PROXY accounts the CTF tokens are held by the
Polymarket-deployed proxy wallet (= POLYMARKET_FUNDER_ADDRESS), NOT the
user's EOA. So the redeem call has to originate FROM the proxy. The proxy
contract exposes `proxy(ProxyCall[])` which lets the EOA owner
(POLYMARKET_WALLET_PRIVATE_KEY) forward arbitrary contract calls through
the proxy. We construct the inner redeemPositions calldata, wrap it in a
ProxyCall(typeCode=1, to=target, value=0, data=inner), and sign+submit
proxy([proxy_call]) from the EOA. Gas is paid in MATIC by the EOA.

Direct Polygon RPC — no Polymarket relayer, no geoblock concern. Works
from Railway as long as POLYGON_RPC_URL is set (free Alchemy/Infura/etc).
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

from eth_account import Account as EthAccount
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound

import config as _shared
from logger_setup import get_logger

log = get_logger("redeem")


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


class AlreadyRedeemedError(RedeemerError):
    """Gas estimate reverted on the inner redeemPositions call — almost
    always means the CTF tokens have already been burned (i.e. the user
    redeemed via the UI, or a previous tx succeeded that we lost track of).
    Treated as a soft "no-op done" instead of paging an error.
    """


class Redeemer:
    def __init__(self) -> None:
        self.rpc_url = os.getenv("POLYGON_RPC_URL", "").strip()
        if not self.rpc_url:
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

    def _web3(self) -> Web3:
        if self._w3 is None:
            from web3.providers.rpc import HTTPProvider
            import requests
            # Polygon RPC isn't geoblocked, so bypass HTTPS_PROXY (iproyal)
            # to avoid bouncing redeem traffic through an unnecessary hop.
            session = requests.Session()
            session.trust_env = False
            self._w3 = Web3(HTTPProvider(self.rpc_url, session=session))
            if not self._w3.is_connected():
                raise RedeemerError(f"Polygon RPC not reachable at {self.rpc_url}")
            log.info(
                "Redeemer initialized | proxy=%s | eoa=%s | rpc=%s",
                self._proxy_address, self._account.address, self.rpc_url,
            )
        return self._w3

    def redeem_position(
        self,
        condition_id: str,
        neg_risk: bool,
        side: str,
        shares: float,
    ) -> str:
        """Submit a redeem tx for one resolved-won position. Returns tx_hash.

        side is "YES" or "NO" (esports binary markets). For neg-risk,
        the YES outcome is index 0 / NO is index 1; amounts are the share
        balance to burn for the winning side.
        """
        w3 = self._web3()

        if neg_risk:
            scaled = int(round(shares * 1_000_000))
            if side == "YES":
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

        inner_bytes = bytes.fromhex(inner.removeprefix("0x"))
        proxy = w3.eth.contract(
            address=self._proxy_address, abi=_PROXY_WALLET_ABI
        )
        proxy_call = (1, target, 0, inner_bytes)

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
        except ContractLogicError as exc:
            raise AlreadyRedeemedError(
                f"redeem would revert (likely already redeemed) "
                f"conditionId={condition_id}: {exc}"
            ) from exc
        except Exception as exc:
            raise RedeemerError(
                f"gas estimate failed for redeem(cond={condition_id}): {exc}"
            ) from exc
        tx_kwargs["gas"] = int(gas_estimate * 1.2)

        gas_price = int(w3.eth.gas_price * 3 // 2)
        gas_price = min(gas_price, 500 * 10**9)
        tx_kwargs["gasPrice"] = gas_price

        unsigned = proxy.functions.proxy([proxy_call]).build_transaction(tx_kwargs)
        signed = self._account.sign_transaction(unsigned)
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
        """True if mined+success, False if mined+reverted, None if not mined yet."""
        w3 = self._web3()
        try:
            r = w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            return None
        if r is None:
            return None
        return int(r.get("status", 0)) == 1


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
