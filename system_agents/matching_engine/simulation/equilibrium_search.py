"""Mô đun tìm kiếm cân bằng ε-Equilibrium cho thị trường đấu giá kép (Giai đoạn 2, Nhiệm vụ J3).

Tuân thủ hợp đồng anti-missions/contract-c.md (mục J3).
Cung cấp:
  1. best_response_pointwise: Tìm phản ứng tối ưu pointwise theo từng nút trên lưới giá.
  2. find_equilibrium: Tìm điểm cân bằng bằng lặp co (damping) ở chế độ nonparametric hoặc linear.
  3. epsilon: Đo khoảng cách tới cân bằng qua eps_opt và eps_xval cùng khoảng tin cậy CI 95%.
"""

from typing import Any, Sequence
import numpy as np

from kda_sim import (
    DEFAULT_NUM_KNOTS,
    DEFAULT_V_KNOTS,
    apply_strategy,
    cs_theta,
    deviator_outcome,
    draw_scenarios,
    theta_to_strategy,
)


class EpsilonResult(dict):
    """Từ điển mở rộng hỗ trợ cả truy cập dạng khóa res['key'] và thuộc tính res.key."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'EpsilonResult' không có thuộc tính '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'EpsilonResult' không có thuộc tính '{name}'")


def _resolve_strategy(strategy: Any) -> tuple[np.ndarray, np.ndarray]:
    """Phân giải chiến lược đầu vào thành (bid_knots, ask_knots)."""
    if isinstance(strategy, (tuple, list)) and len(strategy) == 4 and all(
        isinstance(x, (int, float, np.floating, np.integer)) for x in strategy
    ):
        return theta_to_strategy(strategy)
    elif isinstance(strategy, (tuple, list)) and len(strategy) == 2:
        return np.asarray(strategy[0], dtype=float), np.asarray(strategy[1], dtype=float)
    raise ValueError("strategy phải là (bid_knots, ask_knots) hoặc tuple 4 tham số theta")


def best_response_pointwise(
    strategy: Any,
    side: str,
    m: int,
    k: float,
    rule: str,
    seed: int,
    n_scen: int,
    v_knots: np.ndarray | None = None,
    price_grid_size: int = 81,
    tick: float | None = None,
    scenarios: tuple[np.ndarray, np.ndarray] | None = None,
) -> dict[str, Any]:
    """Tìm phản ứng tối ưu theo từng nút valuation/cost trên lưới giá rời rạc.

    Sử dụng biểu diễn: U(v, b) = v*W(b) - P(b) (người mua) hoặc P(a) - c*W(a) (người bán).
    W và P được tính 1 lần trên price_grid qua deviator_outcome (CRN),
    sau đó phản ứng tối ưu cho mỗi nút v_j là argmax trên lưới.

    Args:
        strategy: Chiến lược của các người chơi khác ((bid_knots, ask_knots) hoặc theta).
        side: Phía của người lệch ("buy" / "bid" hoặc "sell" / "ask").
        m: Số người tham gia mỗi bên thị trường.
        k: Hệ số k-DA, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        seed: Hạt giống ngẫu nhiên để sinh kịch bản CRN (nếu scenarios is None).
        n_scen: Số lượng kịch bản mô phỏng.
        v_knots: Các nút valuation/cost (mặc định np.linspace(0, 1, 41)).
        price_grid_size: Số điểm trên lưới giá khai [0, 1] (mặc định 81).
        tick: Bước giá làm tròn (None nếu liên tục).
        scenarios: Tuple (V, C) truyền trước nếu muốn tránh sinh lại.

    Returns:
        dict chứa:
          "br": Mảng giá khai tối ưu tại các nút v_knots.
          "u_opt": Tiện ích tối ưu đạt được tại các nút.
          "u_strat": Tiện ích của chính chiến lược hiện tại tại các nút (nội suy).
          "gain": Phần cải thiện tiện ích gain(v_j) = max(u_opt - u_strat, 0).
          "v_knots": Mảng các nút valuation v_knots.
          "price_grid": Lưới giá khai price_grid.
          "W": Mảng xác suất khớp lệnh trên price_grid.
          "P": Mảng kỳ vọng thanh toán trên price_grid.
    """
    if v_knots is None:
        v_knots = DEFAULT_V_KNOTS.copy()
    else:
        v_knots = np.asarray(v_knots, dtype=float)

    price_grid = np.linspace(0.0, 1.0, price_grid_size)

    if scenarios is not None:
        V, C = scenarios
    else:
        V, C = draw_scenarios(m=m, n_scen=n_scen, seed=seed)

    bid_knots, ask_knots = _resolve_strategy(strategy)

    side_lower = side.lower()
    is_buyer = side_lower in ("buy", "bid", "buyer")
    is_seller = side_lower in ("sell", "ask", "seller")
    if not (is_buyer or is_seller):
        raise ValueError(f"side phải là 'buy'/'bid' hoặc 'sell'/'ask', nhận được '{side}'")

    # Tính xác suất giao dịch W và khoản trả kỳ vọng P một lần duy nhất trên lưới giá
    W, P = deviator_outcome(
        V, C, (bid_knots, ask_knots), k=k, rule=rule, side=side, price_grid=price_grid, tick=tick
    )

    if is_buyer:
        # Tiện ích người mua: U(v_j, b_g) = v_j * W(b_g) - P(b_g), ràng buộc b_g <= v_j
        U_all = v_knots[:, None] * W[None, :] - P[None, :]
        valid = price_grid[None, :] <= v_knots[:, None] + 1e-12
        U_masked = np.where(valid, U_all, -np.inf)
        best_idx = np.argmax(U_masked, axis=1)

        br = price_grid[best_idx]
        u_opt = np.take_along_axis(U_all, best_idx[:, None], axis=1).squeeze(1)
        u_opt = np.maximum(u_opt, 0.0)

        # Tiện ích của chiến lược hiện tại tại v_knots qua nội suy W và P
        strat_bids = apply_strategy(v_knots, bid_knots, side="bid")
        W_strat = np.interp(strat_bids, price_grid, W)
        P_strat = np.interp(strat_bids, price_grid, P)
        u_strat = v_knots * W_strat - P_strat
        u_strat = np.maximum(u_strat, 0.0)
    else:
        # Tiện ích người bán: U(c_j, a_g) = P(a_g) - c_j * W(a_g), ràng buộc a_g >= c_j
        U_all = P[None, :] - v_knots[:, None] * W[None, :]
        valid = price_grid[None, :] >= v_knots[:, None] - 1e-12
        U_masked = np.where(valid, U_all, -np.inf)
        best_idx = np.argmax(U_masked, axis=1)

        br = price_grid[best_idx]
        u_opt = np.take_along_axis(U_all, best_idx[:, None], axis=1).squeeze(1)
        u_opt = np.maximum(u_opt, 0.0)

        strat_asks = apply_strategy(v_knots, ask_knots, side="ask")
        W_strat = np.interp(strat_asks, price_grid, W)
        P_strat = np.interp(strat_asks, price_grid, P)
        u_strat = P_strat - v_knots * W_strat
        u_strat = np.maximum(u_strat, 0.0)

    gain = np.maximum(u_opt - u_strat, 0.0)

    return {
        "br": br,
        "u_opt": u_opt,
        "u_strat": u_strat,
        "gain": gain,
        "v_knots": v_knots,
        "price_grid": price_grid,
        "W": W,
        "P": P,
    }


def find_equilibrium(
    m: int,
    k: float,
    rule: str,
    seed: int,
    n_scen: int,
    damping: float = 0.5,
    max_iter: int = 40,
    tol: float = 2e-3,
    init: Any = None,
    mode: str = "nonparametric",
    v_knots: np.ndarray | None = None,
    price_grid_size: int = 81,
    tick: float | None = None,
) -> dict[str, Any]:
    """Tìm điểm cân bằng chiến lược bằng phương pháp lặp co (damping).

    Hỗ trợ 2 chế độ:
      - "nonparametric": cập nhật nút <- (1-damping)*nút + damping*br, ép cummax và kẹp [0, v] / [c, 1].
      - "linear": khớp OLS (bình phương nhỏ nhất) 4 tham số θ = (αb, βb, αs, βs).

    Dùng CÙNG một bộ kịch bản huấn luyện (V, C) sinh từ seed cho mọi vòng lặp.

    Args:
        m: Số người tham gia mỗi bên.
        k: Hệ số k-DA, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        seed: Hạt giống sinh kịch bản huấn luyện CRN.
        n_scen: Số kịch bản huấn luyện.
        damping: Hệ số giảm chấn bước cập nhật (0 < damping <= 1.0, mặc định 0.5).
        max_iter: Số vòng lặp tối đa (mặc định 40).
        tol: Ngưỡng dừng dung sai max|delta| (mặc định 2e-3).
        init: Điểm khởi tạo (None, tuple 4 tham số theta, hoặc tuple (bid_knots, ask_knots)).
        mode: Chế độ lặp ("nonparametric" hoặc "linear").
        v_knots: Mảng nút valuation (mặc định 41 nút đều trên [0, 1]).
        price_grid_size: Kích thước lưới giá đánh giá BR (mặc định 81).
        tick: Bước giá làm tròn (None nếu liên tục).

    Returns:
        dict chứa:
          "strategy": tuple (bid_knots, ask_knots).
          "theta": tuple 4 phần tử (nếu mode=="linear", ngược lại None).
          "n_iter": Số vòng lặp thực tế đã chạy.
          "converged": True nếu đạt dung sai tol, False nếu chạm max_iter.
          "history": Danh sách max|delta| qua từng vòng lặp.
          "v_knots": Mảng các nút valuation.
    """
    if v_knots is None:
        v_knots = DEFAULT_V_KNOTS.copy()
    else:
        v_knots = np.asarray(v_knots, dtype=float)

    # CÙNG bộ kịch bản huấn luyện cho mọi vòng lặp
    V, C = draw_scenarios(m=m, n_scen=n_scen, seed=seed)
    scenarios = (V, C)

    # Khởi tạo chiến lược
    current_theta: tuple[float, float, float, float] | None = None
    if mode == "nonparametric":
        if init is None:
            # Mặc định: trung thực
            bid_knots = v_knots.copy()
            ask_knots = v_knots.copy()
        elif isinstance(init, (tuple, list)) and len(init) == 4 and all(
            isinstance(x, (int, float, np.floating, np.integer)) for x in init
        ):
            bid_knots, ask_knots = theta_to_strategy(init, v_knots=v_knots)
        elif isinstance(init, (tuple, list)) and len(init) == 2:
            bid_knots = np.asarray(init[0], dtype=float).copy()
            ask_knots = np.asarray(init[1], dtype=float).copy()
        else:
            raise ValueError("init không hợp lệ cho mode nonparametric")
    elif mode == "linear":
        if init is None:
            current_theta = cs_theta(k)
        elif isinstance(init, (tuple, list)) and len(init) == 4 and all(
            isinstance(x, (int, float, np.floating, np.integer)) for x in init
        ):
            current_theta = (float(init[0]), float(init[1]), float(init[2]), float(init[3]))
        else:
            # Khởi tạo từ cặp knots: khớp OLS ban đầu
            b_init = np.asarray(init[0], dtype=float)
            a_init = np.asarray(init[1], dtype=float)
            X = np.column_stack([np.ones_like(v_knots), v_knots])
            ab0, bb0 = np.linalg.lstsq(X, b_init, rcond=None)[0]
            as0, bs0 = np.linalg.lstsq(X, a_init, rcond=None)[0]
            current_theta = (float(ab0), float(bb0), float(as0), float(bs0))

        bid_knots, ask_knots = theta_to_strategy(current_theta, v_knots=v_knots)
    else:
        raise ValueError(f"mode phải là 'nonparametric' hoặc 'linear', nhận được '{mode}'")

    history: list[float] = []
    converged = False
    n_iter = 0

    for it in range(1, max_iter + 1):
        n_iter = it
        strat_curr = (bid_knots, ask_knots)

        res_b = best_response_pointwise(
            strat_curr,
            side="buy",
            m=m,
            k=k,
            rule=rule,
            seed=seed,
            n_scen=n_scen,
            v_knots=v_knots,
            price_grid_size=price_grid_size,
            tick=tick,
            scenarios=scenarios,
        )
        res_s = best_response_pointwise(
            strat_curr,
            side="sell",
            m=m,
            k=k,
            rule=rule,
            seed=seed,
            n_scen=n_scen,
            v_knots=v_knots,
            price_grid_size=price_grid_size,
            tick=tick,
            scenarios=scenarios,
        )

        br_b = res_b["br"]
        br_s = res_s["br"]

        if mode == "nonparametric":
            new_bid = (1.0 - damping) * bid_knots + damping * br_b
            new_ask = (1.0 - damping) * ask_knots + damping * br_s

            # Ép tăng đơn điệu (cummax) và kẹp bid <= v, ask >= c
            new_bid = np.clip(new_bid, 0.0, v_knots)
            new_bid = np.maximum.accumulate(new_bid)
            new_bid = np.clip(new_bid, 0.0, v_knots)

            new_ask = np.clip(new_ask, v_knots, 1.0)
            new_ask = np.maximum.accumulate(new_ask)
            new_ask = np.clip(new_ask, v_knots, 1.0)
        else:  # mode == "linear"
            # Chỉ khớp trên các nút "có thông tin": nơi người chơi thực sự có xác suất giao dịch
            # dương tại giá khai tối ưu và khai lệch khỏi giá trị thật. Ở các nút còn lại
            # (người mua v thấp hơn ask thấp nhất, người bán c cao hơn bid cao nhất) mọi giá khai
            # đều cho tiện ích 0, nên BR không xác định và sẽ làm lệch đường hồi quy.
            w_b = np.interp(br_b, res_b["price_grid"], res_b["W"])
            w_s = np.interp(br_s, res_s["price_grid"], res_s["W"])
            mask_b = (w_b > 0.02) & (br_b < v_knots - 1e-9)
            mask_s = (w_s > 0.02) & (br_s > v_knots + 1e-9)
            assert current_theta is not None
            c_ab, c_bb, c_as, c_bs = current_theta
            if int(mask_b.sum()) >= 3:
                Xb = np.column_stack([np.ones(int(mask_b.sum())), v_knots[mask_b]])
                ab_fit, bb_fit = np.linalg.lstsq(Xb, br_b[mask_b], rcond=None)[0]
            else:
                ab_fit, bb_fit = c_ab, c_bb
            if int(mask_s.sum()) >= 3:
                Xs = np.column_stack([np.ones(int(mask_s.sum())), v_knots[mask_s]])
                as_fit, bs_fit = np.linalg.lstsq(Xs, br_s[mask_s], rcond=None)[0]
            else:
                as_fit, bs_fit = c_as, c_bs

            new_ab = (1.0 - damping) * c_ab + damping * float(ab_fit)
            new_bb = (1.0 - damping) * c_bb + damping * float(bb_fit)
            new_as = (1.0 - damping) * c_as + damping * float(as_fit)
            new_bs = (1.0 - damping) * c_bs + damping * float(bs_fit)

            current_theta = (new_ab, new_bb, new_as, new_bs)
            new_bid, new_ask = theta_to_strategy(current_theta, v_knots=v_knots)

        delta_b = float(np.max(np.abs(new_bid - bid_knots)))
        delta_s = float(np.max(np.abs(new_ask - ask_knots)))
        delta = max(delta_b, delta_s)
        history.append(delta)

        bid_knots = new_bid
        ask_knots = new_ask

        if delta < tol:
            converged = True
            break

    return {
        "strategy": (bid_knots, ask_knots),
        "theta": current_theta,
        "n_iter": n_iter,
        "converged": converged,
        "history": history,
        "v_knots": v_knots,
    }


def epsilon(
    strategy: Any,
    m: int,
    k: float,
    rule: str,
    train_seed: int,
    val_seed: int,
    n_scen: int,
    v_knots: np.ndarray | None = None,
    price_grid_size: int = 81,
    tick: float | None = None,
    n_blocks: int = 5,
) -> EpsilonResult:
    """Đo khoảng cách tới cân bằng epsilon với hai ước lượng độc lập eps_opt và eps_xval.

    - eps_opt: BR chọn trực tiếp trên kịch bản kiểm định val_seed (chệch lên do optimizer's curse).
    - eps_xval: BR chọn trên kịch bản huấn luyện train_seed, đánh giá trên kịch bản val_seed (không cắt về 0 nên không chệch lên; có thể hơi âm do nhiễu; cận dưới của lợi ích lệch tối đa).

    Cho mỗi loại:
      eps_avg: trung bình theo v của gain(v) (tích phân ex ante theo v ~ U[0, 1]).
      eps_max: max theo v của gain(v).
      eps_rel: eps_avg / U_ex_ante của phía đó.
      CI / ci_95: Khoảng tin cậy 95% của eps_avg bằng cách chia kịch bản val_seed thành n_blocks khối.

    Args:
        strategy: Chiến lược cần đánh giá ((bid_knots, ask_knots) hoặc theta).
        m: Số người tham gia mỗi bên thị trường.
        k: Hệ số k-DA, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        train_seed: Hạt giống kịch bản huấn luyện để chọn BR cho xval.
        val_seed: Hạt giống kịch bản kiểm định độc lập để đánh giá.
        n_scen: Số kịch bản kiểm định và huấn luyện.
        v_knots: Các nút valuation (mặc định 41 nút đều trên [0, 1]).
        price_grid_size: Số điểm lưới giá (mặc định 81).
        tick: Bước giá làm tròn.
        n_blocks: Số khối chia kịch bản để tính khoảng tin cậy CI (tối thiểu 5).

    Returns:
        EpsilonResult chứa:
          "eps_opt": EpsilonResult chi tiết cho ước lượng opt.
          "eps_xval": EpsilonResult chi tiết cho ước lượng xval.
          "eps_rel": Tỷ lệ eps tương đối đại diện (từ eps_xval).
          "eps_avg": Giá trị eps_avg đại diện.
          "eps_max": Giá trị eps_max đại diện.
    """
    if v_knots is None:
        v_knots = DEFAULT_V_KNOTS.copy()
    else:
        v_knots = np.asarray(v_knots, dtype=float)

    price_grid = np.linspace(0.0, 1.0, price_grid_size)
    bid_knots, ask_knots = _resolve_strategy(strategy)
    resolved_strat = (bid_knots, ask_knots)

    # 1. Kịch bản kiểm định độc lập (val_seed)
    V_val, C_val = draw_scenarios(m=m, n_scen=n_scen, seed=val_seed)
    val_scenarios = (V_val, C_val)

    # 2. Ước lượng eps_opt: BR chọn NGAY trên kịch bản kiểm định
    res_val_b = best_response_pointwise(
        resolved_strat,
        side="buy",
        m=m,
        k=k,
        rule=rule,
        seed=val_seed,
        n_scen=n_scen,
        v_knots=v_knots,
        price_grid_size=price_grid_size,
        tick=tick,
        scenarios=val_scenarios,
    )
    res_val_s = best_response_pointwise(
        resolved_strat,
        side="sell",
        m=m,
        k=k,
        rule=rule,
        seed=val_seed,
        n_scen=n_scen,
        v_knots=v_knots,
        price_grid_size=price_grid_size,
        tick=tick,
        scenarios=val_scenarios,
    )

    gain_b_opt = res_val_b["gain"]
    gain_s_opt = res_val_s["gain"]
    u_ex_b = float(np.mean(res_val_b["u_strat"]))
    u_ex_s = float(np.mean(res_val_s["u_strat"]))

    eps_avg_b_opt = float(np.mean(gain_b_opt))
    eps_max_b_opt = float(np.max(gain_b_opt))
    eps_rel_b_opt = eps_avg_b_opt / u_ex_b if u_ex_b > 1e-12 else 0.0

    eps_avg_s_opt = float(np.mean(gain_s_opt))
    eps_max_s_opt = float(np.max(gain_s_opt))
    eps_rel_s_opt = eps_avg_s_opt / u_ex_s if u_ex_s > 1e-12 else 0.0

    # 3. Ước lượng eps_xval: BR chọn trên train_seed, đánh giá trên val_seed
    res_tr_b = best_response_pointwise(
        resolved_strat,
        side="buy",
        m=m,
        k=k,
        rule=rule,
        seed=train_seed,
        n_scen=n_scen,
        v_knots=v_knots,
        price_grid_size=price_grid_size,
        tick=tick,
    )
    res_tr_s = best_response_pointwise(
        resolved_strat,
        side="sell",
        m=m,
        k=k,
        rule=rule,
        seed=train_seed,
        n_scen=n_scen,
        v_knots=v_knots,
        price_grid_size=price_grid_size,
        tick=tick,
    )

    br_train_b = res_tr_b["br"]
    br_train_s = res_tr_s["br"]

    # Đánh giá br_train_b trên kết quả kiểm định W, P (từ res_val_b)
    W_val_b, P_val_b = res_val_b["W"], res_val_b["P"]
    W_xb = np.interp(br_train_b, price_grid, W_val_b)
    P_xb = np.interp(br_train_b, price_grid, P_val_b)
    u_xb = v_knots * W_xb - P_xb
    gain_b_xval = u_xb - res_val_b["u_strat"]  # không cắt về 0: ước lượng không chệch, có thể âm do nhiễu

    # Đánh giá br_train_s trên kết quả kiểm định W, P (từ res_val_s)
    W_val_s, P_val_s = res_val_s["W"], res_val_s["P"]
    W_xs = np.interp(br_train_s, price_grid, W_val_s)
    P_xs = np.interp(br_train_s, price_grid, P_val_s)
    u_xs = P_xs - v_knots * W_xs
    gain_s_xval = u_xs - res_val_s["u_strat"]  # không cắt về 0: ước lượng không chệch, có thể âm do nhiễu

    eps_avg_b_xval = float(np.mean(gain_b_xval))
    eps_max_b_xval = float(np.max(gain_b_xval))
    eps_rel_b_xval = eps_avg_b_xval / u_ex_b if u_ex_b > 1e-12 else 0.0

    eps_avg_s_xval = float(np.mean(gain_s_xval))
    eps_max_s_xval = float(np.max(gain_s_xval))
    eps_rel_s_xval = eps_avg_s_xval / u_ex_s if u_ex_s > 1e-12 else 0.0

    # 4. Tính khoảng tin cậy 95% bằng chia kịch bản kiểm định thành >= 5 khối
    K = max(int(n_blocks), 5)
    block_size = n_scen // K
    block_avg_b_xval: list[float] = []
    block_avg_s_xval: list[float] = []
    block_avg_b_opt: list[float] = []
    block_avg_s_opt: list[float] = []

    for b in range(K):
        s_idx = b * block_size
        e_idx = (b + 1) * block_size
        V_blk = V_val[s_idx:e_idx]
        C_blk = C_val[s_idx:e_idx]

        W_blk_b, P_blk_b = deviator_outcome(
            V_blk, C_blk, resolved_strat, k=k, rule=rule, side="buy", price_grid=price_grid, tick=tick
        )
        W_blk_s, P_blk_s = deviator_outcome(
            V_blk, C_blk, resolved_strat, k=k, rule=rule, side="sell", price_grid=price_grid, tick=tick
        )

        # opt trên khối
        U_blk_b = v_knots[:, None] * W_blk_b[None, :] - P_blk_b[None, :]
        v_b = price_grid[None, :] <= v_knots[:, None] + 1e-12
        opt_b_val = np.take_along_axis(U_blk_b, np.argmax(np.where(v_b, U_blk_b, -np.inf), axis=1)[:, None], axis=1).squeeze(1)
        strat_bids = apply_strategy(v_knots, bid_knots, side="bid")
        u_strat_blk_b = v_knots * np.interp(strat_bids, price_grid, W_blk_b) - np.interp(strat_bids, price_grid, P_blk_b)
        block_avg_b_opt.append(float(np.mean(np.maximum(opt_b_val - u_strat_blk_b, 0.0))))

        U_blk_s = P_blk_s[None, :] - v_knots[:, None] * W_blk_s[None, :]
        v_s = price_grid[None, :] >= v_knots[:, None] - 1e-12
        opt_s_val = np.take_along_axis(U_blk_s, np.argmax(np.where(v_s, U_blk_s, -np.inf), axis=1)[:, None], axis=1).squeeze(1)
        strat_asks = apply_strategy(v_knots, ask_knots, side="ask")
        u_strat_blk_s = np.interp(strat_asks, price_grid, P_blk_s) - v_knots * np.interp(strat_asks, price_grid, W_blk_s)
        block_avg_s_opt.append(float(np.mean(np.maximum(opt_s_val - u_strat_blk_s, 0.0))))

        # xval trên khối
        u_blk_xb = v_knots * np.interp(br_train_b, price_grid, W_blk_b) - np.interp(br_train_b, price_grid, P_blk_b)
        block_avg_b_xval.append(float(np.mean(u_blk_xb - u_strat_blk_b)))

        u_blk_xs = np.interp(br_train_s, price_grid, P_blk_s) - v_knots * np.interp(br_train_s, price_grid, W_blk_s)
        block_avg_s_xval.append(float(np.mean(u_blk_xs - u_strat_blk_s)))

    def _calc_ci(sample_vals: list[float]) -> tuple[float, float]:
        arr = np.asarray(sample_vals, dtype=float)
        mean_v = float(np.mean(arr))
        std_v = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        se = std_v / np.sqrt(len(arr))
        # Bảng giá trị tới hạn Student-t cho độ tin cậy 95% (hai phía, df = K - 1)
        t_crit = {
            4: 2.7764,
            5: 2.5706,
            6: 2.4469,
            7: 2.3646,
            8: 2.3060,
            9: 2.2622,
            10: 2.2281,
        }.get(len(arr) - 1, 1.96)
        ci_low = max(0.0, mean_v - t_crit * se)
        ci_high = mean_v + t_crit * se
        return (float(ci_low), float(ci_high))

    ci_b_xval = _calc_ci(block_avg_b_xval)
    ci_s_xval = _calc_ci(block_avg_s_xval)
    ci_b_opt = _calc_ci(block_avg_b_opt)
    ci_s_opt = _calc_ci(block_avg_s_opt)

    # Đóng gói kết quả chi tiết
    res_opt_buyer = EpsilonResult({
        "eps_avg": eps_avg_b_opt,
        "eps_max": eps_max_b_opt,
        "eps_rel": eps_rel_b_opt,
        "u_ex_ante": u_ex_b,
        "ci_95": ci_b_opt,
        "ci": ci_b_opt,
        "gain": gain_b_opt,
    })
    res_opt_seller = EpsilonResult({
        "eps_avg": eps_avg_s_opt,
        "eps_max": eps_max_s_opt,
        "eps_rel": eps_rel_s_opt,
        "u_ex_ante": u_ex_s,
        "ci_95": ci_s_opt,
        "ci": ci_s_opt,
        "gain": gain_s_opt,
    })
    eps_opt_overall_rel = max(eps_rel_b_opt, eps_rel_s_opt)
    eps_opt_overall_avg = max(eps_avg_b_opt, eps_avg_s_opt)
    eps_opt_overall_ci = ci_b_opt if eps_avg_b_opt >= eps_avg_s_opt else ci_s_opt
    res_opt = EpsilonResult({
        "eps_avg": eps_opt_overall_avg,
        "eps_max": max(eps_max_b_opt, eps_max_s_opt),
        "eps_rel": eps_opt_overall_rel,
        "ci_95": eps_opt_overall_ci,
        "ci": eps_opt_overall_ci,
        "buyer": res_opt_buyer,
        "seller": res_opt_seller,
    })

    res_xval_buyer = EpsilonResult({
        "eps_avg": eps_avg_b_xval,
        "eps_max": eps_max_b_xval,
        "eps_rel": eps_rel_b_xval,
        "u_ex_ante": u_ex_b,
        "ci_95": ci_b_xval,
        "ci": ci_b_xval,
        "gain": gain_b_xval,
    })
    res_xval_seller = EpsilonResult({
        "eps_avg": eps_avg_s_xval,
        "eps_max": eps_max_s_xval,
        "eps_rel": eps_rel_s_xval,
        "u_ex_ante": u_ex_s,
        "ci_95": ci_s_xval,
        "ci": ci_s_xval,
        "gain": gain_s_xval,
    })
    eps_xval_overall_rel = max(eps_rel_b_xval, eps_rel_s_xval)
    eps_xval_overall_avg = max(eps_avg_b_xval, eps_avg_s_xval)
    eps_xval_overall_ci = ci_b_xval if eps_avg_b_xval >= eps_avg_s_xval else ci_s_xval
    res_xval = EpsilonResult({
        "eps_avg": eps_xval_overall_avg,
        "eps_max": max(eps_max_b_xval, eps_max_s_xval),
        "eps_rel": eps_xval_overall_rel,
        "ci_95": eps_xval_overall_ci,
        "ci": eps_xval_overall_ci,
        "buyer": res_xval_buyer,
        "seller": res_xval_seller,
    })

    return EpsilonResult({
        "eps_opt": res_opt,
        "eps_xval": res_xval,
        "eps_rel": eps_xval_overall_rel,
        "eps_avg": eps_xval_overall_avg,
        "eps_max": max(eps_max_b_xval, eps_max_s_xval),
        "strategy": strategy,
        "m": m,
        "k": k,
        "rule": rule,
        "v_knots": v_knots,
    })
