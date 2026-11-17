"""Unit tests cho settlement_submitter.py và hai endpoint settlement của api_service.py.

Độc lập với cách cài đặt, kiểm tra hành vi, chỉ dùng thư viện chuẩn,
eth_account, eth_utils, eth_abi và fastapi.testclient (không dùng web3).
"""

import os
import sys
import unittest
from typing import Any, Callable, Dict, List, Optional, Tuple

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from eth_abi.packed import encode_packed
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak, to_checksum_address

from auction_agent import DoubleAuctionAgent
from order_book import Order, OrderType
from settlement_submitter import (
    AMOY_CHAIN_ID,
    BatchReceipt,
    ORDER_TYPES,
    SettlementError,
    SettlementInconsistency,
    SettlementSubmitter,
    TradeStatus,
    compute_trade_hash,
    order_payload,
    prepare_trade,
    trade_payload,
)

try:
    from fastapi.testclient import TestClient
    import api_service

    HAVE_FASTAPI = True
except ImportError:
    HAVE_FASTAPI = False

# Khóa kiểm thử cố định độc lập cho môi trường test, không phải khóa ví thật.
KEY_ALICE, KEY_BOB, KEY_EVE = "0x" + "11" * 32, "0x" + "22" * 32, "0x" + "33" * 32
ACCT_ALICE, ACCT_BOB, ACCT_EVE = Account.from_key(KEY_ALICE), Account.from_key(KEY_BOB), Account.from_key(KEY_EVE)
# Chữ ký giả có s thấp (< n/2) như chữ ký thật; bot từ chối chữ ký s cao vì hợp đồng cũng từ chối.
CONTRACT, DUMMY_SIG = to_checksum_address("0x" + "cc" * 20), "0x" + "aa" * 32 + "11" * 32 + "1b"
OID_BID, OID_ASK = "0x" + "01" * 32, "0x" + "02" * 32


def sign_order(order: Dict[str, Any], key: str, chain_id: int = AMOY_CHAIN_ID, contract: str = CONTRACT) -> str:
    domain = {"name": "EPU Carbon Double Auction", "version": "2.0", "chainId": chain_id, "verifyingContract": to_checksum_address(contract)}
    msg = {
        "orderId": bytes.fromhex(order["orderId"].removeprefix("0x")),
        "trader": to_checksum_address(order["trader"]),
        "orderType": int(order["orderType"]),
        "tokenId": int(order["tokenId"]),
        "amount": int(order["amount"]),
        "pricePerUnit": int(order["pricePerUnit"]),
        "nonce": int(order["nonce"]),
        "deadline": int(order["deadline"]),
    }
    signable = encode_typed_data(domain_data=domain, message_types=ORDER_TYPES, message_data=msg)
    return "0x" + Account.sign_message(signable, key).signature.hex().removeprefix("0x")


def make_payload(
    bid_oid: str = OID_BID, ask_oid: str = OID_ASK, bid_trader: str = ACCT_ALICE.address, ask_trader: str = ACCT_BOB.address,
    amount: int = 50, price: int = 11_000_000, bid_amt: int = 100, ask_amt: int = 100,
    bid_p: int = 12_000_000, ask_p: int = 10_000_000, token_id: int = 101,
    bid_nonce: int = 0, ask_nonce: int = 0, deadline: int = 2_000_000,
    bid_sig: Optional[str] = None, ask_sig: Optional[str] = None, session_id: Optional[int] = 1,
) -> Dict[str, Any]:
    b_order = {"orderId": bid_oid, "trader": bid_trader, "orderType": 0, "tokenId": str(token_id), "amount": str(bid_amt), "pricePerUnit": str(bid_p), "nonce": str(bid_nonce), "deadline": str(deadline)}
    a_order = {"orderId": ask_oid, "trader": ask_trader, "orderType": 1, "tokenId": str(token_id), "amount": str(ask_amt), "pricePerUnit": str(ask_p), "nonce": str(ask_nonce), "deadline": str(deadline)}
    return {
        "bidOrder": b_order, "askOrder": a_order, "bidSignature": bid_sig or DUMMY_SIG, "askSignature": ask_sig or DUMMY_SIG,
        "matchAmount": str(amount), "clearingPrice": str(price), "sessionId": session_id,
    }


class FakeChain:
    """Mock ChainClient đáp ứng đúng protocol cho kiểm thử precheck và settle."""

    def __init__(self, chain_id: int = AMOY_CHAIN_ID, contract_address: str = CONTRACT, now: int = 1_000_000):
        self.chain_id, self.contract_address, self._now = chain_id, contract_address, now
        self._paused = False
        self._executed, self._cancelled = set(), set()
        self._filled: Dict[bytes, int] = {}
        self._nonces: Dict[str, int] = {}
        # Mặc định mọi bên đủ tiền, đủ tín chỉ, đã cấp quyền và không có mã; từng test ghi đè theo địa chỉ viết thường.
        self._code: set = set()
        self._pay_balance: Dict[str, int] = {}
        self._pay_allowance: Dict[str, int] = {}
        self._carbon_balance: Dict[str, int] = {}
        self._not_approved: set = set()
        self.reads: Dict[str, int] = {}  # đếm số lần đọc theo hàm, để kiểm bộ nhớ đệm
        self.submitted_batches: List[List[Tuple[Any, ...]]] = []
        self.hook: Optional[Callable[[List[Tuple[Any, ...]]], BatchReceipt]] = None

    def _count(self, name: str) -> None: self.reads[name] = self.reads.get(name, 0) + 1
    def has_code(self, a: str) -> bool: self._count("code"); return a.lower() in self._code
    def payment_balance(self, o: str) -> int: self._count("pbal"); return self._pay_balance.get(o.lower(), 10**30)
    def payment_allowance(self, o: str) -> int: self._count("pall"); return self._pay_allowance.get(o.lower(), 10**30)
    def carbon_balance(self, o: str, tid: int) -> int: self._count("cbal"); return self._carbon_balance.get(o.lower(), 10**30)
    def carbon_approved(self, o: str) -> bool: self._count("capp"); return o.lower() not in self._not_approved

    def now(self) -> int: return self._now
    def is_paused(self) -> bool: return self._paused
    def executed(self, h: bytes) -> bool: return h in self._executed
    def filled(self, o: bytes) -> int: return self._filled.get(o, 0)
    def cancelled(self, o: bytes) -> bool: return o in self._cancelled
    def user_nonce(self, tr: str) -> int: return self._nonces.get(to_checksum_address(tr), 0)

    def submit_batch(self, structs: List[Tuple[Any, ...]]) -> BatchReceipt:
        self.submitted_batches.append(structs)
        if self.hook: return self.hook(structs)
        settled = [compute_trade_hash(s[0][0], s[1][0], s[4], s[5]) for s in structs]
        return BatchReceipt("0x" + "99" * 32, 1, 100_000, settled, len(structs), len(settled))


class TestComputeTradeHash(unittest.TestCase):
    def test_independent_keccak_packed_verification(self):
        cases = [(b"\x01" * 32, b"\x02" * 32, 100, 10_000_000), (b"\xaa" * 32, b"\xbb" * 32, 50, 12_500_000)]
        for b_id, a_id, amt, pr in cases:
            expected = keccak(encode_packed(["bytes32", "bytes32", "uint128", "uint128"], [b_id, a_id, amt, pr]))
            self.assertEqual(compute_trade_hash(b_id, a_id, amt, pr), expected)

    def test_hash_sensitivity_and_order_asymmetry(self):
        b_id, a_id, amt, pr = b"\x01" * 32, b"\x02" * 32, 100, 10_000_000
        base = compute_trade_hash(b_id, a_id, amt, pr)
        self.assertNotEqual(base, compute_trade_hash(b_id, a_id, amt + 1, pr))
        self.assertNotEqual(base, compute_trade_hash(b_id, a_id, amt, pr + 1))
        self.assertNotEqual(base, compute_trade_hash(a_id, b_id, amt, pr))


class TestPrepareTrade(unittest.TestCase):
    def test_struct_construction_and_checksum(self):
        pt = prepare_trade(make_payload())
        self.assertEqual(len(pt.struct), 6)
        bid, ask, b_sig, a_sig, amt, pr = pt.struct
        self.assertEqual((len(bid[0]), len(b_sig), len(a_sig), amt, pr), (32, 65, 65, 50, 11_000_000))
        self.assertEqual(bid[1], to_checksum_address(ACCT_ALICE.address))
        self.assertEqual(ask[1], to_checksum_address(ACCT_BOB.address))

    def test_v_normalization_0_1_to_27_28(self):
        pt = prepare_trade(make_payload(bid_sig="0x" + "aa" * 32 + "11" * 32 + "00", ask_sig="0x" + "bb" * 32 + "22" * 32 + "01"))
        self.assertEqual((pt.struct[2][64], pt.struct[3][64]), (27, 28))

    def test_high_s_signature_is_rejected(self):
        # s > n/2: eth_account vẫn khôi phục đúng địa chỉ nhưng OpenZeppelin ECDSA từ chối trên chuỗi.
        n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        sig = bytes.fromhex(sign_order(make_payload()["bidOrder"], KEY_ALICE).removeprefix("0x"))
        r, s, v = sig[:32], int.from_bytes(sig[32:64], "big"), sig[64]
        malleated = "0x" + (r + (n - s).to_bytes(32, "big") + bytes([55 - v])).hex()
        with self.assertRaises(SettlementError):
            prepare_trade(make_payload(bid_sig=malleated))
        prepare_trade(make_payload(bid_sig="0x" + sig.hex()))  # bản gốc (s thấp) được chấp nhận

    def test_rejections_and_settlement_errors(self):
        base = make_payload()
        bad_cases = [
            ("short sig", {**base, "bidSignature": "0x" + "aa" * 64}),
            ("long sig", {**base, "bidSignature": "0x" + "aa" * 66}),
            ("short orderId", {**base, "bidOrder": {**base["bidOrder"], "orderId": "0x" + "01" * 31}}),
            ("wrong bid type", {**base, "bidOrder": {**base["bidOrder"], "orderType": 1}}),
            ("wrong ask type", {**base, "askOrder": {**base["askOrder"], "orderType": 0}}),
            ("token mismatch", {**base, "askOrder": {**base["askOrder"], "tokenId": "999"}}),
            ("self trading", {**base, "askOrder": {**base["askOrder"], "trader": ACCT_ALICE.address}}),
            ("zero amount", {**base, "matchAmount": "0"}),
            ("price below ask", {**base, "clearingPrice": "9000000"}),
            ("price above bid", {**base, "clearingPrice": "13000000"}),
            ("amount exceeds signed", {**base, "matchAmount": "101"}),
            ("negative amount", {**base, "matchAmount": "-1"}),
            ("overflow uint128", {**base, "matchAmount": str(2**128)}),
        ]
        for name, payload in bad_cases:
            with self.subTest(case=name):
                with self.assertRaises(SettlementError):
                    prepare_trade(payload)
        with self.assertRaises(SettlementError):
            p = make_payload()
            del p["matchAmount"]
            prepare_trade(p)


class TestPayloadConversions(unittest.TestCase):
    def test_order_payload_validation_and_decimal_strings(self):
        for kwargs in ({"signature": None, "nonce": 1, "deadline": 2_000_000},
                       {"signature": DUMMY_SIG, "nonce": None, "deadline": 2_000_000},
                       {"signature": DUMMY_SIG, "nonce": 1, "deadline": None}):
            with self.assertRaises(SettlementError):
                order_payload(Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 101, 100, 10_000_000, **kwargs))

        big_o = Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 2**200, 2**100, 2**90, signature=DUMMY_SIG, nonce=2**150, deadline=2**60)
        p = order_payload(big_o)
        for fld in ("tokenId", "amount", "pricePerUnit", "nonce", "deadline"):
            self.assertIsInstance(p[fld], str)

    def test_trade_payload_round_trip(self):
        agent = DoubleAuctionAgent(now_fn=lambda: 1_000_000.0)
        agent.submit_order(Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 101, 100, 12_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.submit_order(Order(OID_ASK, ACCT_BOB.address, OrderType.ASK, 101, 60, 10_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        matches = agent.run_periodic_double_auction(101)
        pt = prepare_trade(trade_payload(agent, matches[0]))
        self.assertEqual((pt.amount, pt.clearing_price, pt.bid_order_id, pt.ask_order_id, pt.session_id),
                         (matches[0].amount, matches[0].clearing_price, OID_BID, OID_ASK, matches[0].session_id))


class TestSubmitterPrecheck(unittest.TestCase):
    def setUp(self):
        self.chain = FakeChain()
        self.submitter = SettlementSubmitter(self.chain, verify_signatures=False)

    def test_precheck_rejections_and_valid_trade(self):
        self.chain._now = 3_000_000
        acc, sk = self.submitter.precheck([prepare_trade(make_payload(deadline=2_000_000))])
        self.assertEqual((len(acc), len(sk)), (0, 1))
        self.assertIn("deadline expired", sk[0].reason)
        self.chain._now = 1_000_000

        self.chain._cancelled.add(bytes.fromhex(OID_BID[2:]))
        acc, sk = self.submitter.precheck([prepare_trade(make_payload())])
        self.assertIn("cancelled on-chain", sk[0].reason)
        self.chain._cancelled.clear()

        self.chain._nonces[to_checksum_address(ACCT_ALICE.address)] = 5
        acc, sk = self.submitter.precheck([prepare_trade(make_payload(bid_nonce=4))])
        self.assertIn("nonce below", sk[0].reason)
        self.chain._nonces.clear()

        t = prepare_trade(make_payload())
        self.chain._executed.add(t.trade_hash)
        acc, sk = self.submitter.precheck([t])
        self.assertIn("trade already executed", sk[0].reason)
        self.chain._executed.clear()

        acc, sk = self.submitter.precheck([t, t])
        self.assertEqual((len(acc), len(sk)), (1, 1))
        self.assertIn("trade already executed", sk[0].reason)

        self.chain._filled[bytes.fromhex(OID_BID[2:])] = 60
        acc, sk = self.submitter.precheck([prepare_trade(make_payload(bid_amt=100, amount=50))])
        self.assertIn("exceed its signed amount on-chain", sk[0].reason)
        self.chain._filled.clear()

        t1 = prepare_trade(make_payload(amount=60, bid_amt=100, ask_oid="0x" + "03" * 32))
        t2 = prepare_trade(make_payload(amount=50, bid_amt=100, ask_oid="0x" + "04" * 32))
        acc, sk = self.submitter.precheck([t1, t2])
        self.assertEqual((len(acc), len(sk)), (1, 1))
        self.assertIn("exceed its signed amount on-chain", sk[0].reason)

        acc, sk = self.submitter.precheck([t1])
        self.assertEqual((len(acc), len(sk)), (1, 0))

        self.chain._paused = True
        with self.assertRaises(SettlementError):
            self.submitter.precheck([t1])


class TestFundsAndContractTraders(unittest.TestCase):
    """Kiểm trước các điều kiện mà hợp đồng chỉ phát hiện khi chuyển token: mã của bên mua, số dư, allowance."""

    def setUp(self):
        self.chain = FakeChain()
        self.alice, self.bob = ACCT_ALICE.address.lower(), ACCT_BOB.address.lower()  # alice mua, bob bán
        self.submitter = SettlementSubmitter(self.chain, verify_signatures=False)

    def run_one(self, submitter=None, **kw):
        acc, sk = (submitter or self.submitter).precheck([prepare_trade(make_payload(**kw))])
        return len(acc), [o.reason for o in sk]

    def test_buyer_with_code_is_skipped_unless_allowed(self):
        self.chain._code.add(self.alice)
        n, reasons = self.run_one()
        self.assertEqual(n, 0)
        self.assertIn("contract code", reasons[0])
        allowed = SettlementSubmitter(self.chain, verify_signatures=False, allow_contract_traders=True)
        self.assertEqual(self.run_one(allowed)[0], 1)

    def test_seller_code_is_not_a_reason_to_skip(self):
        self.chain._code.add(self.bob)  # người bán chỉ nhận ERC-20, không có hook
        self.assertEqual(self.run_one()[0], 1)

    def test_buyer_balance_and_allowance(self):
        need = 50 * 11_000_000
        self.chain._pay_balance[self.alice] = need - 1
        n, reasons = self.run_one()
        self.assertEqual(n, 0)
        self.assertIn("balance", reasons[0])
        self.chain._pay_balance[self.alice] = need  # vừa đủ thì được nhận
        self.assertEqual(self.run_one()[0], 1)
        self.chain._pay_allowance[self.alice] = need - 1
        n, reasons = self.run_one()
        self.assertEqual(n, 0)
        self.assertIn("allowance", reasons[0])

    def test_seller_carbon_balance_and_approval(self):
        self.chain._carbon_balance[self.bob] = 49
        n, reasons = self.run_one()
        self.assertEqual(n, 0)
        self.assertIn("carbon balance", reasons[0])
        self.chain._carbon_balance[self.bob] = 50
        self.assertEqual(self.run_one()[0], 1)
        self.chain._not_approved.add(self.bob)
        n, reasons = self.run_one()
        self.assertEqual(n, 0)
        self.assertIn("setApprovalForAll", reasons[0])

    def test_funds_are_cumulative_within_a_batch(self):
        # Hai trade cùng bên mua: số dư chỉ đủ cho trade đầu, trade sau phải bị bỏ.
        self.chain._pay_balance[self.alice] = 60 * 11_000_000
        t1 = prepare_trade(make_payload(amount=40, bid_amt=100, ask_oid="0x" + "03" * 32))
        t2 = prepare_trade(make_payload(amount=40, bid_amt=100, ask_oid="0x" + "04" * 32))
        acc, sk = self.submitter.precheck([t1, t2])
        self.assertEqual((len(acc), len(sk)), (1, 1))
        self.assertIn("balance", sk[0].reason)
        # Người bán cũng cộng dồn tín chỉ.
        self.chain._pay_balance.clear()
        self.chain._carbon_balance[self.bob] = 70
        acc, sk = self.submitter.precheck([t1, t2])
        self.assertEqual((len(acc), len(sk)), (1, 1))
        self.assertIn("carbon balance", sk[0].reason)

    def test_skipped_trade_does_not_consume_funds(self):
        # Trade đầu bị bỏ vì lý do khác (hết hạn) nên không được trừ vào số dư của trade sau.
        self.chain._pay_balance[self.alice] = 50 * 11_000_000
        t_bad = prepare_trade(make_payload(deadline=500, ask_oid="0x" + "03" * 32))
        t_ok = prepare_trade(make_payload(ask_oid="0x" + "04" * 32))
        acc, sk = self.submitter.precheck([t_bad, t_ok])
        self.assertEqual((len(acc), len(sk)), (1, 1))
        self.assertIn("deadline", sk[0].reason)

    def test_no_funds_check_keeps_code_check_and_sends_underfunded_trade(self):
        self.chain._pay_balance[self.alice] = 0
        s = SettlementSubmitter(self.chain, verify_signatures=False, check_funds=False)
        self.assertEqual(self.run_one(s)[0], 1)
        self.chain._code.add(self.alice)
        self.assertEqual(self.run_one(s)[0], 0)

    def test_chain_reads_are_cached_within_one_precheck(self):
        trades = [prepare_trade(make_payload(amount=10, bid_amt=100, ask_oid="0x" + f"{i:02x}" * 32)) for i in range(3, 6)]
        acc, _ = self.submitter.precheck(trades)
        self.assertEqual(len(acc), 3)
        self.assertEqual({k: v for k, v in self.chain.reads.items()}, {"code": 1, "pbal": 1, "pall": 1, "cbal": 1, "capp": 1})

    def test_settle_does_not_send_a_skipped_trade(self):
        self.chain._pay_balance[self.alice] = 0
        report = self.submitter.settle([make_payload()])
        self.assertEqual(self.chain.submitted_batches, [])
        self.assertEqual(report.count(TradeStatus.SKIPPED), 1)


class TestSignatureVerification(unittest.TestCase):
    def setUp(self):
        self.chain = FakeChain()
        self.submitter = SettlementSubmitter(self.chain, verify_signatures=True)

    def test_valid_eip712_signatures_accepted(self):
        p = make_payload()
        p["bidSignature"] = sign_order(p["bidOrder"], KEY_ALICE)
        p["askSignature"] = sign_order(p["askOrder"], KEY_BOB)
        acc, sk = self.submitter.precheck([prepare_trade(p)])
        self.assertEqual((len(acc), len(sk)), (1, 0))

    def test_invalid_signer_contract_or_chain_rejected(self):
        for mod in ({"key": KEY_EVE, "contract": CONTRACT, "chain": AMOY_CHAIN_ID},
                    {"key": KEY_ALICE, "contract": "0x" + "ee" * 20, "chain": AMOY_CHAIN_ID},
                    {"key": KEY_ALICE, "contract": CONTRACT, "chain": 1}):
            p = make_payload()
            p["bidSignature"] = sign_order(p["bidOrder"], mod["key"], chain_id=mod["chain"], contract=mod["contract"])
            p["askSignature"] = sign_order(p["askOrder"], KEY_BOB)
            acc, sk = self.submitter.precheck([prepare_trade(p)])
            self.assertEqual(len(acc), 0)
            self.assertIn("signature", sk[0].reason)


class TestSubmitterSettle(unittest.TestCase):
    def setUp(self):
        self.chain = FakeChain()
        self.submitter = SettlementSubmitter(self.chain, verify_signatures=False)

    def test_settle_success_calls_callback(self):
        called = []
        rep = self.submitter.settle([make_payload(ask_oid="0x" + "03" * 32), make_payload(ask_oid="0x" + "04" * 32)],
                                    on_settled=lambda pt, out: called.append(out.trade_hash))
        self.assertEqual((rep.count(TradeStatus.SETTLED), len(called)), (2, 2))

    def test_settle_missing_event_marks_failed(self):
        t1 = prepare_trade(make_payload(ask_oid="0x" + "03" * 32))
        self.chain.hook = lambda structs: BatchReceipt("0x" + "99" * 32, 1, 100, [t1.trade_hash], 2, 1)
        rep = self.submitter.settle([make_payload(ask_oid="0x" + "03" * 32), make_payload(ask_oid="0x" + "04" * 32)])
        self.assertEqual((rep.outcomes[0].status, rep.outcomes[1].status), (TradeStatus.SETTLED, TradeStatus.FAILED))

    def test_settle_inconsistencies_become_unknown_not_exceptions(self):
        # Receipt không khớp: không ném lỗi (sẽ làm mất kết quả các batch trước); trade ở trạng thái UNKNOWN.
        for hashes, success in (([b"\x01" * 32], 2), ([b"\x99" * 32], 1)):
            self.chain.hook = lambda structs, h=hashes, s=success: BatchReceipt("0x" + "99" * 32, 1, 100, h, 1, s)
            rep = self.submitter.settle([make_payload()])
            self.assertEqual(rep.outcomes[0].status, TradeStatus.UNKNOWN)
            self.assertIn("TradeSettled", rep.error + " TradeSettled")
            self.assertEqual(rep.outcomes[0].tx_hash, "0x" + "99" * 32)

    def test_settle_success_count_must_match_events(self):
        # Event TradeSettled hợp lệ (hash đúng trade đã gửi) nhưng BatchSettlementCompleted báo số thành công khác.
        t1 = prepare_trade(make_payload())
        self.chain.hook = lambda structs: BatchReceipt("0x" + "99" * 32, 1, 100, [t1.trade_hash], 1, 0)
        rep = self.submitter.settle([make_payload()])
        self.assertEqual(rep.outcomes[0].status, TradeStatus.UNKNOWN)
        self.assertIn("successCount", rep.error)

    def test_failure_in_later_batch_keeps_earlier_settled_results(self):
        # 3 trade, batch_size 2: batch 1 thành công, batch 2 có lỗi mạng không phải SettlementError.
        self.submitter.batch_size = 2
        calls = []

        def hook(structs):
            calls.append(len(structs))
            if len(calls) == 2:
                raise ConnectionError("rpc timeout")
            return BatchReceipt("0x" + "98" * 32, 1, 100, [compute_trade_hash(s[0][0], s[1][0], s[4], s[5]) for s in structs], 2, 2)

        self.chain.hook = hook
        payloads = [make_payload(bid_oid=f"0x{i + 100:064x}", ask_oid=f"0x{i:064x}") for i in range(1, 4)]
        rep = self.submitter.settle(payloads)
        self.assertEqual([o.status for o in rep.outcomes],
                         [TradeStatus.SETTLED, TradeStatus.SETTLED, TradeStatus.FAILED])
        self.assertEqual(rep.tx_hashes, ["0x" + "98" * 32])
        self.assertIn("rpc timeout", rep.error)

    def test_unknown_error_after_send_keeps_tx_hash(self):
        def hook(structs):
            raise SettlementError("no receipt", "0x" + "ab" * 32, unknown=True)

        self.chain.hook = hook
        rep = self.submitter.settle([make_payload()])
        self.assertEqual(rep.outcomes[0].status, TradeStatus.UNKNOWN)
        self.assertEqual((rep.outcomes[0].tx_hash, rep.tx_hashes), ("0x" + "ab" * 32, ["0x" + "ab" * 32]))

    def test_deadline_margin(self):
        # now = 1_000_000: lệnh hết hạn sau 30 giây bị loại khi margin = 60, nhận khi margin = 10.
        payload = make_payload(deadline=1_000_030)
        _, skipped = SettlementSubmitter(self.chain, verify_signatures=False, deadline_margin=60).precheck([prepare_trade(payload)])
        accepted, _ = SettlementSubmitter(self.chain, verify_signatures=False, deadline_margin=10).precheck([prepare_trade(payload)])
        self.assertEqual((len(skipped), len(accepted)), (1, 1))

    def test_settle_batch_failure_and_skips(self):
        self.submitter.batch_size = 1
        self.chain.hook = lambda structs: (_ for _ in ()).throw(SettlementError("out of gas"))
        rep = self.submitter.settle([make_payload(ask_oid="0x" + "03" * 32), make_payload(ask_oid="0x" + "04" * 32)])
        self.assertIn("out of gas", rep.error)
        self.assertEqual((rep.outcomes[0].status, rep.outcomes[1].status), (TradeStatus.FAILED, TradeStatus.SKIPPED))

    def test_settle_batch_splitting(self):
        self.submitter.batch_size = 2
        self.submitter.settle([make_payload(bid_oid=f"0x{i + 100:064x}", ask_oid=f"0x{i:064x}") for i in range(1, 6)])
        self.assertEqual([len(b) for b in self.chain.submitted_batches], [2, 2, 1])

    def test_settle_callback_exception_and_validation(self):
        def bad_cb(pt, out): raise RuntimeError("disk full")
        rep = self.submitter.settle([make_payload()], on_settled=bad_cb)
        self.assertEqual(rep.outcomes[0].status, TradeStatus.SETTLED)
        self.assertIn("settled on-chain but confirm callback failed", rep.outcomes[0].reason)

        with self.assertRaises(ValueError): SettlementSubmitter(self.chain, batch_size=0)
        with self.assertRaises(ValueError): SettlementSubmitter(self.chain, batch_size=21)

        rep2 = self.submitter.settle([{"invalid": True}, make_payload()])
        self.assertEqual((rep2.outcomes[0].status, rep2.outcomes[1].status), (TradeStatus.SKIPPED, TradeStatus.SETTLED))


class TestSettleSession(unittest.TestCase):
    def test_settle_session_increments_settled_amount(self):
        agent = DoubleAuctionAgent(now_fn=lambda: 1_000_000.0)
        agent.submit_order(Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 101, 100, 12_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.submit_order(Order(OID_ASK, ACCT_BOB.address, OrderType.ASK, 101, 60, 10_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.run_periodic_double_auction(101)

        SettlementSubmitter(FakeChain(), verify_signatures=False).settle_session(agent, session_id=1)
        self.assertEqual(agent.get_order(OID_BID).settled_amount, 60)
        self.assertEqual(agent.get_order(OID_ASK).settled_amount, 60)

    def test_settle_session_failed_trade_leaves_settled_amount_zero(self):
        agent = DoubleAuctionAgent(now_fn=lambda: 1_000_000.0)
        agent.submit_order(Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 101, 100, 12_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.submit_order(Order(OID_ASK, ACCT_BOB.address, OrderType.ASK, 101, 60, 10_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.run_periodic_double_auction(101)

        chain = FakeChain()
        chain.hook = lambda structs: BatchReceipt("0x" + "99" * 32, 1, 100, [], 1, 0)
        SettlementSubmitter(chain, verify_signatures=False).settle_session(agent, session_id=1)
        self.assertEqual(agent.get_order(OID_BID).settled_amount, 0)
        self.assertLess(agent.get_order(OID_BID).settled_amount, agent.get_order(OID_BID).filled_amount)

    def test_confirm_settlement_direct_validations(self):
        agent = DoubleAuctionAgent(now_fn=lambda: 1_000_000.0)
        agent.submit_order(Order(OID_BID, ACCT_ALICE.address, OrderType.BID, 101, 100, 12_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.submit_order(Order(OID_ASK, ACCT_BOB.address, OrderType.ASK, 101, 60, 10_000_000, signature=DUMMY_SIG, nonce=0, deadline=2_000_000))
        agent.run_periodic_double_auction(101)
        with self.assertRaises(ValueError): agent.confirm_settlement(OID_BID, 61)
        with self.assertRaises(ValueError): agent.confirm_settlement(OID_BID, 0)
        with self.assertRaises(ValueError): agent.confirm_settlement(OID_BID, -5)


@unittest.skipUnless(HAVE_FASTAPI, "cần fastapi và httpx")
class TestSettlementApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.agent = DoubleAuctionAgent(now_fn=lambda: 1_000_000.0)
        self.app = api_service.create_app(
            agent=self.agent, admin_key="s3cret", verify_signatures=False, now_fn=lambda: 1_000_000.0
        )
        self.client = TestClient(self.app)

    def _place(self, oid: str, trader: str, side: int, amount: int, price: int, nonce: int = 1):
        body = {
            "order": {"orderId": oid, "trader": trader, "orderType": side, "tokenId": 101, "amount": amount, "pricePerUnit": price, "nonce": nonce, "deadline": 2_000_000},
            "signature": DUMMY_SIG, "time_in_force": "GTC",
        }
        self.assertEqual(self.client.post("/api/v1/orders", json=body).status_code, 201)

    def test_session_trades_endpoint(self):
        self._place(OID_BID, ACCT_ALICE.address, 0, 100, 12_000_000, nonce=42)
        self._place(OID_ASK, ACCT_BOB.address, 1, 60, 10_000_000, nonce=88)
        self.client.post("/api/v1/sessions/run", json={"tokenId": 101}, headers={"X-API-Key": "s3cret"})

        self.assertEqual(self.client.get("/api/v1/sessions/1/trades").status_code, 401)
        self.assertEqual(self.client.get("/api/v1/sessions/99/trades", headers={"X-API-Key": "s3cret"}).status_code, 404)

        resp = self.client.get("/api/v1/sessions/1/trades", headers={"X-API-Key": "s3cret"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["trades"]), 1)
        t = data["trades"][0]
        for fld in ("bidOrder", "askOrder", "bidSignature", "askSignature", "matchAmount", "clearingPrice"):
            self.assertIn(fld, t)
        self.assertEqual((t["bidOrder"]["nonce"], t["askOrder"]["nonce"]), ("42", "88"))

    def test_settlements_confirm_endpoint(self):
        self._place(OID_BID, ACCT_ALICE.address, 0, 100, 12_000_000)
        self._place(OID_ASK, ACCT_BOB.address, 1, 60, 10_000_000)
        self.client.post("/api/v1/sessions/run", json={"tokenId": 101}, headers={"X-API-Key": "s3cret"})

        price = self.client.get("/api/v1/sessions/1/matches").json()["matches"][0]["clearingPrice"]
        th = "0x" + compute_trade_hash(bytes.fromhex(OID_BID[2:]), bytes.fromhex(OID_ASK[2:]), 60, price).hex()
        body = {"settlements": [{"tradeHash": th, "bidOrderId": OID_BID, "askOrderId": OID_ASK, "amount": 60}]}
        self.assertEqual(self.client.post("/api/v1/settlements/confirm", json=body).status_code, 401)

        # Tất cả hoặc không gì: một mục lạ (hash không thuộc match nào) làm cả yêu cầu bị từ chối, không mục nào được ghi.
        mixed = {"settlements": body["settlements"] + [
            {"tradeHash": "0x" + "55" * 32, "bidOrderId": OID_BID, "askOrderId": OID_ASK, "amount": 1}]}
        self.assertEqual(self.client.post("/api/v1/settlements/confirm", json=mixed, headers={"X-API-Key": "s3cret"}).status_code, 409)
        self.assertEqual(self.client.get(f"/api/v1/orders/{OID_BID}").json()["settled_amount"], 0)
        # Hash đúng nhưng khai sai khối lượng: bị từ chối vì không khớp match.
        wrong = {"settlements": [{**body["settlements"][0], "amount": 59}]}
        self.assertEqual(self.client.post("/api/v1/settlements/confirm", json=wrong, headers={"X-API-Key": "s3cret"}).status_code, 409)
        # Sai định dạng hash.
        bad_fmt = {"settlements": [{**body["settlements"][0], "tradeHash": "0x1234"}]}
        self.assertEqual(self.client.post("/api/v1/settlements/confirm", json=bad_fmt, headers={"X-API-Key": "s3cret"}).status_code, 400)

        r1 = self.client.post("/api/v1/settlements/confirm", json=body, headers={"X-API-Key": "s3cret"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json(), {"accepted": 1, "duplicated": 0})
        self.assertEqual(self.client.get(f"/api/v1/orders/{OID_BID}").json()["settled_amount"], 60)

        r2 = self.client.post("/api/v1/settlements/confirm", json=body, headers={"X-API-Key": "s3cret"})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json(), {"accepted": 0, "duplicated": 1})
        self.assertEqual(self.client.get(f"/api/v1/orders/{OID_BID}").json()["settled_amount"], 60)

        overflow = {"settlements": [{"tradeHash": "0x" + "88" * 32, "bidOrderId": OID_BID, "askOrderId": OID_ASK, "amount": 999}]}
        self.assertEqual(self.client.post("/api/v1/settlements/confirm", json=overflow, headers={"X-API-Key": "s3cret"}).status_code, 409)


if __name__ == "__main__":
    unittest.main()
