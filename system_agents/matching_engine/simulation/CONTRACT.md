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

## `run_experiment.py` (thí nghiệm A: khai giá trung thực, chia thặng dư theo k)
CLI: `python run_experiment.py a [--n 100,200,500] [--k 0,0.5,1] [--runs 30] [--out results]` (mặc định như trên; `--out` tương đối so với thư mục chứa script, tạo nếu chưa có).
Với mỗi `n`, mỗi `seed` trong `range(runs)`: `valued = generate_valued(n, seed)`; chạy `run_auction(valued, k)` cho từng `k` (bid trung thực).
Ghi:
- `exp_a_raw.csv`, cột theo thứ tự: `k,n,seed,welfare,max_welfare,efficiency,buyer_surplus,seller_surplus,volume,fill_rate` (`efficiency = welfare / max_welfare`, `max_welfare == 0` → 1.0), một dòng mỗi (k, n, seed), dấu phẩy, UTF-8, tiêu đề ở dòng đầu.
- `exp_a_summary.csv`, cột: `k,n,runs,welfare_mean,welfare_std,buyer_share_mean,buyer_share_std,seller_share_mean,seller_share_std,fill_rate_mean`; `buyer_share = buyer_surplus / welfare` (welfare = 0 thì bỏ qua lần chạy đó khi tính trung bình); std là độ lệch chuẩn mẫu (n−1), 1 mẫu thì 0.
- `exp_a_surplus_split.png`: biểu đồ cột nhóm theo `k` (trục x), mỗi `n` một cột, chiều cao = `buyer_share_mean` kèm thanh sai số = `buyer_share_std`; nhãn trục và tiêu đề tiếng Việt; `matplotlib.use("Agg")`; không `plt.show()`.
Kiểm tra bắt buộc trong script: với mỗi (n, seed), `welfare` bằng nhau giữa các `k` (sai số 1e-6) và bằng `max_welfare`; nếu sai in `LỖI: welfare đổi theo k ...` ra stderr và thoát mã 1. Nếu đúng in dòng `Kiểm tra bất biến welfare theo k: OK (<số cấu hình> cấu hình)`.
Cuối cùng in bảng tóm tắt (cột căn thẳng) ra stdout. Trả mã 0 khi thành công. Tham số sai (k ngoài [0,1], n < 2, runs < 1, danh sách rỗng) → `argparse` lỗi, mã 2.

## `strategies.py` (thí nghiệm B: khai giá chiến lược)
Hằng số: `LOW = 5.0`, `HIGH = 15.0` (trùng mặc định của `generate_valued`). Chuẩn hóa `x = (valuation − LOW) / (HIGH − LOW)`.
- `Coeffs = dict[OrderType, tuple[float, float]]`: với mỗi phía, cặp `(a, c)` nghĩa là giá khai chuẩn hóa `a + c·x`.
- `CS_K05: Coeffs = {BID: (1/12, 2/3), ASK: (1/4, 2/3)}` — cân bằng tuyến tính Chatterjee–Samuelson cho 1 mua – 1 bán, valuation đều trên [0,1], k = 0.5.
- `cs_linear_coeffs(k) -> Coeffs` (0 < k < 1): cân bằng tuyến tính dạng đóng của k-double auction 1 mua – 1 bán, valuation đều trên [0,1]: `bid = (v + k·g)/(1+k)`, `ask = (c + (1−k)(a+b))/(2−k)`, giải hệ cho `(a, b, g, d)` (với `a, b` là hệ số chặn và độ dốc của bid, `g, d` của ask). Trả về đúng `CS_K05` khi `k = 0.5`; `k = 0.25 → BID (0.075, 0.8), ASK (0.375, 4/7)`; `k = 0.75 → BID (3/56, 4/7), ASK (0.125, 0.8)`. Suy ra bằng điều kiện bậc nhất và kiểm lại bằng tìm phản ứng tối ưu số trong test; **chưa đối chiếu với bài gốc**. Nghiệm tuyến tính không duy nhất.
- `CS_NUMERIC: dict[float, Coeffs]` với khóa `0.25`, `0.5`, `0.75` = `cs_linear_coeffs(k)` (riêng `0.5 → CS_K05`). (Sửa 2026-11-08 sau review chéo: bản đầu dùng xấp xỉ lưới, lệch tới 0.04 ở độ dốc k = 0.75.)
- `linear_price_fn(coeffs: Coeffs, lam: float = 1.0, low=LOW, high=HIGH) -> Callable[[Valued], float]`:
  - `target = low + (high − low) · (a + c·x)` theo phía của lệnh;
  - `shaded = v + lam · (target − v)` (`lam = 0` → trung thực, `lam = 1` → chiến lược đầy đủ; `0 ≤ lam ≤ 1`, ngoài khoảng → `ValueError`);
  - BID: trả `min(shaded, v)` (không bao giờ khai cao hơn valuation); ASK: trả `max(shaded, v)` (không bao giờ khai thấp hơn chi phí).
Bất biến: `lam = 0` cho đúng `valuation`; BID luôn ≤ valuation, ASK luôn ≥ valuation; kết quả đơn điệu theo `lam`.

## `run_experiment_b.py`
CLI: `python run_experiment_b.py b1 [--trials 20000] [--seed 0]` và `python run_experiment_b.py b2 [--n 100,200,500] [--k 0.25,0.5,0.75] [--lam 0,0.25,0.5,0.75,1] [--runs 20] [--out results]`. Lỗi tham số → mã 2.

**b1 — mỏ neo giải tích (1 mua – 1 bán).** Mỗi lần thử: valuation mua và bán độc lập, đều trên `[LOW, HIGH]` (`snap`), `amount = 1` cả hai, `k = 0.5`, cả hai dùng `linear_price_fn(CS_K05, lam=1)`, `run_auction` như thường. In: tần suất có giao dịch, `efficiency = Σ welfare / Σ max_welfare` (cộng trên mọi lần thử), và so với giá trị lý thuyết `9/32 = 0.28125` và `27/32 = 0.84375` (Claude tự suy ra: giao dịch xảy ra khi và chỉ khi `v − c ≥ 1/4` theo đơn vị chuẩn hóa; đã kiểm bằng Monte Carlo 2·10⁶ mẫu). Thoát mã 0 nếu cả hai lệch ≤ 0.02 (tuyệt đối), ngược lại in `LỖI: ...` ra stderr, mã 1.

**b2 — quét cường độ khai giá, nhiều lệnh.** Với mỗi `(k, n, lam)` và `seed` trong `range(runs)`: `valued = generate_valued(n, seed)`; `price_fn = linear_price_fn(CS_NUMERIC[k], lam)`; `matches = run_auction(valued, k, price_fn)`. Tất cả người tham gia dùng cùng `lam` (đối xứng). Ghi `exp_b2_raw.csv` (cột: `k,n,lam,seed,welfare,max_welfare,efficiency,volume,fill_rate,buyer_share`, với `buyer_share = buyer_surplus / welfare`, welfare = 0 → để trống; **welfare, surplus và fill_rate luôn tính theo valuation thật, không theo giá khai**), `exp_b2_summary.csv` (trung bình và độ lệch chuẩn mẫu của `efficiency`, `fill_rate`, `buyer_share` theo `(k, n, lam)`), và `exp_b2_efficiency.png` (một ô con mỗi `k`; trục x = `lam`, trục y = `efficiency` trung bình, mỗi `n` một đường kèm thanh sai số; nhãn tiếng Việt; `matplotlib.use("Agg")`). Kiểm tra bắt buộc: `lam = 0` phải cho `efficiency == 1.0` (sai số 1e-9) với mọi `(k, n, seed)`; nếu sai in `LỖI: ...` ra stderr, mã 1.

**Giới hạn phải ghi trong docstring đầu file:** hệ số `CS_NUMERIC` là cân bằng tuyến tính của thị trường 1 mua – 1 bán, một đơn vị; áp dụng cho nhiều lệnh nhiều đơn vị chỉ là heuristic. `lam` là tham số quét, không phải cân bằng của thị trường nhiều lệnh. Cân bằng của k-double auction không duy nhất.
