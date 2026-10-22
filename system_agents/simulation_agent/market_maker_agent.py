"""
Sub-Agent 2: Market Simulation / Market Maker Agent
Mô phỏng các tác tử giao dịch tự động (Trading Bots) đại diện cho:
- Doanh nghiệp phát thải (Emitters / Buyers)
- Dự án giảm phát thải (Green Projects / Sellers)
Sử dụng cho pha thực nghiệm và kiểm thử tải của hệ thống.
"""

import os
import sys
import random
import time
from typing import List

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

engine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "matching_engine"))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from order_book import Order, OrderType
from auction_agent import DoubleAuctionAgent

class SimulatedTraderAgent:
    def __init__(self, trader_id: str, trader_type: str, budget: float, valuation: float):
        self.trader_id = trader_id
        self.trader_type = trader_type  # "BUYER" hoặc "SELLER"
        self.budget = budget
        self.valuation = valuation      # Giá trị kỳ vọng nội tại (True valuation)
        self.profit_margin = random.uniform(0.05, 0.20)  # Biên độ kỳ vọng 5% - 20%

    def generate_order(self, token_id: int) -> Order:
        """Tạo lệnh chào mua hoặc chào bán dựa trên chiến lược lợi nhuận"""
        amount = random.randint(10, 100)
        if self.trader_type == "BUYER":
            # Người mua muốn mua dưới giá định giá của mình
            price = round(self.valuation * (1 - self.profit_margin), 2)
            return Order(
                order_id=f"BID_{self.trader_id}_{int(time.time()*1000)%10000}",
                trader_id=self.trader_id,
                order_type=OrderType.BID,
                token_id=token_id,
                amount=amount,
                price=price
            )
        else:
            # Người bán muốn bán trên giá thành chi phí (valuation) của mình
            price = round(self.valuation * (1 + self.profit_margin), 2)
            return Order(
                order_id=f"ASK_{self.trader_id}_{int(time.time()*1000)%10000}",
                trader_id=self.trader_id,
                order_type=OrderType.ASK,
                token_id=token_id,
                amount=amount,
                price=price
            )

def run_simulation(num_buyers=10, num_sellers=10, token_id=101):
    auction_engine = DoubleAuctionAgent(k_parameter=0.5)

    buyers = [
        SimulatedTraderAgent(f"Buyer_{i+1}", "BUYER", budget=50000, valuation=random.uniform(11.0, 16.0))
        for i in range(num_buyers)
    ]
    sellers = [
        SimulatedTraderAgent(f"Seller_{j+1}", "SELLER", budget=0, valuation=random.uniform(8.0, 12.0))
        for j in range(num_sellers)
    ]

    print(f"=== KHỞI CHẠY MÔ PHỎNG THỊ TRƯỜNG: {num_buyers} NGƯỜI MUA x {num_sellers} NGƯỜI BÁN ===")

    for b in buyers:
        order = b.generate_order(token_id)
        auction_engine.submit_order(order)

    for s in sellers:
        order = s.generate_order(token_id)
        auction_engine.submit_order(order)

    matches = auction_engine.run_periodic_double_auction(token_id)

    total_volume = sum(m.amount for m in matches)
    total_value = sum(m.amount * m.clearing_price for m in matches)
    avg_price = total_value / total_volume if total_volume > 0 else 0

    print(f"\n[KẾT QUẢ KHỚP LỆNH THỰC NGHIỆM]")
    print(f"- Số lượt khớp lệnh: {len(matches)}")
    print(f"- Tổng khối lượng giao dịch: {total_volume} tCO2e")
    print(f"- Tổng giá trị giao dịch: ${total_value:,.2f}")
    print(f"- Giá thanh toán trung bình: ${avg_price:.2f} / tCO2e")

    return matches

if __name__ == "__main__":
    run_simulation(num_buyers=8, num_sellers=8, token_id=101)
