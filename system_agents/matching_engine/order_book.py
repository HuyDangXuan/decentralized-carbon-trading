from dataclasses import dataclass, field
from enum import Enum
import time
from typing import List, Optional

class OrderType(Enum):
    BID = "BID"  # Lệnh Mua
    ASK = "ASK"  # Lệnh Bán

@dataclass
class Order:
    order_id: str
    trader_id: str
    order_type: OrderType
    token_id: int        # ID của lô tín chỉ carbon (ERC-1155)
    amount: int          # Khối lượng tín chỉ (tấn CO2 tương đương - tCO2e)
    price: float         # Giá đặt mua tối đa hoặc giá chào bán tối thiểu (USD hoặc Token thanh toán)
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None  # Chữ ký số EIP-712 xác thực từ ví người dùng

@dataclass
class MatchResult:
    bid_order_id: str
    ask_order_id: str
    token_id: int
    amount: int
    clearing_price: float
    timestamp: float = field(default_factory=time.time)
