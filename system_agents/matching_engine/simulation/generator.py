"""Trình tạo dữ liệu ngẫu nhiên cho mô phỏng đấu giá kép (Giai đoạn 2, nhiệm vụ 3)."""

import os
import random
import sys

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)

from model import OrderType, Valued, snap


def generate_valued(
    n: int,
    seed: int,
    low: float = 5.0,
    high: float = 15.0,
    max_amount: int = 50,
    p_buy: float = 0.5,
) -> list[Valued]:
    """Sinh danh sách lệnh tham gia thị trường có valuation ẩn.

    Args:
        n: Số lượng lệnh cần sinh (n >= 2).
        seed: Seed cho bộ sinh số ngẫu nhiên.
        low: Cận dưới khoảng valuation (low < high).
        high: Cận trên khoảng valuation (low < high).
        max_amount: Khối lượng tối đa mỗi lệnh (max_amount >= 1).
        p_buy: Xác suất lệnh là BID (0 <= p_buy <= 1).

    Returns:
        Danh sách n đối tượng Valued.

    Raises:
        ValueError: Nếu các tham số vi phạm điều kiện ràng buộc.
    """
    if n < 2:
        raise ValueError(f"n phải >= 2, nhận được {n}")
    if low >= high:
        raise ValueError(f"low phải < high, nhận được low={low}, high={high}")
    if max_amount < 1:
        raise ValueError(f"max_amount phải >= 1, nhận được {max_amount}")
    if not (0.0 <= p_buy <= 1.0):
        raise ValueError(f"p_buy phải thuộc [0, 1], nhận được {p_buy}")

    rng = random.Random(seed)
    orders: list[Valued] = []

    for i in range(n):
        order_id = f"O{i}"
        arrival = i
        side = OrderType.BID if rng.random() < p_buy else OrderType.ASK
        raw_valuation = rng.uniform(low, high)
        valuation = snap(raw_valuation)
        amount = rng.randint(1, max_amount)

        orders.append(
            Valued(
                order_id=order_id,
                side=side,
                amount=amount,
                valuation=valuation,
                arrival=arrival,
            )
        )

    return orders
