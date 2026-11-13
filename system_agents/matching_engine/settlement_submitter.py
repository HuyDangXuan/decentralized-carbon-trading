"""
Bot Settlement Submitter (Task P.1): đưa kết quả khớp lệnh của Matching Engine lên hợp đồng
`CarbonDoubleAuction.batchSettleTrades` trên Polygon Amoy và ghi nhận kết quả về engine.

Luồng: `MatchResult[]` -> payload `MatchedTrade` (đủ hai lệnh đã ký) -> kiểm tra trước (không tốn gas)
-> `batchSettleTrades` ký bằng ví Operator -> đọc event `TradeSettled` từng giao dịch -> `confirm_settlement`.

Điều cần nhớ về hợp đồng (contracts/CarbonDoubleAuction.sol):
- `batchSettleTrades` bọc từng trade trong try/catch (dòng 193-198): trade lỗi bị bỏ qua IM LẶNG, giao dịch
  vẫn thành công. Vì vậy "tx thành công" không có nghĩa mọi trade đã khớp; chỉ event `TradeSettled` là bằng chứng.
- `tradeHash = keccak256(bidId, askId, matchAmount, clearingPrice)` không có sessionId: khớp lại đúng cặp lệnh,
  đúng khối lượng và giá ở phiên sau sẽ bị bỏ qua (`TradeAlreadyExecuted`). Bước kiểm tra trước phát hiện việc này.
- Hợp đồng không kiểm số dư/allowance trước: thiếu allowance làm trade bị bỏ qua. Bot chưa kiểm hai điều này.

Khóa Operator chỉ đọc từ biến môi trường `SETTLEMENT_OPERATOR_PRIVATE_KEY`, không bao giờ được ghi vào repo hay log.
Logic lõi (payload, kiểm tra trước, đối soát event) chỉ cần `eth-utils`/`eth-account`; `web3` chỉ nạp khi nối RPC thật.
"""

import argparse
import json
import os
import sys
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence, Tuple

from eth_utils import keccak, to_checksum_address

from auction_agent import DoubleAuctionAgent
from order_book import MatchResult, Order, OrderType

AMOY_CHAIN_ID = 80002
DEFAULT_RPC_URL = "https://poly-amoy-testnet.api.pocket.network"
DOMAIN_NAME = "EPU Carbon Double Auction"
DOMAIN_VERSION = "2.0"
MAX_BATCH_SIZE = 20  # Đức đo tới 20 cặp lệnh/batch (~2,74 triệu gas); không đo lớn hơn
ABI_PATH = Path(__file__).resolve().parents[2] / "contracts" / "abis" / "CarbonDoubleAuction.json"
KEY_ENV = "SETTLEMENT_OPERATOR_PRIVATE_KEY"

UINT128_MAX = 2**128 - 1
UINT256_MAX = 2**256 - 1

ORDER_TYPES = {
    "Order": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "trader", "type": "address"},
        {"name": "orderType", "type": "uint8"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "amount", "type": "uint128"},
        {"name": "pricePerUnit", "type": "uint128"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}


class SettlementError(Exception):
    """Lỗi cấu hình, payload hoặc giao dịch on-chain."""


class SettlementInconsistency(SettlementError):
    """Event on-chain không khớp với những gì bot đã gửi; cần người kiểm tra."""


class TradeStatus(str, Enum):
    SETTLED = "SETTLED"  # có event TradeSettled
    SKIPPED = "SKIPPED"  # không gửi: payload sai hoặc kiểm tra trước thất bại
    FAILED = "FAILED"  # đã gửi nhưng hợp đồng bỏ qua trade (hoặc giao dịch lỗi)


# ----------------------------------------------------------------------------- payload
def _int(value: Any, name: str, max_value: int) -> int:
    if isinstance(value, bool):
        raise SettlementError(f"{name} must be an integer, got bool")
    try:
        number = int(value, 10) if isinstance(value, str) else int(value)
    except (TypeError, ValueError):
        raise SettlementError(f"{name} must be an integer, got {value!r}")
    if isinstance(value, float) or not 0 <= number <= max_value:
        raise SettlementError(f"{name} out of range: {value!r}")
    return number


def _bytes32(value: str, name: str) -> bytes:
    try:
        raw = bytes.fromhex(value[2:] if value.startswith(("0x", "0X")) else value)
    except (ValueError, AttributeError):
        raw = b""
    if len(raw) != 32:
        raise SettlementError(f"{name} must be bytes32 (0x + 64 hex)")
    return raw


def _signature(value: Optional[str], name: str) -> bytes:
    """65 byte (r, s, v). `v` ở dạng 0/1 được đổi thành 27/28 vì ecrecover của hợp đồng chỉ nhận 27/28."""
    try:
        raw = bytes.fromhex(value[2:] if value.startswith(("0x", "0X")) else value)  # type: ignore[union-attr]
    except (ValueError, AttributeError):
        raw = b""
    if len(raw) != 65:
        raise SettlementError(f"{name} must be a 65-byte ECDSA signature")
    if raw[64] in (0, 1):
        raw = raw[:64] + bytes([raw[64] + 27])
    return raw


def order_payload(order: Order) -> Dict[str, Any]:
    """Các trường đã ký của một lệnh. Số lớn ở dạng chuỗi thập phân để JSON không mất độ chính xác."""
    if order.signature is None or order.nonce is None or order.deadline is None:
        raise SettlementError(f"order {order.order_id} lacks signature/nonce/deadline (not a signed on-chain order)")
    return {
        "orderId": order.order_id,
        "trader": order.trader_id,
        "orderType": 0 if order.order_type == OrderType.BID else 1,
        "tokenId": str(order.token_id),
        "amount": str(order.amount),
        "pricePerUnit": str(order.price),
        "nonce": str(order.nonce),
        "deadline": str(order.deadline),
    }


def trade_payload(agent: DoubleAuctionAgent, match: MatchResult) -> Dict[str, Any]:
    """Một `MatchedTrade` dạng JSON: hai lệnh gốc kèm chữ ký, khối lượng khớp và giá thanh toán."""
    bid = agent.get_order(match.bid_order_id).order
    ask = agent.get_order(match.ask_order_id).order
    return {
        "bidOrder": order_payload(bid),
        "askOrder": order_payload(ask),
        "bidSignature": bid.signature,
        "askSignature": ask.signature,
        "matchAmount": str(match.amount),
        "clearingPrice": str(match.clearing_price),
        "sessionId": match.session_id,
    }


def _order_tuple(p: Dict[str, Any], name: str) -> Tuple[Any, ...]:
    order_type = _int(p["orderType"], f"{name}.orderType", 1)
    return (
        _bytes32(p["orderId"], f"{name}.orderId"),
        to_checksum_address(p["trader"]),
        order_type,
        _int(p["tokenId"], f"{name}.tokenId", UINT256_MAX),
        _int(p["amount"], f"{name}.amount", UINT128_MAX),
        _int(p["pricePerUnit"], f"{name}.pricePerUnit", UINT128_MAX),
        _int(p["nonce"], f"{name}.nonce", UINT256_MAX),
        _int(p["deadline"], f"{name}.deadline", UINT256_MAX),
    )


def compute_trade_hash(bid_order_id: bytes, ask_order_id: bytes, amount: int, clearing_price: int) -> bytes:
    """keccak256(abi.encodePacked(bytes32, bytes32, uint128, uint128)), đúng dòng 291-296 của hợp đồng."""
    return keccak(bid_order_id + ask_order_id + amount.to_bytes(16, "big") + clearing_price.to_bytes(16, "big"))


@dataclass(frozen=True)
class PreparedTrade:
    struct: Tuple[Any, ...]  # (bidOrder, askOrder, bidSig, askSig, matchAmount, clearingPrice)
    trade_hash: bytes
    session_id: Optional[int] = None

    @property
    def bid(self) -> Tuple[Any, ...]:
        return self.struct[0]

    @property
    def ask(self) -> Tuple[Any, ...]:
        return self.struct[1]

    @property
    def amount(self) -> int:
        return self.struct[4]

    @property
    def clearing_price(self) -> int:
        return self.struct[5]

    @property
    def bid_order_id(self) -> str:
        return "0x" + self.bid[0].hex()

    @property
    def ask_order_id(self) -> str:
        return "0x" + self.ask[0].hex()

    @property
    def hash_hex(self) -> str:
        return "0x" + self.trade_hash.hex()


def prepare_trade(payload: Dict[str, Any]) -> PreparedTrade:
    """Dựng và kiểm tra tính hợp thức cục bộ của một trade. Ném SettlementError nếu payload sai."""
    try:
        bid = _order_tuple(payload["bidOrder"], "bidOrder")
        ask = _order_tuple(payload["askOrder"], "askOrder")
        bid_sig = _signature(payload.get("bidSignature"), "bidSignature")
        ask_sig = _signature(payload.get("askSignature"), "askSignature")
        amount = _int(payload["matchAmount"], "matchAmount", UINT128_MAX)
        price = _int(payload["clearingPrice"], "clearingPrice", UINT128_MAX)
    except KeyError as exc:
        raise SettlementError(f"payload missing field {exc}")
    if bid[2] != 0 or ask[2] != 1:
        raise SettlementError("bidOrder must be orderType 0 and askOrder orderType 1")
    if bid[3] != ask[3]:
        raise SettlementError("tokenId mismatch between bid and ask")
    if bid[1] == ask[1]:
        raise SettlementError("self-trading: same trader on both sides")
    if amount == 0:
        raise SettlementError("matchAmount must be > 0")
    if not ask[5] <= price <= bid[5]:
        raise SettlementError(f"clearingPrice {price} outside [ask {ask[5]}, bid {bid[5]}]")
    if amount > bid[4] or amount > ask[4]:
        raise SettlementError("matchAmount exceeds an order's signed amount")
    session_id = payload.get("sessionId")
    return PreparedTrade(
        struct=(bid, ask, bid_sig, ask_sig, amount, price),
        trade_hash=compute_trade_hash(bid[0], ask[0], amount, price),
        session_id=session_id if isinstance(session_id, int) else None,
    )


def recover_signer(order_tuple: Tuple[Any, ...], signature: bytes, chain_id: int, verifying_contract: str) -> str:
    """Địa chỉ ký lệnh theo EIP-712 (cùng domain với hợp đồng), để bắt lỗi trước khi tốn gas."""
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    message = {
        "orderId": order_tuple[0], "trader": order_tuple[1], "orderType": order_tuple[2],
        "tokenId": order_tuple[3], "amount": order_tuple[4], "pricePerUnit": order_tuple[5],
        "nonce": order_tuple[6], "deadline": order_tuple[7],
    }
    domain = {
        "name": DOMAIN_NAME, "version": DOMAIN_VERSION, "chainId": chain_id,
        "verifyingContract": to_checksum_address(verifying_contract),
    }
    signable = encode_typed_data(domain_data=domain, message_types=ORDER_TYPES, message_data=message)
    return Account.recover_message(signable, signature=signature)


# ----------------------------------------------------------------------------- chain
@dataclass
class BatchReceipt:
    tx_hash: str
    block_number: int
    gas_used: int
    settled_hashes: List[bytes]  # từ event TradeSettled
    trades_count: Optional[int] = None  # từ BatchSettlementCompleted
    success_count: Optional[int] = None


class ChainClient(Protocol):
    chain_id: int
    contract_address: str

    def now(self) -> int: ...
    def is_paused(self) -> bool: ...
    def executed(self, trade_hash: bytes) -> bool: ...
    def filled(self, order_id: bytes) -> int: ...
    def cancelled(self, order_id: bytes) -> bool: ...
    def user_nonce(self, trader: str) -> int: ...
    def submit_batch(self, structs: List[Tuple[Any, ...]]) -> BatchReceipt: ...


class Web3Chain:
    """Nối RPC thật bằng web3.py; ký giao dịch bằng ví Operator (đã có SETTLEMENT_OPERATOR_ROLE)."""

    def __init__(self, w3: Any, contract: Any, account: Any, chain_id: int = AMOY_CHAIN_ID,
                 gas_multiplier: float = 1.3, min_priority_fee_gwei: int = 30, receipt_timeout: int = 180):
        self.w3, self.contract, self.account = w3, contract, account
        self.chain_id = chain_id
        self.contract_address = contract.address
        self.gas_multiplier = gas_multiplier
        self.min_priority_fee = min_priority_fee_gwei * 10**9  # Amoy yêu cầu tối thiểu ~25 gwei
        self.receipt_timeout = receipt_timeout

    @classmethod
    def from_rpc(cls, rpc_url: str, contract_address: str, private_key: str,
                 chain_id: int = AMOY_CHAIN_ID, abi_path: Path = ABI_PATH, **kwargs: Any) -> "Web3Chain":
        from eth_account import Account
        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
        if not w3.is_connected():
            raise SettlementError(f"cannot connect to RPC {rpc_url}")
        if w3.eth.chain_id != chain_id:
            raise SettlementError(f"RPC chain id {w3.eth.chain_id} != expected {chain_id}")
        abi = json.loads(Path(abi_path).read_text(encoding="utf-8"))
        contract = w3.eth.contract(address=to_checksum_address(contract_address), abi=abi)
        return cls(w3, contract, Account.from_key(private_key), chain_id, **kwargs)

    # --- đọc (không tốn gas)
    def now(self) -> int:
        return int(self.w3.eth.get_block("latest")["timestamp"])

    def is_paused(self) -> bool:
        return bool(self.contract.functions.paused().call())

    def executed(self, trade_hash: bytes) -> bool:
        return bool(self.contract.functions.executedTrades(trade_hash).call())

    def filled(self, order_id: bytes) -> int:
        return int(self.contract.functions.filledAmount(order_id).call())

    def cancelled(self, order_id: bytes) -> bool:
        return bool(self.contract.functions.cancelledOrders(order_id).call())

    def user_nonce(self, trader: str) -> int:
        return int(self.contract.functions.userNonces(trader).call())

    # --- ghi
    def submit_batch(self, structs: List[Tuple[Any, ...]]) -> BatchReceipt:
        w3, addr = self.w3, self.account.address
        fn = self.contract.functions.batchSettleTrades(structs)
        gas = int(fn.estimate_gas({"from": addr}) * self.gas_multiplier)
        priority = max(int(w3.eth.max_priority_fee), self.min_priority_fee)
        base_fee = int(w3.eth.get_block("latest").get("baseFeePerGas", 0))
        tx = fn.build_transaction({
            "from": addr,
            "nonce": w3.eth.get_transaction_count(addr, "pending"),
            "gas": gas,
            "chainId": self.chain_id,
            "maxPriorityFeePerGas": priority,
            "maxFeePerGas": base_fee * 2 + priority,
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.receipt_timeout)
        except Exception as exc:  # hết giờ chờ: giao dịch có thể vẫn được đào sau đó
            raise SettlementError(f"no receipt for tx {tx_hash.hex()}: {exc}")
        if receipt["status"] != 1:
            raise SettlementError(f"tx {tx_hash.hex()} reverted")
        from web3.logs import DISCARD  # bỏ qua log của ERC-20/ERC-1155 (không nằm trong ABI) thay vì cảnh báo

        events = self.contract.events
        settled = [bytes(e["args"]["tradeHash"]) for e in events.TradeSettled().process_receipt(receipt, errors=DISCARD)]
        done = events.BatchSettlementCompleted().process_receipt(receipt, errors=DISCARD)
        count = success = None
        if len(done) == 1:
            count, success = int(done[0]["args"]["tradesCount"]), int(done[0]["args"]["successCount"])
        return BatchReceipt("0x" + tx_hash.hex().removeprefix("0x"), int(receipt["blockNumber"]),
                            int(receipt["gasUsed"]), settled, count, success)


# ----------------------------------------------------------------------------- submitter
@dataclass
class TradeOutcome:
    trade_hash: Optional[str]
    bid_order_id: Optional[str]
    ask_order_id: Optional[str]
    amount: Optional[int]
    status: TradeStatus
    reason: Optional[str] = None
    tx_hash: Optional[str] = None


@dataclass
class SettlementReport:
    outcomes: List[TradeOutcome] = field(default_factory=list)
    tx_hashes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def count(self, status: TradeStatus) -> int:
        return sum(1 for o in self.outcomes if o.status == status)


OnSettled = Callable[[PreparedTrade, TradeOutcome], None]


class SettlementSubmitter:
    def __init__(self, chain: ChainClient, batch_size: int = MAX_BATCH_SIZE, verify_signatures: bool = True):
        if not 1 <= batch_size <= MAX_BATCH_SIZE:
            raise ValueError(f"batch_size must be in [1, {MAX_BATCH_SIZE}]")
        self.chain = chain
        self.batch_size = batch_size
        self.verify_signatures = verify_signatures

    def precheck(self, trades: Sequence[PreparedTrade]) -> Tuple[List[PreparedTrade], List[TradeOutcome]]:
        """Mô phỏng các chốt chặn của hợp đồng (theo thứ tự dòng 224-300) bằng lệnh đọc, không tốn gas."""
        if self.chain.is_paused():
            raise SettlementError("contract is paused")
        now = self.chain.now()
        pending_fill: Dict[bytes, int] = {}
        seen: set = set()
        accepted: List[PreparedTrade] = []
        skipped: List[TradeOutcome] = []
        for t in trades:
            reason = self._reject_reason(t, now, pending_fill, seen)
            if reason is None:
                accepted.append(t)
                seen.add(t.trade_hash)
                for order in (t.bid, t.ask):
                    pending_fill[order[0]] = pending_fill.get(order[0], 0) + t.amount
            else:
                skipped.append(self._outcome(t, TradeStatus.SKIPPED, reason))
        return accepted, skipped

    def _reject_reason(self, t: PreparedTrade, now: int, pending: Dict[bytes, int], seen: set) -> Optional[str]:
        sides = ((t.bid, t.struct[2], "bid"), (t.ask, t.struct[3], "ask"))
        if self.verify_signatures:
            for order, sig, side in sides:
                try:
                    signer = recover_signer(order, sig, self.chain.chain_id, self.chain.contract_address)
                except Exception as exc:
                    return f"{side} signature unreadable: {exc}"
                if signer.lower() != order[1].lower():
                    return f"{side} signature does not recover to trader (wrong domain/contract?)"
        for order, _, side in sides:
            if now > order[7]:
                return f"{side} deadline expired"
        for order, _, side in sides:
            if self.chain.cancelled(order[0]):
                return f"{side} order cancelled on-chain"
        for order, _, side in sides:
            if order[6] < self.chain.user_nonce(order[1]):
                return f"{side} nonce below the trader's on-chain nonce"
        if t.trade_hash in seen or self.chain.executed(t.trade_hash):
            return "trade already executed (same pair, amount and price: TradeAlreadyExecuted)"
        for order, _, side in sides:
            if self.chain.filled(order[0]) + pending.get(order[0], 0) + t.amount > order[4]:
                return f"{side} order would exceed its signed amount on-chain"
        return None

    @staticmethod
    def _outcome(t: Optional[PreparedTrade], status: TradeStatus, reason: Optional[str] = None,
                 tx_hash: Optional[str] = None) -> TradeOutcome:
        if t is None:
            return TradeOutcome(None, None, None, None, status, reason, tx_hash)
        return TradeOutcome(t.hash_hex, t.bid_order_id, t.ask_order_id, t.amount, status, reason, tx_hash)

    def settle(self, payloads: Sequence[Dict[str, Any]], on_settled: Optional[OnSettled] = None) -> SettlementReport:
        report = SettlementReport()
        prepared: List[PreparedTrade] = []
        for p in payloads:
            try:
                prepared.append(prepare_trade(p))
            except SettlementError as exc:
                report.outcomes.append(self._outcome(None, TradeStatus.SKIPPED, f"invalid payload: {exc}"))
        accepted, skipped = self.precheck(prepared)
        report.outcomes.extend(skipped)

        for start in range(0, len(accepted), self.batch_size):
            batch = accepted[start:start + self.batch_size]
            try:
                receipt = self.chain.submit_batch([t.struct for t in batch])
            except SettlementError as exc:
                report.error = str(exc)
                report.outcomes.extend(self._outcome(t, TradeStatus.FAILED, str(exc)) for t in batch)
                report.outcomes.extend(
                    self._outcome(t, TradeStatus.SKIPPED, "not sent: an earlier batch failed")
                    for t in accepted[start + self.batch_size:]
                )
                return report
            report.tx_hashes.append(receipt.tx_hash)
            self._reconcile(batch, receipt, report, on_settled)
        return report

    def _reconcile(self, batch: List[PreparedTrade], receipt: BatchReceipt, report: SettlementReport,
                   on_settled: Optional[OnSettled]) -> None:
        sent = {t.trade_hash for t in batch}
        settled = set(receipt.settled_hashes)
        if not settled <= sent or len(settled) != len(receipt.settled_hashes):
            raise SettlementInconsistency(f"tx {receipt.tx_hash}: TradeSettled events do not match the trades sent")
        if receipt.success_count is not None and receipt.success_count != len(settled):
            raise SettlementInconsistency(
                f"tx {receipt.tx_hash}: successCount {receipt.success_count} != {len(settled)} TradeSettled events"
            )
        for t in batch:
            if t.trade_hash in settled:
                outcome = self._outcome(t, TradeStatus.SETTLED, None, receipt.tx_hash)
                report.outcomes.append(outcome)
                if on_settled is not None:
                    try:
                        on_settled(t, outcome)
                    except Exception as exc:  # tiền đã chuyển: không được mất kết quả vì lỗi ghi nhận
                        outcome.reason = f"settled on-chain but confirm callback failed: {exc}"
            else:
                report.outcomes.append(self._outcome(
                    t, TradeStatus.FAILED,
                    "skipped by the contract (try/catch): check buyer USDC allowance/balance, seller token approval",
                    receipt.tx_hash,
                ))

    def settle_session(self, agent: DoubleAuctionAgent, session_id: int) -> SettlementReport:
        """Chế độ trong cùng tiến trình: lấy match của phiên từ `agent` và ghi nhận ngược vào chính nó."""
        payloads = [trade_payload(agent, m) for m in agent.matches[session_id]]

        def confirm(t: PreparedTrade, _: TradeOutcome) -> None:
            agent.confirm_settlement(t.bid_order_id, t.amount)
            agent.confirm_settlement(t.ask_order_id, t.amount)

        return self.settle(payloads, confirm)


# ----------------------------------------------------------------------------- CLI
def _http(method: str, url: str, api_key: Optional[str], body: Optional[dict] = None) -> Any:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-Key", api_key)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Nộp kết quả khớp lệnh của một phiên lên CarbonDoubleAuction (Polygon Amoy).")
    ap.add_argument("--api-url", default="http://localhost:8000")
    ap.add_argument("--session-id", type=int, required=True)
    ap.add_argument("--rpc", default=os.environ.get("AMOY_RPC_URL", DEFAULT_RPC_URL))
    ap.add_argument("--contract", default=os.environ.get("AUCTION_CONTRACT_ADDRESS"))
    ap.add_argument("--batch-size", type=int, default=MAX_BATCH_SIZE)
    ap.add_argument("--dry-run", action="store_true", help="chỉ kiểm tra trước (đọc chain), không gửi giao dịch")
    args = ap.parse_args(argv)

    key = os.environ.get(KEY_ENV)
    api_key = os.environ.get("MATCHING_API_KEY")
    if not key:
        print(f"Thiếu biến môi trường {KEY_ENV} (khóa ví Operator; không đặt trong repo).", file=sys.stderr)
        return 2
    if not args.contract:
        print("Thiếu --contract hoặc biến AUCTION_CONTRACT_ADDRESS.", file=sys.stderr)
        return 2

    chain = Web3Chain.from_rpc(args.rpc, args.contract, key)
    print(f"Operator: {chain.account.address} | contract: {chain.contract_address} | chain {chain.chain_id}")
    base = args.api_url.rstrip("/")
    payloads = _http("GET", f"{base}/api/v1/sessions/{args.session_id}/trades", api_key)["trades"]
    print(f"Phiên {args.session_id}: {len(payloads)} trade từ engine")
    submitter = SettlementSubmitter(chain, args.batch_size)

    if args.dry_run:
        prepared, outcomes = [], []
        for p in payloads:
            try:
                prepared.append(prepare_trade(p))
            except SettlementError as exc:
                outcomes.append(f"invalid payload: {exc}")
        accepted, skipped = submitter.precheck(prepared)
        print(f"DRY-RUN: {len(accepted)} trade sẽ được gửi, {len(skipped) + len(outcomes)} bị bỏ")
        for o in skipped:
            print(f"  SKIPPED {o.trade_hash}: {o.reason}")
        for reason in outcomes:
            print(f"  SKIPPED {reason}")
        return 0

    report = submitter.settle(payloads)
    confirmations = [
        {"tradeHash": o.trade_hash, "bidOrderId": o.bid_order_id, "askOrderId": o.ask_order_id, "amount": o.amount}
        for o in report.outcomes if o.status == TradeStatus.SETTLED
    ]
    for tx in report.tx_hashes:
        print(f"TxHash: {tx}")
    for o in report.outcomes:
        suffix = f" ({o.reason})" if o.reason else ""
        print(f"  {o.status.value} {o.trade_hash}{suffix}")
    if confirmations:
        _http("POST", f"{base}/api/v1/settlements/confirm", api_key, {"settlements": confirmations})
        print(f"Đã ghi nhận {len(confirmations)} trade SETTLED về engine")
    if report.error:
        print(f"LỖI: {report.error}", file=sys.stderr)
    return 1 if report.error or report.count(TradeStatus.FAILED) else 0


if __name__ == "__main__":
    sys.exit(main())
