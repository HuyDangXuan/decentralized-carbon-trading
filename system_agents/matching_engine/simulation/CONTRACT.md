# CONTRACT — bộ mô phỏng thực nghiệm đấu giá kép (Giai đoạn 2, nhiệm vụ 3)

Chủ sở hữu hợp đồng và `model.py`: Claude/Phi. Worker chỉ đọc hai file này.
Kế hoạch thực nghiệm: [`docs/MATCHING_ENGINE_SPEC.md`](../../../docs/MATCHING_ENGINE_SPEC.md) §9.
Chỉ dùng thư viện chuẩn, trừ `run_experiment.py` được dùng `matplotlib` (đã cài). Python 3.10+, PEP 8, đầu ra tiếng Việt in được trên Windows (`sys.stdout.reconfigure(encoding="utf-8")`).

## Quy ước chung
- Import: `from model import Valued, OrderType, MatchResult, TICK, TOKEN_ID, snap, to_order` và `from auction_agent import DoubleAuctionAgent` (sau khi import `model`, đường dẫn đã được thêm).
- **Không hàm nào được sửa đối tượng đầu vào.** `DoubleAuctionAgent.run_periodic_double_auction` trừ trực tiếp vào `Order.amount` nên luôn tạo `Order` mới bằng `to_order`.
- Giá luôn là bội số của `TICK = 0.01`. So sánh số thực dùng sai số 1e-6.
- `valuation` của BID là mức trả tối đa thật, của ASK là chi phí thật.

## `generator.py`
`generate_valued(n: int, seed: int, low: float = 5.0, high: float = 15.0, max_amount: int = 50, p_buy: float = 0.5) -> list[Valued]`
- Dùng `random.Random(seed)`; cùng tham số → cùng kết quả.
- Lệnh thứ `i`: `order_id = f"O{i}"`, `arrival = i`; phía BID với xác suất `p_buy`, ngược lại ASK; `valuation` uniform trên `[low, high]` rồi `snap`; `amount` là số nguyên đều trên `[1, max_amount]`.
- `ValueError` nếu `n < 2`, `low >= high`, `max_amount < 1` hoặc `p_buy` ngoài `[0, 1]`.

## `metrics.py`
- `truthful(v: Valued) -> float`: trả `v.valuation`.
- `run_auction(valued, k: float, price_fn=truthful) -> list[MatchResult]`: tạo `Order` mới bằng `to_order(v, price_fn(v))` theo thứ tự `arrival`, `DoubleAuctionAgent(k)`, `submit_order` từng lệnh, trả kết quả của `run_periodic_double_auction(TOKEN_ID)`.
- `welfare(matches, valued) -> float` = Σ (valuation[bid] − valuation[ask]) · amount, tra theo `order_id`.
- `buyer_surplus` = Σ (valuation[bid] − clearing_price) · amount; `seller_surplus` = Σ (clearing_price − valuation[ask]) · amount.
- `volume(matches) -> int` = Σ amount.
- `max_welfare(valued) -> float` và `efficient_volume(valued) -> int`: phân bổ hiệu quả đa đơn vị — bung mỗi lệnh thành các đơn vị, xếp bên mua giảm dần theo valuation, bên bán tăng dần, ghép lần lượt trong khi valuation mua **không thấp hơn** chi phí bán (khớp cả trường hợp bằng nhau, giống engine; lãi bằng 0 nên không đổi welfare); welfare là tổng chênh lệch, volume là số đơn vị ghép. Nhờ vậy `fill_rate ≤ 1` và bằng 1 khi mọi người khai trung thực. (Sửa 2026-11-08 sau nghiệm thu: bản đầu dùng "lớn hơn hẳn" làm `fill_rate` vượt 1 ở 10/40 cấu hình kiểm tra.)
- `fill_rate(matches, valued) -> float` = `volume / efficient_volume`; `efficient_volume == 0` → `1.0`.
- Hàm trả `float` làm tròn 6 chữ số thập phân.

## Bất biến (test phải kiểm)
1. Cùng `(n, seed)` → `generate_valued` giống hệt; seed khác → khác.
2. `run_auction` không đổi `valued`; gọi hai lần cùng đầu vào → cùng kết quả.
3. Bid trung thực: `welfare` bằng nhau với `k ∈ {0, 0.5, 1}` và bằng `max_welfare`.
4. `buyer_surplus + seller_surplus == welfare` (sai số 1e-6); `k = 0` → `seller_surplus == 0`; `k = 1` → `buyer_surplus == 0`.
5. Mọi match có `ask ≤ clearing_price ≤ bid` theo giá khai; không `order_id` nào khớp vượt `amount` ban đầu.
6. Ví dụ tay: BID(val 12, amount 10), BID(val 8, amount 5), ASK(val 6, amount 7), ASK(val 9, amount 20) với `k = 0.5`, bid trung thực → khớp 7 đơn vị ở giá 9.0 giữa BID-12 và ASK-6, rồi 3 đơn vị giữa BID-12 và ASK-9 ở giá 10.5; `welfare = 7·6 + 3·3 = 51.0`, `max_welfare = 51.0`.
