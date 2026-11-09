"""Unit tests cho module kda_sim.py (Giai đoạn 2, Nhiệm vụ J2).

Tuân thủ đầy đủ các tiêu chí chấp nhận trong anti-missions/contract-c.md:
(1) θ = (0, 1, 0, 1) cho welfare == max_welfare (1e-9) cho cả ba rule.
(2) m = 1: ba rule cho kết quả trùng nhau.
(3) cùng seed → cùng kết quả; khác seed → khác kết quả.
(4) Đối chiếu độc lập: 200 thị trường m = 5 với θ chiến lược cs_theta(0.5) và θ trung thực,
    welfare từ kda_sim với tick=0.01 trùng welfare từ metrics.run_auction + model.to_order (sai số 1e-6).
(5) "kda" thỏa ask <= p <= bid cho mọi cặp được khớp trên 2000 thị trường.
(6b) Với m bid và m ask một đơn vị, rule="kda" cho giá bằng (1-k)*s(m) + k*s(m+1) của mảng gộp 2m báo giá
     (kiểm 5000 thị trường, k in {0.25, 0.5, 1}), và giá kda luôn nằm trong [a(m*), b(m*)].
(6) Phản ví dụ của marginal (BID 10, ASK 1, ASK 2, k=0.5): marginal p=5.5, kda p=1.5.
(7) Hiệu năng: n_scen = 20000, m = 64 một lần welfare chạy dưới 5 giây.
"""

import os
import sys
import time
import unittest
import numpy as np

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from kda_sim import (
    apply_strategy,
    clear,
    cs_theta,
    deviator_utility,
    draw_scenarios,
    max_welfare,
    theta_to_strategy,
    welfare,
)
import metrics
from model import OrderType, Valued, to_order
import strategies


class TestKDASim(unittest.TestCase):
    """Kiểm thử toàn diện các quy tắc giá và thị trường vector hóa kda_sim."""

    def test_cs_theta_matches_formula_and_strategies(self):
        """Kiểm tra cs_theta(k) trùng khớp với strategies.cs_linear_coeffs."""
        for k_val in (0.25, 0.5, 0.75, 1.0):
            th = cs_theta(k_val)
            alpha_b, beta_b, alpha_s, beta_s = th
            expected_ab = k_val * (1.0 - k_val) / (2.0 * (1.0 + k_val))
            expected_bb = 1.0 / (1.0 + k_val)
            expected_as = (1.0 - k_val) / 2.0
            expected_bs = 1.0 / (2.0 - k_val)

            self.assertAlmostEqual(alpha_b, expected_ab, places=12)
            self.assertAlmostEqual(beta_b, expected_bb, places=12)
            self.assertAlmostEqual(alpha_s, expected_as, places=12)
            self.assertAlmostEqual(beta_s, expected_bs, places=12)

            if k_val < 1.0:
                coeffs = strategies.cs_linear_coeffs(k_val)
                self.assertAlmostEqual(alpha_b, coeffs[OrderType.BID][0], places=12)
                self.assertAlmostEqual(beta_b, coeffs[OrderType.BID][1], places=12)
                self.assertAlmostEqual(alpha_s, coeffs[OrderType.ASK][0], places=12)
                self.assertAlmostEqual(beta_s, coeffs[OrderType.ASK][1], places=12)

    def test_theta_to_strategy_clamping(self):
        """Kiểm tra kẹp bid <= v và ask >= c khi chuyển theta sang chiến lược lưới."""
        theta = (0.2, 0.9, 0.1, 0.8)
        v_knots = np.linspace(0.0, 1.0, 21)
        bid_knots, ask_knots = theta_to_strategy(theta, v_knots=v_knots)

        self.assertTrue(np.all(bid_knots <= v_knots + 1e-12))
        self.assertTrue(np.all(ask_knots >= v_knots - 1e-12))

    def test_1_truthful_welfare_equals_max_welfare(self):
        """Bắt buộc (1): θ = (0, 1, 0, 1) cho welfare == max_welfare (sai số 1e-9) cho cả 3 rule."""
        truthful_theta = (0.0, 1.0, 0.0, 1.0)
        rules = ("pair", "marginal", "kda")
        k_values = (0.25, 0.5, 0.75, 1.0)
        m_values = (1, 5, 20)

        for m_val in m_values:
            V, C = draw_scenarios(m=m_val, n_scen=500, seed=123)
            mw = max_welfare(V, C)

            for rule_val in rules:
                for k_val in k_values:
                    w = welfare(V, C, truthful_theta, k=k_val, rule=rule_val)
                    np.testing.assert_allclose(
                        w,
                        mw,
                        atol=1e-9,
                        err_msg=f"Welfare không bằng max_welfare tại m={m_val}, rule={rule_val}, k={k_val}",
                    )

    def test_2_m_equals_1_all_rules_identical(self):
        """Bắt buộc (2): m = 1 ba rule ("pair", "marginal", "kda") cho kết quả trùng nhau."""
        k_values = (0.25, 0.5, 0.75, 1.0)
        V, C = draw_scenarios(m=1, n_scen=1000, seed=456)
        strategy = cs_theta(0.5)

        for k_val in k_values:
            w_pair = welfare(V, C, strategy, k=k_val, rule="pair")
            w_marginal = welfare(V, C, strategy, k=k_val, rule="marginal")
            w_kda = welfare(V, C, strategy, k=k_val, rule="kda")

            np.testing.assert_allclose(w_pair, w_marginal, atol=1e-12)
            np.testing.assert_allclose(w_marginal, w_kda, atol=1e-12)

            bids = apply_strategy(V, theta_to_strategy(strategy)[0], side="bid")
            asks = apply_strategy(C, theta_to_strategy(strategy)[1], side="ask")

            res_pair = clear(bids, asks, k=k_val, rule="pair")
            res_marginal = clear(bids, asks, k=k_val, rule="marginal")
            res_kda = clear(bids, asks, k=k_val, rule="kda")

            np.testing.assert_array_equal(res_pair["m_star"], res_marginal["m_star"])
            np.testing.assert_array_equal(res_marginal["m_star"], res_kda["m_star"])
            np.testing.assert_allclose(res_pair["clearing_price"], res_marginal["clearing_price"], atol=1e-12)
            np.testing.assert_allclose(res_marginal["clearing_price"], res_kda["clearing_price"], atol=1e-12)
            np.testing.assert_allclose(res_pair["total_payment"], res_kda["total_payment"], atol=1e-12)

    def test_3_seed_determinism(self):
        """Bắt buộc (3): Cùng seed → cùng kết quả; khác seed → khác kết quả."""
        V1, C1 = draw_scenarios(m=10, n_scen=200, seed=999)
        V2, C2 = draw_scenarios(m=10, n_scen=200, seed=999)
        V3, C3 = draw_scenarios(m=10, n_scen=200, seed=1000)

        np.testing.assert_array_equal(V1, V2)
        np.testing.assert_array_equal(C1, C2)
        self.assertFalse(np.array_equal(V1, V3))

        w1 = welfare(V1, C1, cs_theta(0.5), k=0.5, rule="kda")
        w2 = welfare(V2, C2, cs_theta(0.5), k=0.5, rule="kda")
        np.testing.assert_array_equal(w1, w2)

    def test_4_independent_benchmark_against_engine(self):
        """Bắt buộc (4): Đối chiếu độc lập trên 200 thị trường m = 5 với θ chiến lược cs_theta(0.5)

        và θ trung thực; welfare từ kda_sim với tick=0.01 trùng welfare từ metrics.run_auction + model.to_order
        với sai số 1e-6.
        """
        n_markets = 200
        m_val = 5
        V, C = draw_scenarios(m=m_val, n_scen=n_markets, seed=777)

        # Cấu hình 1: θ chiến lược cs_theta(0.5)
        theta_strat = cs_theta(0.5)
        w_sim_strat = welfare(V, C, theta_strat, k=0.5, rule="pair", tick=0.01)

        alpha_b, beta_b, alpha_s, beta_s = theta_strat

        def price_fn_strat(v: Valued) -> float:
            if v.side == OrderType.BID:
                return min(v.valuation, alpha_b + beta_b * v.valuation)
            else:
                return max(v.valuation, alpha_s + beta_s * v.valuation)

        for s in range(n_markets):
            valued_orders: list[Valued] = []
            for i in range(m_val):
                valued_orders.append(
                    Valued(
                        order_id=f"B{i}",
                        side=OrderType.BID,
                        amount=1,
                        valuation=float(V[s, i]),
                        arrival=i,
                    )
                )
            for j in range(m_val):
                valued_orders.append(
                    Valued(
                        order_id=f"S{j}",
                        side=OrderType.ASK,
                        amount=1,
                        valuation=float(C[s, j]),
                        arrival=m_val + j,
                    )
                )

            matches = metrics.run_auction(valued_orders, k=0.5, price_fn=price_fn_strat)
            w_bench = metrics.welfare(matches, valued_orders)
            self.assertAlmostEqual(
                w_sim_strat[s],
                w_bench,
                places=5,
                msg=f"Lệch benchmark tại kịch bản {s}: sim={w_sim_strat[s]}, bench={w_bench}",
            )

        # Cấu hình 2: θ trung thực (0, 1, 0, 1)
        truthful_theta = (0.0, 1.0, 0.0, 1.0)
        w_sim_truth = welfare(V, C, truthful_theta, k=0.5, rule="pair", tick=0.01)

        for s in range(n_markets):
            valued_orders = []
            for i in range(m_val):
                valued_orders.append(
                    Valued(
                        order_id=f"B{i}",
                        side=OrderType.BID,
                        amount=1,
                        valuation=float(V[s, i]),
                        arrival=i,
                    )
                )
            for j in range(m_val):
                valued_orders.append(
                    Valued(
                        order_id=f"S{j}",
                        side=OrderType.ASK,
                        amount=1,
                        valuation=float(C[s, j]),
                        arrival=m_val + j,
                    )
                )

            matches = metrics.run_auction(valued_orders, k=0.5, price_fn=metrics.truthful)
            w_bench = metrics.welfare(matches, valued_orders)
            self.assertAlmostEqual(
                w_sim_truth[s],
                w_bench,
                places=5,
                msg=f"Lệch benchmark trung thực tại kịch bản {s}: sim={w_sim_truth[s]}, bench={w_bench}",
            )

    def test_5_kda_price_bounds_2000_markets(self):
        """Bắt buộc (5): "kda" thỏa ask <= p <= bid cho mọi cặp được khớp trên 2000 thị trường."""
        n_markets = 2000
        m_val = 8
        V, C = draw_scenarios(m=m_val, n_scen=n_markets, seed=2026)
        strategy = cs_theta(0.5)

        for k_val in (0.25, 0.5, 0.75, 1.0):
            bids = apply_strategy(V, theta_to_strategy(strategy)[0], side="bid")
            asks = apply_strategy(C, theta_to_strategy(strategy)[1], side="ask")

            res = clear(bids, asks, k=k_val, rule="kda")
            m_star = res["m_star"]
            bids_sorted = res["bids_sorted"]
            asks_sorted = res["asks_sorted"]
            p_mat = res["price_matrix"]

            for i in range(m_val):
                matched_mask = i < m_star
                if np.any(matched_mask):
                    pair_p = p_mat[matched_mask, i]
                    pair_ask = asks_sorted[matched_mask, i]
                    pair_bid = bids_sorted[matched_mask, i]

                    self.assertTrue(
                        np.all(pair_p >= pair_ask - 1e-9),
                        msg=f"Vi phạm p >= ask tại k={k_val}, cặp {i}",
                    )
                    self.assertTrue(
                        np.all(pair_p <= pair_bid + 1e-9),
                        msg=f"Vi phạm p <= bid tại k={k_val}, cặp {i}",
                    )

    def test_6b_kda_pooled_median_formula_5000_markets(self):
        """Bắt buộc (6b): Với m bid và m ask một đơn vị, rule="kda" cho giá bằng (1-k)*s(m) + k*s(m+1)

        của mảng gộp 2m báo giá sắp tăng dần (kiểm 5000 thị trường, k in {0.25, 0.5, 1}),
        và với mọi k giá kda nằm trong [a(m*), b(m*)].
        """
        n_markets = 5000
        m_val = 6
        V, C = draw_scenarios(m=m_val, n_scen=n_markets, seed=5000)
        strategy = cs_theta(0.5)
        bid_knots, ask_knots = theta_to_strategy(strategy)

        bids = apply_strategy(V, bid_knots, side="bid")
        asks = apply_strategy(C, ask_knots, side="ask")

        # Mảng gộp 2m báo giá sắp tăng dần
        pooled = np.concatenate([bids, asks], axis=-1)
        pooled_sorted = np.sort(pooled, axis=-1)
        # s(m) ứng với chỉ số 0-based m-1; s(m+1) ứng với chỉ số 0-based m
        s_m = pooled_sorted[:, m_val - 1]
        s_m_plus_1 = pooled_sorted[:, m_val]

        for k_val in (0.25, 0.5, 1.0):
            res = clear(bids, asks, k=k_val, rule="kda")
            m_star = res["m_star"]
            clearing_p = res["clearing_price"]
            b_m = res["b_m"]
            a_m = res["a_m"]

            # Chỉ xét các thị trường có khớp lệnh (m_star > 0)
            trade_mask = m_star > 0
            self.assertTrue(np.any(trade_mask))

            expected_p = (1.0 - k_val) * s_m[trade_mask] + k_val * s_m_plus_1[trade_mask]
            actual_p = clearing_p[trade_mask]

            np.testing.assert_allclose(
                actual_p,
                expected_p,
                atol=1e-9,
                err_msg=f"Giá kda không khớp công thức mảng gộp tại k={k_val}",
            )

            # Kiểm tra giá nằm trong [a(m*), b(m*)]
            self.assertTrue(
                np.all(actual_p >= a_m[trade_mask] - 1e-9),
                msg=f"Giá kda thấp hơn a(m*) tại k={k_val}",
            )
            self.assertTrue(
                np.all(actual_p <= b_m[trade_mask] + 1e-9),
                msg=f"Giá kda cao hơn b(m*) tại k={k_val}",
            )

    def test_6_marginal_counterexample(self):
        """Bắt buộc (6): Phản ví dụ của marginal: BID 10, ASK 1, ASK 2, k=0.5 -> marginal p=5.5, kda p=1.5."""
        bids = np.array([10.0])
        asks = np.array([1.0, 2.0])

        res_marginal = clear(bids, asks, k=0.5, rule="marginal")
        res_kda = clear(bids, asks, k=0.5, rule="kda")

        self.assertAlmostEqual(res_marginal["clearing_price"], 5.5, places=9)
        self.assertAlmostEqual(res_kda["clearing_price"], 1.5, places=9)
        self.assertEqual(res_marginal["m_star"], 1)
        self.assertEqual(res_kda["m_star"], 1)

    def test_large_scale_performance_welfare(self):
        """Tiêu chí chấp nhận (4): n_scen = 20000, m = 64 một lần welfare chạy dưới 5 giây."""
        V, C = draw_scenarios(m=64, n_scen=20000, seed=8888)
        strategy = cs_theta(0.5)

        t_start = time.perf_counter()
        w = welfare(V, C, strategy, k=0.5, rule="kda")
        t_elapsed = time.perf_counter() - t_start

        self.assertEqual(w.shape, (20000,))
        self.assertLess(
            t_elapsed,
            5.0,
            msg=f"welfare chạy quá 5 giây ({t_elapsed:.4f}s) tại n_scen=20000, m=64",
        )
        print(f"\n[PERF] n_scen=20000, m=64 welfare hoàn thành trong {t_elapsed:.4f} giây.")

    def test_deviator_utility_evaluation(self):
        """Kiểm tra deviator_utility cho cả buyer và seller trên đơn điểm, hàm và lưới."""
        V, C = draw_scenarios(m=4, n_scen=500, seed=314)
        strat = cs_theta(0.5)

        # 1. Buyer deviator với hàm
        u_truth = deviator_utility(V, C, strat, k=0.5, rule="kda", side="buy", bid_fn_or_grid=lambda v: v)
        self.assertIsInstance(u_truth, float)
        self.assertGreater(u_truth, 0.0)

        # 2. Buyer deviator với giá cố định scalar
        u_scalar = deviator_utility(V, C, strat, k=0.5, rule="kda", side="buy", bid_fn_or_grid=0.5)
        self.assertIsInstance(u_scalar, float)

        # 3. Buyer deviator trên lưới giá
        grid = np.linspace(0.1, 0.9, 9)
        u_grid = deviator_utility(V, C, strat, k=0.5, rule="kda", side="buy", bid_fn_or_grid=grid, as_grid=True)
        self.assertIsInstance(u_grid, np.ndarray)
        self.assertEqual(len(u_grid), 9)

        # 4. Seller deviator với hàm
        u_seller = deviator_utility(V, C, strat, k=0.5, rule="kda", side="sell", bid_fn_or_grid=lambda c: c)
        self.assertIsInstance(u_seller, float)
        self.assertGreater(u_seller, 0.0)

    def test_invalid_parameters_raise_errors(self):
        """Kiểm tra xử lý lỗi khi tham số đầu vào không hợp lệ."""
        with self.assertRaises(ValueError):
            cs_theta(0.0)
        with self.assertRaises(ValueError):
            cs_theta(1.1)

        with self.assertRaises(ValueError):
            draw_scenarios(m=0, n_scen=10, seed=1)
        with self.assertRaises(ValueError):
            draw_scenarios(m=5, n_scen=0, seed=1)

        bids = np.array([0.5])
        asks = np.array([0.4])
        with self.assertRaises(ValueError):
            clear(bids, asks, k=0.5, rule="unknown_rule")
        with self.assertRaises(ValueError):
            clear(bids, asks, k=0.0, rule="kda")
        with self.assertRaises(ValueError):
            clear(bids, asks, k=1.5, rule="kda")

    def test_deviator_outcome_identity(self):
        """Bắt buộc J3 (i): deviator_utility == v*W - P trong 1e-12 cho ba rule, cả hai phía."""
        from kda_sim import deviator_outcome

        V, C = draw_scenarios(m=4, n_scen=500, seed=42)
        strat = cs_theta(0.5)

        # Kiểm tra phía người mua: U = v*W(b) - P(b)
        test_buyer_cases = [(0.8, 0.6), (0.5, 0.3), (0.9, 0.9), (0.4, 0.2)]
        b_grid = np.array([b for _, b in test_buyer_cases])

        for rule in ("pair", "marginal", "kda"):
            W_b, P_b = deviator_outcome(V, C, strat, k=0.5, rule=rule, side="buy", price_grid=b_grid)
            for idx, (v_val, b_val) in enumerate(test_buyer_cases):
                V2 = V.copy()
                V2[:, 0] = v_val
                u_exact = deviator_utility(V2, C, strat, k=0.5, rule=rule, side="buy", bid_fn_or_grid=b_val)
                u_formula = v_val * W_b[idx] - P_b[idx]
                self.assertAlmostEqual(
                    u_exact,
                    u_formula,
                    delta=1e-12,
                    msg=f"Lệch identity buyer tại rule={rule}, v={v_val}, b={b_val}",
                )

        # Kiểm tra phía người bán: U = P(a) - c*W(a)
        test_seller_cases = [(0.2, 0.4), (0.5, 0.7), (0.1, 0.1), (0.6, 0.8)]
        a_grid = np.array([a for _, a in test_seller_cases])

        for rule in ("pair", "marginal", "kda"):
            W_s, P_s = deviator_outcome(V, C, strat, k=0.5, rule=rule, side="sell", price_grid=a_grid)
            for idx, (c_val, a_val) in enumerate(test_seller_cases):
                C2 = C.copy()
                C2[:, 0] = c_val
                u_exact = deviator_utility(V, C2, strat, k=0.5, rule=rule, side="sell", bid_fn_or_grid=a_val)
                u_formula = P_s[idx] - c_val * W_s[idx]
                self.assertAlmostEqual(
                    u_exact,
                    u_formula,
                    delta=1e-12,
                    msg=f"Lệch identity seller tại rule={rule}, c={c_val}, a={a_val}",
                )

    def test_deviator_outcome_monotonicity(self):
        """Bắt buộc J3 (ii): W đơn điệu không giảm theo b (mua) và không tăng theo a (bán)."""
        from kda_sim import deviator_outcome

        V, C = draw_scenarios(m=4, n_scen=1000, seed=123)
        strat = cs_theta(0.5)
        grid = np.linspace(0.0, 1.0, 41)

        for rule in ("pair", "marginal", "kda"):
            W_buy, _ = deviator_outcome(V, C, strat, k=0.5, rule=rule, side="buy", price_grid=grid)
            diff_buy = np.diff(W_buy)
            self.assertTrue(
                np.all(diff_buy >= -1e-12),
                msg=f"W_buy không đơn điệu tăng tại rule={rule}, min diff={np.min(diff_buy)}",
            )

            W_sell, _ = deviator_outcome(V, C, strat, k=0.5, rule=rule, side="sell", price_grid=grid)
            diff_sell = np.diff(W_sell)
            self.assertTrue(
                np.all(diff_sell <= 1e-12),
                msg=f"W_sell không đơn điệu giảm tại rule={rule}, max diff={np.max(diff_sell)}",
            )

    def test_deviator_outcome_performance(self):
        """Tiêu chí chấp nhận (5): deviator_outcome m=16, n_scen=20000, lưới 81 dưới 5s."""
        from kda_sim import deviator_outcome

        V, C = draw_scenarios(m=16, n_scen=20000, seed=7777)
        strat = cs_theta(0.5)
        grid = np.linspace(0.0, 1.0, 81)

        t_start = time.perf_counter()
        W, P = deviator_outcome(V, C, strat, k=0.5, rule="kda", side="buy", price_grid=grid)
        elapsed = time.perf_counter() - t_start

        self.assertEqual(len(W), 81)
        self.assertEqual(len(P), 81)
        self.assertLess(
            elapsed,
            5.0,
            msg=f"deviator_outcome chạy quá 5 giây ({elapsed:.4f}s) tại m=16, n_scen=20000, grid=81",
        )
        print(f"\n[PERF] deviator_outcome m=16, n_scen=20000, grid=81 hoàn thành trong {elapsed:.4f}s")


if __name__ == "__main__":
    unittest.main()
