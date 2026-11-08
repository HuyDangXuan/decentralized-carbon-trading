"""Kiểu dữ liệu dùng chung cho bộ mô phỏng thực nghiệm đấu giá kép (Giai đoạn 2, nhiệm vụ 3)."""

import os
import sys
from dataclasses import dataclass

_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from order_book import MatchResult, Order, OrderType  # noqa: E402,F401

TICK = 0.01
TOKEN_ID = 101


@dataclass(frozen=True)
class Valued:
    """Người tham gia có valuation ẩn: BID = mức tối đa sẵn sàng trả, ASK = chi phí tối thiểu."""

    order_id: str
    side: OrderType
    amount: int
    valuation: float
    arrival: int


def snap(price: float) -> float:
    """Làm tròn giá về bội số của TICK."""
    return round(round(price / TICK) * TICK, 2)


def to_order(v: Valued, price: float) -> Order:
    """Tạo Order mới (không dùng chung đối tượng) từ Valued và giá khai."""
    return Order(
        order_id=v.order_id,
        trader_id=v.order_id,
        order_type=v.side,
        token_id=TOKEN_ID,
        amount=v.amount,
        price=snap(price),
        timestamp=float(v.arrival),
    )
