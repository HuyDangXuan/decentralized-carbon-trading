"""Unit tests cho runner thực nghiệm C (Giai đoạn 2, Nhiệm vụ J5).

Tuân thủ hợp đồng anti-missions/contract-c.md (mục J5).
Kiểm tra toàn diện:
  1. Xử lý và kiểm tra hợp lệ tham số CLI (thoát mã 2 khi sai).
  2. Cờ --dry-run chạy mã 0 và không ghi file.
  3. Chạy thực nghiệm thật với tham số nhỏ trong tempdir: tạo đúng CSV, tiêu đề và 1 dòng.
  4. Cờ --resume: bỏ qua cấu hình đã có, không thêm dòng; chạy lại không --resume thoát mã 2.
  5. Hàm hồi quy OLS log-log: độ dốc đúng (-2.0) với c/m^2 và (-1.0) với c/m, báo không đủ điểm khi < 3 điểm.
  6. Tính tất định và độc lập của hạt giống CRC32.
  7. Tính toán tỷ lệ mất hiệu quả và khoảng tin cậy Student-t.
  8. Cảnh báo cố định và docstring theo yêu cầu hợp đồng.
"""

import csv
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zlib

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

import numpy as np

import run_experiment_c
from run_experiment_c import (
    CSV_HEADERS,
    FIXED_WARNING,
    compute_loss_and_ci,
    estimate_runtime_seconds,
    fit_log_log_ols,
    get_seeds,
    main,
    parse_k_list,
    parse_m_list,
    parse_pos_int,
    parse_rule_list,
    plot_loss_scaling,
)


class TestRunExperimentC(unittest.TestCase):
    """Bộ kiểm thử đơn vị cho thực nghiệm C."""

    def test_invalid_cli_arguments_exit_code_2(self):
        """Tham số sai (m < 1, k ngoài (0,1], rule lạ, danh sách rỗng...) -> argparse thoát mã 2."""
        invalid_cases = [
            ["--m", "0"],
            ["--m", "-5"],
            ["--m", "abc"],
            ["--m", ""],
            ["--k", "0"],
            ["--k", "1.5"],
            ["--k", "-0.5"],
            ["--k", "xyz"],
            ["--k", ""],
            ["--rule", "unknown_rule"],
            ["--rule", ""],
            ["--scen", "0"],
            ["--scen", "-100"],
            ["--scen", "abc"],
            ["--eval-scen", "0"],
            ["--eval-scen", "-20"],
            ["--iters", "0"],
            ["--iters", "-1"],
        ]

        for args in invalid_cases:
            with self.subTest(args=args):
                with self.assertRaises(SystemExit) as cm:
                    # Chặn stderr để tránh in thông báo lỗi rác trong lúc test
                    old_stderr = sys.stderr
                    sys.stderr = io.StringIO()
                    try:
                        main(args)
                    finally:
                        sys.stderr = old_stderr
                self.assertEqual(
                    cm.exception.code,
                    2,
                    f"Args {args} phải thoát mã 2, nhận được {cm.exception.code}",
                )

    def test_dry_run_exits_code_0_and_creates_no_files(self):
        """Cờ --dry-run in kế hoạch và thoát mã 0, không tạo bất kỳ file hay thư mục nào."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir) / "output_test_dry_run"
            self.assertFalse(temp_path.exists())

            stdout_buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = stdout_buf
            try:
                code = main(["--dry-run", "--out", str(temp_path)])
            finally:
                sys.stdout = old_stdout

            self.assertEqual(code, 0, "Chế độ dry-run phải trả về mã 0")
            self.assertFalse(
                temp_path.exists(),
                "Thư mục đầu ra không được tạo trong chế độ dry-run",
            )
            output_text = stdout_buf.getvalue()
            self.assertIn("KẾ HOẠCH THỰC NGHIỆM C (DRY RUN)", output_text)
            self.assertIn("Ước lượng thời gian thô", output_text)

    def test_real_run_execution_and_csv_generation(self):
        """Chạy thực nghiệm thật với cấu hình nhỏ trong thư mục tạm:

        --m 2 --k 1 --rule kda --scen 2000 --eval-scen 20000 --iters 4 --out <tempdir>
        Tạo đúng CSV, đúng tiêu đề 20 cột, đúng 1 dòng dữ liệu hợp lệ và biểu đồ PNG.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir)

            stdout_buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = stdout_buf
            try:
                exit_code = main([
                    "--m",
                    "2",
                    "--k",
                    "1",
                    "--rule",
                    "kda",
                    "--scen",
                    "2000",
                    "--eval-scen",
                    "20000",
                    "--iters",
                    "4",
                    "--out",
                    str(temp_path),
                ])
            finally:
                sys.stdout = old_stdout

            self.assertEqual(exit_code, 0, "Lệnh chạy thực nghiệm phải trả về 0")

            # 1. Kiểm tra tồn tại file CSV và PNG
            raw_csv = temp_path / "exp_c_raw.csv"
            chart_png = temp_path / "exp_c_loss.png"

            self.assertTrue(raw_csv.exists(), "exp_c_raw.csv không được tạo")
            self.assertTrue(chart_png.exists(), "exp_c_loss.png không được tạo")
            self.assertGreater(chart_png.stat().st_size, 0, "exp_c_loss.png bị rỗng")

            # 2. Đọc và kiểm tra nội dung CSV
            with open(raw_csv, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                all_rows = list(reader)

            self.assertGreaterEqual(len(all_rows), 2, "CSV phải có ít nhất tiêu đề và 1 dòng")
            header_row = all_rows[0]
            self.assertEqual(header_row, CSV_HEADERS, "Tiêu đề CSV sai hoặc không khớp hợp đồng J5")

            data_rows = all_rows[1:]
            self.assertEqual(len(data_rows), 1, f"Phải có đúng 1 dòng dữ liệu, thực tế: {len(data_rows)}")

            row = data_rows[0]
            self.assertEqual(len(row), len(CSV_HEADERS), "Số lượng cột dữ liệu không khớp tiêu đề")

            k_val = float(row[0])
            m_val = int(row[1])
            rule_val = str(row[2])
            scen_val = int(row[3])
            eval_scen_val = int(row[4])
            converged_str = str(row[5])
            n_iter_val = int(row[6])
            final_delta = float(row[7])
            loss_val = float(row[8])
            loss_ci95_val = float(row[9])
            eps_xval_rel = float(row[10])
            eps_xval_ci95 = float(row[11])
            eps_opt_rel = float(row[12])
            bid_025 = float(row[13])
            bid_050 = float(row[14])
            bid_075 = float(row[15])
            ask_025 = float(row[16])
            ask_050 = float(row[17])
            ask_075 = float(row[18])
            seconds_val = float(row[19])

            self.assertAlmostEqual(k_val, 1.0)
            self.assertEqual(m_val, 2)
            self.assertEqual(rule_val, "kda")
            self.assertEqual(scen_val, 2000)
            self.assertEqual(eval_scen_val, 20000)
            self.assertIn(converged_str, ("True", "False"))
            self.assertLessEqual(n_iter_val, 4)
            self.assertGreaterEqual(final_delta, 0.0)

            # Tổn thất hiệu quả loss nằm trong [0, 1]
            self.assertGreaterEqual(loss_val, 0.0)
            self.assertLessEqual(loss_val, 1.0)
            self.assertGreaterEqual(loss_ci95_val, 0.0)

            # Epsilon metrics
            self.assertGreaterEqual(eps_opt_rel, 0.0)
            self.assertGreaterEqual(eps_xval_ci95, 0.0)

            # Ràng buộc chiến lược: bid <= v và ask >= c
            self.assertLessEqual(bid_025, 0.25 + 1e-6)
            self.assertLessEqual(bid_050, 0.50 + 1e-6)
            self.assertLessEqual(bid_075, 0.75 + 1e-6)
            self.assertGreaterEqual(ask_025, 0.25 - 1e-6)
            self.assertGreaterEqual(ask_050, 0.50 - 1e-6)
            self.assertGreaterEqual(ask_075, 0.75 - 1e-6)

            self.assertGreater(seconds_val, 0.0)

    def test_resume_mode_and_rerun_without_resume(self):
        """Kiểm tra hành vi của --resume và phát hiện trùng lặp file:

        - Chạy lần đầu tạo 1 dòng.
        - Chạy lại với --resume: bỏ qua cấu hình đã có, không thêm dòng mới.
        - Chạy lại không --resume: báo lỗi và thoát mã 2.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir)

            base_args = [
                "--m",
                "2",
                "--k",
                "1",
                "--rule",
                "kda",
                "--scen",
                "2000",
                "--eval-scen",
                "20000",
                "--iters",
                "4",
                "--out",
                str(temp_path),
            ]

            # Lần 1: Chạy tạo 1 dòng
            code1 = main(base_args)
            self.assertEqual(code1, 0)

            raw_csv = temp_path / "exp_c_raw.csv"
            with open(raw_csv, mode="r", encoding="utf-8") as f:
                rows_after_run1 = list(csv.reader(f))
            self.assertEqual(len(rows_after_run1), 2)  # 1 header + 1 data

            # Lần 2: Chạy lại với --resume -> không thêm dòng
            code2 = main(base_args + ["--resume"])
            self.assertEqual(code2, 0)

            with open(raw_csv, mode="r", encoding="utf-8") as f:
                rows_after_run2 = list(csv.reader(f))
            self.assertEqual(
                len(rows_after_run2),
                2,
                "Chạy lại với --resume không được thêm dòng mới cho cấu hình đã có",
            )

            # Lần 3: Chạy lại KHÔNG --resume -> thoát mã 2
            with self.assertRaises(SystemExit) as cm:
                old_stderr = sys.stderr
                sys.stderr = io.StringIO()
                try:
                    main(base_args)
                finally:
                    sys.stderr = old_stderr

            self.assertEqual(
                cm.exception.code,
                2,
                "Chạy lại khi file CSV đã tồn tại mà không có cờ --resume phải thoát mã 2",
            )

    def test_fit_log_log_ols_slopes(self):
        """Hàm hồi quy OLS log-log trả đúng độ dốc -2.0 cho c/m^2 và -1.0 cho c/m."""
        m_vals = [4, 8, 16, 32, 64]

        # 1. Kiểm tra mô hình c / m^2
        c2 = 5.0
        loss_vals_m2 = [c2 / (m ** 2) for m in m_vals]
        res_m2 = fit_log_log_ols(m_vals, loss_vals_m2)

        self.assertIsNotNone(res_m2["slope"])
        self.assertAlmostEqual(res_m2["slope"], -2.0, places=5)
        self.assertAlmostEqual(res_m2["r_squared"], 1.0, places=5)
        self.assertAlmostEqual(res_m2["se"], 0.0, places=5)
        self.assertAlmostEqual(res_m2["ci_half"], 0.0, places=5)
        self.assertEqual(res_m2["df"], 3)  # N - 2 = 5 - 2 = 3

        # 2. Kiểm tra mô hình c / m
        c1 = 3.2
        loss_vals_m1 = [c1 / m for m in m_vals]
        res_m1 = fit_log_log_ols(m_vals, loss_vals_m1)

        self.assertIsNotNone(res_m1["slope"])
        self.assertAlmostEqual(res_m1["slope"], -1.0, places=5)
        self.assertAlmostEqual(res_m1["r_squared"], 1.0, places=5)
        self.assertAlmostEqual(res_m1["se"], 0.0, places=5)
        self.assertAlmostEqual(res_m1["ci_half"], 0.0, places=5)

        # 3. Kiểm tra trường hợp thiếu điểm (< 3 điểm)
        res_insufficient = fit_log_log_ols([4, 8], [0.1, 0.05])
        self.assertIsNone(res_insufficient["slope"])
        self.assertEqual(res_insufficient["msg"], "không đủ điểm")

    def test_crc32_seed_independence_and_determinism(self):
        """Hạt giống CRC32 tất định và độc lập giữa 3 tập (train, val, eval) cũng như các cấu hình."""
        t1, v1, e1 = get_seeds(2, 0.5, "pair")
        t2, v2, e2 = get_seeds(2, 0.5, "pair")

        # Tính tất định
        self.assertEqual((t1, v1, e1), (t2, v2, e2))

        # Tính độc lập giữa train, val, eval
        self.assertNotEqual(t1, v1)
        self.assertNotEqual(t1, e1)
        self.assertNotEqual(v1, e1)

        # Độc lập giữa các tham số m, k, rule
        t_m4, _, _ = get_seeds(4, 0.5, "pair")
        t_k1, _, _ = get_seeds(2, 1.0, "pair")
        t_kda, _, _ = get_seeds(2, 0.5, "kda")

        self.assertNotEqual(t1, t_m4)
        self.assertNotEqual(t1, t_k1)
        self.assertNotEqual(t1, t_kda)

    def test_compute_loss_and_ci_logic(self):
        """Kiểm tra hàm tính loss và khoảng tin cậy 95% qua chia khối."""
        rng = np.random.default_rng(12345)
        n_scen = 1000
        # welfare < max_welfare
        mw = rng.uniform(5.0, 10.0, size=n_scen)
        w = mw * 0.95  # efficiency ~ 0.95, loss ~ 0.05

        eff, loss, ci95 = compute_loss_and_ci(w, mw, num_blocks=10)
        self.assertAlmostEqual(eff, 0.95, places=5)
        self.assertAlmostEqual(loss, 0.05, places=5)
        self.assertAlmostEqual(ci95, 0.0, places=5)  # vì tỷ lệ không đổi giữa các khối

        # Thử trường hợp có biến thiên giữa các khối
        w_noisy = w.copy()
        w_noisy[:100] *= 0.90
        eff2, loss2, ci95_2 = compute_loss_and_ci(w_noisy, mw, num_blocks=10)
        self.assertGreater(loss2, 0.0)
        self.assertGreater(ci95_2, 0.0)

    def test_fixed_warning_and_docstring(self):
        """Docstring đầu file và cảnh báo in ra phải tuân thủ đúng nội dung hợp đồng J5."""
        self.assertIn("lớp lệch là một người, từng điểm", FIXED_WARNING)
        self.assertIn("eps là cận dưới của eps thật", FIXED_WARNING)
        self.assertIn("không phải chứng minh cân bằng", FIXED_WARNING)
        self.assertIn("marginal không phải quy tắc k-double auction", FIXED_WARNING)
        self.assertIn("mẫu độc lập giữa các m nhưng loss ở m lớn có sai số lớn", FIXED_WARNING)

        # Kiểm tra docstring của run_experiment_c
        doc = (run_experiment_c.__doc__ or "").lower()  # không phân biệt hoa thường: docstring viết hoa chữ đầu câu
        self.assertIn("lớp lệch là một người, từng điểm", doc)
        self.assertIn("eps là cận dưới của eps thật", doc)


if __name__ == "__main__":
    unittest.main()
