"""
Sub-Agent 1: Auction & Matching Agent (Tác tử Khớp lệnh & Tối ưu Đấu giá kép định kỳ).

Quản lý sổ lệnh và chạy phiên đấu giá kép định kỳ theo ADR-001 / SRS (FR-06, FR-07, FR-08, FR-09)
bằng lõi số nguyên `session_engine.py` (thay cho bản float cũ, nay nằm ở
`simulation/baseline_agent.py` chỉ để đối chứng thực nghiệm).

Quy ước dữ liệu (README, mục 3):
- `Order.amount`: số nguyên tCO2e (1 token = 1 tCO2e, decimals = 0).
- `Order.price` và `MatchResult.clearing_price`: số nguyên micro-USDC cho mỗi tCO2e (tick = 1).
- Số thực bị từ chối ở `submit_order` để không còn lỗi làm tròn đưa giá ra ngoài dải [ask, bid].

Giới hạn (bản mock, chưa nối blockchain):
- Coi như settlement luôn thành công ngay sau khi khớp (chưa có PENDING_SETTLEMENT / in-flight).
- Chưa kiểm số dư, nonce, hủy on-chain; chỉ kiểm cấu trúc, hạn (`deadline`) và trùng `order_id`.
"""

import sys
import time
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Callable, Dict, List, Optional

from order_book import MatchResult, Order, OrderType
from session_engine import BookOrder, end_session, match_session

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ----- Tham số kiến trúc đã khóa ở ADR-001 (10/11/2026) -----
TIE_BREAK = "age_prorata"  # Quyết định 2: age_prorata + Hamilton, phần dư bằng nhau thì FIFO
# Quyết định 3: P* = floor((b_M + s_M) / 2). Công thức này trong session_engine là quy tắc
# "marginal" (ADR gọi là "kda"); quy tắc "kda" của engine dùng thêm lệnh biên kế tiếp và khác
# công thức ADR. Muốn đổi chỉ cần sửa hằng số này (xem docs/VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md).
PRICING_RULE = "marginal"
ROUNDING = "floor"
# Quyết định 4: rollover_count >= 3 thì EXPIRED, tức lệnh GTC sống tối đa 3 phiên.
MAX_ROLLOVER_SESSIONS = 3


class OrderStatus(str, Enum):
    NEW = "NEW"
    ROLLED_OVER = "ROLLED_OVER"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


ACTIVE_STATUSES = (OrderStatus.NEW, OrderStatus.ROLLED_OVER)


@dataclass
class OrderRecord:
    """Trạng thái nội bộ của một lệnh. `Order` nhận vào không bao giờ bị sửa."""

    order: Order
    seq: int  # thứ tự đến do engine gán (FIFO), người dùng không điều khiển được
    remaining_amount: int
    rollover_count: int = 0
    filled_amount: int = 0
    status: OrderStatus = OrderStatus.NEW


class DoubleAuctionAgent:
    def __init__(
        self,
        k_parameter: float = 0.5,
        pricing: str = PRICING_RULE,
        max_rollover_sessions: int = MAX_ROLLOVER_SESSIONS,
        now_fn: Callable[[], float] = time.time,
    ):
        """
        k_parameter: hệ số k-DA trong [0, 1] (mặc định 0,5 = giá giữa). Được đổi thành phân số
        k_num/k_den để tính giá bằng số nguyên.
        """
        if not 0 <= k_parameter <= 1:
            raise ValueError(f"k_parameter must be in [0, 1], got {k_parameter}")
        if max_rollover_sessions < 1:
            raise ValueError(f"max_rollover_sessions must be >= 1, got {max_rollover_sessions}")
        frac = Fraction(k_parameter).limit_denominator(1000)
        self.k_num, self.k_den = frac.numerator, frac.denominator
        self.pricing = pricing
        self.max_rollover_sessions = max_rollover_sessions
        self._now = now_fn
        self._records: Dict[str, OrderRecord] = {}
        self._next_seq = 1
        self.session_id = 0
        self.matches: Dict[int, List[MatchResult]] = {}

    # ------------------------------------------------------------------ lệnh
    def submit_order(self, order: Order) -> OrderRecord:
        """Đưa lệnh vào sổ lệnh. Ném ValueError nếu lệnh không hợp lệ."""
        if not isinstance(order.order_type, OrderType):
            raise ValueError(f"order_type must be OrderType, got {order.order_type!r}")
        for name, value in (("amount", order.amount), ("price", order.price)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer (price in micro-USDC), got {value!r}")
            if value <= 0:
                raise ValueError(f"{name} must be > 0, got {value}")
        if isinstance(order.token_id, bool) or not isinstance(order.token_id, int):
            raise ValueError(f"token_id must be an integer, got {order.token_id!r}")
        if order.time_in_force not in ("GTC", "IOC"):
            raise ValueError(f"time_in_force must be GTC or IOC, got {order.time_in_force!r}")
        if order.deadline is not None and order.deadline <= self._now():
            raise ValueError(f"order {order.order_id} already past its deadline")
        if order.order_id in self._records:
            raise ValueError(f"Duplicate order_id: {order.order_id}")

        record = OrderRecord(order=order, seq=self._next_seq, remaining_amount=order.amount)
        self._next_seq += 1
        self._records[order.order_id] = record
        return record

    def cancel_order(self, order_id: str) -> OrderRecord:
        """Rút lệnh khỏi các phiên sau (hủy mềm ngoài chuỗi)."""
        record = self._records.get(order_id)
        if record is None:
            raise KeyError(order_id)
        if record.status not in ACTIVE_STATUSES:
            raise ValueError(f"order {order_id} is already {record.status.value}")
        record.status = OrderStatus.CANCELLED
        return record

    def get_order(self, order_id: str) -> OrderRecord:
        return self._records[order_id]

    def snapshot(self, token_id: int) -> Dict[str, List[Dict[str, int]]]:
        """Độ sâu sổ lệnh theo mức giá: bids giảm dần, asks tăng dần."""
        sides: Dict[OrderType, Dict[int, List[int]]] = {OrderType.BID: {}, OrderType.ASK: {}}
        for r in self._records.values():
            if r.status in ACTIVE_STATUSES and r.order.token_id == token_id:
                level = sides[r.order.order_type].setdefault(r.order.price, [0, 0])
                level[0] += r.remaining_amount
                level[1] += 1

        def rows(side: OrderType, reverse: bool) -> List[Dict[str, int]]:
            return [
                {"price": p, "amount": a, "orders": n}
                for p, (a, n) in sorted(sides[side].items(), reverse=reverse)
            ]

        return {"bids": rows(OrderType.BID, True), "asks": rows(OrderType.ASK, False)}

    # ----------------------------------------------------------------- phiên
    def _expire_past_deadline(self, token_id: int) -> None:
        now = self._now()
        for r in self._records.values():
            if (
                r.status in ACTIVE_STATUSES
                and r.order.token_id == token_id
                and r.order.deadline is not None
                and r.order.deadline <= now
            ):
                r.status = OrderStatus.EXPIRED

    def run_periodic_double_auction(self, token_id: int) -> List[MatchResult]:
        """Chạy một phiên cho `token_id`, cập nhật vòng đời lệnh và trả về các khớp (giá nguyên)."""
        self._expire_past_deadline(token_id)
        active = [
            r for r in self._records.values()
            if r.status in ACTIVE_STATUSES and r.order.token_id == token_id
        ]
        book = [
            BookOrder(
                order_id=r.order.order_id,
                side=r.order.order_type.value,
                price_ticks=r.order.price,
                remaining=r.remaining_amount,
                sessions_alive=r.rollover_count,
                seq=r.seq,
                tif=r.order.time_in_force,
            )
            for r in active
        ]

        fills = match_session(book, self.k_num, self.k_den, TIE_BREAK, self.pricing, ROUNDING)
        # Hợp đồng revert SelfTradingNotAllowed nếu người mua trùng người bán: bỏ các khớp đó,
        # phần khối lượng này không được khớp và đi tiếp theo vòng đời bình thường.
        fills = [
            f for f in fills
            if self._records[f.bid_id].order.trader_id != self._records[f.ask_id].order.trader_id
        ]
        outcomes = end_session(book, fills, max_rollover=self.max_rollover_sessions - 1)

        matched: Dict[str, int] = {}
        for f in fills:
            matched[f.bid_id] = matched.get(f.bid_id, 0) + f.amount
            matched[f.ask_id] = matched.get(f.ask_id, 0) + f.amount
        for order_id, status, new_order in outcomes:
            record = self._records[order_id]
            taken = matched.get(order_id, 0)
            record.remaining_amount -= taken
            record.filled_amount += taken
            record.status = OrderStatus(status)
            if new_order is not None:
                record.rollover_count = new_order.sessions_alive

        self.session_id += 1
        results = [
            MatchResult(
                bid_order_id=f.bid_id,
                ask_order_id=f.ask_id,
                token_id=token_id,
                amount=f.amount,
                clearing_price=f.price_ticks,
                session_id=self.session_id,
            )
            for f in fills
        ]
        self.matches[self.session_id] = results
        return results


if __name__ == "__main__":
    agent = DoubleAuctionAgent(k_parameter=0.5)
    usd = 1_000_000  # 1 USD = 10^6 micro-USDC

    # Lệnh chào Bán (token 101)
    agent.submit_order(Order("ASK_1", "Forest_Corp", OrderType.ASK, 101, 100, 10 * usd))
    agent.submit_order(Order("ASK_2", "Solar_Farm", OrderType.ASK, 101, 200, 11_500_000))
    # Lệnh chào Mua
    agent.submit_order(Order("BID_1", "Steel_Company", OrderType.BID, 101, 150, 12 * usd))
    agent.submit_order(Order("BID_2", "Cement_Company", OrderType.BID, 101, 100, 10_500_000))

    print("--- CHẠY THỬ NGHIỆM ĐẤU GIÁ KÉP ĐỊNH KỲ (ADR-001) ---")
    for idx, match in enumerate(agent.run_periodic_double_auction(token_id=101), 1):
        print(f"Khớp lệnh #{idx}: Mua [{match.bid_order_id}] x Bán [{match.ask_order_id}]")
        print(f"  -> Khối lượng: {match.amount} tCO2e | Giá khớp: {match.clearing_price} micro-USDC/tCO2e")
