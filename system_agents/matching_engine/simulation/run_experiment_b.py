"""Bộ chạy thực nghiệm đấu giá kép B (Giai đoạn 2, nhiệm vụ 3).

Thí nghiệm B: Khai giá chiến lược (Strategic Bidding).
- b1: Mỏ neo giải tích (1 mua - 1 bán, cân bằng Chatterjee-Samuelson).
- b2: Quét cường độ khai giá lambda với nhiều lệnh.

Giới hạn:
Hệ số CS_NUMERIC là xấp xỉ cho thị trường 1 mua – 1 bán, một đơn vị; áp dụng
cho nhiều lệnh nhiều đơn vị chỉ là heuristic. lam là tham số quét, không phải
cân bằng của thị trường nhiều lệnh. Cân bằng của k-double auction không duy nhất.
"""

import argparse
import csv
import os
from pathlib import Path
import random
import statistics
import sys
from typing import Any

# Đảm bảo UTF-8 trên Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Đảm bảo đường dẫn import
_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from generator import generate_valued  # noqa: E402
from metrics import (  # noqa: E402
    buyer_surplus,
    fill_rate,
    max_welfare,
    run_auction,
    seller_surplus,
    volume,
    welfare,
)
from model import OrderType, Valued, snap  # noqa: E402
from strategies import CS_K05, CS_NUMERIC, HIGH, LOW, linear_price_fn  # noqa: E402


def parse_trials(value: str) -> int:
    """Parse và kiểm tra số lần thử trials từ chuỗi CLI.

    Ràng buộc: trials >= 1.
    """
    try:
        val = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"trials phải là số nguyên, nhận được '{value}'")
    if val < 1:
        raise argparse.ArgumentTypeError(f"trials phải >= 1, nhận được {val}")
    return val


def parse_seed(value: str) -> int:
    """Parse seed từ chuỗi CLI."""
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"seed phải là số nguyên, nhận được '{value}'")


def parse_k_list_b2(value: str) -> list[float]:
    """Parse và kiểm tra danh sách k từ chuỗi CLI cho thí nghiệm B2.

    Ràng buộc: không rỗng, mỗi k phải có trong CS_NUMERIC (0.25, 0.5, 0.75).
    """
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Danh sách k không được rỗng.")
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("Danh sách k không được rỗng.")

    k_list: list[float] = []
    for p in parts:
        try:
            val = float(p)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Giá trị k không hợp lệ: '{p}'")
        if val not in CS_NUMERIC:
            raise argparse.ArgumentTypeError(
                f"k phải thuộc các giá trị hỗ trợ trong CS_NUMERIC "
                f"{list(CS_NUMERIC.keys())}, nhận được {val}"
            )
        k_list.append(val)
    return k_list


def parse_n_list(value: str) -> list[int]:
    """Parse và kiểm tra danh sách n từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi n >= 2.
    """
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Danh sách n không được rỗng.")
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("Danh sách n không được rỗng.")

    n_list: list[int] = []
    for p in parts:
        try:
            val = int(p)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Giá trị n không hợp lệ: '{p}'")
        if val < 2:
            raise argparse.ArgumentTypeError(f"n phải >= 2, nhận được {val}")
        n_list.append(val)
    return n_list


def parse_lam_list(value: str) -> list[float]:
    """Parse và kiểm tra danh sách lam từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi lam thuộc [0.0, 1.0].
    """
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Danh sách lam không được rỗng.")
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("Danh sách lam không được rỗng.")

    lam_list: list[float] = []
    for p in parts:
        try:
            val = float(p)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Giá trị lam không hợp lệ: '{p}'")
        if val < 0.0 or val > 1.0:
            raise argparse.ArgumentTypeError(f"lam phải thuộc [0, 1], nhận được {val}")
        lam_list.append(val)
    return lam_list


def parse_runs(value: str) -> int:
    """Parse và kiểm tra số lần lặp runs từ chuỗi CLI.

    Ràng buộc: runs >= 1.
    """
    try:
        val = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"runs phải là số nguyên, nhận được '{value}'")
    if val < 1:
        raise argparse.ArgumentTypeError(f"runs phải >= 1, nhận được {val}")
    return val


def build_arg_parser() -> argparse.ArgumentParser:
    """Xây dựng parser dòng lệnh cho thí nghiệm B."""
    parser = argparse.ArgumentParser(
        description="Bộ chạy thực nghiệm đấu giá kép B (Giai đoạn 2, nhiệm vụ 3)."
    )
    subparsers = parser.add_subparsers(dest="experiment", required=True)

    # Subcommand b1
    parser_b1 = subparsers.add_parser(
        "b1",
        help="Thí nghiệm B1: mỏ neo giải tích (1 mua – 1 bán, Chatterjee-Samuelson)",
    )
    parser_b1.add_argument(
        "--trials",
        type=parse_trials,
        default=20000,
        help="Số lần thử nghiệm (mặc định: 20000)",
    )
    parser_b1.add_argument(
        "--seed",
        type=parse_seed,
        default=0,
        help="Seed ngẫu nhiên (mặc định: 0)",
    )

    # Subcommand b2
    parser_b2 = subparsers.add_parser(
        "b2",
        help="Thí nghiệm B2: quét cường độ khai giá lam với nhiều lệnh",
    )
    parser_b2.add_argument(
        "--n",
        type=parse_n_list,
        default=[100, 200, 500],
        help="Danh sách quy mô n, phân cách bằng dấu phẩy (mặc định: 100,200,500)",
    )
    parser_b2.add_argument(
        "--k",
        type=parse_k_list_b2,
        default=[0.25, 0.5, 0.75],
        help="Danh sách hệ số k, phân cách bằng dấu phẩy (mặc định: 0.25,0.5,0.75)",
    )
    parser_b2.add_argument(
        "--lam",
        type=parse_lam_list,
        default=[0.0, 0.25, 0.5, 0.75, 1.0],
        help="Danh sách lam, phân cách bằng dấu phẩy (mặc định: 0,0.25,0.5,0.75,1)",
    )
    parser_b2.add_argument(
        "--runs",
        type=parse_runs,
        default=20,
        help="Số lần chạy cho mỗi cấu hình (mặc định: 20)",
    )
    parser_b2.add_argument(
        "--out",
        type=str,
        default="results",
        help="Thư mục xuất kết quả (tương đối so với script, mặc định: results)",
    )

    return parser


def calc_mean_std(values: list[float]) -> tuple[float, float]:
    """Tính trung bình mẫu và độ lệch chuẩn mẫu (n-1). 1 mẫu thì std = 0.0."""
    if not values:
        return 0.0, 0.0
    mean_val = statistics.mean(values)
    if len(values) <= 1:
        std_val = 0.0
    else:
        std_val = statistics.stdev(values)
    return round(float(mean_val), 6), round(float(std_val), 6)


def run_b1(trials: int = 20000, seed: int = 0) -> tuple[float, float]:
    """Chạy mô phỏng b1 (1 mua – 1 bán, Chatterjee-Samuelson).

    Args:
        trials: Số lần thử (mặc định: 20000).
        seed: Seed cho bộ sinh số ngẫu nhiên (mặc định: 0).

    Returns:
        tuple (trade_freq, efficiency)
    """
    rng = random.Random(seed)
    price_fn = linear_price_fn(CS_K05, lam=1.0, low=LOW, high=HIGH)

    trade_count = 0
    sum_welfare = 0.0
    sum_max_welfare = 0.0

    for _ in range(trials):
        v_b = snap(rng.uniform(LOW, HIGH))
        v_s = snap(rng.uniform(LOW, HIGH))
        bid = Valued(order_id="B0", side=OrderType.BID, amount=1, valuation=v_b, arrival=0)
        ask = Valued(order_id="S0", side=OrderType.ASK, amount=1, valuation=v_s, arrival=1)
        valued = [bid, ask]

        matches = run_auction(valued, k=0.5, price_fn=price_fn)
        w = welfare(matches, valued)
        mw = max_welfare(valued)

        if len(matches) > 0:
            trade_count += 1
        sum_welfare += w
        sum_max_welfare += mw

    trade_freq = trade_count / trials
    efficiency = (sum_welfare / sum_max_welfare) if sum_max_welfare > 0 else 1.0

    return trade_freq, efficiency


def run_experiment_b1(trials: int = 20000, seed: int = 0) -> int:
    """Chạy thí nghiệm B1 (mỏ neo giải tích 1 mua – 1 bán).

    Returns:
        0 nếu sai số so với lý thuyết <= 0.02, ngược lại trả về 1.
    """
    trade_freq, efficiency = run_b1(trials=trials, seed=seed)

    theor_freq = 9 / 32  # 0.28125
    theor_eff = 27 / 32  # 0.84375

    diff_freq = abs(trade_freq - theor_freq)
    diff_eff = abs(efficiency - theor_eff)

    print(f"KẾT QUẢ THÍ NGHIỆM B1 (trials={trials}, seed={seed}):")
    print(
        f"  Tần suất giao dịch thực nghiệm : {trade_freq:.5f} "
        f"(Lý thuyết: {theor_freq:.5f}, Lệch: {diff_freq:.5f})"
    )
    print(
        f"  Hiệu quả thị trường (efficiency): {efficiency:.5f} "
        f"(Lý thuyết: {theor_eff:.5f}, Lệch: {diff_eff:.5f})"
    )

    if diff_freq > 0.02 or diff_eff > 0.02:
        sys.stderr.write(
            f"LỖI: Kết quả b1 lệch quá 0.02 so với lý thuyết: "
            f"diff_freq={diff_freq:.5f}, diff_eff={diff_eff:.5f}\n"
        )
        return 1

    print("Kiểm tra mỏ neo giải tích B1: OK (sai số <= 0.02)")
    return 0


def plot_b2_efficiency(
    summary_rows: list[dict[str, Any]],
    k_list: list[float],
    n_list: list[int],
    lam_list: list[float],
    out_file: Path,
) -> None:
    """Vẽ đồ thị hiệu quả theo lam: một ô con cho mỗi k, mỗi n một đường kèm errorbar."""
    num_k = len(k_list)
    fig, axes = plt.subplots(
        1,
        num_k,
        figsize=(5 * num_k, 5),
        squeeze=False,
        sharey=True,
    )

    summary_map = {(r["k"], r["n"], r["lam"]): r for r in summary_rows}

    for idx, k_val in enumerate(k_list):
        ax = axes[0, idx]
        for n_val in n_list:
            x_vals = []
            y_vals = []
            y_errs = []
            for lam_val in lam_list:
                row = summary_map.get((k_val, n_val, lam_val))
                if row:
                    x_vals.append(lam_val)
                    y_vals.append(row["efficiency_mean"])
                    y_errs.append(row["efficiency_std"])

            ax.errorbar(
                x_vals,
                y_vals,
                yerr=y_errs,
                marker="o",
                capsize=3,
                label=f"n = {n_val}",
            )

        ax.set_title(f"k = {k_val}")
        ax.set_xlabel("Cường độ khai giá (λ)")
        ax.set_xticks(lam_list)
        ax.grid(True, linestyle="--", alpha=0.6)
        if idx == 0:
            ax.set_ylabel("Hiệu quả trung bình (Efficiency)")
        ax.legend()

    fig.suptitle("Hiệu quả thị trường theo cường độ khai giá (Thí nghiệm B2)", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close(fig)


def print_b2_summary_table(summary_rows: list[dict[str, Any]]) -> None:
    """In bảng tóm tắt kết quả căn thẳng các cột ra stdout."""
    headers = [
        "k",
        "n",
        "lam",
        "runs",
        "eff_mean",
        "eff_std",
        "fill_mean",
        "fill_std",
        "b_share_mean",
        "b_share_std",
    ]
    formatted_rows: list[list[str]] = []
    for r in summary_rows:
        formatted_rows.append([
            str(r["k"]),
            str(r["n"]),
            str(r["lam"]),
            str(r["runs"]),
            f"{r['efficiency_mean']:.6f}",
            f"{r['efficiency_std']:.6f}",
            f"{r['fill_rate_mean']:.6f}",
            f"{r['fill_rate_std']:.6f}",
            f"{r['buyer_share_mean']:.6f}",
            f"{r['buyer_share_std']:.6f}",
        ])

    col_widths = [len(h) for h in headers]
    for row in formatted_rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(val))

    sep = "  ".join("-" * w for w in col_widths)
    header_str = "  ".join(h.rjust(col_widths[idx]) for idx, h in enumerate(headers))

    print("\nBẢNG TÓM TẮT KẾT QUẢ THÍ NGHIỆM B2:")
    print(header_str)
    print(sep)
    for row in formatted_rows:
        row_str = "  ".join(val.rjust(col_widths[idx]) for idx, val in enumerate(row))
        print(row_str)
    print(sep)


def run_experiment_b2(
    n_list: list[int],
    k_list: list[float],
    lam_list: list[float],
    runs: int,
    out_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Thực thi toàn bộ thí nghiệm B2 và ghi 3 file kết quả:

    - exp_b2_raw.csv
    - exp_b2_summary.csv
    - exp_b2_efficiency.png
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_rows: list[dict[str, Any]] = []

    for k_val in k_list:
        for n_val in n_list:
            for lam_val in lam_list:
                for seed_val in range(runs):
                    valued = generate_valued(n_val, seed=seed_val)
                    mw = max_welfare(valued)
                    price_fn = linear_price_fn(CS_NUMERIC[k_val], lam=lam_val)
                    matches = run_auction(valued, k=k_val, price_fn=price_fn)

                    w = welfare(matches, valued)
                    bs = buyer_surplus(matches, valued)
                    vol = volume(matches)
                    fr = fill_rate(matches, valued)
                    eff = round(w / mw, 6) if mw > 0 else 1.0

                    # Kiểm tra bắt buộc: lam = 0 phải cho efficiency == 1.0 (sai số 1e-9)
                    if abs(lam_val - 0.0) < 1e-9:
                        if abs(eff - 1.0) > 1e-9:
                            sys.stderr.write(
                                f"LỖI: lam = 0 nhưng efficiency = {eff} != 1.0 "
                                f"tại k={k_val}, n={n_val}, seed={seed_val}\n"
                            )
                            sys.exit(1)

                    # buyer_share = buyer_surplus / welfare, welfare = 0 -> để trống
                    if w > 1e-6:
                        buyer_share_str = f"{round(bs / w, 6):.6f}"
                    else:
                        buyer_share_str = ""

                    record = {
                        "k": k_val,
                        "n": n_val,
                        "lam": lam_val,
                        "seed": seed_val,
                        "welfare": w,
                        "max_welfare": mw,
                        "efficiency": eff,
                        "volume": vol,
                        "fill_rate": fr,
                        "buyer_share": buyer_share_str,
                        "_raw_bs": bs,
                        "_raw_w": w,
                    }
                    raw_rows.append(record)

    print("Kiểm tra bắt buộc lam=0 (efficiency == 1.0): OK")

    # Ghi file 1: exp_b2_raw.csv
    raw_csv_path = out_dir / "exp_b2_raw.csv"
    raw_fieldnames = [
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
    with open(raw_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=raw_fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in raw_rows:
            writer.writerow(r)

    # Tính summary rows
    summary_rows: list[dict[str, Any]] = []
    summary_fieldnames = [
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

    for k_val in k_list:
        for n_val in n_list:
            for lam_val in lam_list:
                group = [
                    r
                    for r in raw_rows
                    if r["k"] == k_val and r["n"] == n_val and r["lam"] == lam_val
                ]
                effs = [float(r["efficiency"]) for r in group]
                frs = [float(r["fill_rate"]) for r in group]
                eff_mean, eff_std = calc_mean_std(effs)
                fr_mean, fr_std = calc_mean_std(frs)

                bs_vals = [r["_raw_bs"] / r["_raw_w"] for r in group if r["_raw_w"] > 1e-6]
                bs_mean, bs_std = calc_mean_std(bs_vals)

                summary_rows.append({
                    "k": k_val,
                    "n": n_val,
                    "lam": lam_val,
                    "runs": runs,
                    "efficiency_mean": eff_mean,
                    "efficiency_std": eff_std,
                    "fill_rate_mean": fr_mean,
                    "fill_rate_std": fr_std,
                    "buyer_share_mean": bs_mean,
                    "buyer_share_std": bs_std,
                })

    # Ghi file 2: exp_b2_summary.csv
    summary_csv_path = out_dir / "exp_b2_summary.csv"
    with open(summary_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
        writer.writeheader()
        for s in summary_rows:
            writer.writerow(s)

    # Ghi file 3: exp_b2_efficiency.png
    chart_path = out_dir / "exp_b2_efficiency.png"
    plot_b2_efficiency(summary_rows, k_list, n_list, lam_list, chart_path)

    # In bảng tóm tắt
    print_b2_summary_table(summary_rows)

    return raw_rows, summary_rows


def main(argv: list[str] | None = None) -> int:
    """Hàm main thực thi script."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.experiment == "b1":
        return run_experiment_b1(trials=args.trials, seed=args.seed)
    elif args.experiment == "b2":
        out_raw = Path(args.out)
        if not out_raw.is_absolute():
            out_dir = Path(_SIM_DIR) / out_raw
        else:
            out_dir = out_raw

        run_experiment_b2(
            n_list=args.n,
            k_list=args.k,
            lam_list=args.lam,
            runs=args.runs,
            out_dir=out_dir,
        )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
