"""Kiểm thử `DoubleAuctionAgent` mới theo ADR-001 / SRS FR-06..FR-09."""

import os
import random
import sys
import unittest

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from auction_agent import DoubleAuctionAgent, MAX_ROLLOVER_SESSIONS, OrderStatus
from order_book import Order, OrderType

TOKEN = 101


def bid(oid, price, amount, trader=None, **kw):
    return Order(oid, trader or f"T_{oid}", OrderType.BID, TOKEN, amount, price, **kw)


def ask(oid, price, amount, trader=None, **kw):
    return Order(oid, trader or f"T_{oid}", OrderType.ASK, TOKEN, amount, price, **kw)


class TestAdrParameters(unittest.TestCase):
    def test_clearing_price_is_floor_of_midpoint_of_marginal_orders(self):
        """Quyết định 3: P* = floor((b_M + s_M) / 2), mọi khớp cùng một giá."""
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B1", 12_000_000, 100))
        agent.submit_order(bid("B2", 10_500_001, 100))
        agent.submit_order(ask("A1", 10_000_000, 100))
        agent.submit_order(ask("A2", 10_000_002, 100))
        matches = agent.run_periodic_double_auction(TOKEN)
        # M = 2: b_M = 10_500_001, s_M = 10_000_002 -> floor(20_500_003 / 2) = 10_250_001
        self.assertEqual({m.clearing_price for m in matches}, {10_250_001})
        self.assertEqual(sum(m.amount for m in matches), 200)

    def test_price_ignores_next_unmatched_orders_per_adr_formula(self):
        """Công thức ADR chỉ dùng lệnh biên đã khớp (b_M, s_M); không dùng lệnh kế tiếp chưa khớp.

        BID 10, ASK 1, ASK 2 (mỗi lệnh 1 đơn vị): chỉ khớp BID với ASK 1, P* = floor((10 + 1) / 2).
        Quy tắc "kda" của engine (dùng thêm ASK 2 chưa khớp) cho giá khác, nên test này chặn việc
        đổi nhầm PRICING_RULE mà không báo.
        """
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B", 10_000_000, 1))
        agent.submit_order(ask("A1", 1_000_000, 1))
        agent.submit_order(ask("A2", 2_000_000, 1))
        (m,) = agent.run_periodic_double_auction(TOKEN)
        self.assertEqual((m.ask_order_id, m.clearing_price), ("A1", 5_500_000))
        self.assertEqual(agent.get_order("A2").status, OrderStatus.ROLLED_OVER)

    def test_price_is_integer_and_inside_ask_bid_range(self):
        """Không còn lỗi round(...,2) đẩy giá ra ngoài [ask, bid] (Đ4)."""
        agent = DoubleAuctionAgent()
        agent.submit_order(ask("A", 10_001, 5))
        agent.submit_order(bid("B", 10_004, 5))
        (m,) = agent.run_periodic_double_auction(TOKEN)
        self.assertIsInstance(m.clearing_price, int)
        self.assertTrue(10_001 <= m.clearing_price <= 10_004)

    def test_gtc_lives_at_most_three_sessions(self):
        """Quyết định 4: rollover_count >= 3 thì EXPIRED, tức tối đa 3 phiên."""
        self.assertEqual(MAX_ROLLOVER_SESSIONS, 3)
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("X", 5, 10))  # không có bên bán
        statuses = []
        for _ in range(4):
            agent.run_periodic_double_auction(TOKEN)
            statuses.append(agent.get_order("X").status)
        self.assertEqual(
            statuses,
            [OrderStatus.ROLLED_OVER, OrderStatus.ROLLED_OVER, OrderStatus.EXPIRED, OrderStatus.EXPIRED],
        )
        self.assertEqual(agent.get_order("X").rollover_count, 2)  # hết hạn ở lần tăng thứ 3, không lưu lại

    def test_ioc_unfilled_is_cancelled_without_rollover(self):
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("I", 10, 10, time_in_force="IOC"))
        agent.submit_order(ask("S", 9, 4))
        (m,) = agent.run_periodic_double_auction(TOKEN)
        self.assertEqual(m.amount, 4)
        self.assertEqual(agent.get_order("I").status, OrderStatus.CANCELLED)
        self.assertEqual(agent.get_order("I").filled_amount, 4)
        self.assertEqual(agent.get_order("S").status, OrderStatus.FILLED)

    def test_older_order_gets_priority_via_age(self):
        """Lệnh đã rollover (tuổi cao hơn) được ưu tiên hơn lệnh mới cùng giá."""
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("OLD", 10, 5))
        agent.run_periodic_double_auction(TOKEN)  # không khớp, OLD rollover
        agent.submit_order(bid("NEW", 10, 5))
        agent.submit_order(ask("S", 8, 5))
        matches = agent.run_periodic_double_auction(TOKEN)
        self.assertEqual([(m.bid_order_id, m.amount) for m in matches], [("OLD", 5)])

    def test_hamilton_conserves_total_and_ties_go_to_earliest(self):
        """Phần dư bằng nhau: FIFO (đến sớm hơn nhận đơn vị dư)."""
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B_FIRST", 10, 3))   # seq nhỏ hơn
        agent.submit_order(bid("A_SECOND", 10, 3))  # order_id nhỏ hơn nhưng đến sau
        agent.submit_order(ask("S", 5, 3))
        matches = agent.run_periodic_double_auction(TOKEN)
        got = {m.bid_order_id: m.amount for m in matches}
        self.assertEqual(sum(got.values()), 3)
        self.assertEqual(got, {"B_FIRST": 2, "A_SECOND": 1})


class TestAgentBehaviour(unittest.TestCase):
    def test_input_orders_are_not_mutated(self):
        """Khác baseline cũ: không trừ trực tiếp vào Order.amount."""
        agent = DoubleAuctionAgent()
        b, a = bid("B", 10, 8), ask("A", 5, 3)
        agent.submit_order(b)
        agent.submit_order(a)
        agent.run_periodic_double_auction(TOKEN)
        self.assertEqual((b.amount, a.amount), (8, 3))
        self.assertEqual(agent.get_order("B").remaining_amount, 5)
        self.assertEqual(agent.get_order("B").status, OrderStatus.ROLLED_OVER)

    def test_float_price_or_amount_rejected(self):
        agent = DoubleAuctionAgent()
        with self.assertRaises(ValueError):
            agent.submit_order(bid("F", 10.5, 5))
        with self.assertRaises(ValueError):
            agent.submit_order(bid("G", 10, 5.0))
        with self.assertRaises(ValueError):
            agent.submit_order(bid("H", 10, 0))

    def test_duplicate_order_id_and_bad_tif_rejected(self):
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("D", 10, 5))
        with self.assertRaises(ValueError):
            agent.submit_order(bid("D", 11, 5))
        with self.assertRaises(ValueError):
            agent.submit_order(bid("E", 10, 5, time_in_force="FOK"))

    def test_self_trade_is_dropped(self):
        """Hợp đồng revert SelfTradingNotAllowed; engine không được phát ra khớp đó."""
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B", 10, 5, trader="same"))
        agent.submit_order(ask("A", 5, 5, trader="same"))
        self.assertEqual(agent.run_periodic_double_auction(TOKEN), [])
        self.assertEqual(agent.get_order("B").filled_amount, 0)
        self.assertEqual(agent.get_order("B").status, OrderStatus.ROLLED_OVER)

    def test_cancel_removes_order_and_rejects_repeat(self):
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B", 10, 5))
        agent.submit_order(ask("A", 5, 5))
        agent.cancel_order("B")
        self.assertEqual(agent.run_periodic_double_auction(TOKEN), [])
        with self.assertRaises(ValueError):
            agent.cancel_order("B")
        with self.assertRaises(KeyError):
            agent.cancel_order("missing")

    def test_deadline_expired_orders_leave_the_book(self):
        clock = [1000.0]
        agent = DoubleAuctionAgent(now_fn=lambda: clock[0])
        agent.submit_order(bid("B", 10, 5, deadline=1500))
        agent.submit_order(ask("A", 5, 5))
        clock[0] = 2000.0
        self.assertEqual(agent.run_periodic_double_auction(TOKEN), [])
        self.assertEqual(agent.get_order("B").status, OrderStatus.EXPIRED)
        with self.assertRaises(ValueError):
            agent.submit_order(bid("LATE", 10, 5, deadline=1999))

    def test_snapshot_aggregates_depth(self):
        agent = DoubleAuctionAgent()
        agent.submit_order(bid("B1", 10, 5))
        agent.submit_order(bid("B2", 10, 3))
        agent.submit_order(bid("B3", 9, 2))
        agent.submit_order(ask("A1", 12, 7))
        snap = agent.snapshot(TOKEN)
        self.assertEqual(snap["bids"], [{"price": 10, "amount": 8, "orders": 2}, {"price": 9, "amount": 2, "orders": 1}])
        self.assertEqual(snap["asks"], [{"price": 12, "amount": 7, "orders": 1}])

    def test_random_sessions_conserve_volume_and_respect_limits(self):
        """Bất biến trên sổ ngẫu nhiên nhiều phiên: khớp bảo toàn, trong dải giá, không vượt amount."""
        rng = random.Random(7)
        for _ in range(60):
            agent = DoubleAuctionAgent()
            n = 0
            for session in range(5):
                for _ in range(rng.randint(2, 8)):
                    n += 1
                    side = bid if rng.random() < 0.5 else ask
                    agent.submit_order(side(f"O{n}", rng.randint(1, 20), rng.randint(1, 9), trader=f"T{rng.randint(1, 6)}"))
                matches = agent.run_periodic_double_auction(TOKEN)
                for m in matches:
                    b = agent.get_order(m.bid_order_id).order
                    a = agent.get_order(m.ask_order_id).order
                    self.assertTrue(a.price <= m.clearing_price <= b.price)
                    self.assertNotEqual(b.trader_id, a.trader_id)
            # Bảo toàn khối lượng theo từng lệnh: đã khớp + còn lại = khối lượng ban đầu, không âm
            for r in agent._records.values():
                self.assertEqual(r.filled_amount + r.remaining_amount, r.order.amount)
                self.assertGreaterEqual(r.remaining_amount, 0)
            # Tổng khối lượng mua khớp = tổng khối lượng bán khớp
            filled_bids = sum(r.filled_amount for r in agent._records.values() if r.order.order_type == OrderType.BID)
            filled_asks = sum(r.filled_amount for r in agent._records.values() if r.order.order_type == OrderType.ASK)
            self.assertEqual(filled_bids, filled_asks)


if __name__ == "__main__":
    unittest.main()
