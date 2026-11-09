"""Bộ chạy thực nghiệm C: Cân bằng xấp xỉ và tốc độ mất hiệu quả theo m (Giai đoạn 2, Nhiệm vụ J5).

Tuân thủ hợp đồng anti-missions/contract-c.md (mục J5).
Script tìm cân bằng xấp xỉ (approximate equilibrium) bằng phương pháp lặp co (damping),
đo khoảng cách cân bằng ε (epsilon) qua cross-validation (eps_xval) và tối ưu hóa trực tiếp (eps_opt),
đo tỷ lệ mất hiệu quả (loss = 1 - efficiency) và tốc độ suy giảm theo quy mô thị trường m (log-log OLS).

CẢNH BÁO VÀ GIỚI HẠN:
Lớp lệch là một người, từng điểm; eps là cận dưới của eps thật;
không phải chứng minh cân bằng; marginal không phải quy tắc k-double auction
của tài liệu gốc; mẫu độc lập giữa các m nhưng loss ở m lớn có sai số lớn.
"""

import argparse
import csv
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Sequence
import zlib

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
import numpy as np  # noqa: E402

from equilibrium_search import (  # noqa: E402
    epsilon,
    find_equilibrium,
)
from kda_sim import (  # noqa: E402
    apply_strategy,
    draw_scenarios,
    max_welfare,
    welfare,
)

CSV_HEADERS: list[str] = [
    "k",
    "m",
    "rule",
    "scen",
    "eval_scen",
    "converged",
    "n_iter",
    "final_delta",
    "loss",
    "loss_ci95",
    "eps_xval_rel",
    "eps_xval_ci95",
    "eps_opt_rel",
    "bid_at_025",
    "bid_at_050",
    "bid_at_075",
    "ask_at_025",
    "ask_at_050",
    "ask_at_075",
    "seconds",
]

# Bảng giá trị tới hạn Student-t hai phía mức ý nghĩa 0.05 (độ tin cậy 95%) cho bậc tự do df
T_CRIT_95: dict[int, float] = {
    1: 12.7062,
    2: 4.3027,
    3: 3.1824,
    4: 2.7764,
    5: 2.5706,
    6: 2.4469,
    7: 2.3646,
    8: 2.3060,
    9: 2.2622,
    10: 2.2281,
    11: 2.2010,
    12: 2.1788,
    13: 2.1604,
    14: 2.1448,
    15: 2.1314,
    16: 2.1199,
    17: 2.1098,
    18: 2.1009,
    19: 2.0930,
    20: 2.0860,
    25: 2.0595,
    30: 2.0423,
}

FIXED_WARNING: str = (
    "lớp lệch là một người, từng điểm; eps là cận dưới của eps thật; "
    "không phải chứng minh cân bằng; marginal không phải quy tắc k-double auction "
    "của tài liệu gốc; mẫu độc lập giữa các m nhưng loss ở m lớn có sai số lớn."
)


def parse_m_list(value: str) -> list[int]:
    """Parse và kiểm tra danh sách m từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi m >= 1.
    """
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Danh sách m không được rỗng.")
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("Danh sách m không được rỗng.")

    m_list: list[int] = []
    for p in parts:
        try:
            val = int(p)
        except ValueError:
            raise argparse.ArgumentTypeError(f"m phải là số nguyên, nhận được '{p}'")
        if val < 1:
            raise argparse.ArgumentTypeError(f"m phải >= 1, nhận được {val}")
        m_list.append(val)
    return m_list


def parse_k_list(value: str) -> list[float]:
    """Parse và kiểm tra danh sách k từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi k thuộc khoảng (0, 1].
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
            raise argparse.ArgumentTypeError(f"k phải là số thực, nhận được '{p}'")
        if val <= 0.0 or val > 1.0:
            raise argparse.ArgumentTypeError(f"k phải thuộc khoảng (0, 1], nhận được {val}")
        k_list.append(val)
    return k_list


def parse_rule_list(value: str) -> list[str]:
    """Parse và kiểm tra danh sách rule từ chuỗi CLI.

    Ràng buộc: không rỗng, mỗi rule thuộc {'pair', 'marginal', 'kda'}.
    """
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Danh sách rule không được rỗng.")
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("Danh sách rule không được rỗng.")

    allowed_rules = {"pair", "marginal", "kda"}
    rule_list: list[str] = []
    for p in parts:
        r = p.lower()
        if r not in allowed_rules:
            raise argparse.ArgumentTypeError(
                f"rule không hợp lệ: '{p}'. Phải là một trong {sorted(allowed_rules)}"
            )
        rule_list.append(r)
    return rule_list


def parse_pos_int(value: str) -> int:
    """Parse số nguyên dương (>= 1)."""
    try:
        val = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Giá trị phải là số nguyên, nhận được '{value}'")
    if val < 1:
        raise argparse.ArgumentTypeError(f"Giá trị phải >= 1, nhận được {val}")
    return val


def get_seeds(m: int, k: float, rule: str) -> tuple[int, int, int]:
    """Sinh 3 hạt giống độc lập (train, val, eval) qua zlib.crc32.

    KHÔNG dùng hash() theo yêu cầu hợp đồng J5.

    Returns:
        tuple (train_seed, val_seed, eval_seed).
    """
    train_seed = zlib.crc32(f"{m}|{k}|{rule}|train".encode("utf-8"))
    val_seed = zlib.crc32(f"{m}|{k}|{rule}|val".encode("utf-8"))
    eval_seed = zlib.crc32(f"{m}|{k}|{rule}|eval".encode("utf-8"))
    return train_seed, val_seed, eval_seed


def compute_loss_and_ci(
    w_eval: np.ndarray,
    mw_eval: np.ndarray,
    num_blocks: int = 10,
) -> tuple[float, float, float]:
    """Tính tỷ lệ mất hiệu quả loss = 1 - efficiency và khoảng tin cậy 95% bằng chia khối.

    Args:
        w_eval: Mảng welfare thực tế theo từng kịch bản (hình dạng (n_scen,)).
        mw_eval: Mảng max_welfare tối đa khả thi theo từng kịch bản.
        num_blocks: Số khối chia kịch bản (tối thiểu 10).

    Returns:
        tuple (efficiency, loss, loss_ci95) với:
          - efficiency: Tỷ lệ tổng thặng dư đạt được sum(w) / sum(mw).
          - loss: 1 - efficiency.
          - loss_ci95: Bán độ rộng khoảng tin cậy 95% theo Student-t (t_crit * SE).
    """
    sum_w = float(np.sum(w_eval))
    sum_mw = float(np.sum(mw_eval))
    efficiency = sum_w / sum_mw if sum_mw > 0 else 0.0
    loss = 1.0 - efficiency

    n_scen = len(w_eval)
    K = max(num_blocks, 10)
    block_size = n_scen // K
    if block_size < 1:
        return efficiency, loss, 0.0

    block_losses: list[float] = []
    for b in range(K):
        s_idx = b * block_size
        e_idx = (b + 1) * block_size if b < K - 1 else n_scen
        w_b = float(np.sum(w_eval[s_idx:e_idx]))
        mw_b = float(np.sum(mw_eval[s_idx:e_idx]))
        eff_b = w_b / mw_b if mw_b > 0 else 0.0
        block_losses.append(1.0 - eff_b)

    loss_std = float(np.std(block_losses, ddof=1)) if len(block_losses) > 1 else 0.0
    loss_se = loss_std / np.sqrt(K)
    df = K - 1
    t_crit = T_CRIT_95.get(df, 1.96)
    loss_ci95 = float(t_crit * loss_se)

    return efficiency, loss, loss_ci95


def fit_log_log_ols(
    m_vals: Sequence[int],
    loss_vals: Sequence[float],
) -> dict[str, Any]:
    """Hồi quy OLS mô hình log-log: log(loss) = alpha + beta * log(m).

    Args:
        m_vals: Danh sách quy mô thị trường m (m >= 1).
        loss_vals: Danh sách giá trị tổn thất hiệu quả loss (loss > 0).

    Returns:
        dict chứa:
          "slope": Độ dốc beta (hoặc None nếu không đủ điểm).
          "intercept": Hệ số tự do alpha.
          "se": Sai số chuẩn của độ dốc beta.
          "ci_low": Cận dưới khoảng tin cậy 95% của beta.
          "ci_high": Cận trên khoảng tin cậy 95% của beta.
          "ci_half": Bán độ rộng CI 95% = t_crit * se.
          "r_squared": Hệ số xác định R².
          "df": Bậc tự do (N - 2).
          "msg": Thông báo trạng thái (e.g. "thành công" hoặc "không đủ điểm").
    """
    N = len(m_vals)
    if N < 3:
        return {
            "slope": None,
            "intercept": None,
            "se": None,
            "ci_low": None,
            "ci_high": None,
            "ci_half": None,
            "r_squared": None,
            "df": max(0, N - 2),
            "msg": "không đủ điểm",
        }

    x = np.log(np.asarray(m_vals, dtype=float))
    # Tránh log(0) bằng cách kẹp dưới ở 1e-15
    y = np.log(np.maximum(np.asarray(loss_vals, dtype=float), 1e-15))

    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))

    ss_xx = float(np.sum((x - x_mean) ** 2))
    ss_xy = float(np.sum((x - x_mean) * (y - y_mean)))
    ss_yy = float(np.sum((y - y_mean) ** 2))

    if ss_xx < 1e-12:
        return {
            "slope": None,
            "intercept": None,
            "se": None,
            "ci_low": None,
            "ci_high": None,
            "ci_half": None,
            "r_squared": None,
            "df": N - 2,
            "msg": "không đủ biến thiên m",
        }

    beta = ss_xy / ss_xx
    alpha = y_mean - beta * x_mean

    residuals = y - (alpha + beta * x)
    ssr = float(np.sum(residuals ** 2))
    df = N - 2
    s2 = ssr / df if df > 0 else 0.0
    se = float(np.sqrt(s2 / ss_xx)) if s2 > 0 and ss_xx > 0 else 0.0

    r2 = (ss_xy ** 2) / (ss_xx * ss_yy) if (ss_xx * ss_yy) > 0 else 1.0

    t_crit = T_CRIT_95.get(df, 1.96)
    ci_half = t_crit * se
    ci_low = beta - ci_half
    ci_high = beta + ci_half

    return {
        "slope": float(beta),
        "intercept": float(alpha),
        "se": se,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "ci_half": float(ci_half),
        "r_squared": float(r2),
        "df": df,
        "msg": "thành công",
    }


def estimate_runtime_seconds(
    m_list: list[int],
    k_list: list[float],
    rule_list: list[str],
    scen: int,
    eval_scen: int,
    iters: int,
) -> float:
    """Ước lượng thô thời gian chạy thực nghiệm tính bằng giây."""
    total_sec = 0.0
    for m in m_list:
        for _ in k_list:
            for _ in rule_list:
                # Hiệu chỉnh theo lần đo thật (09/11/2026, máy của Phi): với scen = 40000 và 40 vòng,
                # m = 2, 4, 6, 16 mất khoảng 136, 144, 200, 424 giây. Mỗi vòng gọi hai lần
                # deviator_outcome (mua và bán) trên lưới 81 giá.
                t_train = iters * 2.0 * (scen / 20000.0) * (0.8 + 0.12 * m) * 0.85
                # epsilon: bốn lần deviator_outcome cộng khối tin cậy, khoảng 3 vòng lặp.
                t_eps = 3.0 * 2.0 * (scen / 20000.0) * (0.8 + 0.12 * m) * 0.85
                # đánh giá hiệu quả: chỉ tính welfare, rất rẻ.
                t_eval = (0.008 + 0.001 * m) * (eval_scen / 10000.0)
                total_sec += (t_train + t_eps + t_eval)
    return total_sec


def print_summary_table(rows: list[dict[str, Any]]) -> None:
    """In bảng tóm tắt kết quả căn thẳng các cột ra stdout."""
    headers = [
        "k",
        "m",
        "rule",
        "scen",
        "eval_scen",
        "conv",
        "iter",
        "delta",
        "loss",
        "loss_ci95",
        "eps_xval_rel",
        "eps_opt_rel",
        "time(s)",
    ]

    formatted_rows: list[list[str]] = []
    for r in rows:
        formatted_rows.append([
            f"{float(r['k']):.2f}",
            str(r["m"]),
            str(r["rule"]),
            str(r["scen"]),
            str(r["eval_scen"]),
            str(r["converged"]),
            str(r["n_iter"]),
            f"{float(r['final_delta']):.6f}",
            f"{float(r['loss']):.6f}",
            f"{float(r['loss_ci95']):.6f}",
            f"{float(r['eps_xval_rel']):.6f}",
            f"{float(r['eps_opt_rel']):.6f}",
            f"{float(r['seconds']):.1f}",
        ])

    col_widths = [len(h) for h in headers]
    for r in formatted_rows:
        for idx, val in enumerate(r):
            col_widths[idx] = max(col_widths[idx], len(val))

    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "  ".join("-" * col_widths[i] for i in range(len(headers)))

    print("\n" + "=" * len(header_line))
    print("BẢNG TÓM TẮT THỰC NGHIỆM C: CÂN BẰNG VÀ TỐN THẤT HIỆU QUẢ")
    print("=" * len(header_line))
    print(header_line)
    print(separator)
    for r in formatted_rows:
        print("  ".join(val.ljust(col_widths[i]) for i, val in enumerate(r)))
    print("=" * len(header_line))


def plot_loss_scaling(rows: list[dict[str, Any]], out_file: Path) -> None:
    """Vẽ biểu đồ log-log tổn thất hiệu quả theo quy mô thị trường m và lưu ra file."""
    if not rows:
        return

    # Nhóm theo (k, rule)
    groups: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for r in rows:
        key = (float(r["k"]), str(r["rule"]))
        groups.setdefault(key, []).append(r)

    fig, ax = plt.subplots(figsize=(8.5, 6.0))
    ax.set_xscale("log")
    ax.set_yscale("log")

    all_m: list[int] = []
    first_curve_m0: float | None = None
    first_curve_loss0: float | None = None

    for (k_val, rule_val), group_items in sorted(groups.items()):
        sorted_items = sorted(group_items, key=lambda x: int(x["m"]))
        m_arr = np.array([int(x["m"]) for x in sorted_items], dtype=float)
        loss_arr = np.array([float(x["loss"]) for x in sorted_items], dtype=float)
        ci_arr = np.array([float(x["loss_ci95"]) for x in sorted_items], dtype=float)

        all_m.extend(int(x["m"]) for x in sorted_items)

        if first_curve_m0 is None and len(m_arr) > 0 and loss_arr[0] > 0:
            first_curve_m0 = float(m_arr[0])
            first_curve_loss0 = float(loss_arr[0])

        ax.errorbar(
            m_arr,
            loss_arr,
            yerr=ci_arr,
            marker="o",
            capsize=3,
            label=f"k={k_val:g}, rule={rule_val}",
        )

    # Thêm hai đường tham chiếu 1/m và 1/m^2 dịch khớp điểm đầu của đường đầu tiên
    if first_curve_m0 is not None and first_curve_loss0 is not None and all_m:
        min_m = min(all_m)
        max_m = max(all_m)
        if min_m == max_m:
            m_grid = np.array([min_m * 0.8, max_m * 1.2])
        else:
            m_grid = np.geomspace(min_m, max_m, 100)

        y_ref_1 = first_curve_loss0 * (first_curve_m0 / m_grid)
        y_ref_2 = first_curve_loss0 * ((first_curve_m0 / m_grid) ** 2)

        ax.plot(
            m_grid,
            y_ref_1,
            linestyle="--",
            color="gray",
            alpha=0.8,
            label=r"Tham chiếu $1/m$ ($O(1/m)$)",
        )
        ax.plot(
            m_grid,
            y_ref_2,
            linestyle=":",
            color="black",
            alpha=0.8,
            label=r"Tham chiếu $1/m^2$ ($O(1/m^2)$)",
        )

    ax.set_xlabel("Số lượng người tham gia mỗi bên (m)")
    ax.set_ylabel("Mức tổn thất hiệu quả (Loss = 1 - Efficiency)")
    ax.set_title("Tốc độ suy giảm tổn thất hiệu quả theo quy mô thị trường m (Log-Log)")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend()

    fig.tight_layout()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    plt.close(fig)


def build_arg_parser() -> argparse.ArgumentParser:
    """Xây dựng parser dòng lệnh cho thực nghiệm C."""
    parser = argparse.ArgumentParser(
        description="Bộ chạy thực nghiệm C: Cân bằng xấp xỉ và tốc độ mất hiệu quả theo m."
    )
    parser.add_argument(
        "--m",
        type=parse_m_list,
        default=[2, 4, 8, 16],
        help="Danh sách quy mô thị trường m, phân cách bằng dấu phẩy (mặc định: 2,4,8,16)",
    )
    parser.add_argument(
        "--k",
        type=parse_k_list,
        default=[0.5, 1.0],
        help="Danh sách hệ số k, phân cách bằng dấu phẩy (mặc định: 0.5,1)",
    )
    parser.add_argument(
        "--rule",
        type=parse_rule_list,
        default=["pair", "marginal", "kda"],
        help="Danh sách quy tắc giá, phân cách bằng dấu phẩy (mặc định: pair,marginal,kda)",
    )
    parser.add_argument(
        "--scen",
        type=parse_pos_int,
        default=40000,
        help="Số kịch bản huấn luyện tìm cân bằng (mặc định: 40000)",
    )
    parser.add_argument(
        "--eval-scen",
        type=parse_pos_int,
        default=400000,
        help="Số kịch bản kiểm định đánh giá hiệu quả (mặc định: 400000)",
    )
    parser.add_argument(
        "--iters",
        type=parse_pos_int,
        default=40,
        help="Số vòng lặp tối đa tìm cân bằng (mặc định: 40)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results",
        help="Thư mục xuất kết quả (mặc định: results)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help="Tiếp tục chạy và bỏ qua các cấu hình đã có trong CSV",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="In kế hoạch thực nghiệm và ước lượng thời gian rồi thoát mà không tính gì",
    )
    return parser


def run_experiment_c(args: argparse.Namespace) -> int:
    """Thực thi toàn bộ quy trình thực nghiệm C."""
    m_list: list[int] = sorted(list(dict.fromkeys(args.m)))
    k_list: list[float] = list(dict.fromkeys(args.k))
    rule_list: list[str] = list(dict.fromkeys(args.rule))
    scen: int = args.scen
    eval_scen: int = args.eval_scen
    iters: int = args.iters
    out_dir = Path(args.out)
    resume: bool = args.resume
    dry_run: bool = args.dry_run

    total_configs = len(m_list) * len(k_list) * len(rule_list)
    est_sec = estimate_runtime_seconds(m_list, k_list, rule_list, scen, eval_scen, iters)

    if dry_run:
        print("=" * 80)
        print("KẾ HOẠCH THỰC NGHIỆM C (DRY RUN)")
        print("=" * 80)
        print(f"Danh sách m: {m_list}")
        print(f"Danh sách k: {k_list}")
        print(f"Danh sách rule: {rule_list}")
        print(f"Số kịch bản huấn luyện (scen): {scen}")
        print(f"Số kịch bản kiểm định (eval-scen): {eval_scen}")
        print(f"Số vòng lặp tối đa (iters): {iters}")
        print(f"Thư mục xuất kết quả (out): {out_dir}")
        print(f"Chế độ resume: {resume}")
        print("-" * 80)
        print(f"Tổng số cấu hình: {total_configs}")
        print(f"Ước lượng thời gian thô: ~{est_sec:.1f} giây (~{est_sec / 60.0:.1f} phút)")
        print(
            "Ghi chú: Đây là ước lượng thời gian thô dựa trên số vòng lặp và quy mô kịch bản;\n"
            "thời gian thực tế phụ thuộc phần cứng và tốc độ hội tụ của từng cấu hình."
        )
        print("=" * 80)
        return 0

    raw_csv_path = out_dir / "exp_c_raw.csv"
    existing_configs: set[tuple[float, int, str]] = set()
    all_rows: list[dict[str, Any]] = []

    if raw_csv_path.exists():
        if not resume:
            sys.stderr.write(
                f"LỖI: File kết quả '{raw_csv_path}' đã tồn tại.\n"
                f"Sử dụng cờ --resume để tiếp tục chạy hoặc chỉ định thư mục khác qua --out.\n"
            )
            raise SystemExit(2)

        # Đọc các cấu hình đã có trong file CSV
        with open(raw_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    k_c = float(r["k"])
                    m_c = int(r["m"])
                    rule_c = str(r["rule"])
                    existing_configs.add((k_c, m_c, rule_c))
                    all_rows.append(r)
                except (KeyError, ValueError):
                    continue
        print(f"Đã phát hiện {len(existing_configs)} cấu hình đã chạy trong {raw_csv_path}.")

    out_dir.mkdir(parents=True, exist_ok=True)
    need_header = not raw_csv_path.exists() or raw_csv_path.stat().st_size == 0

    csv_file = open(raw_csv_path, mode="a", encoding="utf-8", newline="")
    csv_writer = csv.writer(csv_file)
    if need_header:
        csv_writer.writerow(CSV_HEADERS)
        csv_file.flush()

    try:
        # Chạy theo thứ tự m tăng dần
        configs = [(m, k, rule) for m in m_list for k in k_list for rule in rule_list]
        for cfg_idx, (m, k, rule) in enumerate(configs, 1):
            if (float(k), int(m), str(rule)) in existing_configs:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{cfg_idx}/{total_configs}] "
                    f"Bỏ qua (k={k:g}, m={m}, rule={rule}) vì đã có trong CSV."
                )
                continue

            t_start = time.time()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[{timestamp}] [{cfg_idx}/{total_configs}] "
                f"Bắt đầu: m={m}, k={k:g}, rule={rule} (scen={scen}, iters={iters}) ..."
            )

            # 1. Hạt giống CRC32 độc lập
            train_seed, val_seed, eval_seed = get_seeds(m, k, rule)

            # 2. Tìm cân bằng qua find_equilibrium
            eq_res = find_equilibrium(
                m=m,
                k=k,
                rule=rule,
                seed=train_seed,
                n_scen=scen,
                max_iter=iters,
                mode="nonparametric",
            )
            strategy = eq_res["strategy"]
            converged = bool(eq_res["converged"])
            n_iter = int(eq_res["n_iter"])
            history = eq_res.get("history", [])
            final_delta = float(history[-1]) if history else 0.0
            v_knots = eq_res["v_knots"]

            # 3. Đo epsilon
            eps_res = epsilon(
                strategy=strategy,
                m=m,
                k=k,
                rule=rule,
                train_seed=train_seed,
                val_seed=val_seed,
                n_scen=scen,
                v_knots=v_knots,
            )
            eps_xval_rel = float(eps_res["eps_xval"]["eps_rel"])
            ci_low_x, ci_high_x = eps_res["eps_xval"]["ci_95"]
            eps_xval_ci95 = float((ci_high_x - ci_low_x) / 2.0)
            eps_opt_rel = float(eps_res["eps_opt"]["eps_rel"])

            # Đánh giá giá trị khai tại các nút 0.25, 0.50, 0.75
            eval_knots = np.array([0.25, 0.50, 0.75])
            bids_k = apply_strategy(eval_knots, strategy[0], side="bid", v_knots=v_knots)
            asks_k = apply_strategy(eval_knots, strategy[1], side="ask", v_knots=v_knots)
            bid_025, bid_050, bid_075 = float(bids_k[0]), float(bids_k[1]), float(bids_k[2])
            ask_025, ask_050, ask_075 = float(asks_k[0]), float(asks_k[1]), float(asks_k[2])

            # 4. Hiệu quả trên kịch bản đánh giá eval_scen
            V_eval, C_eval = draw_scenarios(m=m, n_scen=eval_scen, seed=eval_seed)
            w_eval = welfare(V_eval, C_eval, strategy, k=k, rule=rule)
            mw_eval = max_welfare(V_eval, C_eval)

            eff, loss, loss_ci95 = compute_loss_and_ci(w_eval, mw_eval, num_blocks=10)
            elapsed_sec = float(time.time() - t_start)

            # 5. Ghi ngay vào CSV và flush
            row_data = [
                f"{k:g}",
                f"{m}",
                f"{rule}",
                f"{scen}",
                f"{eval_scen}",
                f"{converged}",
                f"{n_iter}",
                f"{final_delta:.8f}",
                f"{loss:.8f}",
                f"{loss_ci95:.8f}",
                f"{eps_xval_rel:.8f}",
                f"{eps_xval_ci95:.8f}",
                f"{eps_opt_rel:.8f}",
                f"{bid_025:.6f}",
                f"{bid_050:.6f}",
                f"{bid_075:.6f}",
                f"{ask_025:.6f}",
                f"{ask_050:.6f}",
                f"{ask_075:.6f}",
                f"{elapsed_sec:.2f}",
            ]
            csv_writer.writerow(row_data)
            csv_file.flush()

            row_dict = dict(zip(CSV_HEADERS, row_data))
            all_rows.append(row_dict)
            existing_configs.add((float(k), int(m), str(rule)))

            print(
                f"    -> Xong trong {elapsed_sec:.1f}s | conv={converged} ({n_iter} vòng, delta={final_delta:.4e}) | "
                f"loss={loss:.5f}±{loss_ci95:.5f} | eps_xval_rel={eps_xval_rel:.4f}"
            )
    finally:
        csv_file.close()

    # 6. Khi xong tất cả:
    # (a) In bảng tóm tắt
    print_summary_table(all_rows)

    # (b) Hồi quy OLS log(loss) ~ log(m) cho mỗi (k, rule) với m >= 4
    print("\n" + "=" * 80)
    print("KẾT QUẢ HỒI QUY OLS LOG-LOG: log(loss) ~ log(m) (cho m >= 4)")
    print("=" * 80)

    # Nhóm theo (k, rule)
    grouped_for_ols: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for r in all_rows:
        key = (float(r["k"]), str(r["rule"]))
        grouped_for_ols.setdefault(key, []).append(r)

    for (k_val, rule_val), items in sorted(grouped_for_ols.items()):
        # Chỉ dùng m >= 4
        filtered = [x for x in items if int(x["m"]) >= 4]
        filtered_sorted = sorted(filtered, key=lambda x: int(x["m"]))
        m_vals = [int(x["m"]) for x in filtered_sorted]
        loss_vals = [float(x["loss"]) for x in filtered_sorted]

        ols_res = fit_log_log_ols(m_vals, loss_vals)
        if ols_res["slope"] is not None:
            slope = ols_res["slope"]
            se = ols_res["se"]
            ci_low = ols_res["ci_low"]
            ci_high = ols_res["ci_high"]
            r2 = ols_res["r_squared"]
            df_val = ols_res["df"]
            print(
                f"- (k={k_val:g}, rule={rule_val}): Độ dốc = {slope:.4f} ± {ols_res['ci_half']:.4f} "
                f"(Khoảng tin cậy 95%: [{ci_low:.4f}, {ci_high:.4f}], SE={se:.4f}, df={df_val}, R²={r2:.4f}, điểm={m_vals})"
            )
        else:
            print(f"- (k={k_val:g}, rule={rule_val}): {ols_res['msg']} (số điểm m >= 4 là {len(m_vals)})")
    print("=" * 80)

    # (c) Ghi biểu đồ exp_c_loss.png
    chart_path = out_dir / "exp_c_loss.png"
    plot_loss_scaling(all_rows, chart_path)
    print(f"Đã lưu biểu đồ: {chart_path}")

    # (d) In cảnh báo cố định
    print(f"\nCẢNH BÁO: {FIXED_WARNING}\n")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Điểm vào chính của script run_experiment_c."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    return run_experiment_c(args)


if __name__ == "__main__":
    sys.exit(main())
