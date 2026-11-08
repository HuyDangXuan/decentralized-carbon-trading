"""Unit tests cho runner thực nghiệm (Giai đoạn 2, nhiệm vụ 3).

Kiểm tra runner run_experiment.py theo đúng hợp đồng trong CONTRACT.md.
"""

import csv
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from run_experiment import main, run_experiment_a


class TestRunExperimentA(unittest.TestCase):
    """Bộ kiểm thử cho thí nghiệm A trong run_experiment.py."""

    def test_run_experiment_a_outputs_and_invariants(self):
        """Kiểm tra thí nghiệm A với n=50, runs=2 trong thư mục tạm:

        - Tồn tại 3 file đầu ra (raw, summary, png).
        - Tiêu đề cột đúng thứ tự trong CONTRACT.md.
        - Số dòng raw = số_k * số_n * runs (3 * 1 * 2 = 6).
        - buyer_share của k=0 bằng 1.0 và của k=1 bằng 0.0 (bid trung thực).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir)

            # Chạy qua main với CLI args
            exit_code = main(["a", "--n", "50", "--runs", "2", "--out", str(temp_path)])
            self.assertEqual(exit_code, 0)

            # 1. Kiểm tra tồn tại 3 file đầu ra
            raw_path = temp_path / "exp_a_raw.csv"
            summary_path = temp_path / "exp_a_summary.csv"
            chart_path = temp_path / "exp_a_surplus_split.png"

            self.assertTrue(raw_path.exists(), "exp_a_raw.csv không tồn tại")
            self.assertTrue(summary_path.exists(), "exp_a_summary.csv không tồn tại")
            self.assertTrue(chart_path.exists(), "exp_a_surplus_split.png không tồn tại")
            self.assertGreater(chart_path.stat().st_size, 0, "exp_a_surplus_split.png rỗng")

            # 2. Kiểm tra exp_a_raw.csv
            expected_raw_headers = [
                "k",
                "n",
                "seed",
                "welfare",
                "max_welfare",
                "efficiency",
                "buyer_surplus",
                "seller_surplus",
                "volume",
                "fill_rate",
            ]
            with open(raw_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                raw_rows = list(reader)

            self.assertEqual(raw_rows[0], expected_raw_headers, "Tiêu đề exp_a_raw.csv sai thứ tự")

            # Số dòng dữ liệu = số_k (3: 0, 0.5, 1) * số_n (1: 50) * runs (2) = 6 dòng
            data_rows = raw_rows[1:]
            self.assertEqual(len(data_rows), 6, f"Số dòng raw phải là 6, thực tế: {len(data_rows)}")

            for row in data_rows:
                k_val = float(row[0])
                w = float(row[3])
                mw = float(row[4])
                bs = float(row[6])
                ss = float(row[7])

                # welfare == max_welfare
                self.assertAlmostEqual(w, mw, places=5)
                # buyer_surplus + seller_surplus == welfare
                self.assertAlmostEqual(bs + ss, w, places=5)

                if abs(k_val - 0.0) < 1e-6:
                    self.assertGreater(w, 0.0)
                    buyer_share = bs / w
                    self.assertAlmostEqual(
                        buyer_share,
                        1.0,
                        places=5,
                        msg="buyer_share của k=0 phải bằng 1.0",
                    )
                    self.assertAlmostEqual(ss, 0.0, places=5)
                elif abs(k_val - 1.0) < 1e-6:
                    self.assertGreater(w, 0.0)
                    buyer_share = bs / w
                    self.assertAlmostEqual(
                        buyer_share,
                        0.0,
                        places=5,
                        msg="buyer_share của k=1 phải bằng 0.0",
                    )
                    self.assertAlmostEqual(bs, 0.0, places=5)

            # 3. Kiểm tra exp_a_summary.csv
            expected_summary_headers = [
                "k",
                "n",
                "runs",
                "welfare_mean",
                "welfare_std",
                "buyer_share_mean",
                "buyer_share_std",
                "seller_share_mean",
                "seller_share_std",
                "fill_rate_mean",
            ]
            with open(summary_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                summary_rows = list(reader)

            self.assertEqual(summary_rows[0], expected_summary_headers, "Tiêu đề exp_a_summary.csv sai thứ tự")
            summary_data = summary_rows[1:]
            self.assertEqual(len(summary_data), 3, "Summary phải có 3 dòng (cho k in {0, 0.5, 1})")

            for row in summary_data:
                k_val = float(row[0])
                bs_mean = float(row[5])
                bs_std = float(row[6])
                ss_mean = float(row[7])
                ss_std = float(row[8])

                if abs(k_val - 0.0) < 1e-6:
                    self.assertAlmostEqual(bs_mean, 1.0, places=5, msg="buyer_share_mean của k=0 phải bằng 1.0")
                    self.assertAlmostEqual(bs_std, 0.0, places=5)
                    self.assertAlmostEqual(ss_mean, 0.0, places=5)
                elif abs(k_val - 1.0) < 1e-6:
                    self.assertAlmostEqual(bs_mean, 0.0, places=5, msg="buyer_share_mean của k=1 phải bằng 0.0")
                    self.assertAlmostEqual(bs_std, 0.0, places=5)
                    self.assertAlmostEqual(ss_mean, 1.0, places=5)

    def test_invalid_k_argument_exits_code_2(self):
        """Tham số k sai (k > 1, k < 0, danh sách rỗng) -> argparse lỗi, mã thoát 2."""
        # k = 1.5
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--k", "1.5"])
        self.assertEqual(cm.exception.code, 2)

        # k = -0.1
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--k", "-0.1"])
        self.assertEqual(cm.exception.code, 2)

        # k rỗng
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--k", ""])
        self.assertEqual(cm.exception.code, 2)

    def test_invalid_n_and_runs_arguments_exit_code_2(self):
        """Tham số n < 2, runs < 1, danh sách rỗng -> argparse lỗi, mã thoát 2."""
        # n < 2
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--n", "1"])
        self.assertEqual(cm.exception.code, 2)

        # n rỗng
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--n", ""])
        self.assertEqual(cm.exception.code, 2)

        # runs < 1
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--runs", "0"])
        self.assertEqual(cm.exception.code, 2)

        # runs âm
        with self.assertRaises(SystemExit) as cm:
            main(["a", "--runs", "-5"])
        self.assertEqual(cm.exception.code, 2)

        # Không truyền subcommand hợp lệ
        with self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(cm.exception.code, 2)

        with self.assertRaises(SystemExit) as cm:
            main(["unknown_exp"])
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
