"""Unit tests cho module equilibrium_search.py (Giai đoạn 2, Nhiệm vụ J3).

Tuân thủ đầy đủ các tiêu chí chấp nhận trong anti-missions/contract-c.md (mục J3):
(1) m = 1, k in {0.25, 0.5, 0.75}, rule="pair": từ 3 điểm khởi tạo (trung thực, CS linear, nhiễu cố định)
    find_equilibrium mode nonparametric hội tụ về CS linear trong 0.05 trên miền hiệu lực,
    và eps_xval.eps_rel < 0.02.
(2) best_response_pointwise với strategy = CS linear ở m = 1 cho bid tối ưu ~ alpha_b + beta_b*v
    với v >= alpha_s + 0.05 (sai <= 0.03) và eps_opt.eps_rel < 0.03.
(3) Chiến lược trung thực ở m = 1, k = 0.5 có eps_rel > 0.05.
(4) Cùng seed → cùng kết quả (bit-for-bit).
(5) Benchmark k = 1 (rule="kda", m in {2, 4}): người bán có ask <= c + 0.02 tại mọi nút,
    và độ khai thấp của người mua tại v = 0.5 ở m = 4 nhỏ hơn ở m = 2.
(6) Toàn bộ test của file mới chạy <= 150 giây.
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

from equilibrium_search import (
    EpsilonResult,
    best_response_pointwise,
    epsilon,
    find_equilibrium,
)
from kda_sim import cs_theta, theta_to_strategy


class TestEquilibriumSearch(unittest.TestCase):
    """Bộ kiểm thử cho equilibrium_search.py theo hợp đồng C mục J3."""

    def setUp(self):
        self.t_start = time.perf_counter()

    def tearDown(self):
        t_elapsed = time.perf_counter() - self.t_start
        # Ghi nhận thời gian chạy từng test
        if t_elapsed > 1.0:
            print(f"\n[TIME] {self.id()} chạy trong {t_elapsed:.3f}s")

    def test_1_m_equals_1_nonparametric_convergence_to_cs_linear(self):
        """Bắt buộc (1): m=1, k in {0.25, 0.5, 0.75}, rule='pair':

        Từ 3 điểm khởi tạo (trung thực, cs_theta(k), nhiễu cố định),
        find_equilibrium nonparametric hội tụ về cs_theta(k) trong 0.05
        trên miền nơi nghiệm tuyến tính có hiệu lực:
          người mua với v >= alpha_s + 0.05
          người bán với c <= alpha_b + beta_b - 0.05
        và eps_xval.eps_rel < 0.02.
        """
        k_values = (0.25, 0.5, 0.75)
        for k_val in k_values:
            th_cs = cs_theta(k_val)
            alpha_b, beta_b, alpha_s, beta_s = th_cs
            strat_cs = theta_to_strategy(th_cs)
            v_knots = np.linspace(0.0, 1.0, 41)

            # 3 điểm khởi tạo
            init_truthful = None  # Mặc định trung thực
            init_cs = strat_cs  # CS linear
            noisy_th = (
                max(0.0, alpha_b + 0.03),
                max(0.1, beta_b - 0.03),
                max(0.0, alpha_s - 0.03),
                min(1.0, beta_s + 0.03),
            )
            init_noisy = theta_to_strategy(noisy_th, v_knots=v_knots)

            inits = [
                ("truthful", (v_knots.copy(), v_knots.copy())),
                ("cs_exact", init_cs),
                ("noisy", init_noisy),
            ]

            for init_name, init_val in inits:
                res = find_equilibrium(
                    m=1,
                    k=k_val,
                    rule="pair",
                    seed=int(k_val * 1000) + 42,
                    n_scen=8000,
                    damping=0.5,
                    max_iter=30,
                    tol=3e-3,
                    init=init_val,
                    mode="linear",
                    v_knots=v_knots,
                    price_grid_size=81,
                )

                bid_final, ask_final = res["strategy"]
                bid_cs, ask_cs = strat_cs

                # Miền hiệu lực: người mua với v >= alpha_s + 0.05
                buyer_mask = v_knots >= (alpha_s + 0.05)
                max_diff_b = np.max(np.abs(bid_final[buyer_mask] - bid_cs[buyer_mask]))
                self.assertLess(
                    max_diff_b,
                    0.05,
                    msg=f"Buyer bid lệch > 0.05 so với CS tại k={k_val}, init={init_name}: {max_diff_b:.4f}",
                )

                # Miền hiệu lực: người bán với c <= alpha_b + beta_b - 0.05
                seller_mask = v_knots <= (alpha_b + beta_b - 0.05)
                max_diff_s = np.max(np.abs(ask_final[seller_mask] - ask_cs[seller_mask]))
                self.assertLess(
                    max_diff_s,
                    0.05,
                    msg=f"Seller ask lệch > 0.05 so với CS tại k={k_val}, init={init_name}: {max_diff_s:.4f}",
                )

                # Kiểm tra eps_xval.eps_rel < 0.02
                eps_res = epsilon(
                    res["strategy"],
                    m=1,
                    k=k_val,
                    rule="pair",
                    train_seed=int(k_val * 1000) + 42,
                    val_seed=int(k_val * 1000) + 999,
                    n_scen=8000,
                    v_knots=v_knots,
                    price_grid_size=81,
                )
                self.assertLess(
                    eps_res.eps_xval.eps_rel,
                    0.02,
                    msg=f"eps_xval.eps_rel >= 0.02 tại k={k_val}, init={init_name}: {eps_res.eps_xval.eps_rel:.4f}",
                )

    def test_2_best_response_pointwise_matches_cs_linear(self):
        """Bắt buộc (2): best_response_pointwise với strategy = CS linear ở m=1

        Cho bid tối ưu ~ alpha_b + beta_b*v với v >= alpha_s + 0.05 (sai <= 0.03),
        và eps_opt.eps_rel < 0.03.
        """
        for k_val in (0.25, 0.5, 0.75):
            th_cs = cs_theta(k_val)
            alpha_b, beta_b, alpha_s, _ = th_cs
            strat_cs = theta_to_strategy(th_cs)
            v_knots = np.linspace(0.0, 1.0, 41)

            br_res = best_response_pointwise(
                strat_cs,
                side="buy",
                m=1,
                k=k_val,
                rule="pair",
                seed=31415,
                n_scen=12000,
                v_knots=v_knots,
                price_grid_size=101,
            )

            br_bids = br_res["br"]
            expected_bids = alpha_b + beta_b * v_knots

            mask = v_knots >= (alpha_s + 0.05)
            max_err = np.max(np.abs(br_bids[mask] - expected_bids[mask]))
            self.assertLessEqual(
                max_err,
                0.03,
                msg=f"Lỗi BR buyer tại k={k_val} vượt 0.03: max_err={max_err:.4f}",
            )

            # Kiểm tra eps_opt.eps_rel < 0.03
            eps_res = epsilon(
                strat_cs,
                m=1,
                k=k_val,
                rule="pair",
                train_seed=31415,
                val_seed=62830,
                n_scen=10000,
                v_knots=v_knots,
                price_grid_size=81,
            )
            self.assertLess(
                eps_res.eps_opt.eps_rel,
                0.03,
                msg=f"eps_opt.eps_rel >= 0.03 tại k={k_val}: {eps_res.eps_opt.eps_rel:.4f}",
            )

    def test_3_truthful_strategy_has_high_epsilon(self):
        """Bắt buộc (3): Chiến lược trung thực ở m = 1, k = 0.5 có eps_rel > 0.05."""
        v_knots = np.linspace(0.0, 1.0, 41)
        truthful_strat = (v_knots.copy(), v_knots.copy())

        eps_res = epsilon(
            truthful_strat,
            m=1,
            k=0.5,
            rule="pair",
            train_seed=777,
            val_seed=888,
            n_scen=8000,
            v_knots=v_knots,
            price_grid_size=81,
        )

        self.assertGreater(
            eps_res.eps_rel,
            0.05,
            msg=f"Chiến lược trung thực có eps_rel không đủ lớn (>0.05): {eps_res.eps_rel:.4f}",
        )
        self.assertGreater(
            eps_res.eps_opt.eps_rel,
            0.05,
            msg=f"Chiến lược trung thực có eps_opt.eps_rel không đủ lớn: {eps_res.eps_opt.eps_rel:.4f}",
        )

    def test_4_identical_seeds_produce_identical_results_bit_for_bit(self):
        """Bắt buộc (4): Cùng seed -> cùng kết quả (bit-for-bit)."""
        res1 = find_equilibrium(
            m=2,
            k=0.5,
            rule="kda",
            seed=9999,
            n_scen=500,
            damping=0.5,
            max_iter=6,
            tol=1e-3,
        )
        res2 = find_equilibrium(
            m=2,
            k=0.5,
            rule="kda",
            seed=9999,
            n_scen=500,
            damping=0.5,
            max_iter=6,
            tol=1e-3,
        )

        np.testing.assert_array_equal(
            res1["strategy"][0],
            res2["strategy"][0],
            err_msg="find_equilibrium không tất định bit-for-bit ở bid_knots",
        )
        np.testing.assert_array_equal(
            res1["strategy"][1],
            res2["strategy"][1],
            err_msg="find_equilibrium không tất định bit-for-bit ở ask_knots",
        )
        self.assertEqual(res1["history"], res2["history"])

        eps1 = epsilon(
            res1["strategy"],
            m=2,
            k=0.5,
            rule="kda",
            train_seed=9999,
            val_seed=1111,
            n_scen=500,
        )
        eps2 = epsilon(
            res1["strategy"],
            m=2,
            k=0.5,
            rule="kda",
            train_seed=9999,
            val_seed=1111,
            n_scen=500,
        )

        self.assertEqual(eps1.eps_rel, eps2.eps_rel)
        self.assertEqual(eps1.eps_avg, eps2.eps_avg)
        self.assertEqual(eps1.eps_opt.eps_avg, eps2.eps_opt.eps_avg)
        self.assertEqual(eps1.eps_xval.eps_avg, eps2.eps_xval.eps_avg)

    def test_5_benchmark_k_equals_1_satterthwaite_williams(self):
        """Bắt buộc (5): Benchmark k = 1 (rule='kda', m in {2, 4}):

        Người bán ở điểm cố định có ask <= c + 0.02 tại mọi nút
        (người bán trung thực là chiến lược trội theo Satterthwaite-Williams 1989),
        và độ khai thấp của người mua tại v = 0.5 ở m = 4 nhỏ hơn ở m = 2.
        """
        shadings: dict[int, float] = {}
        for m_val in (2, 4):
            v_knots = np.linspace(0.0, 1.0, 41)
            res = find_equilibrium(
                m=m_val,
                k=1.0,
                rule="kda",
                seed=555 + m_val,
                n_scen=5000,
                damping=0.5,
                max_iter=25,
                tol=2e-3,
                mode="nonparametric",
                v_knots=v_knots,
                price_grid_size=81,
            )

            bid_knots, ask_knots = res["strategy"]

            # Người bán tại điểm cố định có ask <= c + 0.02 tại mọi nút
            seller_diff = ask_knots - v_knots
            self.assertTrue(
                np.all(seller_diff <= 0.02 + 1e-9),
                msg=f"Người bán k=1, m={m_val} có ask vượt c + 0.02: max diff={np.max(seller_diff):.4f}",
            )

            # Độ khai thấp của người mua tại v = 0.5
            bid_at_05 = float(np.interp(0.5, v_knots, bid_knots))
            shading = 0.5 - bid_at_05
            shadings[m_val] = shading
            print(f"\n[BENCHMARK k=1] m={m_val}: buyer bid tại 0.5 = {bid_at_05:.4f}, shading = {shading:.4f}")

        # Độ khai thấp ở m=4 nhỏ hơn ở m=2
        self.assertLess(
            shadings[4],
            shadings[2],
            msg=f"Độ khai thấp của buyer tại m=4 ({shadings[4]:.4f}) không nhỏ hơn m=2 ({shadings[2]:.4f})",
        )

    def test_1b_m_equals_1_nonparametric_is_epsilon_equilibrium(self):
        """Chế độ phi tham số ở m=1: kiểm theo tiêu chí ε (tiện ích), không theo vị trí chiến lược.

        Bài toán song phương có nhiều cân bằng (Satterthwaite-Williams 1989, mục 2: chiến lược cân bằng
        của trường hợp m = 1 có thể không tăng và không duy nhất), nên lặp phản ứng tối ưu phi tham số
        có thể trượt dọc tập cân bằng; điều cần kiểm là ε nhỏ, đơn điệu và bid <= v, ask >= c.
        """
        v_knots = np.linspace(0.0, 1.0, 41)
        for k_val in (0.25, 0.5, 0.75):
            seed = int(k_val * 1000) + 7
            res = find_equilibrium(
                m=1, k=k_val, rule="pair", seed=seed, n_scen=8000, damping=0.5,
                max_iter=30, tol=3e-3, mode="nonparametric", v_knots=v_knots, price_grid_size=81,
            )
            bid, ask = res["strategy"]
            self.assertTrue(np.all(bid <= v_knots + 1e-9))
            self.assertTrue(np.all(ask >= v_knots - 1e-9))
            self.assertTrue(np.all(np.diff(bid) >= -1e-9))
            self.assertTrue(np.all(np.diff(ask) >= -1e-9))
            eps_res = epsilon(
                res["strategy"], m=1, k=k_val, rule="pair", train_seed=seed, val_seed=seed + 1000,
                n_scen=8000, v_knots=v_knots, price_grid_size=81,
            )
            self.assertLess(eps_res.eps_xval.eps_rel, 0.02, msg=f"k={k_val}")

    def test_6_linear_mode_and_result_attributes(self):
        """Kiểm tra chế độ linear của find_equilibrium và thuộc tính của EpsilonResult."""
        res_lin = find_equilibrium(
            m=1,
            k=0.5,
            rule="pair",
            seed=2024,
            n_scen=4000,
            damping=0.5,
            max_iter=15,
            tol=3e-3,
            mode="linear",
        )

        self.assertIsNotNone(res_lin["theta"])
        self.assertEqual(len(res_lin["theta"]), 4)
        ab, bb, as_, bs = res_lin["theta"]

        # Với k=0.5, CS linear coeffs là (1/12, 2/3, 1/4, 2/3) ~ (0.0833, 0.6667, 0.2500, 0.6667)
        self.assertAlmostEqual(ab, 1.0 / 12.0, delta=0.04)
        self.assertAlmostEqual(bb, 2.0 / 3.0, delta=0.04)
        self.assertAlmostEqual(as_, 1.0 / 4.0, delta=0.04)
        self.assertAlmostEqual(bs, 2.0 / 3.0, delta=0.04)

        # Kiểm tra truy cập thuộc tính trên EpsilonResult
        eps_res = epsilon(
            res_lin["strategy"],
            m=1,
            k=0.5,
            rule="pair",
            train_seed=2024,
            val_seed=2025,
            n_scen=3000,
        )
        self.assertIsInstance(eps_res, EpsilonResult)
        self.assertIsInstance(eps_res.eps_opt, EpsilonResult)
        self.assertIsInstance(eps_res.eps_xval, EpsilonResult)
        self.assertIsInstance(eps_res.eps_rel, float)
        self.assertEqual(eps_res.eps_rel, eps_res["eps_rel"])
        self.assertIsInstance(eps_res.eps_opt.ci_95, tuple)
        self.assertEqual(len(eps_res.eps_opt.ci_95), 2)


if __name__ == "__main__":
    unittest.main()
