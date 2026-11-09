"""Bộ kiểm thử đơn vị cho session_engine.py (J1).

Kiểm tra toàn bộ bất biến và kịch bản bắt buộc từ (a) đến (i) theo CONTRACT C.
"""

import os
import random
import sys
import unittest

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(_SIM_DIR)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from session_engine import BookOrder, Fill, match_session
from order_book import Order, OrderType
from auction_agent import DoubleAuctionAgent


class TestSessionEngine(unittest.TestCase):
    """Kiểm thử toàn diện engine khớp lệnh định kỳ."""

    def test_a_conservation_and_remaining(self):
        """(a) Σ bid khớp = Σ ask khớp, không lệnh nào khớp vượt remaining."""
        orders = [
            BookOrder(order_id="B1", side="BID", price_ticks=100, remaining=15, sessions_alive=1),
            BookOrder(order_id="B2", side="BID", price_ticks=90, remaining=20, sessions_alive=0),
            BookOrder(order_id="B3", side="BID", price_ticks=85, remaining=10, sessions_alive=2),
            BookOrder(order_id="A1", side="ASK", price_ticks=80, remaining=12, sessions_alive=0),
            BookOrder(order_id="A2", side="ASK", price_ticks=85, remaining=18, sessions_alive=3),
            BookOrder(order_id="A3", side="ASK", price_ticks=95, remaining=25, sessions_alive=1),
        ]
        order_map = {o.order_id: o for o in orders}

        for tb in ("age_prorata", "fifo"):
            for pr in ("pair", "marginal", "kda"):
                fills = match_session(orders, tie_break=tb, pricing=pr)
                self.assertGreater(len(fills), 0)

                bid_fills = {}
                ask_fills = {}
                for f in fills:
                    self.assertGreater(f.amount, 0)
                    bid_fills[f.bid_id] = bid_fills.get(f.bid_id, 0) + f.amount
                    ask_fills[f.ask_id] = ask_fills.get(f.ask_id, 0) + f.amount

                # Bảo toàn khối lượng hai phía
                self.assertEqual(sum(bid_fills.values()), sum(ask_fills.values()))

                # Không vượt remaining
                for bid_id, amt in bid_fills.items():
                    self.assertLessEqual(amt, order_map[bid_id].remaining)
                for ask_id, amt in ask_fills.items():
                    self.assertLessEqual(amt, order_map[ask_id].remaining)

    def test_b_price_bounds_and_matrix(self):
        """(b) ask ≤ price ≤ bid cho mọi fill trên ma trận 3 pricing × 4 rounding × 3 k_num × 3 k_den."""
        orders = [
            BookOrder(order_id="B1", side="BID", price_ticks=150, remaining=10),
            BookOrder(order_id="B2", side="BID", price_ticks=120, remaining=15),
            BookOrder(order_id="A1", side="ASK", price_ticks=80, remaining=12),
            BookOrder(order_id="A2", side="ASK", price_ticks=110, remaining=20),
        ]
        order_map = {o.order_id: o for o in orders}

        pricings = ("pair", "marginal", "kda")
        roundings = ("floor", "ceil", "half_up", "half_even")
        k_dens = (2, 3, 7)

        count = 0
        for pr in pricings:
            for rd in roundings:
                for k_den in k_dens:
                    for k_num in (0, 1, k_den):
                        count += 1
                        fills = match_session(
                            orders,
                            k_num=k_num,
                            k_den=k_den,
                            pricing=pr,
                            rounding=rd,
                        )
                        self.assertGreater(len(fills), 0)
                        for f in fills:
                            bid_p = order_map[f.bid_id].price_ticks
                            ask_p = order_map[f.ask_id].price_ticks
                            self.assertGreaterEqual(f.price_ticks, ask_p)
                            self.assertLessEqual(f.price_ticks, bid_p)

        self.assertEqual(count, 3 * 4 * 3 * 3)

    def test_c_determinism_and_permutation_invariance(self):
        """(c) Tất định và bất biến hoán vị thứ tự đầu vào."""
        base_orders = [
            BookOrder(order_id="B1", side="BID", price_ticks=120, remaining=10, sessions_alive=1, seq=3),
            BookOrder(order_id="B2", side="BID", price_ticks=120, remaining=15, sessions_alive=2, seq=1),
            BookOrder(order_id="B3", side="BID", price_ticks=110, remaining=8, sessions_alive=0, seq=4),
            BookOrder(order_id="A1", side="ASK", price_ticks=90, remaining=12, sessions_alive=2, seq=2),
            BookOrder(order_id="A2", side="ASK", price_ticks=100, remaining=20, sessions_alive=1, seq=5),
            BookOrder(order_id="A3", side="ASK", price_ticks=120, remaining=5, sessions_alive=0, seq=6),
        ]

        for tb in ("age_prorata", "fifo"):
            expected_fills = match_session(base_orders, tie_break=tb)

            # Thử 20 hoán vị ngẫu nhiên khác nhau của cùng danh sách lệnh
            rng = random.Random(12345)
            for _ in range(20):
                shuffled = list(base_orders)
                rng.shuffle(shuffled)
                fills = match_session(shuffled, tie_break=tb)
                self.assertEqual(fills, expected_fills)

    def test_d_baseline_comparison_300_books(self):
        """(d) Đối chứng baseline trên 300 sổ ngẫu nhiên cho cả hai tie_break."""
        rng = random.Random(42)

        for i in range(300):
            n_orders = rng.randint(2, 40)
            orders: list[BookOrder] = []

            # Đảm bảo ít nhất 1 BID và 1 ASK để có thể khớp
            has_bid = False
            has_ask = False
            for idx in range(n_orders):
                side = "BID" if (idx == 0 or (idx > 1 and rng.random() < 0.5)) else "ASK"
                if side == "BID":
                    has_bid = True
                else:
                    has_ask = True
                price = rng.randint(1, 30)
                rem = rng.randint(1, 20)
                alive = rng.randint(0, 5)
                seq = rng.randint(0, 100)
                orders.append(
                    BookOrder(
                        order_id=f"O_{i}_{idx}",
                        side=side,
                        price_ticks=price,
                        remaining=rem,
                        sessions_alive=alive,
                        seq=seq,
                    )
                )

            order_map = {o.order_id: o for o in orders}

            # 1. Chạy baseline DoubleAuctionAgent
            agent = DoubleAuctionAgent(k_parameter=0.5)
            for o in orders:
                agent.submit_order(
                    Order(
                        order_id=o.order_id,
                        trader_id=o.order_id,
                        order_type=OrderType.BID if o.side == "BID" else OrderType.ASK,
                        token_id=101,
                        amount=o.remaining,
                        price=float(o.price_ticks),
                        timestamp=float(o.seq),
                    )
                )
            base_matches = agent.run_periodic_double_auction(101)
            base_vol = sum(m.amount for m in base_matches)
            base_welfare = sum(
                m.amount * (order_map[m.bid_order_id].price_ticks - order_map[m.ask_order_id].price_ticks)
                for m in base_matches
            )

            # 2. Đối chứng với tie_break = age_prorata
            sim_fills_age = match_session(orders, tie_break="age_prorata")
            sim_vol_age = sum(f.amount for f in sim_fills_age)
            sim_welfare_age = sum(
                f.amount * (order_map[f.bid_id].price_ticks - order_map[f.ask_id].price_ticks)
                for f in sim_fills_age
            )
            self.assertEqual(sim_vol_age, base_vol)
            self.assertEqual(sim_welfare_age, base_welfare)

            # 3. Đối chứng với tie_break = fifo
            sim_fills_fifo = match_session(orders, tie_break="fifo")
            sim_vol_fifo = sum(f.amount for f in sim_fills_fifo)
            sim_welfare_fifo = sum(
                f.amount * (order_map[f.bid_id].price_ticks - order_map[f.ask_id].price_ticks)
                for f in sim_fills_fifo
            )
            self.assertEqual(sim_vol_fifo, base_vol)
            self.assertEqual(sim_welfare_fifo, base_welfare)

    def test_e_prorata_hamilton_hand_example(self):
        """(e) Pro-rata: tổng phân bổ = khả dụng, không vượt remaining, Hamilton ví dụ tay."""
        # Ví dụ tay từ hợp đồng: avail=10, r=(7, 5, 3) -> (5, 3, 2)
        # S = 7 + 5 + 3 = 15
        # 10 * 7 / 15 = 4 + 10/15 -> q=4, rem=10
        # 10 * 5 / 15 = 3 + 5/15  -> q=3, rem=5
        # 10 * 3 / 15 = 2 + 0/15  -> q=2, rem=0
        # R = 10 - 9 = 1 đơn vị dư cấp cho lệnh có rem lớn nhất (10/15) -> 4+1=5, 3, 2
        orders = [
            BookOrder(order_id="B1", side="BID", price_ticks=100, remaining=7, sessions_alive=0),
            BookOrder(order_id="B2", side="BID", price_ticks=100, remaining=5, sessions_alive=0),
            BookOrder(order_id="B3", side="BID", price_ticks=100, remaining=3, sessions_alive=0),
            BookOrder(order_id="A1", side="ASK", price_ticks=100, remaining=10, sessions_alive=0),
        ]
        fills = match_session(orders, tie_break="age_prorata")
        allocs = {f.bid_id: 0 for f in fills}
        for f in fills:
            allocs[f.bid_id] += f.amount

        self.assertEqual(allocs.get("B1", 0), 5)
        self.assertEqual(allocs.get("B2", 0), 3)
        self.assertEqual(allocs.get("B3", 0), 2)
        self.assertEqual(sum(allocs.values()), 10)

        # Kiểm tra phá hòa phần dư: ưu tiên remaining lớn hơn khi rem bằng nhau
        # r = (6, 3, 1), avail = 5, S = 10
        # B1: 5 * 6 / 10 = 3 (rem 0)
        # B2: 5 * 3 / 10 = 1 (rem 5)
        # B3: 5 * 1 / 10 = 0 (rem 5)
        # Base sum = 4, R = 1. Cả B2 và B3 đều có rem = 5.
        # Phá hòa: remaining B2 (3) > B3 (1) -> B2 nhận phần dư -> phân bổ: (3, 2, 0)
        orders_tie = [
            BookOrder(order_id="T1", side="BID", price_ticks=100, remaining=6, sessions_alive=0),
            BookOrder(order_id="T2", side="BID", price_ticks=100, remaining=3, sessions_alive=0),
            BookOrder(order_id="T3", side="BID", price_ticks=100, remaining=1, sessions_alive=0),
            BookOrder(order_id="AT", side="ASK", price_ticks=100, remaining=5, sessions_alive=0),
        ]
        fills_tie = match_session(orders_tie, tie_break="age_prorata")
        allocs_tie = {f.bid_id: 0 for f in fills_tie}
        for f in fills_tie:
            allocs_tie[f.bid_id] += f.amount
        self.assertEqual(allocs_tie.get("T1", 0), 3)
        self.assertEqual(allocs_tie.get("T2", 0), 2)
        self.assertEqual(allocs_tie.get("T3", 0), 0)

    def test_f_age_vs_fifo_scenarios(self):
        """(f) Kịch bản tuổi: lệnh già (alive=2, seq=9) và lệnh trẻ (alive=0, seq=1)."""
        orders = [
            BookOrder(order_id="OLD", side="BID", price_ticks=100, remaining=10, sessions_alive=2, seq=9),
            BookOrder(order_id="YOUNG", side="BID", price_ticks=100, remaining=10, sessions_alive=0, seq=1),
            BookOrder(order_id="ASK", side="ASK", price_ticks=100, remaining=10, sessions_alive=0, seq=0),
        ]

        # age_prorata ưu tiên lệnh già
        fills_age = match_session(orders, tie_break="age_prorata")
        self.assertEqual(len(fills_age), 1)
        self.assertEqual(fills_age[0].bid_id, "OLD")
        self.assertEqual(fills_age[0].amount, 10)

        # fifo ưu tiên lệnh trẻ vì seq nhỏ hơn
        fills_fifo = match_session(orders, tie_break="fifo")
        self.assertEqual(len(fills_fifo), 1)
        self.assertEqual(fills_fifo[0].bid_id, "YOUNG")
        self.assertEqual(fills_fifo[0].amount, 10)

    def test_g_spec_section_10_edge_cases(self):
        """(g) Kịch bản spec §10: sổ trống, một phía, bid < ask, bid = ask, partial fill, trùng id, lỗi đầu vào."""
        # 1. Sổ trống
        self.assertEqual(match_session([]), [])

        # 2. Một phía trống
        self.assertEqual(match_session([BookOrder("B1", "BID", 100, 10)]), [])
        self.assertEqual(match_session([BookOrder("A1", "ASK", 100, 10)]), [])

        # 3. bid < ask toàn bộ
        no_match = [
            BookOrder("B1", "BID", 90, 10),
            BookOrder("A1", "ASK", 100, 10),
        ]
        self.assertEqual(match_session(no_match), [])

        # 4. bid = ask khớp đúng
        eq_match = [
            BookOrder("B1", "BID", 100, 5),
            BookOrder("A1", "ASK", 100, 5),
        ]
        fills_eq = match_session(eq_match)
        self.assertEqual(len(fills_eq), 1)
        self.assertEqual(fills_eq[0].amount, 5)
        self.assertEqual(fills_eq[0].price_ticks, 100)

        # 5. Partial fill và phân bổ 0 bị bỏ
        partial = [
            BookOrder("B1", "BID", 120, 10),
            BookOrder("B2", "BID", 80, 10),  # Không khớp (alloc 0)
            BookOrder("A1", "ASK", 100, 4),
        ]
        fills_part = match_session(partial)
        self.assertEqual(len(fills_part), 1)
        self.assertEqual(fills_part[0].bid_id, "B1")
        self.assertEqual(fills_part[0].ask_id, "A1")
        self.assertEqual(fills_part[0].amount, 4)
        # B2 không xuất hiện trong fills
        self.assertNotIn("B2", [f.bid_id for f in fills_part])

        # 6. Trùng order_id -> ValueError
        dup = [
            BookOrder("D1", "BID", 100, 5),
            BookOrder("D1", "ASK", 100, 5),
        ]
        with self.assertRaises(ValueError):
            match_session(dup)

        # 7. Các tham số không hợp lệ
        valid = [BookOrder("B", "BID", 10, 1), BookOrder("A", "ASK", 10, 1)]
        with self.assertRaises(ValueError):
            match_session(valid, k_den=0)
        with self.assertRaises(ValueError):
            match_session(valid, k_den=-1)
        with self.assertRaises(ValueError):
            match_session(valid, k_num=-1, k_den=2)
        with self.assertRaises(ValueError):
            match_session(valid, k_num=3, k_den=2)
        with self.assertRaises(ValueError):
            match_session(valid, tie_break="unknown")
        with self.assertRaises(ValueError):
            match_session(valid, pricing="unknown")
        with self.assertRaises(ValueError):
            match_session(valid, rounding="unknown")
        with self.assertRaises(ValueError):
            match_session([BookOrder("B", "BID", 0, 1), BookOrder("A", "ASK", 10, 1)])
        with self.assertRaises(ValueError):
            match_session([BookOrder("B", "BID", 10, 0), BookOrder("A", "ASK", 10, 1)])
        with self.assertRaises(ValueError):
            match_session([BookOrder("B", "OTHER", 10, 1), BookOrder("A", "ASK", 10, 1)])

    def test_h_hand_example(self):
        """(h) Ví dụ tay: BID(12×10), BID(8×5), ASK(6×7), ASK(9×20), tick = giá×100, k=1/2, age_prorata."""
        orders = [
            BookOrder(order_id="BID12", side="BID", price_ticks=1200, remaining=10),
            BookOrder(order_id="BID8", side="BID", price_ticks=800, remaining=5),
            BookOrder(order_id="ASK6", side="ASK", price_ticks=600, remaining=7),
            BookOrder(order_id="ASK9", side="ASK", price_ticks=900, remaining=20),
        ]

        # 1. pair: (BID12, ASK6) 7 đơn vị giá 900; (BID12, ASK9) 3 đơn vị giá 1050
        fills_pair = match_session(orders, k_num=1, k_den=2, tie_break="age_prorata", pricing="pair")
        self.assertEqual(len(fills_pair), 2)
        self.assertEqual(fills_pair[0], Fill(bid_id="BID12", ask_id="ASK6", amount=7, price_ticks=900))
        self.assertEqual(fills_pair[1], Fill(bid_id="BID12", ask_id="ASK9", amount=3, price_ticks=1050))

        # 2. marginal: b_m=1200, a_m=900 -> cả hai giá 1050
        fills_marg = match_session(orders, k_num=1, k_den=2, tie_break="age_prorata", pricing="marginal")
        self.assertEqual(len(fills_marg), 2)
        self.assertEqual(fills_marg[0], Fill(bid_id="BID12", ask_id="ASK6", amount=7, price_ticks=1050))
        self.assertEqual(fills_marg[1], Fill(bid_id="BID12", ask_id="ASK9", amount=3, price_ticks=1050))

        # 3. kda: b_next=800, a_next=900 (còn 17 đơn vị ASK9) -> hi=min(1200, 900)=900, lo=max(900, 800)=900 -> cả hai giá 900
        fills_kda = match_session(orders, k_num=1, k_den=2, tie_break="age_prorata", pricing="kda")
        self.assertEqual(len(fills_kda), 2)
        self.assertEqual(fills_kda[0], Fill(bid_id="BID12", ask_id="ASK6", amount=7, price_ticks=900))
        self.assertEqual(fills_kda[1], Fill(bid_id="BID12", ask_id="ASK9", amount=3, price_ticks=900))

    def test_i_marginal_counterexample(self):
        """(i) Phản ví dụ của marginal: BID 10×1, ASK 1×1, ASK 2×1, k=1/2 (tick×100)."""
        orders = [
            BookOrder(order_id="BID10", side="BID", price_ticks=1000, remaining=1),
            BookOrder(order_id="ASK1", side="ASK", price_ticks=100, remaining=1),
            BookOrder(order_id="ASK2", side="ASK", price_ticks=200, remaining=1),
        ]

        # marginal: b_m=1000, a_m=100 -> p=550 (ASK2 không khớp dù sẵn lòng bán ở 550)
        fills_marg = match_session(orders, k_num=1, k_den=2, pricing="marginal")
        self.assertEqual(len(fills_marg), 1)
        self.assertEqual(fills_marg[0], Fill(bid_id="BID10", ask_id="ASK1", amount=1, price_ticks=550))

        # kda: a_next=200, không có b_next -> hi=min(1000, 200)=200, lo=100 -> p=150
        fills_kda = match_session(orders, k_num=1, k_den=2, pricing="kda")
        self.assertEqual(len(fills_kda), 1)
        self.assertEqual(fills_kda[0], Fill(bid_id="BID10", ask_id="ASK1", amount=1, price_ticks=150))

    def test_half_even_hand_examples(self):
        """Ví dụ tay kiểm tra rounding='half_even' với k=1/2, bid+ask lẻ cho cả q chẵn và q lẻ."""
        # Trường hợp 1: bid=3, ask=2 -> n = 3 + 2 = 5, k_den = 2.
        # q = 5 // 2 = 2 (chẵn), r = 1.
        # 2*r == k_den (2 == 2). Vì q chẵn nên half_even giữ nguyên q = 2.
        orders_q_even = [
            BookOrder("B", "BID", price_ticks=3, remaining=1),
            BookOrder("A", "ASK", price_ticks=2, remaining=1),
        ]
        fills_he_even = match_session(orders_q_even, k_num=1, k_den=2, pricing="pair", rounding="half_even")
        self.assertEqual(fills_he_even[0].price_ticks, 2)

        # So sánh cùng n=5 với các phép làm tròn khác:
        fills_fl = match_session(orders_q_even, k_num=1, k_den=2, pricing="pair", rounding="floor")
        self.assertEqual(fills_fl[0].price_ticks, 2)
        fills_ce = match_session(orders_q_even, k_num=1, k_den=2, pricing="pair", rounding="ceil")
        self.assertEqual(fills_ce[0].price_ticks, 3)
        fills_hu = match_session(orders_q_even, k_num=1, k_den=2, pricing="pair", rounding="half_up")
        self.assertEqual(fills_hu[0].price_ticks, 3)

        # Trường hợp 2: bid=4, ask=3 -> n = 4 + 3 = 7, k_den = 2.
        # q = 7 // 2 = 3 (lẻ), r = 1.
        # 2*r == k_den (2 == 2). Vì q lẻ nên half_even làm tròn lên số chẵn gần nhất: q + 1 = 4.
        orders_q_odd = [
            BookOrder("B", "BID", price_ticks=4, remaining=1),
            BookOrder("A", "ASK", price_ticks=3, remaining=1),
        ]
        fills_he_odd = match_session(orders_q_odd, k_num=1, k_den=2, pricing="pair", rounding="half_even")
        self.assertEqual(fills_he_odd[0].price_ticks, 4)

        # So sánh cùng n=7 với các phép làm tròn khác:
        fills_fl_odd = match_session(orders_q_odd, k_num=1, k_den=2, pricing="pair", rounding="floor")
        self.assertEqual(fills_fl_odd[0].price_ticks, 3)
        fills_ce_odd = match_session(orders_q_odd, k_num=1, k_den=2, pricing="pair", rounding="ceil")
        self.assertEqual(fills_ce_odd[0].price_ticks, 4)
        fills_hu_odd = match_session(orders_q_odd, k_num=1, k_den=2, pricing="pair", rounding="half_up")
        self.assertEqual(fills_hu_odd[0].price_ticks, 4)


if __name__ == "__main__":
    unittest.main()
