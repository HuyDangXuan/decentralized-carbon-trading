"""Chiến lược khai giá cho mô phỏng đấu giá kép (Giai đoạn 2, nhiệm vụ 3).

Thí nghiệm B: Khai giá chiến lược (Strategic Bidding).
Tuân thủ hợp đồng trong CONTRACT.md (mục strategies.py).

Giới hạn:
Hệ số CS_NUMERIC là cân bằng tuyến tính của thị trường 1 mua – 1 bán, một đơn vị; áp dụng
cho nhiều lệnh nhiều đơn vị chỉ là heuristic. lam là tham số quét, không phải
cân bằng của thị trường nhiều lệnh. Cân bằng của k-double auction không duy nhất.
"""

import os
import sys
from typing import Callable, Union

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
_ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from model import OrderType, Valued  # noqa: E402

LOW: float = 5.0
HIGH: float = 15.0

Coeffs = dict[OrderType, tuple[float, float]]

BID = OrderType.BID
ASK = OrderType.ASK

# Cân bằng tuyến tính Chatterjee–Samuelson cho 1 mua – 1 bán, valuation đều trên [0, 1], k = 0.5
CS_K05: Coeffs = {
    BID: (1 / 12, 2 / 3),
    ASK: (1 / 4, 2 / 3),
}

def cs_linear_coeffs(k: float) -> Coeffs:
    """Cân bằng tuyến tính (dạng đóng) của k-double auction, 1 mua – 1 bán, valuation đều trên [0, 1].

    Suy ra từ điều kiện bậc nhất của từng phía, giả sử đối tác dùng chiến lược tuyến tính:
      bid = (v + k*g) / (1 + k)                       (g = hệ số chặn của ask)
      ask = (c + (1 - k)*(a + b)) / (2 - k)           (a, b = hệ số chặn, độ dốc của bid)
    Giải hệ cho (a, b, g, d). Với k = 0.5 trả đúng (1/12, 2/3) và (1/4, 2/3) của Chatterjee-Samuelson.
    Đã kiểm lại bằng tìm phản ứng tối ưu số (test_strategies); CHƯA đối chiếu với bài gốc.
    Nghiệm tuyến tính không duy nhất: đây chỉ là một cân bằng. Hợp lệ với 0 < k < 1.
    """
    if not (0.0 < k < 1.0):
        raise ValueError(f"k phải thuộc (0, 1), nhận được {k}")
    b_slope = 1.0 / (1.0 + k)
    d_slope = 1.0 / (2.0 - k)
    # a = k*g/(1+k) và g = (1-k)*(a+b)/(2-k)  =>  g = (1-k)*b / ((2-k) - (1-k)*k/(1+k))
    g = (1.0 - k) * b_slope / ((2.0 - k) - (1.0 - k) * k / (1.0 + k))
    a = k * g / (1.0 + k)
    return {BID: (a, b_slope), ASK: (g, d_slope)}


# Khóa 0.25, 0.5, 0.75; dạng đóng của cs_linear_coeffs (CS_K05 là hằng số tham chiếu của k = 0.5).
CS_NUMERIC: dict[float, Coeffs] = {
    0.25: cs_linear_coeffs(0.25),
    0.5: CS_K05,
    0.75: cs_linear_coeffs(0.75),
}


def linear_price_fn(
    coeffs: Union[Coeffs, float, int],
    lam: float = 1.0,
    low: float = LOW,
    high: float = HIGH,
) -> Callable[[Valued], float]:
    """Tạo hàm tính giá khai chiến lược tuyến tính với tham số shading lam.

    Args:
        coeffs: Cặp hệ số (a, c) cho mỗi phía lệnh (hoặc giá trị k thuộc CS_NUMERIC).
        lam: Tham số quét cường độ khai giá, thuộc [0, 1] (0: trung thực, 1: đầy đủ).
        low: Cận dưới khoảng valuation (mặc định LOW = 5.0).
        high: Cận trên khoảng valuation (mặc định HIGH = 15.0).

    Returns:
        Hàm nhận vào đối tượng Valued và trả về giá khai (float).

    Raises:
        ValueError: Nếu lam ngoài [0, 1] hoặc low >= high hoặc coeffs không hợp lệ.
    """
    if not (0.0 <= lam <= 1.0):
        raise ValueError(f"lam phải thuộc [0, 1], nhận được {lam}")
    if low >= high:
        raise ValueError(f"low phải < high, nhận được low={low}, high={high}")

    resolved_coeffs: Coeffs
    if isinstance(coeffs, (int, float)):
        k_key = float(coeffs)
        if k_key in CS_NUMERIC:
            resolved_coeffs = CS_NUMERIC[k_key]
        else:
            raise ValueError(
                f"k={coeffs} không tồn tại trong CS_NUMERIC {list(CS_NUMERIC.keys())}"
            )
    else:
        resolved_coeffs = coeffs

    diff = high - low

    def price_fn(v: Valued) -> float:
        if v.side not in resolved_coeffs:
            raise ValueError(f"Phía lệnh {v.side} không có trong bộ hệ số coeffs")

        a, c = resolved_coeffs[v.side]
        v_val = v.valuation
        x = (v_val - low) / diff
        target = low + diff * (a + c * x)
        shaded = v_val + lam * (target - v_val)

        if v.side == OrderType.BID:
            return min(shaded, v_val)
        elif v.side == OrderType.ASK:
            return max(shaded, v_val)
        else:
            raise ValueError(f"Loại lệnh không hỗ trợ: {v.side}")

    return price_fn
