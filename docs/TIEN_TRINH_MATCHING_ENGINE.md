# Tiến trình phần Matching Engine & mô phỏng (Nguyễn Bảo Phi)

Cập nhật: 10/11/2026 (Giai đoạn 2, tuần 2). Branch: `auction-algorithm-engineer` (đặt theo vai trò Auction Algorithm Engineer trong bảng phân công Giai đoạn 2). Danh sách việc cần trao đổi với từng bên nằm ở [`VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md`](VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md).

## 1. Đã làm được

| Hạng mục theo bảng Giai đoạn 2 | Hạn | Tình trạng | Sản phẩm |
|---|---|---|---|
| Thiết kế logic Matching Engine và đặc tả API Service | 25/11 | **Bản đầy đủ, đã cập nhật 10/11 theo bài gốc; chờ nhóm chốt các quyết định mở và điền kết quả thí nghiệm C** | [`MATCHING_ENGINE_SPEC.md`](MATCHING_ENGINE_SPEC.md) |
| Script mô phỏng thực nghiệm toán học (100–500 lệnh) | 10/12 | **Đã chạy được, đã có kết quả (A, B1, B2); thí nghiệm C (cân bằng, tốc độ mất hiệu quả theo m) đang chạy** | `system_agents/matching_engine/simulation/` |
| Phối hợp với Đức về hợp đồng đấu giá và EIP-712 | 05/12 | Đã đối chiếu spec hai bên, danh sách điểm lệch đã lập | `VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md` |

### 1.1. Spec Matching Engine
- Mô hình dữ liệu ánh xạ sang struct `Order` được ký EIP-712 trong spec hợp đồng của Đức (`docs/SMART_CONTRACT_SPEC.md`, branch `docs/smart-contract-spec`, commit `3194bad`).
- Vòng đời lệnh, quy tắc phá hòa (ưu tiên theo giá, rồi theo tuổi lệnh, rồi pro-rata với phần dư chia theo largest remainder; FIFO là phương án thay thế), rollover GTC/IOC, API REST và WebSocket, luồng settlement.
- **Cập nhật 10/11:** quy tắc giá chung đổi từ "cặp biên" (không làm sạch thị trường) sang k-double auction `kda` (`p = (1−k)·s(m) + k·s(m+1)`, khái quát hóa của nhóm từ định nghĩa ở `k = 1` trong Satterthwaite–Williams 1989; phạm vi theo `k` của kết quả O(1/m²) chưa kiểm chứng); thêm đề xuất làm tròn `half_even`; thêm biện pháp chống thao túng phần dư và ưu tiên theo tuổi; thêm nguồn [SW89], [RSW94], [W85], [CS06] kèm mức đã đọc.
- Đã ghi rõ giới hạn tin cậy với engine và các ràng buộc từ hợp đồng: kiểm trạng thái on-chain trước khi gửi, cuộc đua với `deadline`, phân bổ bằng 0, `cancelOrder`/`incrementNonce`.
- Đã qua review chéo bằng model khác (Claude Opus 4.6 review spec; Opus 5.5 review thí nghiệm và hợp đồng đợt 2) và hai vòng tham vấn Argon (mức suy nghĩ "Cao"). Các điểm hợp lý đã được đưa vào spec, điểm chưa kiểm chứng được ghi rõ trong §7 và §11.

### 1.2. Bộ mô phỏng (`system_agents/matching_engine/simulation/`)
| File | Vai trò |
|---|---|
| `CONTRACT.md`, `model.py` | Hợp đồng và kiểu dữ liệu dùng chung (người phụ trách giữ) |
| `generator.py`, `metrics.py` | Sinh lệnh có valuation ẩn; welfare, thặng dư mua/bán, fill rate, phân bổ hiệu quả |
| `run_experiment.py` | Thí nghiệm A: khai giá trung thực, k ∈ {0, 0,5, 1}, n ∈ {100, 200, 500}, 30 seed |
| `strategies.py`, `run_experiment_b.py` | Thí nghiệm B: chiến lược khai giá tuyến tính (hệ số dạng đóng `cs_linear_coeffs`), B1 (1 mua – 1 bán), B2 (quét cường độ λ) |
| `verify_closed_forms.py` | Kiểm tra công thức đóng bằng mô phỏng lớn |
| `kda_sim.py` | Thị trường vector hóa m mua + m bán một đơn vị, ba quy tắc giá (`pair`, `marginal`, `kda`), tiện ích kỳ vọng của người lệch (common random numbers) |
| `equilibrium_search.py` | Phản ứng tối ưu từng điểm (`U = v·W(b) − P(b)`), `find_equilibrium` (phi tham số hoặc tuyến tính), `epsilon` (`eps_opt` chệch lên, `eps_xval` kiểm chéo) |
| `run_experiment_c.py` | Thí nghiệm C: mất hiệu quả ở cân bằng xấp xỉ theo m, ba quy tắc giá, ghi từng dòng, chạy tiếp được |
| `session_engine.py` | Engine tham chiếu thuần số nguyên cho spec §5–§7: `match_session` (giá → tuổi → pro-rata Hamilton; `pair`/`marginal`/`kda`; làm tròn `floor`/`ceil`/`half_up`/`half_even`) |
| `test_*.py` | toàn bộ suite pass ở lần chạy gần nhất (xem lệnh bên dưới) |
| `results/` | CSV và đồ thị của A, B2 và C |

Chạy lại: `python -m unittest discover -s system_agents/matching_engine/simulation`, `python .../run_experiment.py a`, `python .../run_experiment_b.py b1`, `python .../run_experiment_b.py b2`, `python .../verify_closed_forms.py`.

### 1.3. Kết quả đã có và cách đọc đúng
- **A:** welfare bằng nhau với mọi k (90 cặp n × seed); `buyer_share` = 1 / 0,5 / 0 ứng với k = 0 / 0,5 / 1. Đây là **kiểm tra đúng đắn** của bộ mô phỏng (hệ quả đại số của công thức giá), không phải phát hiện.
- **B1:** tần suất giao dịch 0,283 và efficiency 0,847, khớp lý thuyết 9/32 và 27/32 (suy ra độc lập bởi ba bên, Monte Carlo 2·10⁶ mẫu). Test còn kiểm k = 0,25 và 0,75.
- **B2:** efficiency giảm từ 1,000 xuống khoảng 0,92–0,94 khi cường độ khai giá λ tăng 0 → 1; hội tụ lên giới hạn giải tích 0,9375 (k = 0,5, λ = 1) khi n tăng (đã kiểm n = 4000). Đây là **độ nhạy với cường độ khai giá ngoại sinh**, không phải cân bằng thị trường.
- **Đối chiếu với bài gốc (Satterthwaite–Williams 1989, đã đọc toàn văn):** ở k = 1 với quy tắc `kda`, mất hiệu quả tương đối là 0,0735 / 0,0181 / 0,00406 cho m = 2 / 4 / 8 (thí nghiệm C, 400.000 kịch bản đánh giá), so với 0,0742 / 0,0175 / 0,0042 trong Bảng 6.1 của bài: sai lệch tương đối 0,9% / 3,4% / 3,3%, **vượt khoảng tin cậy lấy mẫu** (±0,0006; ±0,00014; ±0,00003), nên chỉ gọi là "gần", không gọi là "khớp"; nguyên nhân khả dĩ là sai số của chiến lược cân bằng xấp xỉ (chưa tách riêng). Người bán khai đúng giá trị như bài chứng minh. Đây là đối chiếu độc lập quan trọng của quy trình tìm cân bằng, chưa phải kiểm chứng chính xác.
- **Thí nghiệm C (đang chạy, số liệu sớm, chưa kết luận):** ở k = 1, `kda` giảm theo tỉ lệ ≈ 4,1 rồi 4,5 mỗi lần m nhân đôi (gần O(1/m²)), `pair` ≈ 2,1 rồi 1,9 (gần O(1/m)); nhưng ở k = 0,5 (m = 2, 4) `pair` và `kda` **không phân biệt được** (0,0727 → 0,0156 so với 0,0671 → 0,0153). Vì vậy giả thuyết "giá theo cặp hội tụ chậm hơn" mới chỉ được ủng hộ ở k = 1. Mọi cấu hình có `converged = False` theo `tol`; ε (eps_xval tương đối) từ dưới 10⁻⁴ đến 3,0·10⁻², lớn nhất ở `pair`, k = 0,5, m = 2, nơi chiến lược có dạng bất thường (bid tại v = 0,25 bằng 0,031). Chờ m = 16 và hồi quy log–log.
- Hệ số cân bằng tuyến tính dạng đóng cho mọi k: `bid = k(1−k)/(2(1+k)) + v/(1+k)`, `ask = (1−k)/2 + c/(2−k)`; ba nguồn độc lập cùng kết quả.

### 1.4. Lỗi đã bắt và sửa nhờ đối chiếu chéo
| Lỗi | Phát hiện bởi | Xử lý |
|---|---|---|
| `fill_rate` vượt 1 do hợp đồng không tính khớp bid = ask | Kiểm độc lập của người phụ trách | Sửa hợp đồng và `metrics.py`, thêm test hồi quy |
| `--k nan` và giá trị trùng lọt qua bộ phân tích tham số | Reviewer Opus 5.5 | Sửa, thêm test hồi quy |
| Hệ số xấp xỉ lưới cho k = 0,25 và 0,75 lệch tới 0,04 | Reviewer Opus 5.5, rồi Argon | Thay bằng dạng đóng, thêm test vét cạn và giá trị chính xác |
| Trích sai nơi đăng của Bosshard và cs. (Argon) | Tìm kiếm web | Ghi vào spec §9.6; không dùng |
| Quy tắc giá chung "cặp biên" không làm sạch thị trường (BID 10, ASK 1, ASK 2) | Reviewer Opus 5.5 | Thay bằng `kda`; giữ `marginal` chỉ để đối chứng |
| Phần dư pro-rata chia theo `order_id` thiên lệch và bị khai thác (chọn id, tách lệnh) | Argon, kiểm lại bằng suy luận | Đổi sang largest remainder; giới hạn chống thao túng ghi ở spec §5.2 |
| Test đối chiếu numpy với baseline bỏ qua làm tròn tick (ví dụ v=0,6, c=0,352 khớp thêm một cặp sau làm tròn) | Reviewer Opus 5.5 | Làm tròn tick ở cả hai phía khi so |
| Seed dùng `hash()` không tái lập (ngẫu nhiên theo tiến trình) | Reviewer Opus 5.5 | Dùng `zlib.crc32` |
| Chế độ tuyến tính khớp cả nút không giao dịch; `eps_xval` bị cắt về 0 nên chệch lên | Người phụ trách nghiệm thu J3 | Chỉ khớp trên nút có xác suất thắng dương; bỏ phép cắt |
| Bộ test của engine không bắt được hai đột biến (phá hòa Hamilton theo khối lượng, thứ tự tuổi khi ghép cặp) | Kiểm đột biến mã của người phụ trách | Bổ sung hai test hồi quy |

## 2. Còn vấn đề cần giải quyết

### 2.1. Phụ thuộc người khác (chi tiết ở `VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md`)
- **Đức:** đơn vị `amount` (kg hay tCO2e, chênh 1000 lần); đơn vị `pricePerUnit`; hướng làm tròn giá khớp; kiểm `filledAmount` mới nêu cho phía bid; quyền gọi `cancelOrder`; `time_in_force` có nằm trong struct được ký không; code `contracts/` trên `main` chưa theo spec mới.
- **Huy:** sửa câu chữ nhiệm vụ 3 trên Google Doc (với khai trung thực, welfare không đổi theo k); chốt độ dài phiên, tie-break mặc định, giá theo cặp hay giá chung, giới hạn rollover; SRS/UML cần phản ánh vòng đời lệnh và rollover.
- **Thắng:** tiêu chí "lớp tín chỉ" được khớp với nhau; đối chiếu wireframe Trading Floor với API.

### 2.2. Việc nghiên cứu còn mở (của phần Phi)
1. **Đọc bài gốc.** Đã đọc toàn văn Satterthwaite–Williams (1989). Còn Chatterjee–Samuelson (1983) và Rustichini–Satterthwaite–Williams (1994) (mới đọc tóm tắt trang tạp chí; chưa biết kết quả có đúng cho mọi k). Chưa trích hệ số hay định lý của hai bài này vào báo cáo chung trước khi đọc.
2. **Hiệu quả của thị trường nhiều lệnh ở cân bằng:** đã có quy trình tìm ε-equilibrium (phản ứng tối ưu từng điểm, ε đo trên seed kiểm định riêng) và đã kiểm với bài gốc ở k = 1; thí nghiệm C đang chạy; chưa có kết luận cho k = 0,5 và cho giá theo từng cặp. Giới hạn: ε chỉ đo theo lệch của một người, từng điểm, nên là cận dưới.
3. **Kiểm định tốc độ mất hiệu quả theo m** (O(1/m²) của Rustichini và cs. cho giá chung): thí nghiệm C dùng mẫu độc lập giữa các m, không làm tròn tick, một đơn vị mỗi lệnh, m = 2, 4, 8, 16; còn thiếu: hồi quy log–log kèm khoảng tin cậy khi chạy xong, và mở rộng nhiều đơn vị mỗi lệnh.
4. ~~Nhánh giá chung của phiên~~ **Đã làm**: `kda` và `marginal` so với `pair` trong thí nghiệm C; còn phải đưa kết luận vào spec §9.5 khi xong.
5. Giả thuyết "giá theo từng cặp hội tụ chậm hơn `kda`": ủng hộ ở k = 1, không ủng hộ ở k = 0,5 (số liệu m ≤ 4); chỉ được trích sau khi có m = 8, 16 ở cả hai k và độ dốc kèm khoảng tin cậy. Không tìm thấy định lý công bố nào cho giá theo từng cặp.
6. Con số "xác suất bỏ lỡ 1/6" của một nguồn thứ cấp chưa khớp với suy ra của nhóm (7/32 hoặc 7/16); cần mở nguồn gốc.

### 2.3. Việc triển khai (Giai đoạn 3 và tuần 5–8)
- Tích hợp `age_prorata`, rollover GTC/IOC và API Service vào engine chính (hiện mới có engine tham chiếu số nguyên trong `simulation/`, chưa dùng thay cho `auction_agent.py`; baseline chỉ có FIFO, giá làm tròn `round(…, 2)` và trừ trực tiếp vào `Order.amount`).
- Giá khớp số nguyên bảo đảm `ask ≤ giá ≤ bid` (hợp đồng revert `PriceMismatch` nếu vi phạm).
- Viết test case theo danh sách ở spec §10; threat modeling (front-running ngoài chuỗi của người vận hành engine, MEV, quản lý khóa của Settlement Submitter).

### 2.4. Giới hạn cần nhớ khi viết báo cáo
- Kết quả A là hệ quả đại số; kết quả B2 không phải cân bằng và không dùng để xếp hạng các k.
- Mẫu giữa các n lồng nhau (common random numbers), không phải mẫu độc lập.
- Số liệu gas trong spec hợp đồng (112k, 145k, 920k) chưa được benchmark thực.
- Phần tham vấn Argon và hai review model khác là nguồn tham khảo đã được kiểm lại; không thay cho việc đọc bài gốc.

### 2.5. Quy trình
- Commit `7285ba3` (spec bản đầu) đã nằm trên `main` ở remote do lần push đầu chưa dùng branch; trưởng nhóm đã được báo.
- Các commit tiếp theo nằm trên branch `auction-algorithm-engineer`; chỉ push lên branch này, không push lên `main`.
