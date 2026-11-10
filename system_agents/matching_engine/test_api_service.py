"""Kiểm thử API Service mock (FR-15). Bỏ qua nếu chưa cài fastapi/eth-account (xem requirements.txt)."""

import os
import sys
import unittest

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
    from fastapi.testclient import TestClient

    import api_service
    from auction_agent import DoubleAuctionAgent

    HAVE_DEPS = True
except ImportError:  # pragma: no cover
    HAVE_DEPS = False

NOW = 1_000_000.0
FUTURE = 2_000_000
CONTRACT = "0x" + "ab" * 20
# Khóa kiểm thử sinh cố định cho test cục bộ; không phải khóa thật của ai.
KEY_ALICE = b"\x01" * 32
KEY_BOB = b"\x02" * 32


def oid(n: int) -> str:
    return "0x" + f"{n:064x}"


@unittest.skipUnless(HAVE_DEPS, "cần fastapi, eth-account, httpx")
class TestApiService(unittest.TestCase):
    def setUp(self):
        self.clock = [NOW]
        self.agent = DoubleAuctionAgent(now_fn=lambda: self.clock[0])
        self.app = api_service.create_app(
            agent=self.agent, contract_address=CONTRACT, now_fn=lambda: self.clock[0]
        )
        self.client = TestClient(self.app)
        self.alice = Account.from_key(KEY_ALICE)
        self.bob = Account.from_key(KEY_BOB)
        self.domain = {
            "name": "EPU Carbon Double Auction", "version": "2.0", "chainId": 80002,
            "verifyingContract": CONTRACT,
        }

    # ---- tiện ích
    def sign(self, key, types, message):
        signable = encode_typed_data(domain_data=self.domain, message_types=types, message_data=message)
        return "0x" + Account.sign_message(signable, private_key=key).signature.hex().removeprefix("0x")

    def order_body(self, key, acct, n, order_type, price, amount, tif="GTC", token=101, deadline=FUTURE):
        message = {
            "orderId": oid(n), "trader": acct.address, "orderType": order_type, "tokenId": token,
            "amount": amount, "pricePerUnit": price, "nonce": 0, "deadline": deadline,
        }
        return {"order": message, "signature": self.sign(key, api_service.ORDER_TYPES, message), "time_in_force": tif}

    def post(self, body):
        return self.client.post("/api/v1/orders", json=body)

    # ---- đặt lệnh
    def test_valid_signed_order_accepted(self):
        r = self.post(self.order_body(KEY_ALICE, self.alice, 1, 0, 10_000_000, 5))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"orderId": oid(1), "status": "NEW"})
        got = self.client.get(f"/api/v1/orders/{oid(1)}").json()
        self.assertEqual((got["amount"], got["remaining_amount"], got["status"]), (5, 5, "NEW"))

    def test_signature_from_other_wallet_rejected(self):
        body = self.order_body(KEY_BOB, self.bob, 2, 0, 10, 5)
        body["order"]["trader"] = self.alice.address  # Bob ký nhưng khai là Alice
        self.assertEqual(self.post(body).status_code, 401)

    def test_tampered_price_rejected(self):
        body = self.order_body(KEY_ALICE, self.alice, 3, 0, 10, 5)
        body["order"]["pricePerUnit"] = 1  # sửa giá sau khi ký
        self.assertEqual(self.post(body).status_code, 401)

    def test_garbage_signature_rejected(self):
        body = self.order_body(KEY_ALICE, self.alice, 4, 0, 10, 5)
        body["signature"] = "0x1234"
        self.assertEqual(self.post(body).status_code, 401)

    def test_bad_structure_and_values_are_400(self):
        good = self.order_body(KEY_ALICE, self.alice, 5, 0, 10, 5)
        for field, value in (("amount", 0), ("pricePerUnit", -1), ("orderType", 2), ("orderId", "0x12")):
            body = {**good, "order": {**good["order"], field: value}}
            self.assertEqual(self.post(body).status_code, 400, field)
        self.assertEqual(self.post({"order": good["order"]}).status_code, 400)  # thiếu signature

    def test_expired_deadline_is_400(self):
        body = self.order_body(KEY_ALICE, self.alice, 6, 0, 10, 5, deadline=int(NOW) - 1)
        self.assertEqual(self.post(body).status_code, 400)

    def test_duplicate_order_id_is_409(self):
        body = self.order_body(KEY_ALICE, self.alice, 7, 0, 10, 5)
        self.assertEqual(self.post(body).status_code, 201)
        self.assertEqual(self.post(body).status_code, 409)

    def test_unknown_order_is_404(self):
        self.assertEqual(self.client.get(f"/api/v1/orders/{oid(99)}").status_code, 404)

    # ---- phiên và sổ lệnh
    def test_session_run_uses_adr_price_and_updates_orderbook(self):
        self.post(self.order_body(KEY_ALICE, self.alice, 10, 0, 12_000_000, 100))  # BID
        self.post(self.order_body(KEY_BOB, self.bob, 11, 1, 10_000_000, 60))       # ASK
        book = self.client.get("/api/v1/orderbook/101").json()
        self.assertEqual(book["bids"], [{"price": 12_000_000, "amount": 100, "orders": 1}])
        self.assertEqual(book["asks"], [{"price": 10_000_000, "amount": 60, "orders": 1}])

        r = self.client.post("/api/v1/sessions/run", json={"tokenId": 101}).json()
        self.assertEqual(r["session_id"], 1)
        self.assertEqual(len(r["matches"]), 1)
        m = r["matches"][0]
        # ADR-001: floor((12_000_000 + 10_000_000) / 2) = 11_000_000
        self.assertEqual((m["amount"], m["clearingPrice"]), (60, 11_000_000))

        book = self.client.get("/api/v1/orderbook/101").json()
        self.assertEqual(book["bids"], [{"price": 12_000_000, "amount": 40, "orders": 1}])
        self.assertEqual(book["asks"], [])
        self.assertEqual(self.client.get("/api/v1/sessions/1/matches").json()["matches"], r["matches"])
        self.assertEqual(self.client.get("/api/v1/sessions/current").json()["next_session_id"], 2)
        self.assertEqual(self.client.get("/api/v1/sessions/9/matches").status_code, 404)

    def test_session_run_requires_admin_key_when_configured(self):
        app = api_service.create_app(agent=DoubleAuctionAgent(), admin_key="s3cret", verify_signatures=False)
        c = TestClient(app)
        self.assertEqual(c.post("/api/v1/sessions/run", json={"tokenId": 1}).status_code, 401)
        self.assertEqual(c.post("/api/v1/sessions/run", json={"tokenId": 1}, headers={"X-API-Key": "s3cret"}).status_code, 200)

    # ---- hủy lệnh
    def cancel_body(self, key, n, cancel_nonce, deadline=FUTURE):
        message = {"orderId": oid(n), "cancelNonce": cancel_nonce, "deadline": deadline}
        return {
            "signature": self.sign(key, api_service.CANCEL_TYPES, message),
            "cancel_nonce": cancel_nonce, "deadline": deadline,
        }

    def delete(self, n, body):
        return self.client.request("DELETE", f"/api/v1/orders/{oid(n)}", json=body)

    def test_cancel_with_valid_signature_removes_order(self):
        self.post(self.order_body(KEY_ALICE, self.alice, 20, 0, 10, 5))
        r = self.delete(20, self.cancel_body(KEY_ALICE, 20, 1))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "CANCELLED")
        self.assertEqual(r.json()["onchain_valid_until"], FUTURE)
        self.assertEqual(self.client.get("/api/v1/orderbook/101").json()["bids"], [])
        # hủy lần hai: dù đổi cancel_nonce, lệnh đã CANCELLED
        self.assertEqual(self.delete(20, self.cancel_body(KEY_ALICE, 20, 2)).status_code, 409)

    def test_cancel_by_other_wallet_rejected_and_order_stays(self):
        self.post(self.order_body(KEY_ALICE, self.alice, 21, 0, 10, 5))
        self.assertEqual(self.delete(21, self.cancel_body(KEY_BOB, 21, 1)).status_code, 401)
        self.assertEqual(self.client.get(f"/api/v1/orders/{oid(21)}").json()["status"], "NEW")

    def test_cancel_nonce_cannot_be_replayed_on_other_order(self):
        self.post(self.order_body(KEY_ALICE, self.alice, 22, 0, 10, 5))
        self.post(self.order_body(KEY_ALICE, self.alice, 23, 0, 11, 5))
        self.assertEqual(self.delete(22, self.cancel_body(KEY_ALICE, 22, 7)).status_code, 200)
        # cùng cancel_nonce của cùng trader: bị từ chối dù chữ ký (cho order 23) hợp lệ
        self.assertEqual(self.delete(23, self.cancel_body(KEY_ALICE, 23, 7)).status_code, 409)
        self.assertEqual(self.delete(99, self.cancel_body(KEY_ALICE, 99, 8)).status_code, 404)

    def test_expired_cancel_request_is_400(self):
        self.post(self.order_body(KEY_ALICE, self.alice, 24, 0, 10, 5))
        self.assertEqual(self.delete(24, self.cancel_body(KEY_ALICE, 24, 1, deadline=int(NOW) - 1)).status_code, 400)

    # ---- WebSocket
    def test_websocket_snapshot_update_and_match_events(self):
        with self.client.websocket_connect("/ws/orderbook/101") as ws:
            first = ws.receive_json()
            self.assertEqual(first["event"], "orderbook.snapshot")
            self.assertEqual(first["data"], {"bids": [], "asks": []})

            self.post(self.order_body(KEY_ALICE, self.alice, 30, 0, 12_000_000, 10))
            upd = ws.receive_json()
            self.assertEqual(upd["event"], "orderbook.update")
            self.assertEqual(upd["data"]["bids"], [{"price": 12_000_000, "amount": 10, "orders": 1}])

            self.post(self.order_body(KEY_BOB, self.bob, 31, 1, 10_000_000, 10))
            ws.receive_json()  # orderbook.update của lệnh bán
            self.client.post("/api/v1/sessions/run", json={"tokenId": 101})
            ev = ws.receive_json()
            self.assertEqual(ev["event"], "match.executed")
            self.assertEqual(ev["status"], "pending")
            self.assertEqual(ev["data"]["clearingPrice"], 11_000_000)


if __name__ == "__main__":
    unittest.main()
