"""Bộ chạy thực nghiệm đấu giá kép (Giai đoạn 2, nhiệm vụ 3).

Thí nghiệm A: Khai giá trung thực, chia thặng dư theo hệ số k.
Tuân thủ đầy đủ hợp đồng tại CONTRACT.md.
"""

import argparse
import csv
import os
from pathlib import Path
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


def parse_k_list(value: str) -> list[float]:
    """Parse và kiểm tra danh sách k từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi k thuộc [0.0, 1.0].
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
        if not (0.0 <= val <= 1.0):
            raise argparse.ArgumentTypeError(f"k phải thuộc [0, 1], nhận được {val}")
        k_list.append(val)
    if len(set(k_list)) != len(k_list):
        raise argparse.ArgumentTypeError("Danh sách k có giá trị trùng nhau.")
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
    if len(set(n_list)) != len(n_list):
        raise argparse.ArgumentTypeError("Danh sách n có giá trị trùng nhau.")
    return n_list


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
    """Xây dựng parser dòng lệnh cho runner thực nghiệm."""
    parser = argparse.ArgumentParser(
        description="Bộ chạy thực nghiệm mô phỏng đấu giá kép (Giai đoạn 2, nhiệm vụ 3)."
    )
    subparsers = parser.add_subparsers(dest="experiment", required=True)

    parser_a = subparsers.add_parser(
        "a",
        help="Thí nghiệm A: khai giá trung thực, chia thặng dư theo k",
    )
    parser_a.add_argument(
        "--n",
        type=parse_n_list,
        default=[100, 200, 500],
        help="Danh sách quy mô thị trường n, phân cách bằng dấu phẩy (mặc định: 100,200,500)",
    )
    parser_a.add_argument(
        "--k",
        type=parse_k_list,
        default=[0.0, 0.5, 1.0],
        help="Danh sách hệ số k, phân cách bằng dấu phẩy (mặc định: 0,0.5,1)",
    )
    parser_a.add_argument(
        "--runs",
        type=parse_runs,
        default=30,
        help="Số lần chạy ngẫu nhiên cho mỗi cấu hình (mặc định: 30)",
    )
    parser_a.add_argument(
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


def plot_surplus_split(
    summary_rows: list[dict[str, Any]],
    k_list: list[float],
    n_list: list[int],
    out_file: Path,
) -> None:
    """Vẽ biểu đồ cột nhóm theo k, mỗi n một cột, chiều cao = buyer_share_mean +- std."""
    summary_map = {(row["k"], row["n"]): row for row in summary_rows}

    fig, ax = plt.subplots(figsize=(8, 6))

    num_k = len(k_list)
    num_n = len(n_list)

    total_width = 0.8
    bar_width = total_width / max(num_n, 1)

    for j, n_val in enumerate(n_list):
        x_positions = []
        heights = []
        errors = []

        for i, k_val in enumerate(k_list):
            pos = i - (total_width / 2.0) + (j + 0.5) * bar_width
            x_positions.append(pos)
            row = summary_map.get((k_val, n_val), {})
            heights.append(row.get("buyer_share_mean", 0.0))
            errors.append(row.get("buyer_share_std", 0.0))

        ax.bar(
            x_positions,
            heights,
            width=bar_width,
            yerr=errors,
            capsize=4,
            label=f"n = {n_val}",
        )

    ax.set_xticks(range(num_k))
    ax.set_xticklabels([f"k = {k}" for k in k_list])
    ax.set_xlabel("Hệ số k (Quy tắc định giá)")
    ax.set_ylabel("Tỷ phần thặng dư người mua (Buyer Share)")
    ax.set_title("Phân chia thặng dư theo hệ số k (Thí nghiệm A)")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(title="Quy mô thị trường (n)")

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close(fig)


def print_summary_table(summary_rows: list[dict[str, Any]]) -> None:
    """In bảng tóm tắt kết quả căn thẳng các cột ra stdout."""
    headers = [
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
    formatted_rows: list[list[str]] = []
    for r in summary_rows:
        formatted_rows.append([
            str(r["k"]),
            str(r["n"]),
            str(r["runs"]),
            f"{r['welfare_mean']:.6f}",
            f"{r['welfare_std']:.6f}",
            f"{r['buyer_share_mean']:.6f}",
            f"{r['buyer_share_std']:.6f}",
            f"{r['seller_share_mean']:.6f}",
            f"{r['seller_share_std']:.6f}",
            f"{r['fill_rate_mean']:.6f}",
        ])

    col_widths = [len(h) for h in headers]
    for row in formatted_rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(val))

    sep = "  ".join("-" * w for w in col_widths)
    header_str = "  ".join(h.rjust(col_widths[idx]) for idx, h in enumerate(headers))

    print("\nBẢNG TÓM TẮT KẾT QUẢ THÍ NGHIỆM A:")
    print(header_str)
    print(sep)
    for row in formatted_rows:
        row_str = "  ".join(val.rjust(col_widths[idx]) for idx, val in enumerate(row))
        print(row_str)
    print(sep)


def run_experiment_a(
    n_list: list[int],
    k_list: list[float],
    runs: int,
    out_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Thực thi toàn bộ thí nghiệm A và ghi 3 file kết quả.

    Returns:
        tuple (raw_rows, summary_rows)
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_rows: list[dict[str, Any]] = []

    # Cấu trúc lưu tạm để kiểm tra bất biến welfare theo (n, seed)
    # key: (n, seed) -> dict[k, dict_of_metrics]
    sim_by_config: dict[tuple[int, int], dict[float, dict[str, Any]]] = {}

    for n_val in n_list:
        for seed_val in range(runs):
            valued = generate_valued(n_val, seed=seed_val)
            mw = max_welfare(valued)

            config_key = (n_val, seed_val)
            sim_by_config[config_key] = {}

            for k_val in k_list:
                matches = run_auction(valued, k=k_val)
                w = welfare(matches, valued)
                bs = buyer_surplus(matches, valued)
                ss = seller_surplus(matches, valued)
                vol = volume(matches)
                fr = fill_rate(matches, valued)
                eff = round(w / mw, 6) if mw > 0 else 1.0

                record = {
                    "k": k_val,
                    "n": n_val,
                    "seed": seed_val,
                    "welfare": w,
                    "max_welfare": mw,
                    "efficiency": eff,
                    "buyer_surplus": bs,
                    "seller_surplus": ss,
                    "volume": vol,
                    "fill_rate": fr,
                }
                raw_rows.append(record)
                sim_by_config[config_key][k_val] = record

    # Kiểm tra bắt buộc: với mỗi (n, seed), welfare bằng nhau giữa các k (sai số 1e-6) và bằng max_welfare
    for (n_val, seed_val), results_by_k in sim_by_config.items():
        base_k = k_list[0]
        base_mw = results_by_k[base_k]["max_welfare"]
        base_w = results_by_k[base_k]["welfare"]

        for k_val in k_list:
            cur_w = results_by_k[k_val]["welfare"]
            if abs(cur_w - base_mw) > 1e-6:
                sys.stderr.write(
                    f"LỖI: welfare đổi theo k tại n={n_val}, seed={seed_val}: "
                    f"k={k_val} có welfare={cur_w} khác max_welfare={base_mw}\n"
                )
                sys.exit(1)
            if abs(cur_w - base_w) > 1e-6:
                sys.stderr.write(
                    f"LỖI: welfare đổi theo k tại n={n_val}, seed={seed_val}: "
                    f"k={k_val} có welfare={cur_w} khác k={base_k} có welfare={base_w}\n"
                )
                sys.exit(1)

    total_configs = len(n_list) * runs
    print(f"Kiểm tra bất biến welfare theo k: OK ({total_configs} cấu hình)")

    # Sắp xếp raw_rows theo (k, n, seed) để dữ liệu có trật tự nhất quán
    raw_rows.sort(key=lambda r: (r["k"], r["n"], r["seed"]))

    # Ghi file 1: exp_a_raw.csv
    raw_csv_path = out_dir / "exp_a_raw.csv"
    raw_fieldnames = [
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
    with open(raw_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=raw_fieldnames)
        writer.writeheader()
        for r in raw_rows:
            writer.writerow(r)

    # Tính toán summary
    summary_rows: list[dict[str, Any]] = []
    summary_fieldnames = [
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

    for k_val in k_list:
        for n_val in n_list:
            group = [r for r in raw_rows if r["k"] == k_val and r["n"] == n_val]
            welfares = [r["welfare"] for r in group]
            fill_rates = [r["fill_rate"] for r in group]

            w_mean, w_std = calc_mean_std(welfares)
            fr_mean = round(float(statistics.mean(fill_rates)), 6) if fill_rates else 0.0

            # buyer_share = buyer_surplus / welfare (welfare == 0 thì bỏ qua lần chạy đó)
            buyer_shares: list[float] = []
            seller_shares: list[float] = []
            for r in group:
                if r["welfare"] > 1e-6:
                    buyer_shares.append(r["buyer_surplus"] / r["welfare"])
                    seller_shares.append(r["seller_surplus"] / r["welfare"])

            bs_mean, bs_std = calc_mean_std(buyer_shares)
            ss_mean, ss_std = calc_mean_std(seller_shares)

            summary_record = {
                "k": k_val,
                "n": n_val,
                "runs": runs,
                "welfare_mean": w_mean,
                "welfare_std": w_std,
                "buyer_share_mean": bs_mean,
                "buyer_share_std": bs_std,
                "seller_share_mean": ss_mean,
                "seller_share_std": ss_std,
                "fill_rate_mean": fr_mean,
            }
            summary_rows.append(summary_record)

    # Ghi file 2: exp_a_summary.csv
    summary_csv_path = out_dir / "exp_a_summary.csv"
    with open(summary_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
        writer.writeheader()
        for s in summary_rows:
            writer.writerow(s)

    # Ghi file 3: exp_a_surplus_split.png
    chart_path = out_dir / "exp_a_surplus_split.png"
    plot_surplus_split(summary_rows, k_list, n_list, chart_path)

    # In bảng tóm tắt ra stdout
    print_summary_table(summary_rows)

    return raw_rows, summary_rows


def main(argv: list[str] | None = None) -> int:
    """Hàm main thực thi script."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.experiment == "a":
        out_raw = Path(args.out)
        if not out_raw.is_absolute():
            out_dir = Path(_SIM_DIR) / out_raw
        else:
            out_dir = out_raw

        run_experiment_a(
            n_list=args.n,
            k_list=args.k,
            runs=args.runs,
            out_dir=out_dir,
        )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
