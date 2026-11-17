"""Unit tests cho Web3Chain và các hàm CLI (_confirm, _recover) trong settlement_submitter.py.

Chỉ dùng thư viện chuẩn và các đối tượng giả (fake/mock), không phụ thuộc vào RPC thật.
"""

import io
import os
import sys
import unittest
import urllib.error
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from settlement_submitter import (
    AMOY_CHAIN_ID,
    BatchReceipt,
    SettlementError,
    SettlementSubmitter,
    TradeOutcome,
    TradeStatus,
    Web3Chain,
    _confirm,
    _recover,
    prepare_trade,
)

try:
    import web3
    HAVE_WEB3 = True
except ImportError:
    HAVE_WEB3 = False

DUMMY_CONTRACT = "0x" + "cc" * 20
DUMMY_OPERATOR = "0x" + "aa" * 20
DUMMY_SIG = "0x" + "aa" * 32 + "11" * 32 + "1b"


def _make_payload(
    bid_oid: str = "0x" + "01" * 32, ask_oid: str = "0x" + "02" * 32, amount: int = 50, price: int = 11_000_000,
) -> Dict[str, Any]:
    b = {"orderId": bid_oid, "trader": "0x" + "11" * 20, "orderType": 0, "tokenId": "101",
         "amount": "100", "pricePerUnit": "12000000", "nonce": "0", "deadline": "2000000"}
    a = {"orderId": ask_oid, "trader": "0x" + "22" * 20, "orderType": 1, "tokenId": "101",
         "amount": "100", "pricePerUnit": "10000000", "nonce": "0", "deadline": "2000000"}
    return {"bidOrder": b, "askOrder": a, "bidSignature": DUMMY_SIG, "askSignature": DUMMY_SIG,
            "matchAmount": str(amount), "clearingPrice": str(price), "sessionId": 1}


@unittest.skipUnless(HAVE_WEB3, "cần thư viện web3 để kiểm thử Web3Chain")
class TestWeb3Chain(unittest.TestCase):
    def setUp(self):
        self.w3, self.contract, self.account = MagicMock(), MagicMock(), MagicMock()
        self.contract.address, self.account.address = DUMMY_CONTRACT, DUMMY_OPERATOR
        self.chain = Web3Chain(self.w3, self.contract, self.account, AMOY_CHAIN_ID, 1.3, 30, 180)

        self.fn = self.contract.functions.batchSettleTrades.return_value
        self.fn.estimate_gas.return_value = 100_000
        self.fn.build_transaction.return_value = {"to": DUMMY_CONTRACT}

        self.w3.eth.max_priority_fee = 25 * 10**9
        self.w3.eth.get_block.return_value = {"timestamp": 1_000_000, "baseFeePerGas": 15 * 10**9}
        self.w3.eth.get_transaction_count.return_value = 10
        self.account.sign_transaction.return_value.raw_transaction = b"dummy_signed_raw_tx"

        self.tx_hash_bytes = bytes.fromhex("11" * 32)
        self.expected_tx_hash = "0x" + "11" * 32
        self.w3.eth.send_raw_transaction.return_value = self.tx_hash_bytes
        self.w3.eth.wait_for_transaction_receipt.return_value = {"status": 1, "blockNumber": 500, "gasUsed": 85000}

        self.contract.events.TradeSettled.return_value.process_receipt.return_value = [
            {"args": {"tradeHash": bytes.fromhex("01" * 32)}, "address": DUMMY_CONTRACT}
        ]
        self.contract.events.BatchSettlementCompleted.return_value.process_receipt.return_value = [
            {"args": {"tradesCount": 1, "successCount": 1}, "address": DUMMY_CONTRACT}
        ]

    def test_submit_batch_build_tx_error_raises_known_error_without_send(self):
        # 1. submit_batch lỗi ở bước dựng giao dịch: ném SettlementError (unknown=False, tx_hash=None)
        self.fn.estimate_gas.side_effect = ValueError("execution reverted: out of gas")
        with self.assertRaises(SettlementError) as ctx:
            self.chain.submit_batch([("dummy_struct",)])
        self.assertFalse(ctx.exception.unknown)
        self.assertIsNone(ctx.exception.tx_hash)
        self.w3.eth.send_raw_transaction.assert_not_called()

    def test_submit_batch_timeout_after_send_raises_unknown_with_tx_hash(self):
        # 2a. Lỗi sau khi gửi: wait_for_transaction_receipt ném TimeoutError
        self.w3.eth.wait_for_transaction_receipt.side_effect = TimeoutError("timeout waiting for receipt")
        with self.assertRaises(SettlementError) as ctx:
            self.chain.submit_batch([("dummy_struct",)])
        self.assertTrue(ctx.exception.unknown)
        self.assertEqual(ctx.exception.tx_hash, self.expected_tx_hash)
        self.assertTrue(ctx.exception.tx_hash.startswith("0x"))

    def test_submit_batch_send_raw_connection_error_raises_unknown_without_hash(self):
        # 2b. Lỗi khi gửi: send_raw_transaction ném ConnectionError
        self.w3.eth.send_raw_transaction.side_effect = ConnectionError("RPC connection reset")
        with self.assertRaises(SettlementError) as ctx:
            self.chain.submit_batch([("dummy_struct",)])
        self.assertTrue(ctx.exception.unknown)
        self.assertIsNone(ctx.exception.tx_hash)

    def test_submit_batch_reverted_receipt_status_zero_raises_known_error(self):
        # 3. Biên nhận status == 0: SettlementError với unknown == False và tx_hash đúng
        self.w3.eth.wait_for_transaction_receipt.return_value = {"status": 0, "blockNumber": 500, "gasUsed": 30000}
        with self.assertRaises(SettlementError) as ctx:
            self.chain.submit_batch([("dummy_struct",)])
        self.assertFalse(ctx.exception.unknown)
        self.assertEqual(ctx.exception.tx_hash, self.expected_tx_hash)
        self.assertIn("reverted", str(ctx.exception))

    def test_submit_batch_success_returns_batch_receipt_and_checks_tx_parameters(self):
        # 4. Thành công: trả BatchReceipt đúng; build_transaction nhận đúng các tham số EIP-1559
        hash1, hash2 = bytes.fromhex("01" * 32), bytes.fromhex("02" * 32)
        self.contract.events.TradeSettled.return_value.process_receipt.return_value = [
            {"args": {"tradeHash": hash1}, "address": DUMMY_CONTRACT},
            {"args": {"tradeHash": hash2}, "address": DUMMY_CONTRACT},
        ]
        self.contract.events.BatchSettlementCompleted.return_value.process_receipt.return_value = [
            {"args": {"tradesCount": 2, "successCount": 2}, "address": DUMMY_CONTRACT}
        ]

        receipt = self.chain.submit_batch([("struct1",), ("struct2",)])

        self.fn.build_transaction.assert_called_once()
        tx_args = self.fn.build_transaction.call_args[0][0]
        self.assertEqual(tx_args["chainId"], AMOY_CHAIN_ID)
        self.assertGreaterEqual(tx_args["maxPriorityFeePerGas"], 30 * 10**9)
        expected_priority = max(25 * 10**9, 30 * 10**9)
        expected_base_fee = 15 * 10**9
        self.assertEqual(tx_args["maxPriorityFeePerGas"], expected_priority)
        self.assertEqual(tx_args["maxFeePerGas"], expected_base_fee * 2 + expected_priority)
        self.assertEqual(tx_args["gas"], int(100_000 * 1.3))

        self.assertEqual(receipt.tx_hash, self.expected_tx_hash)
        self.assertEqual(receipt.block_number, 500)
        self.assertEqual(receipt.gas_used, 85000)
        self.assertEqual(receipt.settled_hashes, [hash1, hash2])
        for h in receipt.settled_hashes:
            self.assertIsInstance(h, bytes)
        self.assertEqual(receipt.trades_count, 2)
        self.assertEqual(receipt.success_count, 2)

    def test_parse_receipt_filters_logs_by_contract_address_case_insensitive(self):
        # 5. Lọc log: event từ địa chỉ khác bị bỏ qua; so sánh địa chỉ không phân biệt hoa thường
        own_upper, own_lower, foreign = DUMMY_CONTRACT.upper(), DUMMY_CONTRACT.lower(), "0x" + "ee" * 20
        h_own1, h_foreign, h_own2 = bytes.fromhex("01" * 32), bytes.fromhex("02" * 32), bytes.fromhex("03" * 32)

        self.contract.events.TradeSettled.return_value.process_receipt.return_value = [
            {"args": {"tradeHash": h_own1}, "address": own_upper},
            {"args": {"tradeHash": h_foreign}, "address": foreign},
            {"args": {"tradeHash": h_own2}, "address": own_lower},
        ]
        self.contract.events.BatchSettlementCompleted.return_value.process_receipt.return_value = [
            {"args": {"tradesCount": 2, "successCount": 2}, "address": foreign},
            {"args": {"tradesCount": 2, "successCount": 2}, "address": own_upper},
        ]

        receipt = self.chain._parse_receipt(self.expected_tx_hash, {"blockNumber": 10, "gasUsed": 5000})
        self.assertEqual(receipt.settled_hashes, [h_own1, h_own2])
        self.assertNotIn(h_foreign, receipt.settled_hashes)
        self.assertEqual(receipt.trades_count, 2)
        self.assertEqual(receipt.success_count, 2)

    def test_parse_receipt_unexpected_batch_completed_event_count_raises_unknown(self):
        # 6. Số event BatchSettlementCompleted hợp lệ khác 1 (0 hoặc 2): SettlementError unknown=True
        fake_receipt = {"blockNumber": 10, "gasUsed": 5000}
        self.contract.events.TradeSettled.return_value.process_receipt.return_value = []
        ev = {"args": {"tradesCount": 1, "successCount": 1}, "address": DUMMY_CONTRACT}
        for count, events in ((0, []), (2, [ev, ev])):
            with self.subTest(count=count):
                self.contract.events.BatchSettlementCompleted.return_value.process_receipt.return_value = events
                with self.assertRaises(SettlementError) as ctx:
                    self.chain._parse_receipt(self.expected_tx_hash, fake_receipt)
                self.assertTrue(ctx.exception.unknown)
                self.assertEqual(ctx.exception.tx_hash, self.expected_tx_hash)
                self.assertIn(f"got {count}", str(ctx.exception))

    def test_receipt_for_success_returns_batch_receipt(self):
        # 7a. receipt_for: trả BatchReceipt đúng khi thành công
        tx_hash = "0x" + "33" * 32
        self.w3.eth.get_transaction_receipt.return_value = {"status": 1, "blockNumber": 600, "gasUsed": 70000}
        res = self.chain.receipt_for(tx_hash)
        self.assertEqual(res.tx_hash, tx_hash)
        self.assertEqual(res.block_number, 600)
        self.assertEqual(res.gas_used, 70000)

    def test_receipt_for_read_error_raises_unknown_settlement_error(self):
        # 7b. receipt_for: lỗi đọc receipt -> SettlementError unknown=True
        tx_hash = "0x" + "33" * 32
        self.w3.eth.get_transaction_receipt.side_effect = RuntimeError("RPC connection lost")
        with self.assertRaises(SettlementError) as ctx:
            self.chain.receipt_for(tx_hash)
        self.assertTrue(ctx.exception.unknown)
        self.assertEqual(ctx.exception.tx_hash, tx_hash)

    def test_receipt_for_status_zero_raises_known_settlement_error(self):
        # 7c. receipt_for: status == 0 -> SettlementError unknown=False
        tx_hash = "0x" + "33" * 32
        self.w3.eth.get_transaction_receipt.return_value = {"status": 0, "blockNumber": 600, "gasUsed": 20000}
        with self.assertRaises(SettlementError) as ctx:
            self.chain.receipt_for(tx_hash)
        self.assertFalse(ctx.exception.unknown)
        self.assertEqual(ctx.exception.tx_hash, tx_hash)
        self.assertIn("reverted", str(ctx.exception))

    def test_web3_chain_read_only_methods(self):
        # Kiểm tra các hàm đọc không tốn gas của Web3Chain
        self.w3.eth.get_block.return_value = {"timestamp": 1_234_567}
        self.assertEqual(self.chain.now(), 1_234_567)

        self.contract.functions.paused.return_value.call.return_value = True
        self.assertTrue(self.chain.is_paused())

        self.contract.functions.executedTrades.return_value.call.return_value = True
        self.assertTrue(self.chain.executed(b"\x01" * 32))

        self.contract.functions.filledAmount.return_value.call.return_value = 50
        self.assertEqual(self.chain.filled(b"\x02" * 32), 50)

        self.contract.functions.cancelledOrders.return_value.call.return_value = False
        self.assertFalse(self.chain.cancelled(b"\x02" * 32))

        self.contract.functions.userNonces.return_value.call.return_value = 7
        self.assertEqual(self.chain.user_nonce(DUMMY_OPERATOR), 7)


    def test_has_code_distinguishes_eoa_from_code(self):
        # EOA thường: get_code trả b""; hợp đồng hoặc EOA ủy quyền EIP-7702: có byte.
        self.w3.eth.get_code.return_value = b""
        self.assertFalse(self.chain.has_code("0x" + "11" * 20))
        self.w3.eth.get_code.return_value = bytes.fromhex("ef0100" + "22" * 20)
        self.assertTrue(self.chain.has_code("0x" + "11" * 20))

    def test_token_reads_use_the_tokens_named_by_the_auction_contract(self):
        owner = "0x" + "11" * 20
        self.contract.functions.paymentToken.return_value.call.return_value = "0x" + "aa" * 20
        self.contract.functions.carbonToken.return_value.call.return_value = "0x" + "bb" * 20
        payment, carbon = MagicMock(), MagicMock()
        self.w3.eth.contract.side_effect = lambda address, abi: payment if address == "0x" + "aa" * 20 else carbon
        payment.functions.balanceOf.return_value.call.return_value = 7
        payment.functions.allowance.return_value.call.return_value = 9
        carbon.functions.balanceOf.return_value.call.return_value = 3
        carbon.functions.isApprovedForAll.return_value.call.return_value = True

        self.assertEqual(self.chain.payment_balance(owner), 7)
        self.assertEqual(self.chain.payment_allowance(owner), 9)
        self.assertEqual(self.chain.carbon_balance(owner, 101), 3)
        self.assertTrue(self.chain.carbon_approved(owner))
        # allowance và quyền ERC-1155 phải tính cho đúng hợp đồng đấu giá làm spender/operator
        spender = payment.functions.allowance.call_args[0][1]
        self.assertEqual(spender, DUMMY_CONTRACT)
        self.assertEqual(carbon.functions.isApprovedForAll.call_args[0][1], DUMMY_CONTRACT)
        carbon.functions.balanceOf.assert_called_once()
        self.assertEqual(carbon.functions.balanceOf.call_args[0][1], 101)
        self.contract.functions.paymentToken.assert_called_once()  # token chỉ được tra một lần


class TestSettlementCliFunctions(unittest.TestCase):
    @patch("settlement_submitter._http")
    def test_confirm_empty_list_returns_true_without_http_call(self, mock_http):
        # 8a. _confirm danh sách rỗng -> True và không gọi _http
        res = _confirm("http://localhost:8000", "test-key", [])
        self.assertTrue(res)
        mock_http.assert_not_called()

    @patch("settlement_submitter._http")
    def test_confirm_success_sends_required_keys_and_returns_true(self, mock_http):
        # 8b. _confirm thành công -> True, body có đúng các khóa tradeHash, bidOrderId, askOrderId, amount
        outcome = TradeOutcome(
            trade_hash="0x" + "11" * 32, bid_order_id="0x" + "01" * 32, ask_order_id="0x" + "02" * 32,
            amount=50, status=TradeStatus.SETTLED,
        )
        res = _confirm("http://localhost:8000", "test-key", [outcome])
        self.assertTrue(res)
        mock_http.assert_called_once()
        args, _ = mock_http.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "http://localhost:8000/api/v1/settlements/confirm")
        self.assertEqual(args[2], "test-key")
        body = args[3]
        self.assertIn("settlements", body)
        self.assertEqual(len(body["settlements"]), 1)
        item = body["settlements"][0]
        self.assertEqual(set(item.keys()), {"tradeHash", "bidOrderId", "askOrderId", "amount"})
        self.assertEqual(item["tradeHash"], "0x" + "11" * 32)
        self.assertEqual(item["bidOrderId"], "0x" + "01" * 32)
        self.assertEqual(item["askOrderId"], "0x" + "02" * 32)
        self.assertEqual(item["amount"], 50)

    @patch("settlement_submitter._http")
    def test_confirm_http_409_returns_false_and_prints_stderr(self, mock_http):
        # 8c. _confirm nhận urllib.error.HTTPError (mã 409) -> False và in lỗi ra stderr
        err = urllib.error.HTTPError(
            url="http://localhost:8000/api/v1/settlements/confirm",
            code=409, msg="Conflict", hdrs={}, fp=io.BytesIO(b"conflict with existing trades"),
        )
        mock_http.side_effect = err
        outcome = TradeOutcome("0x11", "0x01", "0x02", 50, TradeStatus.SETTLED)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            res = _confirm("http://localhost:8000", "test-key", [outcome])
        self.assertFalse(res)
        self.assertIn("409", mock_stderr.getvalue())

    @patch("settlement_submitter._http")
    def test_confirm_os_error_returns_false_and_prints_stderr(self, mock_http):
        # 8d. _confirm nhận OSError -> False
        mock_http.side_effect = OSError("Connection refused")
        outcome = TradeOutcome("0x11", "0x01", "0x02", 50, TradeStatus.SETTLED)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            res = _confirm("http://localhost:8000", "test-key", [outcome])
        self.assertFalse(res)
        self.assertIn("Connection refused", mock_stderr.getvalue())

    @patch("settlement_submitter._http")
    def test_recover_filters_foreign_hashes_and_reports_session_trades(self, mock_http):
        # 9a. _recover với chain giả: chỉ 2 trade của phiên được báo (kiểm body _http), trả 0
        p1 = _make_payload(bid_oid="0x" + "01" * 32, ask_oid="0x" + "02" * 32)
        p2 = _make_payload(bid_oid="0x" + "03" * 32, ask_oid="0x" + "04" * 32)
        t1, t2 = prepare_trade(p1), prepare_trade(p2)
        foreign_hash = bytes.fromhex("99" * 32)
        tx_hash = "0x" + "77" * 32

        fake_chain = Mock()
        fake_chain.receipt_for.return_value = BatchReceipt(
            tx_hash=tx_hash, block_number=100, gas_used=50000,
            settled_hashes=[t1.trade_hash, foreign_hash, t2.trade_hash],
            trades_count=3, success_count=3,
        )

        mock_http.return_value = {"accepted": 2}
        ret = _recover(fake_chain, [p1, p2], tx_hash, "http://localhost:8000", "test-key")
        self.assertEqual(ret, 0)
        mock_http.assert_called_once()
        sent_items = mock_http.call_args[0][3]["settlements"]
        self.assertEqual(len(sent_items), 2)
        sent_hashes = [x["tradeHash"] for x in sent_items]
        self.assertEqual(sent_hashes, [t1.hash_hex, t2.hash_hex])
        self.assertNotIn("0x" + foreign_hash.hex(), sent_hashes)

    @patch("settlement_submitter._http")
    def test_recover_returns_one_on_http_failure(self, mock_http):
        # 9b. _recover: nếu _http lỗi thì trả 1
        p1 = _make_payload()
        t1 = prepare_trade(p1)
        tx_hash = "0x" + "77" * 32
        fake_chain = Mock()
        fake_chain.receipt_for.return_value = BatchReceipt(
            tx_hash=tx_hash, block_number=100, gas_used=50000,
            settled_hashes=[t1.trade_hash], trades_count=1, success_count=1,
        )
        mock_http.side_effect = OSError("failed to connect to engine")
        with patch("sys.stderr", new_callable=io.StringIO):
            ret = _recover(fake_chain, [p1], tx_hash, "http://localhost:8000", "test-key")
        self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
