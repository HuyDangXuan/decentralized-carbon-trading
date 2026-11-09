"""Mô phỏng thị trường đấu giá kép k-DA vector hóa (Giai đoạn 2, Nhiệm vụ J2).

Tuân thủ hợp đồng anti-missions/contract-c.md (mục J2 và Các quy tắc giá).
Hỗ trợ 3 quy tắc định giá: "pair", "marginal", "kda".
Mọi tính toán vector hóa theo trục kịch bản (không vòng lặp Python theo kịch bản).
"""

from typing import Any, Callable, Sequence, Union
import numpy as np

# Số lượng nút mặc định cho lưới chiến lược
DEFAULT_NUM_KNOTS: int = 41
DEFAULT_V_KNOTS: np.ndarray = np.linspace(0.0, 1.0, DEFAULT_NUM_KNOTS)


def cs_theta(k: float) -> tuple[float, float, float, float]:
    """Hệ số cân bằng tuyến tính Chatterjee–Samuelson: (αb, βb, αs, βs).

    Trùng khớp với công thức đóng và strategies.cs_linear_coeffs:
      αb = k*(1-k) / (2*(1+k))
      βb = 1 / (1+k)
      αs = (1-k) / 2
      βs = 1 / (2-k)

    Args:
        k: Hệ số đấu giá, thuộc (0, 1].

    Returns:
        tuple (alpha_b, beta_b, alpha_s, beta_s).

    Raises:
        ValueError: Nếu k không thuộc (0, 1].
    """
    if not (0.0 < k <= 1.0):
        raise ValueError(f"k phải thuộc (0, 1], nhận được {k}")
    alpha_b = k * (1.0 - k) / (2.0 * (1.0 + k))
    beta_b = 1.0 / (1.0 + k)
    alpha_s = (1.0 - k) / 2.0
    beta_s = 1.0 / (2.0 - k)
    return (alpha_b, beta_b, alpha_s, beta_s)


def theta_to_strategy(
    theta: Sequence[float],
    v_knots: np.ndarray | None = None,
    num_knots: int = DEFAULT_NUM_KNOTS,
) -> tuple[np.ndarray, np.ndarray]:
    """Chuyển đổi tham số tuyến tính θ = (αb, βb, αs, βs) thành chiến lược nút rời rạc.

    Áp dụng kẹp:
      bid = min(v, αb + βb*v)
      ask = max(c, αs + βs*c)

    Args:
        theta: Bộ 4 tham số (alpha_b, beta_b, alpha_s, beta_s).
        v_knots: Mảng nút valuation (mặc định num_knots điểm đều trên [0, 1]).
        num_knots: Số lượng nút đều nếu v_knots là None.

    Returns:
        tuple (bid_knots, ask_knots) tương ứng trên lưới nút.
    """
    if len(theta) != 4:
        raise ValueError(f"theta phải có đúng 4 phần tử, nhận được {len(theta)}")
    if v_knots is None:
        v_knots = np.linspace(0.0, 1.0, num_knots)

    alpha_b, beta_b, alpha_s, beta_s = theta
    bid_knots = np.minimum(v_knots, alpha_b + beta_b * v_knots)
    ask_knots = np.maximum(v_knots, alpha_s + beta_s * v_knots)
    return (bid_knots, ask_knots)


def apply_strategy(
    val: np.ndarray,
    knots: np.ndarray,
    side: str = "bid",
    v_knots: np.ndarray | None = None,
) -> np.ndarray:
    """Nội suy tuyến tính từng đoạn chiến lược trên lưới nút và kẹp chặn.

    Args:
        val: Mảng giá trị valuation thật (hình dạng bất kỳ).
        knots: Mảng giá trị chiến lược tại các nút.
        side: Phía lệnh ("bid" / "buy" hoặc "ask" / "sell").
        v_knots: Mảng nút định nghĩa chiến lược (mặc định chia đều trên [0, 1]).

    Returns:
        Mảng giá khai sau khi kẹp (cùng hình dạng với val).
    """
    if v_knots is None:
        v_knots = np.linspace(0.0, 1.0, len(knots))

    flat_val = val.ravel()
    out = np.interp(flat_val, v_knots, knots).reshape(val.shape)

    side_lower = side.lower()
    if side_lower in ("bid", "buy"):
        return np.minimum(val, out)
    elif side_lower in ("ask", "sell"):
        return np.maximum(val, out)
    else:
        raise ValueError(f"Phía lệnh không hợp lệ: {side}")


def draw_scenarios(
    m: int,
    n_scen: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Sinh kịch bản valuation độc lập đều trên [0, 1] cho m người mua và m người bán.

    Dùng riêng một Generator rng = numpy.random.default_rng(seed) để đảm bảo tính tất định.

    Args:
        m: Số lượng người tham gia mỗi bên (m >= 1).
        n_scen: Số kịch bản cần sinh (n_scen >= 1).
        seed: Hạt giống ngẫu nhiên nguyên.

    Returns:
        tuple (V, C) là 2 mảng ndarray hình dạng (n_scen, m).
    """
    if m < 1:
        raise ValueError(f"m phải >= 1, nhận được {m}")
    if n_scen < 1:
        raise ValueError(f"n_scen phải >= 1, nhận được {n_scen}")

    rng = np.random.default_rng(seed)
    V = rng.uniform(0.0, 1.0, size=(n_scen, m))
    C = rng.uniform(0.0, 1.0, size=(n_scen, m))
    return V, C


def clear(
    bids: np.ndarray,
    asks: np.ndarray,
    k: float,
    rule: str,
    tick: float | None = None,
) -> dict[str, Any]:
    """Khớp lệnh thị trường đấu giá kép và tính toán mức giá khớp.

    Hỗ trợ 3 quy tắc giá theo hợp đồng C:
      - "pair": mỗi cặp ghép hưởng giá k*bid + (1-k)*ask của chính cặp đó.
      - "marginal": mọi cặp cùng giá k*b_m + (1-k)*a_m.
      - "kda": mọi cặp cùng giá p = k*hi + (1-k)*lo với hi = min(b_m, a_next), lo = max(a_m, b_next).

    Vector hóa hoàn toàn theo trục kịch bản. Chấp nhận đầu vào 1D (1 kịch bản) hoặc 2D (n_scen, m).

    Args:
        bids: Mảng giá chào mua (n_scen, m_b) hoặc (m_b,).
        asks: Mảng giá chào bán (n_scen, m_s) hoặc (m_s,).
        k: Hệ số phân chia thặng dư, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        tick: Bước giá làm tròn (tick=None: không làm tròn; tick=0.01: snap bội số của 0.01).

    Returns:
        dict chứa:
          "m_star": Số cặp khớp thành công.
          "price_matrix": Ma trận giá khớp cho các cặp (giá trị 0 nếu không khớp).
          "clearing_price": Mức giá thanh toán thị trường chung (cho rule marginal/kda).
          "total_payment": Tổng số tiền thanh toán của thị trường.
          "hi": Cận trên hi trong quy tắc kda.
          "lo": Cận dưới lo trong quy tắc kda.
          "b_m": Giá bid thấp nhất được khớp.
          "a_m": Giá ask cao nhất được khớp.
    """
    if not (0.0 < k <= 1.0):
        raise ValueError(f"k phải thuộc (0, 1], nhận được {k}")
    if rule not in ("pair", "marginal", "kda"):
        raise ValueError(f"rule phải là 'pair', 'marginal', hoặc 'kda', nhận được '{rule}'")

    is_1d = (bids.ndim == 1 and asks.ndim == 1)
    bids_arr = np.atleast_2d(bids).copy()
    asks_arr = np.atleast_2d(asks).copy()

    if tick is not None and tick > 0:
        bids_arr = np.round(bids_arr / tick) * tick
        asks_arr = np.round(asks_arr / tick) * tick

    n_scen, m_b = bids_arr.shape
    _, m_s = asks_arr.shape
    M = min(m_b, m_s)

    # Sắp xếp bids giảm dần, asks tăng dần theo từng kịch bản
    bids_sorted = np.sort(bids_arr, axis=-1)[:, ::-1]
    asks_sorted = np.sort(asks_arr, axis=-1)

    # Xác định các cặp khớp: bid >= ask
    matched = bids_sorted[:, :M] >= asks_sorted[:, :M]
    m_star = np.sum(matched, axis=-1)  # shape (n_scen,)

    row_idx = np.arange(n_scen)
    m_idx = np.maximum(m_star - 1, 0)

    # b_m: bid thấp nhất khớp; a_m: ask cao nhất khớp
    b_m = np.where(m_star > 0, bids_sorted[row_idx, m_idx], 0.0)
    a_m = np.where(m_star > 0, asks_sorted[row_idx, m_idx], 0.0)

    # b_next: bid cao nhất chưa khớp; a_next: ask thấp nhất chưa khớp
    has_b_next = (m_star < m_b)
    b_next_idx = np.minimum(m_star, m_b - 1)
    b_next = np.where(has_b_next, bids_sorted[row_idx, b_next_idx], -np.inf)

    has_a_next = (m_star < m_s)
    a_next_idx = np.minimum(m_star, m_s - 1)
    a_next = np.where(has_a_next, asks_sorted[row_idx, a_next_idx], np.inf)

    # hi = min(b_m, a_next) (nếu không có a_next thì bằng b_m)
    # lo = max(a_m, b_next) (nếu không có b_next thì bằng a_m)
    hi = np.minimum(b_m, a_next)
    lo = np.maximum(a_m, b_next)

    # Tính toán giá theo từng quy tắc
    if rule == "kda":
        p_unif = k * hi + (1.0 - k) * lo
        p_unif = np.where(m_star > 0, p_unif, 0.0)
        clearing_price = p_unif
        price_matrix = np.where(matched, p_unif[:, None], 0.0)
    elif rule == "marginal":
        p_unif = k * b_m + (1.0 - k) * a_m
        p_unif = np.where(m_star > 0, p_unif, 0.0)
        clearing_price = p_unif
        price_matrix = np.where(matched, p_unif[:, None], 0.0)
    else:  # "pair"
        p_pair = k * bids_sorted[:, :M] + (1.0 - k) * asks_sorted[:, :M]
        price_matrix = np.where(matched, p_pair, 0.0)
        clearing_price = np.where(m_star > 0, price_matrix[row_idx, m_idx], 0.0)

    # Làm tròn giá khớp nếu tick được khai báo
    if tick is not None and tick > 0:
        price_matrix = np.round(price_matrix / tick) * tick
        price_matrix = np.where(matched, price_matrix, 0.0)
        clearing_price = np.round(clearing_price / tick) * tick
        clearing_price = np.where(m_star > 0, clearing_price, 0.0)

    # Đảm bảo bất biến ask <= p <= bid cho mọi cặp khớp
    price_matrix = np.where(
        matched,
        np.clip(price_matrix, asks_sorted[:, :M], bids_sorted[:, :M]),
        0.0,
    )

    total_payment = np.sum(price_matrix, axis=-1)

    if is_1d:
        return {
            "m_star": int(m_star[0]),
            "price_matrix": price_matrix[0],
            "prices": price_matrix[0],
            "clearing_price": float(clearing_price[0]),
            "total_payment": float(total_payment[0]),
            "hi": float(hi[0]),
            "lo": float(lo[0]),
            "b_m": float(b_m[0]),
            "a_m": float(a_m[0]),
            "bids_sorted": bids_sorted[0],
            "asks_sorted": asks_sorted[0],
        }

    return {
        "m_star": m_star,
        "price_matrix": price_matrix,
        "prices": price_matrix,
        "clearing_price": clearing_price,
        "total_payment": total_payment,
        "hi": hi,
        "lo": lo,
        "b_m": b_m,
        "a_m": a_m,
        "bids_sorted": bids_sorted,
        "asks_sorted": asks_sorted,
    }


def welfare(
    V: np.ndarray,
    C: np.ndarray,
    strategy: Any,
    k: float,
    rule: str,
    tick: float | None = None,
) -> np.ndarray:
    """Tính tổng thặng dư xã hội (social welfare) = Σ (v - c) theo valuation thật.

    Vector hóa hoàn toàn theo trục kịch bản.

    Args:
        V: Mảng valuation người mua, hình dạng (n_scen, m).
        C: Mảng chi phí người bán, hình dạng (n_scen, m).
        strategy: Cặp (bid_knots, ask_knots) hoặc tuple 4 tham số θ qua theta_to_strategy.
        k: Hệ số phân chia thặng dư, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        tick: Bước giá làm tròn giá khai (None nếu không làm tròn).

    Returns:
        Mảng 1D hình dạng (n_scen,) chứa welfare cho mỗi kịch bản.
    """
    if isinstance(strategy, (tuple, list)) and len(strategy) == 4 and all(
        isinstance(x, (int, float, np.floating, np.integer)) for x in strategy
    ):
        bid_knots, ask_knots = theta_to_strategy(strategy)
    elif isinstance(strategy, (tuple, list)) and len(strategy) == 2:
        bid_knots, ask_knots = strategy
    else:
        raise ValueError("strategy phải là (bid_knots, ask_knots) hoặc tuple 4 tham số theta")

    bids = apply_strategy(V, bid_knots, side="bid")
    asks = apply_strategy(C, ask_knots, side="ask")

    if tick is not None and tick > 0:
        bids = np.round(bids / tick) * tick
        asks = np.round(asks / tick) * tick

    # Sắp xếp ổn định (stable sort) để bảo tồn thứ tự đến / chỉ số nếu giá trùng nhau
    order_b = np.argsort(-bids, axis=-1, kind="stable")
    order_a = np.argsort(asks, axis=-1, kind="stable")

    bids_sorted = np.take_along_axis(bids, order_b, axis=-1)
    V_sorted = np.take_along_axis(V, order_b, axis=-1)

    asks_sorted = np.take_along_axis(asks, order_a, axis=-1)
    C_sorted = np.take_along_axis(C, order_a, axis=-1)

    M = min(V.shape[-1], C.shape[-1])
    matched = bids_sorted[:, :M] >= asks_sorted[:, :M]

    surplus = (V_sorted[:, :M] - C_sorted[:, :M]) * matched
    return np.sum(surplus, axis=-1)


def max_welfare(V: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Thặng dư xã hội tối đa khả thi (first-best social welfare).

    Xếp người mua giảm dần theo v, người bán tăng dần theo c, ghép khi v >= c.

    Args:
        V: Mảng valuation người mua, hình dạng (n_scen, m).
        C: Mảng chi phí người bán, hình dạng (n_scen, m).

    Returns:
        Mảng 1D hình dạng (n_scen,) chứa thặng dư tối đa.
    """
    V_sorted = np.sort(V, axis=-1)[:, ::-1]
    C_sorted = np.sort(C, axis=-1)
    M = min(V.shape[-1], C.shape[-1])
    gains = np.maximum(V_sorted[:, :M] - C_sorted[:, :M], 0.0)
    return np.sum(gains, axis=-1)


def deviator_utility(
    V: np.ndarray,
    C: np.ndarray,
    strategy: Any,
    k: float,
    rule: str,
    side: str,
    bid_fn_or_grid: Any,
    tick: float | None = None,
    as_grid: bool | None = None,
) -> Union[float, np.ndarray]:
    """Tính tiện ích kỳ vọng của một người chơi lệch (người số 0) bên phía `side`.

    Các người chơi còn lại giữ nguyên chiến lược cơ sở `strategy`.
    Dùng chung toàn bộ kịch bản (V, C) để triệt tiêu phương sai (common random numbers).

    Args:
        V: Mảng valuation người mua, hình dạng (n_scen, m).
        C: Mảng chi phí người bán, hình dạng (n_scen, m).
        strategy: Chiến lược của các người chơi khác (knots hoặc theta).
        k: Hệ số đấu giá, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        side: Phía của người lệch ("buy" / "bid" hoặc "sell" / "ask").
        bid_fn_or_grid: Giá khai cụ thể (float), hàm sinh giá fn(val), hoặc lưới giá.
        tick: Bước giá làm tròn (nếu có).
        as_grid: Ép kiểu đánh giá theo lưới (True) hoặc đơn điểm (False).

    Returns:
        Tiện ích kỳ vọng (float) hoặc mảng tiện ích kỳ vọng trên lưới (ndarray).
    """
    if isinstance(strategy, (tuple, list)) and len(strategy) == 4 and all(
        isinstance(x, (int, float, np.floating, np.integer)) for x in strategy
    ):
        bid_knots, ask_knots = theta_to_strategy(strategy)
    elif isinstance(strategy, (tuple, list)) and len(strategy) == 2:
        bid_knots, ask_knots = strategy
    else:
        raise ValueError("strategy phải là (bid_knots, ask_knots) hoặc tuple 4 tham số theta")

    n_scen, m = V.shape
    bids_base = apply_strategy(V, bid_knots, side="bid")
    asks_base = apply_strategy(C, ask_knots, side="ask")

    side_lower = side.lower()
    is_buyer = side_lower in ("buy", "bid", "buyer")
    is_seller = side_lower in ("sell", "ask", "seller")
    if not (is_buyer or is_seller):
        raise ValueError(f"side phải là 'buy'/'bid' hoặc 'sell'/'ask', nhận được '{side}'")

    def _eval_single(dev_val: float | np.ndarray) -> float:
        bids = bids_base.copy()
        asks = asks_base.copy()

        if is_buyer:
            v0 = V[:, 0]
            if isinstance(dev_val, (int, float, np.floating, np.integer)):
                b0 = np.full(n_scen, float(dev_val))
            else:
                b0 = np.asarray(dev_val)
            b0 = np.minimum(v0, b0)
            bids[:, 0] = b0
        else:
            c0 = C[:, 0]
            if isinstance(dev_val, (int, float, np.floating, np.integer)):
                a0 = np.full(n_scen, float(dev_val))
            else:
                a0 = np.asarray(dev_val)
            a0 = np.maximum(c0, a0)
            asks[:, 0] = a0

        clear_res = clear(bids, asks, k=k, rule=rule, tick=tick)
        m_star = clear_res["m_star"]

        if is_buyer:
            # Tìm vị trí xếp hạng của người mua 0 sau sắp xếp stable
            if tick is not None and tick > 0:
                bids_snapped = np.round(bids / tick) * tick
            else:
                bids_snapped = bids
            order_b = np.argsort(-bids_snapped, axis=-1, kind="stable")
            # rank0 là vị trí của index 0 trong order_b
            rank0 = np.where(order_b == 0)[1]
            matched0 = rank0 < m_star

            if rule == "pair":
                row_idx = np.arange(n_scen)
                asks_sorted = clear_res["asks_sorted"]
                p_dev = k * b0 + (1.0 - k) * asks_sorted[row_idx, np.minimum(rank0, m - 1)]
                if tick is not None and tick > 0:
                    p_dev = np.round(p_dev / tick) * tick
            else:
                p_dev = clear_res["clearing_price"]

            utility = np.where(matched0, v0 - p_dev, 0.0)
            return float(np.mean(utility))
        else:
            # Tìm vị trí xếp hạng của người bán 0 sau sắp xếp stable
            if tick is not None and tick > 0:
                asks_snapped = np.round(asks / tick) * tick
            else:
                asks_snapped = asks
            order_a = np.argsort(asks_snapped, axis=-1, kind="stable")
            rank0 = np.where(order_a == 0)[1]
            matched0 = rank0 < m_star

            if rule == "pair":
                row_idx = np.arange(n_scen)
                bids_sorted = clear_res["bids_sorted"]
                p_dev = k * bids_sorted[row_idx, np.minimum(rank0, m - 1)] + (1.0 - k) * a0
                if tick is not None and tick > 0:
                    p_dev = np.round(p_dev / tick) * tick
            else:
                p_dev = clear_res["clearing_price"]

            utility = np.where(matched0, p_dev - c0, 0.0)
            return float(np.mean(utility))

    # Xử lý theo loại đối số truyền vào
    if callable(bid_fn_or_grid):
        ref_val = V[:, 0] if is_buyer else C[:, 0]
        dev_vals = bid_fn_or_grid(ref_val)
        return _eval_single(dev_vals)

    if isinstance(bid_fn_or_grid, (int, float, np.floating, np.integer)):
        return _eval_single(float(bid_fn_or_grid))

    is_iterable = isinstance(bid_fn_or_grid, (list, tuple, np.ndarray))
    should_be_grid = as_grid if as_grid is not None else (is_iterable and len(bid_fn_or_grid) != n_scen)

    if should_be_grid:
        return np.array([_eval_single(val) for val in bid_fn_or_grid])

    # Trường hợp mảng kịch bản
    return _eval_single(np.asarray(bid_fn_or_grid))


def deviator_outcome(
    V: np.ndarray,
    C: np.ndarray,
    strategy: Any,
    k: float,
    rule: str,
    side: str,
    price_grid: Sequence[float] | np.ndarray,
    tick: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Tính xác suất giao dịch W và khoản thanh toán kỳ vọng P trên lưới giá khai.

    Người lệch là người 0 phía `side` (valuation/cost cột 0 của V/C KHÔNG được dùng).
    Các người chơi còn lại (cột 1..m-1 phía đó và toàn bộ phía kia) chơi `strategy`.
    Dùng chung toàn bộ kịch bản (V, C) để triệt tiêu phương sai (common random numbers).

    Tiện ích kỳ vọng của người lệch khi có valuation v (người mua) hoặc cost c (người bán):
      Người mua: U(v, b) = v * W(b) - P(b)
      Người bán: U(c, a) = P(a) - c * W(a)

    Args:
        V: Mảng valuation người mua, hình dạng (n_scen, m).
        C: Mảng chi phí người bán, hình dạng (n_scen, m).
        strategy: Chiến lược của các người chơi khác ((bid_knots, ask_knots) hoặc theta).
        k: Hệ số đấu giá k-DA, thuộc (0, 1].
        rule: Quy tắc định giá ("pair", "marginal", "kda").
        side: Phía của người lệch ("buy" / "bid" hoặc "sell" / "ask").
        price_grid: Lưới giá khai cần đánh giá (1D sequence hoặc ndarray).
        tick: Bước giá làm tròn (None nếu liên tục).

    Returns:
        tuple (win_prob, exp_pay):
          win_prob: Mảng 1D xác suất khớp lệnh W(price) tương ứng từng giá trên price_grid.
          exp_pay: Mảng 1D khoản trả/nhận kỳ vọng P(price) tương ứng từng giá trên price_grid.

    Raises:
        ValueError: Nếu k, rule, side hoặc strategy không hợp lệ.
    """
    if not (0.0 < k <= 1.0):
        raise ValueError(f"k phải thuộc (0, 1], nhận được {k}")
    if rule not in ("pair", "marginal", "kda"):
        raise ValueError(f"rule phải là 'pair', 'marginal', hoặc 'kda', nhận được '{rule}'")

    if isinstance(strategy, (tuple, list)) and len(strategy) == 4 and all(
        isinstance(x, (int, float, np.floating, np.integer)) for x in strategy
    ):
        bid_knots, ask_knots = theta_to_strategy(strategy)
    elif isinstance(strategy, (tuple, list)) and len(strategy) == 2:
        bid_knots, ask_knots = strategy
    else:
        raise ValueError("strategy phải là (bid_knots, ask_knots) hoặc tuple 4 tham số theta")

    side_lower = side.lower()
    is_buyer = side_lower in ("buy", "bid", "buyer")
    is_seller = side_lower in ("sell", "ask", "seller")
    if not (is_buyer or is_seller):
        raise ValueError(f"side phải là 'buy'/'bid' hoặc 'sell'/'ask', nhận được '{side}'")

    n_scen, m = V.shape
    bids = apply_strategy(V, bid_knots, side="bid")
    asks = apply_strategy(C, ask_knots, side="ask")

    grid_arr = np.asarray(price_grid, dtype=float)
    n_grid = len(grid_arr)

    win_prob = np.zeros(n_grid, dtype=float)
    exp_pay = np.zeros(n_grid, dtype=float)
    row_idx = np.arange(n_scen)

    for g in range(n_grid):
        p_val = float(grid_arr[g])
        if is_buyer:
            bids[:, 0] = p_val
            clear_res = clear(bids, asks, k=k, rule=rule, tick=tick)
            m_star = clear_res["m_star"]

            if tick is not None and tick > 0:
                bids_snapped = np.round(bids / tick) * tick
            else:
                bids_snapped = bids
            order_b = np.argsort(-bids_snapped, axis=-1, kind="stable")
            rank0 = np.where(order_b == 0)[1]
            matched0 = rank0 < m_star

            if rule == "pair":
                asks_sorted = clear_res["asks_sorted"]
                p_dev = k * p_val + (1.0 - k) * asks_sorted[row_idx, np.minimum(rank0, m - 1)]
                if tick is not None and tick > 0:
                    p_dev = np.round(p_dev / tick) * tick
            else:
                p_dev = clear_res["clearing_price"]

            win_prob[g] = float(np.mean(matched0))
            exp_pay[g] = float(np.mean(np.where(matched0, p_dev, 0.0)))
        else:
            asks[:, 0] = p_val
            clear_res = clear(bids, asks, k=k, rule=rule, tick=tick)
            m_star = clear_res["m_star"]

            if tick is not None and tick > 0:
                asks_snapped = np.round(asks / tick) * tick
            else:
                asks_snapped = asks
            order_a = np.argsort(asks_snapped, axis=-1, kind="stable")
            rank0 = np.where(order_a == 0)[1]
            matched0 = rank0 < m_star

            if rule == "pair":
                bids_sorted = clear_res["bids_sorted"]
                p_dev = k * bids_sorted[row_idx, np.minimum(rank0, m - 1)] + (1.0 - k) * p_val
                if tick is not None and tick > 0:
                    p_dev = np.round(p_dev / tick) * tick
            else:
                p_dev = clear_res["clearing_price"]

            win_prob[g] = float(np.mean(matched0))
            exp_pay[g] = float(np.mean(np.where(matched0, p_dev, 0.0)))

    return win_prob, exp_pay

