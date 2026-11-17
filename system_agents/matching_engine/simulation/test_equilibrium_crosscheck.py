"""Kiểm thử đơn vị cho equilibrium_crosscheck (Nhiệm vụ B2).

Kiểm tra:
  1. Hàm clear() trên >= 5 ví dụ tay (M=0, hòa bid=ask, 1 bid=10 & 2 asks=[1, 2],
     bất đối xứng next bid, multi-pair có cả next bid & next ask, cận k=1.0).
  2. Bất biến giá của clear(): pair nằm trong [a(i), b(i)], marginal mọi cặp cùng giá,
     kda mọi cặp cùng giá và nằm trong [a(M), b(M)].
  3. Xử lý lỗi đầu vào không hợp lệ của clear() và solve().
  4. Tính tất định của solve(): cùng seed -> cùng kết quả.
  5. Đối chiếu nghiệm solve(m=1) với nghiệm đóng cs_linear_coeffs(k) tại k in {0.25, 0.5, 0.75},
     sai số tuyệt đối mỗi tham số <= 0.03.
"""

from __future__ import annotations

import os
import sys
import unittest
import numpy as np

# Đảm bảo đường dẫn simulation có trong sys.path để import
_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)

from equilibrium_crosscheck import clear, solve
from strategies import cs_linear_coeffs


class TestClearHandCalculated(unittest.TestCase):
    """Bộ kiểm thử clear() trên các ví dụ tính tay độc lập."""

    def test_example_1_m_zero_no_overlap(self):
        """Ví dụ 1: M = 0 (không có cặp lệnh nào có bid >= ask).

        Tính tay:
          Bids: [2.0, 1.0] -> sắp xếp giảm dần: [2.0, 1.0]
          Asks: [3.0, 4.0] -> sắp xếp tăng dần: [3.0, 4.0]
          Cặp 1: b(1)=2.0 < a(1)=3.0 -> không khớp.
          => M = 0, prices = [].
        Áp dụng cho mọi quy tắc ('pair', 'marginal', 'kda') với k = 0.5.
        """
        bids = [2.0, 1.0]
        asks = [3.0, 4.0]
        for rule in ("pair", "marginal", "kda"):
            m_matched, prices = clear(bids, asks, k=0.5, rule=rule)
            self.assertEqual(m_matched, 0, f"Thất bại ở quy tắc {rule}")
            self.assertEqual(prices, [], f"Thất bại ở quy tắc {rule}")

    def test_example_2_tie_bid_equals_ask(self):
        """Ví dụ 2: Hòa bid = ask (khớp cả khi bằng nhau theo hợp đồng).

        Tính tay:
          Bids: [5.0, 3.0] -> sắp xếp giảm dần: b(1)=5.0, b(2)=3.0
          Asks: [2.0, 3.0] -> sắp xếp tăng dần: a(1)=2.0, a(2)=3.0
          Cặp 1: b(1)=5.0 >= a(1)=2.0 -> khớp.
          Cặp 2: b(2)=3.0 >= a(2)=3.0 -> hòa bid=ask, khớp!
          => M = 2.
          Với k = 0.5:
            - pair:
                Cặp 1: 0.5 * 5.0 + 0.5 * 2.0 = 3.5
                Cặp 2: 0.5 * 3.0 + 0.5 * 3.0 = 3.0
                prices = [3.5, 3.0]
            - marginal:
                b(M)=b(2)=3.0, a(M)=a(2)=3.0
                giá chung = 0.5 * 3.0 + 0.5 * 3.0 = 3.0
                prices = [3.0, 3.0]
            - kda:
                m_b=2, m_s=2 -> không có lệnh kế tiếp.
                hi = b(2) = 3.0, lo = a(2) = 3.0
                giá chung = 0.5 * 3.0 + 0.5 * 3.0 = 3.0
                prices = [3.0, 3.0]
        """
        bids = [5.0, 3.0]
        asks = [2.0, 3.0]
        k = 0.5

        m_pair, p_pair = clear(bids, asks, k=k, rule="pair")
        self.assertEqual(m_pair, 2)
        self.assertEqual(len(p_pair), 2)
        self.assertAlmostEqual(p_pair[0], 3.5, places=7)
        self.assertAlmostEqual(p_pair[1], 3.0, places=7)

        m_marg, p_marg = clear(bids, asks, k=k, rule="marginal")
        self.assertEqual(m_marg, 2)
        self.assertEqual(p_marg, [3.0, 3.0])

        m_kda, p_kda = clear(bids, asks, k=k, rule="kda")
        self.assertEqual(m_kda, 2)
        self.assertEqual(p_kda, [3.0, 3.0])

    def test_example_3_contract_example_1bid_2asks(self):
        """Ví dụ 3: Ví dụ bắt buộc theo hợp đồng (1 bid=10, 2 asks=[1, 2] với k=1/2).

        Tính tay từ định nghĩa:
          Bids: [10.0] (m_b = 1) -> b(1) = 10.0
          Asks: [1.0, 2.0] (m_s = 2) -> a(1) = 1.0, a(2) = 2.0
          Cặp 1: b(1)=10.0 >= a(1)=1.0 -> khớp.
          Không có cặp 2 vì m_b = 1.
          => M = 1. b(M) = 10.0, a(M) = 1.0.
          Quy tắc marginal với k = 0.5:
            giá = k * b(M) + (1 - k) * a(M) = 0.5 * 10.0 + 0.5 * 1.0 = 5.5
            prices = [5.5]
          Quy tắc kda với k = 0.5:
            m_b = 1 => không có bid kế tiếp => lo = a(M) = 1.0
            m_s = 2 => có ask kế tiếp a(2) = 2.0 => hi = min(b(M), a(2)) = min(10.0, 2.0) = 2.0
            giá = k * hi + (1 - k) * lo = 0.5 * 2.0 + 0.5 * 1.0 = 1.0 + 0.5 = 1.5
            prices = [1.5]
          Quy tắc pair với k = 0.5:
            giá = 0.5 * 10.0 + 0.5 * 1.0 = 5.5
            prices = [5.5]
        """
        bids = [10.0]
        asks = [1.0, 2.0]
        k = 0.5

        # Kiểm tra marginal ra đúng 5.5
        m_marg, p_marg = clear(bids, asks, k=k, rule="marginal")
        self.assertEqual(m_marg, 1)
        self.assertEqual(len(p_marg), 1)
        self.assertAlmostEqual(p_marg[0], 5.5, places=7)

        # Kiểm tra kda ra đúng 1.5
        m_kda, p_kda = clear(bids, asks, k=k, rule="kda")
        self.assertEqual(m_kda, 1)
        self.assertEqual(len(p_kda), 1)
        self.assertAlmostEqual(p_kda[0], 1.5, places=7)

        # Kiểm tra pair ra đúng 5.5
        m_pair, p_pair = clear(bids, asks, k=k, rule="pair")
        self.assertEqual(m_pair, 1)
        self.assertAlmostEqual(p_pair[0], 5.5, places=7)

    def test_example_4_asymmetric_next_bid_exists(self):
        """Ví dụ 4: Khớp bất đối xứng có bid kế tiếp (2 bids=[8.0, 4.0], 1 ask=[2.0], k=0.5).

        Tính tay:
          Bids: [8.0, 4.0] (m_b = 2) -> b(1)=8.0, b(2)=4.0
          Asks: [2.0] (m_s = 1) -> a(1)=2.0
          Cặp 1: b(1)=8.0 >= a(1)=2.0 -> khớp. M = 1.
          b(M) = 8.0, a(M) = 2.0.
          Quy tắc pair:
            giá = 0.5 * 8.0 + 0.5 * 2.0 = 5.0 -> prices = [5.0]
          Quy tắc marginal:
            giá = 0.5 * 8.0 + 0.5 * 2.0 = 5.0 -> prices = [5.0]
          Quy tắc kda:
            m_s = 1 => không có ask kế tiếp => hi = b(M) = 8.0
            m_b = 2 => có bid kế tiếp b(2) = 4.0 => lo = max(a(M), b(2)) = max(2.0, 4.0) = 4.0
            giá = 0.5 * 8.0 + 0.5 * 4.0 = 4.0 + 2.0 = 6.0
            prices = [6.0]
        """
        bids = [8.0, 4.0]
        asks = [2.0]
        k = 0.5

        m_pair, p_pair = clear(bids, asks, k=k, rule="pair")
        self.assertEqual(m_pair, 1)
        self.assertAlmostEqual(p_pair[0], 5.0, places=7)

        m_marg, p_marg = clear(bids, asks, k=k, rule="marginal")
        self.assertEqual(m_marg, 1)
        self.assertAlmostEqual(p_marg[0], 5.0, places=7)

        m_kda, p_kda = clear(bids, asks, k=k, rule="kda")
        self.assertEqual(m_kda, 1)
        self.assertAlmostEqual(p_kda[0], 6.0, places=7)

    def test_example_5_multi_pair_with_both_next_orders(self):
        """Ví dụ 5: 3 bids=[9.0, 7.0, 3.0], 3 asks=[1.0, 5.0, 8.0], k=0.25 (có cả next bid & ask).

        Tính tay:
          Bids: b(1)=9.0, b(2)=7.0, b(3)=3.0
          Asks: a(1)=1.0, a(2)=5.0, a(3)=8.0
          Cặp 1: b(1)=9.0 >= a(1)=1.0 -> khớp.
          Cặp 2: b(2)=7.0 >= a(2)=5.0 -> khớp.
          Cặp 3: b(3)=3.0 < a(3)=8.0 -> không khớp.
          => M = 2. b(M)=7.0, a(M)=5.0.
          Lệnh kế tiếp: b(3)=3.0, a(3)=8.0.
          Với k = 0.25:
            - pair:
                Cặp 1: 0.25 * 9.0 + 0.75 * 1.0 = 2.25 + 0.75 = 3.0
                Cặp 2: 0.25 * 7.0 + 0.75 * 5.0 = 1.75 + 3.75 = 5.5
                prices = [3.0, 5.5]
            - marginal:
                giá chung = 0.25 * 7.0 + 0.75 * 5.0 = 5.5
                prices = [5.5, 5.5]
            - kda:
                hi = min(b(M), a(3)) = min(7.0, 8.0) = 7.0
                lo = max(a(M), b(3)) = max(5.0, 3.0) = 5.0
                giá chung = 0.25 * 7.0 + 0.75 * 5.0 = 5.5
                prices = [5.5, 5.5]
        """
        bids = [9.0, 7.0, 3.0]
        asks = [1.0, 5.0, 8.0]
        k = 0.25

        m_pair, p_pair = clear(bids, asks, k=k, rule="pair")
        self.assertEqual(m_pair, 2)
        self.assertAlmostEqual(p_pair[0], 3.0, places=7)
        self.assertAlmostEqual(p_pair[1], 5.5, places=7)

        m_marg, p_marg = clear(bids, asks, k=k, rule="marginal")
        self.assertEqual(m_marg, 2)
        self.assertEqual(p_marg, [5.5, 5.5])

        m_kda, p_kda = clear(bids, asks, k=k, rule="kda")
        self.assertEqual(m_kda, 2)
        self.assertEqual(p_kda, [5.5, 5.5])

    def test_example_6_boundary_k_equals_1(self):
        """Ví dụ 6: Cận k = 1.0 (toàn bộ thặng dư trao cho bên mua / giá theo bid).

        Tính tay:
          Bids: [6.0], Asks: [2.0], k=1.0.
          M = 1.
          pair: 1.0 * 6.0 + 0.0 * 2.0 = 6.0
          marginal: 1.0 * 6.0 + 0.0 * 2.0 = 6.0
          kda: hi=6.0, lo=2.0 -> 1.0 * 6.0 + 0.0 * 2.0 = 6.0
        """
        bids = [6.0]
        asks = [2.0]
        k = 1.0
        for rule in ("pair", "marginal", "kda"):
            m_matched, prices = clear(bids, asks, k=k, rule=rule)
            self.assertEqual(m_matched, 1)
            self.assertEqual(prices, [6.0])


class TestClearInvariants(unittest.TestCase):
    """Kiểm tra các bất biến cấu trúc và xử lý ngoại lệ của hàm clear()."""

    def test_pair_prices_always_bounded_by_orders(self):
        """Bất biến: với rule 'pair', giá p(i) luôn nằm trong đoạn [a(i), b(i)]."""
        rng = np.random.default_rng(42)
        for _ in range(20):
            m_b = rng.integers(1, 10)
            m_s = rng.integers(1, 10)
            bids = rng.uniform(0.0, 10.0, size=m_b)
            asks = rng.uniform(0.0, 10.0, size=m_s)
            k = float(rng.uniform(0.01, 1.0))

            M, prices = clear(bids, asks, k=k, rule="pair")
            if M > 0:
                b_sort = np.sort(bids)[::-1]
                a_sort = np.sort(asks)
                for i in range(M):
                    self.assertGreaterEqual(prices[i], a_sort[i] - 1e-9)
                    self.assertLessEqual(prices[i], b_sort[i] + 1e-9)

    def test_marginal_uniform_price(self):
        """Bất biến: với rule 'marginal', mọi cặp khớp đều có cùng một mức giá."""
        rng = np.random.default_rng(123)
        for _ in range(20):
            bids = rng.uniform(1.0, 10.0, size=8)
            asks = rng.uniform(0.0, 8.0, size=8)
            k = float(rng.uniform(0.05, 0.95))

            M, prices = clear(bids, asks, k=k, rule="marginal")
            if M > 0:
                self.assertEqual(len(prices), M)
                for p in prices:
                    self.assertAlmostEqual(p, prices[0], places=7)

    def test_kda_uniform_price_and_bounds(self):
        """Bất biến: với rule 'kda', mọi cặp khớp có cùng giá và nằm trong [a(M), b(M)]."""
        rng = np.random.default_rng(456)
        for _ in range(20):
            bids = rng.uniform(1.0, 10.0, size=8)
            asks = rng.uniform(0.0, 8.0, size=8)
            k = float(rng.uniform(0.05, 0.95))

            M, prices = clear(bids, asks, k=k, rule="kda")
            if M > 0:
                self.assertEqual(len(prices), M)
                b_sort = np.sort(bids)[::-1]
                a_sort = np.sort(asks)
                for p in prices:
                    self.assertAlmostEqual(p, prices[0], places=7)
                    self.assertGreaterEqual(p, a_sort[M - 1] - 1e-9)
                    self.assertLessEqual(p, b_sort[M - 1] + 1e-9)

    def test_invalid_parameters_raise_value_error(self):
        """clear() phải tung ValueError khi k hoặc rule không hợp lệ."""
        # k <= 0 hoặc k > 1
        with self.assertRaises(ValueError):
            clear([5.0], [3.0], k=0.0, rule="pair")
        with self.assertRaises(ValueError):
            clear([5.0], [3.0], k=-0.5, rule="marginal")
        with self.assertRaises(ValueError):
            clear([5.0], [3.0], k=1.0001, rule="kda")

        # rule không hợp lệ
        with self.assertRaises(ValueError):
            clear([5.0], [3.0], k=0.5, rule="invalid_rule")
        with self.assertRaises(ValueError):
            clear([5.0], [3.0], k=0.5, rule="")


class TestSolveEquilibrium(unittest.TestCase):
    """Kiểm thử nghiệm cân bằng từ hàm solve() và đối chiếu nghiệm đóng."""

    def test_solve_determinism(self):
        """Cùng tham số và cùng seed phải cho kết quả giống hệt nhau."""
        res1 = solve(m=1, k=0.5, rule="pair", n_scen=5000, seed=999, max_iter=20)
        res2 = solve(m=1, k=0.5, rule="pair", n_scen=5000, seed=999, max_iter=20)

        self.assertEqual(res1["seed"], res2["seed"])
        self.assertEqual(res1["n_evals"], res2["n_evals"])
        self.assertAlmostEqual(res1["exploitability"], res2["exploitability"], places=9)
        for v1, v2 in zip(res1["theta"], res2["theta"]):
            self.assertAlmostEqual(v1, v2, places=9)

    def test_solve_m1_matches_cs_linear_coeffs(self):
        """Với m=1: kết quả solve() khớp cs_linear_coeffs(k) sai số <= 0.03 với k in {0.25, 0.5, 0.75}."""
        test_ks = (0.25, 0.5, 0.75)

        for k in test_ks:
            coeffs_dict = cs_linear_coeffs(k)

            # Trích xuất hệ số từ cs_linear_coeffs
            exp_bid = None
            exp_ask = None
            for key, val in coeffs_dict.items():
                name = str(key).upper()
                if "BID" in name:
                    exp_bid = val
                elif "ASK" in name:
                    exp_ask = val
            self.assertIsNotNone(exp_bid)
            self.assertIsNotNone(exp_ask)
            a_theo, b_theo = exp_bid
            g_theo, d_theo = exp_ask

            # Chạy solve với m=1
            res = solve(m=1, k=k, rule="marginal", n_scen=10000, seed=0, max_iter=30)
            ab, bb, as_, bs = res["theta"]

            err_ab = abs(ab - a_theo)
            err_bb = abs(bb - b_theo)
            err_as = abs(as_ - g_theo)
            err_bs = abs(bs - d_theo)

            self.assertLessEqual(
                err_ab,
                0.03,
                f"k={k}: sai số ab={ab} so với {a_theo} là {err_ab:.4f} > 0.03",
            )
            self.assertLessEqual(
                err_bb,
                0.03,
                f"k={k}: sai số bb={bb} so với {b_theo} là {err_bb:.4f} > 0.03",
            )
            self.assertLessEqual(
                err_as,
                0.03,
                f"k={k}: sai số as={as_} so với {g_theo} là {err_as:.4f} > 0.03",
            )
            self.assertLessEqual(
                err_bs,
                0.03,
                f"k={k}: sai số bs={bs} so với {d_theo} là {err_bs:.4f} > 0.03",
            )

    def test_solve_invalid_parameters(self):
        """solve() phải tung ValueError khi m, k, rule hoặc n_scen không hợp lệ."""
        with self.assertRaises(ValueError):
            solve(m=0, k=0.5, rule="pair")
        with self.assertRaises(ValueError):
            solve(m=1, k=0.0, rule="pair")
        with self.assertRaises(ValueError):
            solve(m=1, k=1.5, rule="pair")
        with self.assertRaises(ValueError):
            solve(m=1, k=0.5, rule="unknown_rule")
        with self.assertRaises(ValueError):
            solve(m=1, k=0.5, rule="pair", n_scen=0)


if __name__ == "__main__":
    unittest.main()
