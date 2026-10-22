"""
Sub-Agent 1: Auction & Matching Agent (Tác tử Khớp lệnh & Tối ưu Đấu giá kép)
Chịu trách nhiệm quản lý Sổ lệnh (OrderBook), thực hiện thuật toán Đấu giá kép (Double Auction)
và tạo bằng chứng khớp lệnh để thanh quyết toán trên Smart Contract.
"""

import sys
from typing import List, Tuple
from order_book import Order, OrderType, MatchResult

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class DoubleAuctionAgent:
    def __init__(self, k_parameter: float = 0.5):
        """
        k_parameter: Hệ số trong k-Double Auction rule (0 <= k <= 1).
        k = 0.5: Mid-price settlement (Giá thanh toán là trung bình giữa giá mua và bán).
        k = 0: Giá thanh toán theo giá chào bán (thuận lợi cho người mua).
        k = 1: Giá thanh toán theo giá chào mua (thuận lợi cho người bán).
        """
        self.k = k_parameter
        self.bids: List[Order] = []
        self.asks: List[Order] = []

    def submit_order(self, order: Order) -> None:
        """Đưa lệnh vào sổ lệnh"""
        if order.order_type == OrderType.BID:
            self.bids.append(order)
            # Sắp xếp lệnh mua giảm dần theo giá (người mua trả cao nhất ưu tiên trước)
            self.bids.sort(key=lambda x: (-x.price, x.timestamp))
        else:
            self.asks.append(order)
            # Sắp xếp lệnh bán tăng dần theo giá (người bán giá thấp nhất ưu tiên trước)
            self.asks.sort(key=lambda x: (x.price, x.timestamp))

    def run_periodic_double_auction(self, token_id: int) -> List[MatchResult]:
        """
        Khớp lệnh đấu giá kép định kỳ (Periodic Double Auction - PDA)
        cho một loại tín chỉ carbon (token_id).
        """
        filtered_bids = [b for b in self.bids if b.token_id == token_id and b.amount > 0]
        filtered_asks = [a for a in self.asks if a.token_id == token_id and a.amount > 0]

        matches: List[MatchResult] = []
        i, j = 0, 0

        while i < len(filtered_bids) and j < len(filtered_asks):
            best_bid = filtered_bids[i]
            best_ask = filtered_asks[j]

            # Điều kiện khớp: Giá mua >= Giá bán
            if best_bid.price >= best_ask.price:
                match_amount = min(best_bid.amount, best_ask.amount)
                # Tính mức giá thị trường cân bằng (Market-Clearing Price theo k-rule)
                clearing_price = self.k * best_bid.price + (1 - self.k) * best_ask.price

                match = MatchResult(
                    bid_order_id=best_bid.order_id,
                    ask_order_id=best_ask.order_id,
                    token_id=token_id,
                    amount=match_amount,
                    clearing_price=round(clearing_price, 2)
                )
                matches.append(match)

                # Cập nhật số lượng còn lại
                best_bid.amount -= match_amount
                best_ask.amount -= match_amount

                if best_bid.amount == 0:
                    i += 1
                if best_ask.amount == 0:
                    j += 1
            else:
                # Không còn cặp nào có giá mua >= giá bán
                break

        # Cập nhật lại danh sách lệnh sau khi khớp
        self.bids = [b for b in self.bids if b.amount > 0]
        self.asks = [a for a in self.asks if a.amount > 0]

        return matches


if __name__ == "__main__":
    agent = DoubleAuctionAgent(k_parameter=0.5)

    # Giả lập lệnh chào Bán (Dự án trồng rừng, tín chỉ Vintage 2026, Token ID: 101)
    agent.submit_order(Order(order_id="ASK_1", trader_id="Forest_Corp", order_type=OrderType.ASK, token_id=101, amount=100, price=10.0))
    agent.submit_order(Order(order_id="ASK_2", trader_id="Solar_Farm", order_type=OrderType.ASK, token_id=101, amount=200, price=11.5))

    # Giả lập lệnh chào Mua (Nhà máy nhiệt điện / xi măng cần bù trừ phát thải)
    agent.submit_order(Order(order_id="BID_1", trader_id="Steel_Company", order_type=OrderType.BID, token_id=101, amount=150, price=12.0))
    agent.submit_order(Order(order_id="BID_2", trader_id="Cement_Company", order_type=OrderType.BID, token_id=101, amount=100, price=10.5))

    print("--- CHẠY THỬ NGHIỆM ĐẤU GIÁ KÉP (DOUBLE AUCTION AGENT) ---")
    results = agent.run_periodic_double_auction(token_id=101)

    for idx, match in enumerate(results, 1):
        print(f"Khớp lệnh #{idx}: Mua [{match.bid_order_id}] x Bán [{match.ask_order_id}]")
        print(f"  -> Khối lượng: {match.amount} tCO2e | Giá khớp: ${match.clearing_price}/tCO2e")
