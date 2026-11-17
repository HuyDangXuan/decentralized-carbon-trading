"""Bộ giải cân bằng xấp xỉ độc lập cho đấu giá kép đơn vị đơn (Nhiệm vụ B2).

Mô-đun kiểm chéo độc lập với equilibrium_search.find_equilibrium:
  1. clear(bids, asks, k, rule): Khớp lệnh thị trường cho 'pair', 'marginal', 'kda'.
  2. solve(m, k, rule, n_scen, seed): Tìm chiến lược tuyến tính qua Nelder-Mead
     cực tiểu hóa độ khai thác (exploitability) trên lưới giá và valuation rời rạc.
  3. CLI in bảng kết quả (m, k, rule, ab, bb, as, bs, exploitability).

Quy tắc:
  - Chỉ dùng numpy và thư viện chuẩn (không scipy).
  - Không import auction_agent, session_engine, model, metrics, strategies, kda_sim.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Callable, Sequence
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clear(
    bids: Sequence[float] | np.ndarray,
    asks: Sequence[float] | np.ndarray,
    k: float,
    rule: str,
) -> tuple[int, list[float]]:
    """Khớp lệnh thị trường đấu giá kép và trả về số cặp khớp cùng danh sách giá khớp."""
    if not (isinstance(k, (int, float)) and 0.0 < k <= 1.0):
        raise ValueError(f"k phải thuộc (0, 1], nhận được {k}")
    if rule not in ("pair", "marginal", "kda"):
        raise ValueError(f"rule phải là 'pair', 'marginal', hoặc 'kda', nhận được '{rule}'")

    b_arr = np.asarray(bids, dtype=float).ravel()
    a_arr = np.asarray(asks, dtype=float).ravel()
    m_b, m_s = len(b_arr), len(a_arr)
    M_cand = min(m_b, m_s)
    if M_cand == 0:
        return 0, []

    b_sorted = np.sort(b_arr)[::-1]
    a_sorted = np.sort(a_arr)
    matched = b_sorted[:M_cand] >= a_sorted[:M_cand]
    M = int(np.sum(matched))
    if M == 0:
        return 0, []

    if rule == "pair":
        prices = [float(k * b_sorted[i] + (1.0 - k) * a_sorted[i]) for i in range(M)]
    elif rule == "marginal":
        p_val = float(k * b_sorted[M - 1] + (1.0 - k) * a_sorted[M - 1])
        prices = [p_val] * M
    else:  # "kda"
        b_m, a_m = float(b_sorted[M - 1]), float(a_sorted[M - 1])
        hi = float(min(b_m, a_sorted[M])) if M < m_s else b_m
        lo = float(max(a_m, b_sorted[M])) if M < m_b else a_m
        p_val = float(k * hi + (1.0 - k) * lo)
        prices = [p_val] * M

    return M, prices


def _clear_batch_core(
    bids: np.ndarray, asks: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sắp xếp và tính số cặp khớp m_star cho ma trận kịch bản (n_scen, m)."""
    b_sorted = np.sort(bids, axis=-1)[:, ::-1]
    a_sorted = np.sort(asks, axis=-1)
    M = min(bids.shape[-1], asks.shape[-1])
    matched = b_sorted[:, :M] >= a_sorted[:, :M]
    m_star = np.sum(matched, axis=-1)
    return m_star, b_sorted, a_sorted


def _calc_p_dev(
    rule: str,
    k: float,
    b_sorted: np.ndarray,
    a_sorted: np.ndarray,
    m_star: np.ndarray,
    row_idx: np.ndarray,
    rank0: np.ndarray,
    p_val: float,
    is_buyer: bool,
    m: int,
) -> np.ndarray:
    """Tính mức giá thanh toán cho người chơi lệch vị trí rank0."""
    if rule == "pair":
        if is_buyer:
            other_p = a_sorted[row_idx, np.minimum(rank0, m - 1)]
            return k * p_val + (1.0 - k) * other_p
        other_p = b_sorted[row_idx, np.minimum(rank0, m - 1)]
        return k * other_p + (1.0 - k) * p_val

    m_idx = np.maximum(m_star - 1, 0)
    b_m, a_m = b_sorted[row_idx, m_idx], a_sorted[row_idx, m_idx]
    if rule == "marginal":
        return np.where(m_star > 0, k * b_m + (1.0 - k) * a_m, 0.0)

    b_next = np.where(m_star < m, b_sorted[row_idx, np.minimum(m_star, m - 1)], -np.inf)
    a_next = np.where(m_star < m, a_sorted[row_idx, np.minimum(m_star, m - 1)], np.inf)
    hi, lo = np.minimum(b_m, a_next), np.maximum(a_m, b_next)
    return np.where(m_star > 0, k * hi + (1.0 - k) * lo, 0.0)


def _eval_m1(
    theta: tuple[float, float, float, float],
    k: float,
    V0: np.ndarray,
    C0: np.ndarray,
    price_grid: np.ndarray,
    val_grid: np.ndarray,
) -> tuple[float, float]:
    """Tính exploitability cho trường hợp m=1 bằng phân phối tích lũy giải tích."""
    ab, bb, as_, bs = theta
    n_scen = len(V0)

    a_seller = np.clip(as_ + bs * C0, C0, 1.0)
    a_sort = np.sort(a_seller)
    p_sum_a = np.cumsum(a_sort)
    idx_b = np.searchsorted(a_sort, price_grid, side="right")
    W_b = idx_b / n_scen
    sum_a = np.where(idx_b > 0, p_sum_a[np.maximum(idx_b - 1, 0)], 0.0)
    P_b = (k * price_grid * idx_b + (1.0 - k) * sum_a) / n_scen

    b_buyer = np.clip(ab + bb * V0, 0.0, V0)
    b_sort = np.sort(b_buyer)
    p_sum_b = np.cumsum(b_sort)
    idx_left = np.searchsorted(b_sort, price_grid, side="left")
    idx_s = n_scen - idx_left
    W_s = idx_s / n_scen
    sum_b = np.where(
        idx_s > 0,
        p_sum_b[-1] - np.where(idx_left > 0, p_sum_b[np.maximum(idx_left - 1, 0)], 0.0),
        0.0,
    )
    P_s = (k * sum_b + (1.0 - k) * price_grid * idx_s) / n_scen

    U_b = val_grid[:, None] * W_b[None, :] - P_b[None, :]
    valid_b = price_grid[None, :] <= val_grid[:, None] + 1e-12
    u_opt_b = np.maximum(0.0, np.max(np.where(valid_b, U_b, -np.inf), axis=1))
    b_strat = np.clip(ab + bb * val_grid, 0.0, val_grid)
    u_strat_b = np.maximum(
        0.0,
        val_grid * np.interp(b_strat, price_grid, W_b) - np.interp(b_strat, price_grid, P_b),
    )
    gain_b = np.maximum(0.0, u_opt_b - u_strat_b)

    U_s = P_s[None, :] - val_grid[:, None] * W_s[None, :]
    valid_s = price_grid[None, :] >= val_grid[:, None] - 1e-12
    u_opt_s = np.maximum(0.0, np.max(np.where(valid_s, U_s, -np.inf), axis=1))
    a_strat = np.clip(as_ + bs * val_grid, val_grid, 1.0)
    u_strat_s = np.maximum(
        0.0,
        np.interp(a_strat, price_grid, P_s) - val_grid * np.interp(a_strat, price_grid, W_s),
    )
    gain_s = np.maximum(0.0, u_opt_s - u_strat_s)

    exp_max = max(float(np.max(gain_b)), float(np.max(gain_s)))
    loss = exp_max + 0.5 * (float(np.mean(gain_b)) + float(np.mean(gain_s)))
    return exp_max, loss


def _eval_m_general(
    theta: tuple[float, float, float, float],
    m: int,
    k: float,
    rule: str,
    V: np.ndarray,
    C: np.ndarray,
    price_grid: np.ndarray,
    val_grid: np.ndarray,
) -> tuple[float, float]:
    """Tính exploitability cho trường hợp m > 1 qua mô phỏng Monte Carlo vector hóa."""
    ab, bb, as_, bs = theta
    n_scen, n_grid = len(V), len(price_grid)
    bids_other = np.clip(ab + bb * V[:, 1:], 0.0, V[:, 1:])
    asks_other = np.clip(as_ + bs * C[:, 1:], C[:, 1:], 1.0)
    bids_all = np.clip(ab + bb * V, 0.0, V)
    asks_all = np.clip(as_ + bs * C, C, 1.0)
    row_idx = np.arange(n_scen)

    W_b, P_b = np.zeros(n_grid, dtype=float), np.zeros(n_grid, dtype=float)
    bids_buf = np.empty((n_scen, m), dtype=float)
    bids_buf[:, 1:] = bids_other
    for g, bg in enumerate(price_grid):
        bids_buf[:, 0] = bg
        m_star, b_sorted, a_sorted = _clear_batch_core(bids_buf, asks_all)
        order_b = np.argsort(-bids_buf, axis=-1, kind="stable")
        rank0 = np.where(order_b == 0)[1]
        matched0 = rank0 < m_star
        p_dev = _calc_p_dev(rule, k, b_sorted, a_sorted, m_star, row_idx, rank0, bg, True, m)
        W_b[g] = float(np.mean(matched0))
        P_b[g] = float(np.mean(np.where(matched0, p_dev, 0.0)))

    W_s, P_s = np.zeros(n_grid, dtype=float), np.zeros(n_grid, dtype=float)
    asks_buf = np.empty((n_scen, m), dtype=float)
    asks_buf[:, 1:] = asks_other
    for g, ag in enumerate(price_grid):
        asks_buf[:, 0] = ag
        m_star, b_sorted, a_sorted = _clear_batch_core(bids_all, asks_buf)
        order_a = np.argsort(asks_buf, axis=-1, kind="stable")
        rank0 = np.where(order_a == 0)[1]
        matched0 = rank0 < m_star
        p_dev = _calc_p_dev(rule, k, b_sorted, a_sorted, m_star, row_idx, rank0, ag, False, m)
        W_s[g] = float(np.mean(matched0))
        P_s[g] = float(np.mean(np.where(matched0, p_dev, 0.0)))

    U_b = val_grid[:, None] * W_b[None, :] - P_b[None, :]
    valid_b = price_grid[None, :] <= val_grid[:, None] + 1e-12
    u_opt_b = np.maximum(0.0, np.max(np.where(valid_b, U_b, -np.inf), axis=1))
    b_strat = np.clip(ab + bb * val_grid, 0.0, val_grid)
    u_strat_b = np.maximum(
        0.0,
        val_grid * np.interp(b_strat, price_grid, W_b) - np.interp(b_strat, price_grid, P_b),
    )
    gain_b = np.maximum(0.0, u_opt_b - u_strat_b)

    U_s = P_s[None, :] - val_grid[:, None] * W_s[None, :]
    valid_s = price_grid[None, :] >= val_grid[:, None] - 1e-12
    u_opt_s = np.maximum(0.0, np.max(np.where(valid_s, U_s, -np.inf), axis=1))
    a_strat = np.clip(as_ + bs * val_grid, val_grid, 1.0)
    u_strat_s = np.maximum(
        0.0,
        np.interp(a_strat, price_grid, P_s) - val_grid * np.interp(a_strat, price_grid, W_s),
    )
    gain_s = np.maximum(0.0, u_opt_s - u_strat_s)

    exp_max = max(float(np.max(gain_b)), float(np.max(gain_s)))
    loss = exp_max + 0.5 * (float(np.mean(gain_b)) + float(np.mean(gain_s)))
    return exp_max, loss


def _nelder_mead(
    obj_fn: Callable[[tuple[float, float, float, float]], tuple[float, float]],
    x0: tuple[float, float, float, float],
    max_iter: int = 40,
    tol: float = 1e-4,
    step: float = 0.02,
) -> tuple[tuple[float, float, float, float], float, int]:
    """Tối ưu hóa không đạo hàm Nelder-Mead Simplex."""
    dim = len(x0)
    sim = [list(x0)] + [[x0[d] + (step if d == i else 0.0) for d in range(dim)] for i in range(dim)]
    n_evals = 0
    f_vals, exp_vals = [], []
    for pt in sim:
        exp_m, loss = obj_fn(tuple(pt))
        f_vals.append(loss)
        exp_vals.append(exp_m)
        n_evals += 1

    alpha, gamma, rho, sigma = 1.0, 2.0, 0.5, 0.5

    for _ in range(max_iter):
        order = np.argsort(f_vals)
        sim = [sim[i] for i in order]
        f_vals = [f_vals[i] for i in order]
        exp_vals = [exp_vals[i] for i in order]

        if max(abs(f_vals[i] - f_vals[0]) for i in range(1, len(sim))) < tol:
            break

        centroid = [sum(sim[i][d] for i in range(dim)) / dim for d in range(dim)]
        xr = [centroid[d] + alpha * (centroid[d] - sim[-1][d]) for d in range(dim)]
        exp_r, fr = obj_fn(tuple(xr))
        n_evals += 1

        if fr < f_vals[0]:
            xe = [centroid[d] + gamma * (xr[d] - centroid[d]) for d in range(dim)]
            exp_e, fe = obj_fn(tuple(xe))
            n_evals += 1
            sim[-1], f_vals[-1], exp_vals[-1] = (xe, fe, exp_e) if fe < fr else (xr, fr, exp_r)
        elif fr < f_vals[-2]:
            sim[-1], f_vals[-1], exp_vals[-1] = xr, fr, exp_r
        else:
            xc = [
                centroid[d] + rho * (xr[d] - centroid[d])
                if fr < f_vals[-1]
                else centroid[d] - rho * (centroid[d] - sim[-1][d])
                for d in range(dim)
            ]
            exp_c, fc = obj_fn(tuple(xc))
            n_evals += 1
            if fc < (fr if fr < f_vals[-1] else f_vals[-1]):
                sim[-1], f_vals[-1], exp_vals[-1] = xc, fc, exp_c
            else:
                for i in range(1, len(sim)):
                    sim[i] = [sim[0][d] + sigma * (sim[i][d] - sim[0][d]) for d in range(dim)]
                    exp_i, fi = obj_fn(tuple(sim[i]))
                    n_evals += 1
                    f_vals[i], exp_vals[i] = fi, exp_i

    best_idx = int(np.argmin(f_vals))
    return tuple(float(x) for x in sim[best_idx]), float(exp_vals[best_idx]), n_evals


def solve(
    m: int,
    k: float,
    rule: str,
    n_scen: int = 20000,
    seed: int = 0,
    max_iter: int = 40,
) -> dict[str, Any]:
    """Tìm chiến lược cân bằng xấp xỉ tuyến tính bằng cực tiểu hóa độ khai thác."""
    if m < 1:
        raise ValueError(f"m phải >= 1, nhận được {m}")
    if not (isinstance(k, (int, float)) and 0.0 < k <= 1.0):
        raise ValueError(f"k phải thuộc (0, 1], nhận được {k}")
    if rule not in ("pair", "marginal", "kda"):
        raise ValueError(f"rule phải là 'pair', 'marginal', hoặc 'kda', nhận được '{rule}'")
    if n_scen < 1:
        raise ValueError(f"n_scen phải >= 1, nhận được {n_scen}")

    rng = np.random.default_rng(seed)
    V = rng.uniform(0.0, 1.0, size=(n_scen, m))
    C = rng.uniform(0.0, 1.0, size=(n_scen, m))
    price_grid = np.linspace(0.0, 1.0, 101)
    val_grid = np.linspace(0.0, 1.0, 21)

    if k == 1.0:
        ab0, bb0, as0, bs0 = 0.0, 0.5, 0.0, 1.0
    else:
        bb0 = 1.0 / (1.0 + k)
        bs0 = 1.0 / (2.0 - k)
        ab0 = k * (1.0 - k) / (2.0 * (1.0 + k))
        as0 = (1.0 - k) / 2.0

    if m > 1:
        w = 1.0 / float(m)
        bb0, bs0 = (1.0 - w) + w * bb0, (1.0 - w) + w * bs0
        ab0, as0 = w * ab0, w * as0

    x0 = (ab0, bb0, as0, bs0)
    if m == 1:
        V0, C0 = V[:, 0], C[:, 0]
        obj_fn = lambda theta: _eval_m1(theta, k, V0, C0, price_grid, val_grid)
    else:
        obj_fn = lambda theta: _eval_m_general(theta, m, k, rule, V, C, price_grid, val_grid)

    best_theta, exploitability, n_evals = _nelder_mead(obj_fn, x0, max_iter=max_iter)
    return {
        "theta": best_theta,
        "exploitability": exploitability,
        "n_evals": n_evals,
        "seed": seed,
    }


def main() -> None:
    """Giao diện dòng lệnh CLI cho equilibrium_crosscheck."""
    parser = argparse.ArgumentParser(description="Bộ tìm cân bằng xấp xỉ độc lập cho k-double auction.")
    parser.add_argument("--m", type=str, default="2,4,8", help="Danh sách m (ví dụ '2,4,8')")
    parser.add_argument("--k", type=str, default="0.5,1", help="Danh sách k (ví dụ '0.5,1')")
    parser.add_argument("--rule", type=str, default="pair,marginal,kda", help="Danh sách rule")
    parser.add_argument("--scen", type=int, default=20000, help="Số kịch bản Monte Carlo")
    parser.add_argument("--seed", type=int, default=0, help="Hạt giống sinh ngẫu nhiên")
    args = parser.parse_args()

    m_list = [int(x.strip()) for x in args.m.split(",") if x.strip()]
    k_list = [float(x.strip()) for x in args.k.split(",") if x.strip()]
    rule_list = [x.strip() for x in args.rule.split(",") if x.strip()]

    print("m,k,rule,ab,bb,as,bs,exploitability")
    for m in m_list:
        for k in k_list:
            for rule in rule_list:
                res = solve(m=m, k=k, rule=rule, n_scen=args.scen, seed=args.seed)
                ab, bb, as_, bs = res["theta"]
                exp_val = res["exploitability"]
                print(f"{m},{k},{rule},{ab:.4f},{bb:.4f},{as_:.4f},{bs:.4f},{exp_val:.6f}")


if __name__ == "__main__":
    main()
