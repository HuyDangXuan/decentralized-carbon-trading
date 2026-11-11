"""Unit tests cho chiến lược khai giá và thí nghiệm B (Giai đoạn 2, nhiệm vụ 3).

Tuân thủ tiêu chí chấp nhận trong hợp đồng (CONTRACT.md):
1. lam = 0 cho đúng valuation (trung thực).
2. BID <= valuation, ASK >= valuation với 1000 valuation ngẫu nhiên và lam in {0.25, 0.5, 1}.
3. Đơn điệu theo lam.
4. lam ngoài [0, 1] -> ValueError.
5. b1 với trials=20000 cho tần suất giao dịch trong 0.28125 ± 0.02 và efficiency trong 0.84375 ± 0.02.
6. b2 với n=50, runs=2 trong thư mục tempfile tạo đủ 3 file đầu ra và số dòng raw = số_k × số_n × số_lam × runs.
"""

import csv
import os
from pathlib import Path
import random
import sys
import tempfile
import unittest

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from model import OrderType, Valued, snap  # noqa: E402
from run_experiment_b import (  # noqa: E402
    main,
    run_b1,
    run_experiment_b1,
    run_experiment_b2,
)
from strategies import (  # noqa: E402
    CS_K05,
    CS_NUMERIC,
    HIGH,
    LOW,
    linear_price_fn,
)


class TestStrategies(unittest.TestCase):
    """Kiểm thử cho module strategies.py và các bất biến chiến lược khai giá."""

    def test_lam_zero_is_truthful(self):
        """Tiêu chí 1: lam = 0 trung thực (trả về đúng valuation với mọi lệnh)."""
        test_valuations = [5.0, 7.5, 10.0, 12.5, 15.0]
        all_coeffs = [CS_K05] + list(CS_NUMERIC.values())

        for coeffs in all_coeffs:
            price_fn = linear_price_fn(coeffs, lam=0.0)
            for val in test_valuations:
                bid = Valued(
                    order_id="B",
                    side=OrderType.BID,
                    amount=1,
                    valuation=val,
                    arrival=0,
                )
                ask = Valued(
                    order_id="S",
                    side=OrderType.ASK,
                    amount=1,
                    valuation=val,
                    arrival=1,
                )
                self.assertEqual(price_fn(bid), val)
                self.assertEqual(price_fn(ask), val)

    def test_bid_and_ask_bounds_with_1000_random_valuations(self):
        """Tiêu chí 2: BID <= valuation, ASK >= valuation với 1000 valuation ngẫu nhiên

        và lam in {0.25, 0.5, 1}.
        """
        rng = random.Random(42)
        random_valuations = [snap(rng.uniform(LOW, HIGH)) for _ in range(1000)]
        target_lams = [0.25, 0.5, 1.0]
        target_k = [0.25, 0.5, 0.75]

        for val in random_valuations:
            bid = Valued(
                order_id="B",
                side=OrderType.BID,
                amount=1,
                valuation=val,
                arrival=0,
            )
            ask = Valued(
                order_id="S",
                side=OrderType.ASK,
                amount=1,
                valuation=val,
                arrival=1,
            )

            for k in target_k:
                coeffs = CS_NUMERIC[k]
                for lam in target_lams:
                    price_fn = linear_price_fn(coeffs, lam=lam)
                    bid_price = price_fn(bid)
                    ask_price = price_fn(ask)

                    self.assertLessEqual(
                        bid_price,
                        val,
                        msg=f"BID vi phạm: {bid_price} > {val} (k={k}, lam={lam})",
                    )
                    self.assertGreaterEqual(
                        ask_price,
                        val,
                        msg=f"ASK vi phạm: {ask_price} < {val} (k={k}, lam={lam})",
                    )

    def test_monotonicity_in_lam(self):
        """Tiêu chí 3: Đơn điệu theo lam.

        Khi lam tăng: BID không tăng (khai giảm dần hoặc bằng), ASK không giảm (khai tăng dần hoặc bằng).
        """
        rng = random.Random(100)
        test_valuations = [snap(rng.uniform(LOW, HIGH)) for _ in range(200)]
        lam_values = [0.0, 0.25, 0.5, 0.75, 1.0]

        for k, coeffs in CS_NUMERIC.items():
            for val in test_valuations:
                bid = Valued(
                    order_id="B",
                    side=OrderType.BID,
                    amount=1,
                    valuation=val,
                    arrival=0,
                )
                ask = Valued(
                    order_id="S",
                    side=OrderType.ASK,
                    amount=1,
                    valuation=val,
                    arrival=1,
                )

                bid_prices = [linear_price_fn(coeffs, lam=l)(bid) for l in lam_values]
                ask_prices = [linear_price_fn(coeffs, lam=l)(ask) for l in lam_values]

                # BID đơn điệu giảm theo lam
                for i in range(len(bid_prices) - 1):
                    self.assertGreaterEqual(
                        bid_prices[i],
                        bid_prices[i + 1] - 1e-9,
                        msg=f"BID không đơn điệu giảm tại k={k}, val={val}: {bid_prices}",
                    )

                # ASK đơn điệu tăng theo lam
                for i in range(len(ask_prices) - 1):
                    self.assertLessEqual(
                        ask_prices[i],
                        ask_prices[i + 1] + 1e-9,
                        msg=f"ASK không đơn điệu tăng tại k={k}, val={val}: {ask_prices}",
                    )

    def test_invalid_lam_raises_value_error(self):
        """Tiêu chí 4: lam ngoài [0, 1] -> ValueError."""
        invalid_lams = [-0.01, 1.01, -1.0, 2.0, float("nan")]
        for lam in invalid_lams:
            with self.assertRaises(ValueError, msg=f"Không báo lỗi với lam={lam}"):
                linear_price_fn(CS_K05, lam=lam)

        # Kiểm tra thêm low >= high
        with self.assertRaises(ValueError):
            linear_price_fn(CS_K05, lam=0.5, low=15.0, high=5.0)

        # Kiểm tra k không hợp lệ
        with self.assertRaises(ValueError):
            linear_price_fn(0.99, lam=0.5)


class TestRunExperimentB(unittest.TestCase):
    """Kiểm thử cho module run_experiment_b.py (b1 và b2)."""

    def test_experiment_b1_analytical_anchor(self):
        """Tiêu chí 5: b1 với trials=20000 cho tần suất giao dịch trong 0.28125 ± 0.02

        và efficiency trong 0.84375 ± 0.02.
        """
        trade_freq, eff = run_b1(trials=20000, seed=0)
        self.assertAlmostEqual(
            trade_freq,
            0.28125,
            delta=0.02,
            msg=f"Tần suất giao dịch b1 ({trade_freq}) lệch quá 0.02 so với 0.28125",
        )
        self.assertAlmostEqual(
            eff,
            0.84375,
            delta=0.02,
            msg=f"Hiệu quả b1 ({eff}) lệch quá 0.02 so với 0.84375",
        )
        code = run_experiment_b1(trials=20000, seed=0)
        self.assertEqual(code, 0, "run_experiment_b1 thất bại hoặc sai số > 0.02")

    def test_experiment_b2_temporary_directory_outputs(self):
        """Tiêu chí 6: b2 với n=50, runs=2 trong thư mục tempfile tạo đủ 3 file đầu ra

        và số dòng raw = số_k × số_n × số_lam × runs.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_path = Path(tmp_dir)

            # Chạy qua main với CLI args: n=50, runs=2 (dùng k và lam mặc định: k có 3, lam có 5)
            exit_code = main(["b2", "--n", "50", "--runs", "2", "--out", str(temp_path)])
            self.assertEqual(exit_code, 0)

            # 1. Kiểm tra tồn tại đủ 3 file đầu ra
            raw_path = temp_path / "exp_b2_raw.csv"
            summary_path = temp_path / "exp_b2_summary.csv"
            chart_path = temp_path / "exp_b2_efficiency.png"

            self.assertTrue(raw_path.exists(), "exp_b2_raw.csv không tồn tại")
            self.assertTrue(summary_path.exists(), "exp_b2_summary.csv không tồn tại")
            self.assertTrue(chart_path.exists(), "exp_b2_efficiency.png không tồn tại")
            self.assertGreater(chart_path.stat().st_size, 0, "exp_b2_efficiency.png rỗng")

            # 2. Kiểm tra exp_b2_raw.csv
            expected_raw_headers = [
                "k",
                "n",
                "lam",
                "seed",
                "welfare",
                "max_welfare",
                "efficiency",
                "volume",
                "fill_rate",
                "buyer_share",
            ]
            with open(raw_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                raw_rows = list(reader)

            self.assertEqual(raw_rows[0], expected_raw_headers, "Tiêu đề exp_b2_raw.csv sai thứ tự")

            # Số dòng raw = số_k (3) * số_n (1) * số_lam (5) * runs (2) = 30 dòng dữ liệu
            data_rows = raw_rows[1:]
            expected_count = 3 * 1 * 5 * 2
            self.assertEqual(
                len(data_rows),
                expected_count,
                f"Số dòng raw phải là {expected_count}, thực tế: {len(data_rows)}",
            )

            # Kiểm tra bất biến lam = 0 có efficiency == 1.0
            for row in data_rows:
                lam_val = float(row[2])
                eff_val = float(row[6])
                if abs(lam_val - 0.0) < 1e-9:
                    self.assertAlmostEqual(
                        eff_val,
                        1.0,
                        places=6,
                        msg=f"lam=0 phải có efficiency=1.0, nhận được {eff_val}",
                    )

            # 3. Kiểm tra exp_b2_summary.csv
            expected_summary_headers = [
                "k",
                "n",
                "lam",
                "runs",
                "efficiency_mean",
                "efficiency_std",
                "fill_rate_mean",
                "fill_rate_std",
                "buyer_share_mean",
                "buyer_share_std",
            ]
            with open(summary_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                summary_rows = list(reader)

            self.assertEqual(
                summary_rows[0],
                expected_summary_headers,
                "Tiêu đề exp_b2_summary.csv sai thứ tự",
            )
            # Số dòng summary = số_k (3) * số_n (1) * số_lam (5) = 15 dòng dữ liệu
            summary_data = summary_rows[1:]
            self.assertEqual(len(summary_data), 15)

    def test_cli_argument_errors_exit_code_2(self):
        """Kiểm tra các trường hợp tham số CLI không hợp lệ dẫn đến exit code 2."""
        # Không truyền subcommand
        with self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(cm.exception.code, 2)

        # Subcommand sai
        with self.assertRaises(SystemExit) as cm:
            main(["c"])
        self.assertEqual(cm.exception.code, 2)

        # b1: trials < 1
        with self.assertRaises(SystemExit) as cm:
            main(["b1", "--trials", "0"])
        self.assertEqual(cm.exception.code, 2)

        # b2: k không có trong CS_NUMERIC
        with self.assertRaises(SystemExit) as cm:
            main(["b2", "--k", "0.1"])
        self.assertEqual(cm.exception.code, 2)

        # b2: lam ngoài [0, 1]
        with self.assertRaises(SystemExit) as cm:
            main(["b2", "--lam", "1.5"])
        self.assertEqual(cm.exception.code, 2)

        # b2: n < 2
        with self.assertRaises(SystemExit) as cm:
            main(["b2", "--n", "1"])
        self.assertEqual(cm.exception.code, 2)

        # b2: runs < 1
        with self.assertRaises(SystemExit) as cm:
            main(["b2", "--runs", "0"])
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
