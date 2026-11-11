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
    # Giá đặt mua tối đa hoặc giá chào bán tối thiểu. Với `DoubleAuctionAgent` (ADR-001) phải là
    # số nguyên micro-USDC mỗi tCO2e; baseline mô phỏng cũ vẫn dùng số thực USD.
    price: float
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None  # Chữ ký số EIP-712 xác thực từ ví người dùng
    time_in_force: str = "GTC"       # "GTC" | "IOC" (ADR-001, Quyết định 4)
    deadline: Optional[int] = None   # Unix time hết hạn chữ ký (giây); None = không giới hạn

@dataclass
class MatchResult:
    bid_order_id: str
    ask_order_id: str
    token_id: int
    amount: int
    clearing_price: float  # DoubleAuctionAgent: số nguyên micro-USDC mỗi tCO2e
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[int] = None
