"""Bộ kiểm thử đơn vị cho thực nghiệm C mở rộng (run_experiment_c_multiunit.py).

Tuân thủ hợp đồng anti-A3-multiunit-exp.mission.md, đã sửa sau khi nghiệm thu:
  (a) hàm max_welfare trên 2 ví dụ tay (nêu cách tính trong chú thích), gồm ví dụ nhiều đơn vị.
  (b) chiến lược tuyến tính dựng từ (ab, bb, as, bs), chiến lược tuyến tính từng đoạn và nạp .npz cho đúng giá khai.
  (c) cùng (k, m, rule) cho cùng loss (tất định).
  (d) với chiến lược trung thực (bid = v, ask = c) thì loss = 0 trong sai số làm tròn ticks (<= 1e-5).
  (e) tham số sai -> SystemExit mã 2.
  (f) thiếu file chiến lược in cảnh báo THIẾU ra stderr.
  (g) ghi đúng các cột của hai CSV vào thư mục tạm.
  (h) với max_amount = 1, phúc lợi khớp hàm một đơn vị kda_sim.welfare / max_welfare (oracle độc lập),
      dùng chiến lược không thẳng hàng. Bản đầu ép chiến lược thành đường thẳng từ 3 điểm nên test này bắt được lỗi đó.
Thời gian chạy: <= 20 giây tổng.
"""

import csv
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(_SIM_DIR)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from kda_sim import apply_strategy, max_welfare, welfare
from run_experiment_c_multiunit import (
    build_arg_parser,
    compute_max_welfare,
    evaluate_book,
    linear_strategy,
    load_strategies,
    main,
    run_configuration,
)


def _save_npz(directory: Path, k: float, m: int, rule: str, strategy) -> None:
    v_knots, bid_knots, ask_knots = strategy
    np.savez(
        directory / f"strategy_k{k:g}_m{m}_{rule}.npz",
        v_knots=v_knots, bid_knots=bid_knots, ask_knots=ask_knots, k=k, m=m, rule=rule,
    )


class TestMultiunitExperiment(unittest.TestCase):
    """Kiểm thử toàn diện các chức năng của run_experiment_c_multiunit."""

    def test_max_welfare_hand_examples(self) -> None:
        """Kiểm thử (a): max_welfare trên 2 ví dụ tính tay độc lập."""
        # Ví dụ tay 1: mua B1 (v=12, 10 đơn vị), B2 (v=8, 5); bán S1 (c=6, 7), S2 (c=9, 20).
        #   7 đơn vị B1 ghép S1: 7*(12-6) = 42; 3 đơn vị B1 ghép S2: 3*(12-9) = 9;
        #   B2 (8) < S2 (9) nên dừng. Tổng = 51.
        mw_1 = compute_max_welfare([(12.0, 10), (8.0, 5)], [(6.0, 7), (9.0, 20)])
        self.assertAlmostEqual(mw_1, 51.0, places=6)

        # Ví dụ tay 2: mua (0.9, 3), (0.7, 4), (0.4, 2); bán (0.2, 2), (0.5, 4), (0.8, 5).
        #   2 đơn vị 0.9-0.2: 1.40; 1 đơn vị 0.9-0.5: 0.40; 3 đơn vị 0.7-0.5: 0.60;
        #   0.7 < 0.8 nên dừng. Tổng = 2.40.
        mw_2 = compute_max_welfare([(0.90, 3), (0.70, 4), (0.40, 2)], [(0.20, 2), (0.50, 4), (0.80, 5)])
        self.assertAlmostEqual(mw_2, 2.40, places=6)

    def test_linear_strategy_and_npz_roundtrip(self) -> None:
        """Kiểm thử (b): chiến lược cho đúng giá khai, nội suy từng đoạn không bị ép thành đường thẳng."""
        strat = linear_strategy(0.1, 0.8, 0.2, 0.7)
        v = np.array([0.0, 0.25, 0.5, 1.0])
        # bid = min(v, 0.1 + 0.8 v): 0 -> 0 ; 0.25 -> min(0.25, 0.30) = 0.25 ; 0.5 -> 0.5 ; 1.0 -> 0.9
        bids = apply_strategy(v, strat[1], side="bid", v_knots=strat[0])
        np.testing.assert_allclose(bids, [0.0, 0.25, 0.5, 0.9], atol=1e-12)
        # ask = max(c, 0.2 + 0.7 c): 0 -> 0.2 ; 0.25 -> 0.375 ; 0.5 -> 0.55 ; 1.0 -> max(1.0, 0.9) = 1.0
        asks = apply_strategy(v, strat[2], side="ask", v_knots=strat[0])
        np.testing.assert_allclose(asks, [0.2, 0.375, 0.55, 1.0], atol=1e-12)

        # Ba nút không thẳng hàng: tại 0.25 nội suy giữa (0 -> 0.0) và (0.5 -> 0.3) = 0.15; tại 0.75 giữa 0.3 và 0.9 = 0.6.
        knots_v = np.array([0.0, 0.5, 1.0])
        pw = (knots_v, np.array([0.0, 0.3, 0.9]), np.array([0.1, 0.7, 1.0]))
        out = apply_strategy(np.array([0.25, 0.75]), pw[1], side="bid", v_knots=pw[0])
        np.testing.assert_allclose(out, [0.15, 0.6], atol=1e-12)

        with tempfile.TemporaryDirectory() as tmp_dir:
            _save_npz(Path(tmp_dir), 0.5, 8, "kda", pw)
            loaded = load_strategies(tmp_dir)
            self.assertEqual(list(loaded), [(0.5, 8, "kda")])
            for got, want in zip(loaded[(0.5, 8, "kda")], pw):
                np.testing.assert_array_equal(got, want)

    def test_determinism(self) -> None:
        """Kiểm thử (c): cùng (k, m, rule) cho cùng loss tất định."""
        kwargs = dict(
            k=0.5, m=4, rule="marginal", books=20, max_amount=5,
            strategy=linear_strategy(0.1, 0.8, 0.2, 0.7),
        )
        res1 = run_configuration(**kwargs)
        res2 = run_configuration(**kwargs)
        for key in ("loss", "loss_ci95", "welfare_mean", "max_welfare_mean"):
            self.assertEqual(res1[key], res2[key])

    def test_truthful_strategy_loss_zero(self) -> None:
        """Kiểm thử (d): với chiến lược trung thực (bid = v, ask = c) thì loss <= 1e-5."""
        truthful = linear_strategy(0.0, 1.0, 0.0, 1.0)
        for rule in ("marginal", "pair"):
            res = run_configuration(
                k=0.5, m=8, rule=rule, books=30, max_amount=5, strategy=truthful,
            )
            self.assertLessEqual(res["loss"], 1e-5)

    def test_invalid_cli_arguments_exit_code_2(self) -> None:
        """Kiểm thử (e): tham số sai -> SystemExit mã 2."""
        parser = build_arg_parser()
        invalid_cases = [
            ["--strategies", "x", "--rule", "unknown_rule"],
            ["--strategies", "x", "--m", "-5"],
            ["--strategies", "x", "--k", "2.0"],
            ["--strategies", "x", "--k", "0.0"],
            ["--strategies", "x", "--books", "0"],
            ["--strategies", "x", "--max-amount", "-1"],
            [],  # thiếu --strategies
        ]
        for args in invalid_cases:
            with self.assertRaises(SystemExit) as cm:
                stderr_trap = io.StringIO()
                old_stderr = sys.stderr
                try:
                    sys.stderr = stderr_trap
                    parser.parse_args(args)
                finally:
                    sys.stderr = old_stderr
            self.assertEqual(cm.exception.code, 2)

    def test_missing_config_warning(self) -> None:
        """Kiểm thử (f): thiếu file chiến lược in cảnh báo THIẾU ra stderr."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            _save_npz(tmp_path, 0.5, 16, "marginal", linear_strategy(0.1, 0.8, 0.2, 0.7))

            stderr_trap = io.StringIO()
            old_stderr = sys.stderr
            try:
                sys.stderr = stderr_trap
                ret = main([
                    "--strategies", str(tmp_path),
                    "--m", "16,32",
                    "--rule", "marginal",
                    "--k", "0.5",
                    "--books", "5",
                    "--out", str(tmp_path / "out"),
                ])
            finally:
                sys.stderr = old_stderr

            self.assertEqual(ret, 0)
            stderr_output = stderr_trap.getvalue()
            self.assertIn("THIẾU: (0.5, 32, marginal)", stderr_output)
            self.assertIn("Còn < 2 giá trị m cho (0.5, marginal), không hồi quy", stderr_output)

    def test_csv_output_columns_and_content(self) -> None:
        """Kiểm thử (g): ghi đúng các cột của hai CSV vào thư mục tạm."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            out_dir = tmp_path / "results_out"
            for m_val in (4, 8, 16):
                _save_npz(tmp_path, 0.5, m_val, "marginal", linear_strategy(0.1, 0.8, 0.2, 0.7))

            stdout_trap = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = stdout_trap
                ret = main([
                    "--strategies", str(tmp_path),
                    "--m", "4,8,16",
                    "--rule", "marginal",
                    "--k", "0.5",
                    "--books", "10",
                    "--max-amount", "5",
                    "--out", str(out_dir),
                ])
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 0)

            raw_path = out_dir / "exp_c_multiunit_raw.csv"
            self.assertTrue(raw_path.is_file())
            with open(raw_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                expected_raw_header = [
                    "k", "m", "rule", "books", "max_amount", "loss", "loss_ci95", "welfare_mean", "max_welfare_mean"
                ]
                self.assertEqual(header, expected_raw_header)
                self.assertEqual(len(list(reader)), 3)

            slopes_path = out_dir / "exp_c_multiunit_slopes.csv"
            self.assertTrue(slopes_path.is_file())
            with open(slopes_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header, ["k", "rule", "n_points", "slope", "slope_ci_half", "r2"])
                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][:3], ["0.5", "marginal", "3"])

            self.assertTrue((out_dir / "exp_c_multiunit_loss.png").is_file())

    def test_single_unit_oracle_matches_kda_sim(self) -> None:
        """Kiểm thử (h): max_amount = 1 phải khớp hàm một đơn vị kda_sim (oracle độc lập)."""
        # Chiến lược 4 nút không thẳng hàng, để lộ lỗi nếu bị ép thành đường thẳng.
        knots_v = np.linspace(0.0, 1.0, 4)  # welfare() của kda_sim giả định lưới nút đều
        strat = (knots_v, np.array([0.0, 0.2, 0.5, 0.85]), np.array([0.15, 0.4, 0.7, 1.0]))
        m, n_books = 8, 300
        rng = np.random.default_rng(12345)
        V = rng.uniform(0.0, 1.0, size=(n_books, m))
        C = rng.uniform(0.0, 1.0, size=(n_books, m))
        bid_strat = apply_strategy(V, strat[1], side="bid", v_knots=knots_v)
        self.assertGreater(float(np.max(np.abs(bid_strat - V))), 0.01)  # chiến lược không phải trung thực
        ones = np.ones(m, dtype=int)
        for k_num, k_den in ((1, 2), (1, 1)):
            for rule in ("pair", "marginal", "kda"):
                ref_w = welfare(V, C, (strat[1], strat[2]), k=k_num / k_den, rule=rule)
                ref_mw = max_welfare(V, C)
                w_sum = mw_sum = 0.0
                for i in range(n_books):
                    res = evaluate_book(V[i], ones, C[i], ones, k_num, k_den, rule, strat)
                    if res is None:
                        continue
                    w_sum += res[1]
                    mw_sum += res[2]
                # Cùng 300 sổ lệnh. Tick 1e-6 có thể đổi vài cặp sát giá nên chỉ cho sai số nhỏ.
                self.assertAlmostEqual(w_sum, float(np.sum(ref_w)), delta=2e-3 * float(np.sum(ref_mw)),
                                       msg=f"k={k_num}/{k_den} rule={rule}")
                self.assertAlmostEqual(mw_sum, float(np.sum(ref_mw)), delta=1e-9)


if __name__ == "__main__":
    unittest.main()
