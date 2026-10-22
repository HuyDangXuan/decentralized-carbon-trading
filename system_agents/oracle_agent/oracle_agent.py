"""
Sub-Agent 4: Carbon Oracle & Price Monitoring Agent
Chịu trách nhiệm:
1. Cung cấp giá carbon tham chiếu từ các nguồn dữ liệu thị trường (Benchmark Pricing).
2. Thiết lập biên độ trần/sàn (Circuit Breakers) để tránh thao túng giá.
3. Cảnh báo hành vi wash trading hoặc giá bất thường.
"""

import sys
import time
from typing import Dict, Tuple

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class CarbonOracleAgent:
    def __init__(self):
        # Giá tham chiếu cho các loại dự án ($/tCO2e)
        self.reference_prices: Dict[str, float] = {
            "FORESTRY_AFOLU": 14.50,       # Tín chỉ lâm nghiệp / trồng rừng
            "RENEWABLE_ENERGY": 8.20,      # Năng lượng tái tạo
            "ENERGY_EFFICIENCY": 6.80,     # Tiết kiệm năng lượng công nghiệp
            "COOKSTOVE": 7.50              # Bếp cải tiến cộng đồng
        }
        self.allowed_deviation_pct = 0.40  # Cho phép biên độ dao động +/- 40%

    def get_price_corridor(self, project_type: str) -> Tuple[float, float, float]:
        """Trả về (giá tham chiếu, giá sàn cho phép, giá trần cho phép)"""
        base_price = self.reference_prices.get(project_type, 10.0)
        floor_price = round(base_price * (1 - self.allowed_deviation_pct), 2)
        ceiling_price = round(base_price * (1 + self.allowed_deviation_pct), 2)
        return base_price, floor_price, ceiling_price

    def inspect_order_price(self, project_type: str, order_price: float) -> Tuple[bool, str]:
        """Kiểm tra lệnh đặt giá xem có bất thường hay vi phạm dải giá không"""
        base, floor, ceiling = self.get_price_corridor(project_type)
        if order_price < floor:
            return False, f"CẢNH BÁO: Giá đặt (${order_price}) quá thấp so với giá sàn (${floor})"
        if order_price > ceiling:
            return False, f"CẢNH BÁO: Giá đặt (${order_price}) vượt quá giá trần (${ceiling})"
        return True, "HỢP LỆ: Giá nằm trong dải giao dịch an toàn"

if __name__ == "__main__":
    oracle = CarbonOracleAgent()
    p_type = "FORESTRY_AFOLU"
    base, floor, ceiling = oracle.get_price_corridor(p_type)

    print("--- TÁC TỬ ORACLE & GIÁM SÁT GIÁ CARBON ---")
    print(f"Loại hình tín chỉ: {p_type}")
    print(f"Giá tham chiếu quốc tế: ${base}/tCO2e")
    print(f"Dải giá an toàn: [Sàn: ${floor} <-> Trần: ${ceiling}]")

    test_prices = [5.0, 14.0, 25.0]
    for p in test_prices:
        valid, msg = oracle.inspect_order_price(p_type, p)
        print(f"Kiểm tra lệnh giá ${p:5.2f} -> {msg}")
