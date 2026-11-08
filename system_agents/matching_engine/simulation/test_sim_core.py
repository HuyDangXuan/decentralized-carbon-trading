"""Unit tests kiểm tra toàn bộ 6 bất biến theo CONTRACT.md của bộ mô phỏng thực nghiệm."""

import os
import sys
import unittest

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)

from generator import generate_valued
from metrics import (
    buyer_surplus,
    efficient_volume,
    fill_rate,
    max_welfare,
    run_auction,
    seller_surplus,
    truthful,
    volume,
    welfare,
)
from model import OrderType, Valued, snap


class TestSimCoreInvariants(unittest.TestCase):
    """Bộ kiểm thử 6 bất biến của simulation core theo CONTRACT.md."""

    def test_invariant_1_generator_reproducibility_and_validation(self):
        """Bất biến 1: Cùng (n, seed) -> generate_valued giống hệt; seed khác -> khác.

        Kiểm tra thêm ràng buộc tham số (ValueError).
        """
        # Cùng (n, seed)
        orders_a1 = generate_valued(50, seed=42)
        orders_a2 = generate_valued(50, seed=42)
        self.assertEqual(orders_a1, orders_a2)

        # Seed khác -> khác
        orders_b = generate_valued(50, seed=43)
        self.assertNotEqual(orders_a1, orders_b)

        # Kiểm tra cấu trúc từng lệnh
        for i, o in enumerate(orders_a1):
            self.assertEqual(o.order_id, f"O{i}")
            self.assertEqual(o.arrival, i)
            self.assertIn(o.side, (OrderType.BID, OrderType.ASK))
            self.assertTrue(1 <= o.amount <= 50)
            self.assertTrue(5.0 <= o.valuation <= 15.0)
            self.assertEqual(o.valuation, snap(o.valuation))

        # Kiểm tra các ngoại lệ ValueError theo hợp đồng
        with self.assertRaises(ValueError):
            generate_valued(1, seed=42)  # n < 2
        with self.assertRaises(ValueError):
            generate_valued(10, seed=42, low=15.0, high=5.0)  # low >= high
        with self.assertRaises(ValueError):
            generate_valued(10, seed=42, low=10.0, high=10.0)  # low >= high
        with self.assertRaises(ValueError):
            generate_valued(10, seed=42, max_amount=0)  # max_amount < 1
        with self.assertRaises(ValueError):
            generate_valued(10, seed=42, p_buy=-0.01)  # p_buy ngoài [0, 1]
        with self.assertRaises(ValueError):
            generate_valued(10, seed=42, p_buy=1.01)  # p_buy ngoài [0, 1]

    def test_invariant_2_run_auction_purity_and_determinism(self):
        """Bất biến 2: run_auction không đổi valued; gọi hai lần cùng đầu vào -> cùng kết quả."""
        valued = generate_valued(60, seed=100)
        # Ghi lại trạng thái ban đầu của valued
        snapshot = [(v.order_id, v.side, v.amount, v.valuation, v.arrival) for v in valued]

        # Lần chạy 1
        matches_run1 = run_auction(valued, k=0.5)

        # Kiểm tra valued không hề bị thay đổi
        current_state = [(v.order_id, v.side, v.amount, v.valuation, v.arrival) for v in valued]
        self.assertEqual(snapshot, current_state)

        # Lần chạy 2
        matches_run2 = run_auction(valued, k=0.5)

        # Hai lần chạy cho kết quả giống hệt nhau
        self.assertEqual(len(matches_run1), len(matches_run2))
        for m1, m2 in zip(matches_run1, matches_run2):
            self.assertEqual(m1.bid_order_id, m2.bid_order_id)
            self.assertEqual(m1.ask_order_id, m2.ask_order_id)
            self.assertEqual(m1.token_id, m2.token_id)
            self.assertEqual(m1.amount, m2.amount)
            self.assertAlmostEqual(m1.clearing_price, m2.clearing_price, places=6)

    def test_invariant_3_truthful_welfare_across_k_and_max_welfare(self):
        """Bất biến 3: Bid trung thực: welfare bằng nhau với k in {0, 0.5, 1} và bằng max_welfare.

        Kiểm tra trên ít nhất 5 seed với n = 200 theo yêu cầu acceptance.
        """
        seeds = [101, 202, 303, 404, 505]
        for s in seeds:
            valued = generate_valued(n=200, seed=s)
            mw = max_welfare(valued)

            w_k0 = welfare(run_auction(valued, k=0.0), valued)
            w_k05 = welfare(run_auction(valued, k=0.5), valued)
            w_k1 = welfare(run_auction(valued, k=1.0), valued)

            # welfare bằng nhau với mọi k
            self.assertAlmostEqual(w_k0, w_k05, places=5, msg=f"Seed {s}: k=0 vs k=0.5")
            self.assertAlmostEqual(w_k05, w_k1, places=5, msg=f"Seed {s}: k=0.5 vs k=1.0")

            # welfare bằng max_welfare
            self.assertAlmostEqual(w_k05, mw, places=5, msg=f"Seed {s}: welfare vs max_welfare")

    def test_invariant_4_surplus_split_and_extremes(self):
        """Bất biến 4: buyer_surplus + seller_surplus == welfare (sai số 1e-6).

        k = 0 -> seller_surplus == 0; k = 1 -> buyer_surplus == 0.
        Kiểm tra trên ít nhất 5 seed với n = 200 theo yêu cầu acceptance.
        """
        seeds = [101, 202, 303, 404, 505]
        for s in seeds:
            valued = generate_valued(n=200, seed=s)

            for k_val in (0.0, 0.5, 1.0):
                matches = run_auction(valued, k=k_val)
                w = welfare(matches, valued)
                bs = buyer_surplus(matches, valued)
                ss = seller_surplus(matches, valued)

                # buyer_surplus + seller_surplus == welfare
                self.assertAlmostEqual(bs + ss, w, places=5, msg=f"Seed {s}, k={k_val}: tổng thặng dư")

                if k_val == 0.0:
                    self.assertAlmostEqual(ss, 0.0, places=5, msg=f"Seed {s}: k=0 seller_surplus")
                    self.assertAlmostEqual(bs, w, places=5, msg=f"Seed {s}: k=0 buyer_surplus == welfare")
                elif k_val == 1.0:
                    self.assertAlmostEqual(bs, 0.0, places=5, msg=f"Seed {s}: k=1 buyer_surplus")
                    self.assertAlmostEqual(ss, w, places=5, msg=f"Seed {s}: k=1 seller_surplus == welfare")

    def test_invariant_5_clearing_price_and_amount_bounds(self):
        """Bất biến 5: Mọi match có ask <= clearing_price <= bid theo giá khai.

        Không order_id nào khớp vượt amount ban đầu.
        Kiểm tra trên ít nhất 5 seed với n = 200 theo yêu cầu acceptance.
        """
        seeds = [101, 202, 303, 404, 505]
        for s in seeds:
            valued = generate_valued(n=200, seed=s)
            val_map = {v.order_id: v.valuation for v in valued}
            amt_map = {v.order_id: v.amount for v in valued}

            for k_val in (0.0, 0.5, 1.0):
                matches = run_auction(valued, k=k_val)
                matched_amounts: dict[str, int] = {}

                for m in matches:
                    ask_price = val_map[m.ask_order_id]
                    bid_price = val_map[m.bid_order_id]

                    # ask <= clearing_price <= bid (dung sai số thực 1e-6)
                    self.assertGreaterEqual(
                        m.clearing_price,
                        ask_price - 1e-6,
                        msg=f"Seed {s}, k={k_val}: clearing_price >= ask",
                    )
                    self.assertLessEqual(
                        m.clearing_price,
                        bid_price + 1e-6,
                        msg=f"Seed {s}, k={k_val}: clearing_price <= bid",
                    )

                    matched_amounts[m.bid_order_id] = matched_amounts.get(m.bid_order_id, 0) + m.amount
                    matched_amounts[m.ask_order_id] = matched_amounts.get(m.ask_order_id, 0) + m.amount

                # Không order_id nào khớp vượt amount ban đầu
                for order_id, matched_amt in matched_amounts.items():
                    self.assertLessEqual(
                        matched_amt,
                        amt_map[order_id],
                        msg=f"Seed {s}, k={k_val}: {order_id} khớp vượt amount ban đầu",
                    )

    def test_invariant_6_contract_manual_example(self):
        """Bất biến 6: Ví dụ tay số 6 của hợp đồng:

        BID(val 12, amount 10), BID(val 8, amount 5),
        ASK(val 6, amount 7), ASK(val 9, amount 20)
        với k = 0.5, bid trung thực:
        -> khớp 7 đơn vị ở giá 9.0 giữa BID-12 và ASK-6
        -> rồi 3 đơn vị giữa BID-12 và ASK-9 ở giá 10.5
        welfare = 7*6 + 3*3 = 51.0
        max_welfare = 51.0
        """
        # Định nghĩa 4 lệnh theo đúng mô tả ví dụ tay
        bid12 = Valued(order_id="BID_12", side=OrderType.BID, amount=10, valuation=12.0, arrival=0)
        bid8 = Valued(order_id="BID_8", side=OrderType.BID, amount=5, valuation=8.0, arrival=1)
        ask6 = Valued(order_id="ASK_6", side=OrderType.ASK, amount=7, valuation=6.0, arrival=2)
        ask9 = Valued(order_id="ASK_9", side=OrderType.ASK, amount=20, valuation=9.0, arrival=3)

        valued = [bid12, bid8, ask6, ask9]

        matches = run_auction(valued, k=0.5, price_fn=truthful)

        # Phải khớp đúng 2 lần
        self.assertEqual(len(matches), 2)

        # Match 1: 7 đơn vị ở giá 9.0 giữa BID-12 và ASK-6
        m1 = matches[0]
        self.assertEqual(m1.bid_order_id, "BID_12")
        self.assertEqual(m1.ask_order_id, "ASK_6")
        self.assertEqual(m1.amount, 7)
        self.assertAlmostEqual(m1.clearing_price, 9.0, places=6)

        # Match 2: 3 đơn vị ở giá 10.5 giữa BID-12 và ASK-9
        m2 = matches[1]
        self.assertEqual(m2.bid_order_id, "BID_12")
        self.assertEqual(m2.ask_order_id, "ASK_9")
        self.assertEqual(m2.amount, 3)
        self.assertAlmostEqual(m2.clearing_price, 10.5, places=6)

        # Welfare = 7*6 + 3*3 = 51.0
        w = welfare(matches, valued)
        self.assertEqual(w, 51.0)

        # Max welfare = 51.0
        mw = max_welfare(valued)
        self.assertEqual(mw, 51.0)

        # Volume = 10, Efficient Volume = 10, Fill rate = 1.0
        self.assertEqual(volume(matches), 10)
        self.assertEqual(efficient_volume(valued), 10)
        self.assertEqual(fill_rate(matches, valued), 1.0)

        # Surplus chia đều:
        # buyer_surplus = (12 - 9)*7 + (12 - 10.5)*3 = 21 + 4.5 = 25.5
        # seller_surplus = (9 - 6)*7 + (10.5 - 9)*3 = 21 + 4.5 = 25.5
        bs = buyer_surplus(matches, valued)
        ss = seller_surplus(matches, valued)
        self.assertEqual(bs, 25.5)
        self.assertEqual(ss, 25.5)
        self.assertEqual(bs + ss, 51.0)

    def test_edge_cases_and_fill_rate(self):
        """Kiểm tra các trường hợp biên: không khớp, danh sách rỗng, đơn biên."""
        # Thị trường chỉ có người mua
        only_bids = [
            Valued(order_id="B1", side=OrderType.BID, amount=10, valuation=10.0, arrival=0)
        ]
        matches = run_auction(only_bids, k=0.5)
        self.assertEqual(len(matches), 0)
        self.assertEqual(welfare(matches, only_bids), 0.0)
        self.assertEqual(max_welfare(only_bids), 0.0)
        self.assertEqual(volume(matches), 0)
        self.assertEqual(efficient_volume(only_bids), 0)
        self.assertEqual(fill_rate(matches, only_bids), 1.0)  # efficient_volume == 0 -> 1.0

    def test_fill_rate_is_one_when_truthful_even_with_ties(self):
        """Hồi quy: bid == ask trung thực vẫn khớp, fill_rate không được vượt 1."""
        tied = [
            Valued(order_id="B1", side=OrderType.BID, amount=5, valuation=10.0, arrival=0),
            Valued(order_id="S1", side=OrderType.ASK, amount=5, valuation=10.0, arrival=1),
        ]
        matches = run_auction(tied, k=0.5)
        self.assertEqual(volume(matches), 5)
        self.assertEqual(efficient_volume(tied), 5)
        self.assertEqual(fill_rate(matches, tied), 1.0)
        for seed in range(10):
            d = generate_valued(500, seed)
            for k in (0, 0.5, 1):
                self.assertLessEqual(fill_rate(run_auction(d, k), d), 1.0 + 1e-9)


if __name__ == "__main__":
    unittest.main()
