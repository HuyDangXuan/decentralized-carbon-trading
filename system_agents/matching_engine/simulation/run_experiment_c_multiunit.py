"""Bộ chạy thực nghiệm C mở rộng: Tổn thất hiệu quả với lệnh nhiều đơn vị.

CẢNH BÁO VÀ GIỚI HẠN (Robustness Check):
Đây là kiểm tra độ bền: chiến lược lấy từ cân bằng của trò chơi MỘT đơn vị
(single-unit equilibrium từ Thực nghiệm C), KHÔNG phải cân bằng của trò chơi
nhiều đơn vị; áp dụng cho lệnh nhiều đơn vị là một heuristic.

Chiến lược là hàm tuyến tính từng đoạn trên lưới nút (đúng như Thực nghiệm C), đọc từ các file
`strategy_k{k}_m{m}_{rule}.npz` do `export_strategies_c.py` tạo. Không dùng đường thẳng khớp từ 3 điểm vì
làm sai lệch chiến lược (bản đầu làm vậy nên không tái hiện được loss một đơn vị khi max_amount=1).
Kiểm tra tin cậy: với --max-amount 1, loss phải khớp loss một đơn vị trong exp_c_raw.csv.
"""

import argparse
import csv
from fractions import Fraction
import math
import os
from pathlib import Path
import sys
from typing import Any, Sequence
import zlib

# Đảm bảo UTF-8 console và đường dẫn import
for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
_ENGINE_DIR = os.path.dirname(_SIM_DIR)
for d in (_SIM_DIR, _ENGINE_DIR):
    if d not in sys.path:
        sys.path.insert(0, d)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from kda_sim import apply_strategy  # noqa: E402
from run_experiment_c import compute_loss_and_ci, fit_log_log_ols  # noqa: E402
from session_engine import BookOrder, match_session  # noqa: E402


Strategy = tuple[np.ndarray, np.ndarray, np.ndarray]  # (v_knots, bid_knots, ask_knots)


def linear_strategy(ab: float, bb: float, as_: float, bs: float) -> Strategy:
    """Chiến lược tuyến tính bid = ab + bb*v, ask = as + bs*c (kẹp bid <= v, ask >= c khi áp dụng)."""
    v_knots = np.array([0.0, 1.0])
    return (
        v_knots,
        np.array([ab, ab + bb], dtype=float),
        np.array([as_, as_ + bs], dtype=float),
    )


def load_strategies(strategy_dir: str | Path) -> dict[tuple[float, int, str], Strategy]:
    """Đọc mọi file strategy_k*_m*_*.npz trong thư mục."""
    out: dict[tuple[float, int, str], Strategy] = {}
    for path in sorted(Path(strategy_dir).glob("strategy_k*_m*_*.npz")):
        with np.load(path, allow_pickle=False) as z:
            key = (round(float(z["k"]), 6), int(z["m"]), str(z["rule"]).lower())
            out[key] = (
                np.asarray(z["v_knots"], dtype=float),
                np.asarray(z["bid_knots"], dtype=float),
                np.asarray(z["ask_knots"], dtype=float),
            )
    return out


def compute_max_welfare(
    buyers: list[tuple[float, int]],
    sellers: list[tuple[float, int]],
) -> float:
    """Tính phúc lợi tối đa đa đơn vị: ghép mua giảm dần theo v với bán tăng dần theo c (v >= c)."""
    sorted_buyers = sorted(buyers, key=lambda x: -x[0])
    sorted_sellers = sorted(sellers, key=lambda x: x[0])
    i = j = 0
    rem_b = sorted_buyers[0][1] if sorted_buyers else 0
    rem_s = sorted_sellers[0][1] if sorted_sellers else 0
    mw = 0.0

    while i < len(sorted_buyers) and j < len(sorted_sellers):
        v, c = sorted_buyers[i][0], sorted_sellers[j][0]
        if v < c:
            break
        match_amt = min(rem_b, rem_s)
        mw += match_amt * (v - c)
        rem_b -= match_amt
        rem_s -= match_amt
        if rem_b == 0:
            i += 1
            if i < len(sorted_buyers):
                rem_b = sorted_buyers[i][1]
        if rem_s == 0:
            j += 1
            if j < len(sorted_sellers):
                rem_s = sorted_sellers[j][1]
    return mw


def evaluate_book(
    v: np.ndarray,
    q_b: np.ndarray,
    c: np.ndarray,
    q_s: np.ndarray,
    k_num: int,
    k_den: int,
    rule: str,
    strategy: Strategy,
) -> tuple[float, float, float] | None:
    """Khớp một sổ lệnh đã cho (giá trị, khối lượng) và trả (loss, phúc lợi, phúc lợi tối đa)."""
    v_knots, bid_knots, ask_knots = strategy
    bids = apply_strategy(np.asarray(v, dtype=float), bid_knots, side="bid", v_knots=v_knots)
    asks = apply_strategy(np.asarray(c, dtype=float), ask_knots, side="ask", v_knots=v_knots)
    m = len(v)

    orders: list[BookOrder] = []
    v_map: dict[str, float] = {}
    c_map: dict[str, float] = {}
    seq = 0

    for idx in range(m):
        b_ticks = max(1, min(int(round(float(bids[idx]) * 1_000_000)), int(math.floor(v[idx] * 1_000_000))))
        b_id = f"B_{idx}"
        v_map[b_id] = float(v[idx])
        orders.append(BookOrder(b_id, "BID", b_ticks, int(q_b[idx]), 0, seq, "GTC"))
        seq += 1

    for jdx in range(len(c)):
        a_ticks = max(1, max(int(round(float(asks[jdx]) * 1_000_000)), int(math.ceil(c[jdx] * 1_000_000))))
        a_id = f"A_{jdx}"
        c_map[a_id] = float(c[jdx])
        orders.append(BookOrder(a_id, "ASK", a_ticks, int(q_s[jdx]), 0, seq, "GTC"))
        seq += 1

    mw = compute_max_welfare(
        [(float(v[i]), int(q_b[i])) for i in range(m)],
        [(float(c[j]), int(q_s[j])) for j in range(len(c))],
    )
    if mw <= 0.0:
        return None

    fills = match_session(orders, k_num, k_den, "age_prorata", rule, "floor")
    w = sum(f.amount * (v_map[f.bid_id] - c_map[f.ask_id]) for f in fills)
    return 1.0 - (w / mw), w, mw


def simulate_book(
    m: int,
    k_num: int,
    k_den: int,
    rule: str,
    max_amount: int,
    strategy: Strategy,
    rng: np.random.Generator,
) -> tuple[float, float, float] | None:
    """Mô phỏng 1 sổ lệnh gồm m lệnh mua và m lệnh bán."""
    v = rng.uniform(0.0, 1.0, size=m)
    q_b = rng.integers(1, max_amount + 1, size=m)
    c = rng.uniform(0.0, 1.0, size=m)
    q_s = rng.integers(1, max_amount + 1, size=m)
    return evaluate_book(v, q_b, c, q_s, k_num, k_den, rule, strategy)


def run_configuration(
    k: float,
    m: int,
    rule: str,
    books: int,
    max_amount: int,
    strategy: Strategy,
) -> dict[str, Any]:
    """Chạy mô phỏng books sổ lệnh cho một cấu hình (k, m, rule)."""
    frac = Fraction(k).limit_denominator(1000)
    seed = zlib.crc32(f"{m}|{k}|{rule}".encode("utf-8"))
    rng = np.random.default_rng(seed)

    losses, welfares, max_welfares = [], [], []
    for _ in range(books):
        res = simulate_book(m, frac.numerator, frac.denominator, rule, max_amount, strategy, rng)
        if res is not None:
            losses.append(res[0])
            welfares.append(res[1])
            max_welfares.append(res[2])

    n = len(losses)
    # Cùng cách tính với Thực nghiệm C: loss = 1 - sum(w)/sum(mw) (ratio of means), CI chia khối.
    if n >= 10:
        _eff, loss_mean, loss_ci95 = compute_loss_and_ci(np.array(welfares), np.array(max_welfares), num_blocks=10)
    else:
        loss_mean, loss_ci95 = (float(np.mean(losses)) if n > 0 else 0.0), 0.0
    return {
        "k": k,
        "m": m,
        "rule": rule,
        "books": n,
        "max_amount": max_amount,
        "loss": loss_mean,
        "loss_ci95": loss_ci95,
        "welfare_mean": float(np.mean(welfares)) if n > 0 else 0.0,
        "max_welfare_mean": float(np.mean(max_welfares)) if n > 0 else 0.0,
    }


def _parse_csv_list(val: str, type_fn: Any, name: str) -> list[Any]:
    if not val or not val.strip():
        raise argparse.ArgumentTypeError(f"Danh sách {name} không được rỗng.")
    res = [type_fn(p.strip()) for p in val.split(",") if p.strip()]
    if not res:
        raise argparse.ArgumentTypeError(f"Danh sách {name} không được rỗng.")
    return res


def parse_m_list(v: str) -> list[int]:
    try:
        return _parse_csv_list(v, lambda x: int(x) if int(x) >= 1 else (_ for _ in ()).throw(ValueError()), "m")
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(f"m phải là số nguyên >= 1: '{v}'")


def parse_k_list(v: str) -> list[float]:
    try:
        return _parse_csv_list(v, lambda x: float(x) if 0.0 < float(x) <= 1.0 else (_ for _ in ()).throw(ValueError()), "k")
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(f"k phải thuộc (0, 1]: '{v}'")


def parse_rule_list(v: str) -> list[str]:
    allowed = {"marginal", "pair", "kda"}
    try:
        return _parse_csv_list(v, lambda x: x.lower() if x.lower() in allowed else (_ for _ in ()).throw(ValueError()), "rule")
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(f"rule phải là marginal/pair/kda: '{v}'")


def parse_pos_int(v: str) -> int:
    try:
        val = int(v)
        if val >= 1:
            return val
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(f"Giá trị phải là số nguyên >= 1: '{v}'")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Thực nghiệm C mở rộng (lệnh nhiều đơn vị).")
    p.add_argument("--strategies", type=str, required=True, help="Thư mục chứa strategy_k*_m*_*.npz (từ export_strategies_c.py)")
    p.add_argument("--m", type=parse_m_list, default=[16, 32, 64], help="m (mặc định: 16,32,64)")
    p.add_argument("--rule", type=parse_rule_list, default=["marginal"], help="rule (mặc định: marginal)")
    p.add_argument("--k", type=parse_k_list, default=None, help="k (mặc định: lấy từ các file chiến lược)")
    p.add_argument("--books", type=parse_pos_int, default=200, help="Số sổ lệnh (mặc định: 200)")
    p.add_argument("--max-amount", type=parse_pos_int, default=10, help="Khối lượng tối đa (mặc định: 10)")
    p.add_argument("--out", type=str, default="results", help="Thư mục xuất (mặc định: results)")
    return p


def print_summary_table(raw_rows: list[dict[str, Any]]) -> None:
    """In bảng tóm tắt kết quả căn thẳng ra stdout."""
    headers = ["k", "m", "rule", "books", "max_amt", "loss", "loss_ci95", "welfare", "max_welfare"]
    formatted = [
        [
            f"{float(r['k']):.2f}", str(r["m"]), str(r["rule"]), str(r["books"]), str(r["max_amount"]),
            f"{float(r['loss']):.6f}", f"{float(r['loss_ci95']):.6f}",
            f"{float(r['welfare_mean']):.2f}", f"{float(r['max_welfare_mean']):.2f}",
        ]
        for r in raw_rows
    ]
    widths = [len(h) for h in headers]
    for row in formatted:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(val))
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep = "  ".join("-" * widths[i] for i in range(len(headers)))
    print("\n" + "=" * len(header_line))
    print("BẢNG TÓM TẮT THỰC NGHIỆM C MỞ RỘNG (LỆNH NHIỀU ĐƠN VỊ)")
    print("=" * len(header_line))
    print(header_line)
    print(sep)
    for row in formatted:
        print("  ".join(val.ljust(widths[i]) for i, val in enumerate(row)))
    print("=" * len(header_line))


def plot_multiunit_loss(
    raw_rows: list[dict[str, Any]],
    slopes: dict[tuple[float, str], float | None],
    out_file: Path,
) -> None:
    """Vẽ biểu đồ log-log tổn thất hiệu quả theo m."""
    if not raw_rows:
        return
    groups: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for r in raw_rows:
        groups.setdefault((float(r["k"]), str(r["rule"])), []).append(r)

    fig, ax = plt.subplots(figsize=(8.5, 6.0))
    ax.set_xscale("log")
    ax.set_yscale("log")

    for (k_val, rule_val), items in sorted(groups.items()):
        sorted_items = sorted(items, key=lambda x: int(x["m"]))
        m_arr = np.array([int(x["m"]) for x in sorted_items], dtype=float)
        loss_arr = np.array([float(x["loss"]) for x in sorted_items], dtype=float)
        ci_arr = np.array([float(x["loss_ci95"]) for x in sorted_items], dtype=float)
        s_val = slopes.get((k_val, rule_val))
        lbl = f"k={k_val:g}, {rule_val} (độ dốc: {s_val:.3f})" if s_val is not None else f"k={k_val:g}, {rule_val}"
        ax.errorbar(m_arr, loss_arr, yerr=ci_arr, marker="o", capsize=3, label=lbl)

    ax.set_xlabel("Số lượng người tham gia mỗi bên m (log scale)")
    ax.set_ylabel("Mức tổn thất hiệu quả Loss = 1 - Efficiency (log scale)")
    ax.set_title("Tổn thất hiệu quả theo m (lệnh nhiều đơn vị, chiến lược từ cân bằng một đơn vị)")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    plt.close(fig)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    strategies = load_strategies(args.strategies)
    all_k_in_csv = sorted({k for (k, _, _) in strategies.keys()})
    target_k = [round(x, 6) for x in args.k] if args.k is not None else all_k_in_csv

    if not target_k:
        sys.stderr.write("LỖI: Không tìm thấy file chiến lược nào trong --strategies.\n")
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_results: list[dict[str, Any]] = []
    group_m_loss: dict[tuple[float, str], list[tuple[int, float]]] = {}

    for k_val in target_k:
        for rule_val in args.rule:
            key = (k_val, rule_val)
            for m_val in args.m:
                strat_key = (k_val, m_val, rule_val)
                if strat_key not in strategies:
                    sys.stderr.write(f"THIẾU: ({k_val}, {m_val}, {rule_val})\n")
                    sys.stderr.flush()
                    continue

                row_res = run_configuration(
                    k_val, m_val, rule_val, args.books, args.max_amount, strategies[strat_key]
                )
                raw_results.append(row_res)
                if row_res["loss"] > 0:
                    group_m_loss.setdefault(key, []).append((m_val, row_res["loss"]))

    raw_headers = ["k", "m", "rule", "books", "max_amount", "loss", "loss_ci95", "welfare_mean", "max_welfare_mean"]
    with open(out_dir / "exp_c_multiunit_raw.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=raw_headers)
        writer.writeheader()
        writer.writerows(raw_results)

    slope_results: list[dict[str, Any]] = []
    slopes_map: dict[tuple[float, str], float | None] = {}
    slope_headers = ["k", "rule", "n_points", "slope", "slope_ci_half", "r2"]

    for (k_val, rule_val), m_loss_list in sorted(group_m_loss.items()):
        m_loss_list.sort(key=lambda x: x[0])
        n_pts = len(m_loss_list)
        if n_pts < 2:
            sys.stderr.write(f"CẢNH BÁO: Còn < 2 giá trị m cho ({k_val}, {rule_val}), không hồi quy\n")
            sys.stderr.flush()
            slopes_map[(k_val, rule_val)] = None
            continue

        m_vals = [x[0] for x in m_loss_list]
        loss_vals = [x[1] for x in m_loss_list]
        fit_res = fit_log_log_ols(m_vals, loss_vals)

        if fit_res.get("slope") is not None:
            slope_results.append({
                "k": k_val, "rule": rule_val, "n_points": n_pts,
                "slope": fit_res["slope"], "slope_ci_half": fit_res["ci_half"], "r2": fit_res["r_squared"],
            })
            slopes_map[(k_val, rule_val)] = fit_res["slope"]
        else:
            sys.stderr.write(f"CẢNH BÁO: Không đủ điểm hồi quy cho ({k_val}, {rule_val}): {fit_res.get('msg')}\n")
            sys.stderr.flush()
            slopes_map[(k_val, rule_val)] = None

    with open(out_dir / "exp_c_multiunit_slopes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=slope_headers)
        writer.writeheader()
        writer.writerows(slope_results)

    plot_multiunit_loss(raw_results, slopes_map, out_dir / "exp_c_multiunit_loss.png")
    print_summary_table(raw_results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
