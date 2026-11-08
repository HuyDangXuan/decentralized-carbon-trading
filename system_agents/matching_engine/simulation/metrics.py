"""Các chỉ số và hàm chạy đấu giá cho bộ mô phỏng thực nghiệm (Giai đoạn 2, nhiệm vụ 3)."""

import os
import sys
from typing import Callable

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)

from model import MatchResult, OrderType, TOKEN_ID, Valued, to_order
from auction_agent import DoubleAuctionAgent


def truthful(v: Valued) -> float:
    """Chiến lược khai giá trung thực: trả về đúng valuation thực tế."""
    return v.valuation


def run_auction(
    valued: list[Valued],
    k: float,
    price_fn: Callable[[Valued], float] = truthful,
) -> list[MatchResult]:
    """Chạy phiên đấu giá kép với hệ số k và hàm sinh giá khai.

    Tạo Order mới bằng to_order theo thứ tự arrival, không làm thay đổi
    đối tượng Valued đầu vào.
    """
    sorted_valued = sorted(valued, key=lambda v: v.arrival)
    agent = DoubleAuctionAgent(k_parameter=k)

    for v in sorted_valued:
        price = price_fn(v)
        order = to_order(v, price)
        agent.submit_order(order)

    return agent.run_periodic_double_auction(TOKEN_ID)


def welfare(matches: list[MatchResult], valued: list[Valued]) -> float:
    """Tính tổng thặng dư xã hội (social welfare):

    welfare = Σ (valuation[bid] − valuation[ask]) · amount
    Làm tròn 6 chữ số thập phân.
    """
    val_map = {v.order_id: v.valuation for v in valued}
    total = sum((val_map[m.bid_order_id] - val_map[m.ask_order_id]) * m.amount for m in matches)
    return round(float(total), 6)


def buyer_surplus(matches: list[MatchResult], valued: list[Valued]) -> float:
    """Tính thặng dư của người mua:

    buyer_surplus = Σ (valuation[bid] − clearing_price) · amount
    Làm tròn 6 chữ số thập phân.
    """
    val_map = {v.order_id: v.valuation for v in valued}
    total = sum((val_map[m.bid_order_id] - m.clearing_price) * m.amount for m in matches)
    return round(float(total), 6)


def seller_surplus(matches: list[MatchResult], valued: list[Valued]) -> float:
    """Tính thặng dư của người bán:

    seller_surplus = Σ (clearing_price − valuation[ask]) · amount
    Làm tròn 6 chữ số thập phân.
    """
    val_map = {v.order_id: v.valuation for v in valued}
    total = sum((m.clearing_price - val_map[m.ask_order_id]) * m.amount for m in matches)
    return round(float(total), 6)


def volume(matches: list[MatchResult]) -> int:
    """Tổng khối lượng tín chỉ carbon đã khớp: volume = Σ amount."""
    return int(sum(m.amount for m in matches))


def _compute_efficient_allocation(valued: list[Valued]) -> tuple[float, int]:
    """Tính phân bổ hiệu quả tối đa theo đơn vị (multi-unit efficient allocation).

    Bên mua xếp giảm dần theo valuation, bên bán xếp tăng dần.
    Ghép lần lượt trong khi valuation mua >= chi phí bán (sai số 1e-6).
    """
    bids: list[list[float | int]] = [
        [v.valuation, v.amount] for v in valued if v.side == OrderType.BID and v.amount > 0
    ]
    asks: list[list[float | int]] = [
        [v.valuation, v.amount] for v in valued if v.side == OrderType.ASK and v.amount > 0
    ]

    # Bên mua giảm dần theo valuation
    bids.sort(key=lambda x: -float(x[0]))
    # Bên bán tăng dần theo valuation (chi phí)
    asks.sort(key=lambda x: float(x[0]))

    total_welfare = 0.0
    matched_units = 0
    i, j = 0, 0

    while i < len(bids) and j < len(asks):
        bid_val = float(bids[i][0])
        bid_amt = int(bids[i][1])
        ask_val = float(asks[j][0])
        ask_amt = int(asks[j][1])

        # Ghép trong khi valuation mua không thấp hơn chi phí bán (khớp bid == ask như engine;
        # lãi bằng 0 nên không đổi welfare, nhưng giữ fill_rate <= 1 với bid trung thực)
        if bid_val - ask_val > -1e-6:
            match_amt = min(bid_amt, ask_amt)
            total_welfare += (bid_val - ask_val) * match_amt
            matched_units += match_amt

            bids[i][1] = bid_amt - match_amt
            asks[j][1] = ask_amt - match_amt

            if bids[i][1] == 0:
                i += 1
            if asks[j][1] == 0:
                j += 1
        else:
            break

    return round(float(total_welfare), 6), matched_units


def max_welfare(valued: list[Valued]) -> float:
    """Thặng dư xã hội tối đa khả thi từ toàn bộ valuation của các lệnh."""
    total_w, _ = _compute_efficient_allocation(valued)
    return total_w


def efficient_volume(valued: list[Valued]) -> int:
    """Khối lượng giao dịch hiệu quả tối đa (số đơn vị khớp trong phân bổ tối ưu)."""
    _, eff_vol = _compute_efficient_allocation(valued)
    return eff_vol


def fill_rate(matches: list[MatchResult], valued: list[Valued]) -> float:
    """Tỷ lệ lấp đầy thị trường so với mức chuẩn hiệu quả tối đa:

    fill_rate = volume / efficient_volume; nếu efficient_volume == 0 thì trả về 1.0.
    Làm tròn 6 chữ số thập phân.
    """
    eff_vol = efficient_volume(valued)
    if eff_vol == 0:
        return 1.0
    return round(float(volume(matches) / eff_vol), 6)
