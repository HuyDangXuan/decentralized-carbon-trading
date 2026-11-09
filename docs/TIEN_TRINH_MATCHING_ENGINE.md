# Tiến trình phần Matching Engine & mô phỏng (Nguyễn Bảo Phi)

Cập nhật: 08/11/2026 (Giai đoạn 2, tuần 2). Branch: `auction-algorithm-engineer` (đặt theo vai trò Auction Algorithm Engineer trong bảng phân công Giai đoạn 2). Danh sách việc cần trao đổi với từng bên nằm ở [`VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md`](VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md).

## 1. Đã làm được

| Hạng mục theo bảng Giai đoạn 2 | Hạn | Tình trạng | Sản phẩm |
|---|---|---|---|
| Thiết kế logic Matching Engine và đặc tả API Service | 25/11 | **Bản đầy đủ, chờ nhóm chốt các quyết định mở** | [`MATCHING_ENGINE_SPEC.md`](MATCHING_ENGINE_SPEC.md) |
| Script mô phỏng thực nghiệm toán học (100–500 lệnh) | 10/12 | **Đã chạy được, đã có kết quả** | `system_agents/matching_engine/simulation/` |
| Phối hợp với Đức về hợp đồng đấu giá và EIP-712 | 05/12 | Đã đối chiếu spec hai bên, danh sách điểm lệch đã lập | `VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md` |

### 1.1. Spec Matching Engine
- Mô hình dữ liệu ánh xạ sang struct `Order` được ký EIP-712 trong spec hợp đồng của Đức (`docs/SMART_CONTRACT_SPEC.md`, branch `docs/smart-contract-spec`, commit `3194bad`).
- Vòng đời lệnh, quy tắc phá hòa (ưu tiên theo giá, rồi theo tuổi lệnh, rồi pro-rata; FIFO là phương án thay thế), rollover GTC/IOC, API REST và WebSocket, luồng settlement.
- Đã ghi rõ giới hạn tin cậy với engine và các ràng buộc từ hợp đồng: kiểm trạng thái on-chain trước khi gửi, cuộc đua với `deadline`, phân bổ bằng 0, `cancelOrder`/`incrementNonce`.
- Đã qua review chéo bằng model khác (Claude Opus 4.6 review spec; Opus 5.5 review thí nghiệm) và đối chiếu với tham vấn Argon (mức suy nghĩ "Cao"). Các điểm hợp lý đã được đưa vào spec.

### 1.2. Bộ mô phỏng (`system_agents/matching_engine/simulation/`)
| File | Vai trò |
|---|---|
| `CONTRACT.md`, `model.py` | Hợp đồng và kiểu dữ liệu dùng chung (người phụ trách giữ) |
| `generator.py`, `metrics.py` | Sinh lệnh có valuation ẩn; welfare, thặng dư mua/bán, fill rate, phân bổ hiệu quả |
| `run_experiment.py` | Thí nghiệm A: khai giá trung thực, k ∈ {0, 0,5, 1}, n ∈ {100, 200, 500}, 30 seed |
| `strategies.py`, `run_experiment_b.py` | Thí nghiệm B: chiến lược khai giá tuyến tính (hệ số dạng đóng `cs_linear_coeffs`), B1 (1 mua – 1 bán), B2 (quét cường độ λ) |
| `verify_closed_forms.py` | Kiểm tra công thức đóng bằng mô phỏng lớn |
| `test_*.py` | 27 test |
| `results/` | CSV và đồ thị của A và B2 |

Chạy lại: `python -m unittest discover -s system_agents/matching_engine/simulation`, `python .../run_experiment.py a`, `python .../run_experiment_b.py b1`, `python .../run_experiment_b.py b2`, `python .../verify_closed_forms.py`.

### 1.3. Kết quả đã có và cách đọc đúng
- **A:** welfare bằng nhau với mọi k (90 cặp n × seed); `buyer_share` = 1 / 0,5 / 0 ứng với k = 0 / 0,5 / 1. Đây là **kiểm tra đúng đắn** của bộ mô phỏng (hệ quả đại số của công thức giá), không phải phát hiện.
- **B1:** tần suất giao dịch 0,283 và efficiency 0,847, khớp lý thuyết 9/32 và 27/32 (suy ra độc lập bởi ba bên, Monte Carlo 2·10⁶ mẫu). Test còn kiểm k = 0,25 và 0,75.
- **B2:** efficiency giảm từ 1,000 xuống khoảng 0,92–0,94 khi cường độ khai giá λ tăng 0 → 1; hội tụ lên giới hạn giải tích 0,9375 (k = 0,5, λ = 1) khi n tăng (đã kiểm n = 4000). Đây là **độ nhạy với cường độ khai giá ngoại sinh**, không phải cân bằng thị trường.
- Hệ số cân bằng tuyến tính dạng đóng cho mọi k: `bid = k(1−k)/(2(1+k)) + v/(1+k)`, `ask = (1−k)/2 + c/(2−k)`; ba nguồn độc lập cùng kết quả.

### 1.4. Lỗi đã bắt và sửa nhờ đối chiếu chéo
| Lỗi | Phát hiện bởi | Xử lý |
|---|---|---|
| `fill_rate` vượt 1 do hợp đồng không tính khớp bid = ask | Kiểm độc lập của người phụ trách | Sửa hợp đồng và `metrics.py`, thêm test hồi quy |
| `--k nan` và giá trị trùng lọt qua bộ phân tích tham số | Reviewer Opus 5.5 | Sửa, thêm test hồi quy |
| Hệ số xấp xỉ lưới cho k = 0,25 và 0,75 lệch tới 0,04 | Reviewer Opus 5.5, rồi Argon | Thay bằng dạng đóng, thêm test vét cạn và giá trị chính xác |
| Trích sai nơi đăng của Bosshard và cs. (Argon) | Tìm kiếm web | Ghi vào spec §9.6; không dùng |

## 2. Còn vấn đề cần giải quyết

### 2.1. Phụ thuộc người khác (chi tiết ở `VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md`)
- **Đức:** đơn vị `amount` (kg hay tCO2e, chênh 1000 lần); đơn vị `pricePerUnit`; hướng làm tròn giá khớp; kiểm `filledAmount` mới nêu cho phía bid; quyền gọi `cancelOrder`; `time_in_force` có nằm trong struct được ký không; code `contracts/` trên `main` chưa theo spec mới.
- **Huy:** sửa câu chữ nhiệm vụ 3 trên Google Doc (với khai trung thực, welfare không đổi theo k); chốt độ dài phiên, tie-break mặc định, giá theo cặp hay giá chung, giới hạn rollover; SRS/UML cần phản ánh vòng đời lệnh và rollover.
- **Thắng:** tiêu chí "lớp tín chỉ" được khớp với nhau; đối chiếu wireframe Trading Floor với API.

### 2.2. Việc nghiên cứu còn mở (của phần Phi)
1. **Đọc bài gốc** Chatterjee–Samuelson (1983), Satterthwaite–Williams (1989), Rustichini–Satterthwaite–Williams (1994). Hiện chỉ có nguồn thứ cấp và phép suy ra của nhóm; chưa trích hệ số hay định lý vào báo cáo chung trước khi đọc.
2. **Chưa có kết luận về hiệu quả của thị trường nhiều lệnh ở cân bằng.** Cần tìm ε-equilibrium trong lớp chiến lược bốn tham số (lặp phản ứng tối ưu có làm trơn, đo sai số trên seed kiểm định riêng), kiểm quy trình trên n = 2 phải tái tạo dạng đóng.
3. **Kiểm định tốc độ mất hiệu quả theo n** (dự đoán O(1/m²) của Rustichini và cs. áp dụng cho giá chung): cần mẫu độc lập giữa các n (hiện lồng nhau), ít nhất 5 mức n, 200–500 seed, stratified 50/50 số lệnh mua – bán, bỏ làm tròn 0,01 khi đo hội tụ.
4. **Nhánh giá chung của phiên** để đối chứng với giá theo từng cặp (engine hiện định giá theo từng cặp, nên không so trực tiếp với định lý giá chung).
5. Giả thuyết chưa kiểm: "trong giá theo từng cặp, động cơ khai giá không suy giảm như O(1/m)". Chỉ được trích sau khi có thí nghiệm.
6. Con số "xác suất bỏ lỡ 1/6" của một nguồn thứ cấp chưa khớp với suy ra của nhóm (7/32 hoặc 7/16); cần mở nguồn gốc.

### 2.3. Việc triển khai (Giai đoạn 3 và tuần 5–8)
- Cài đặt `age_prorata`, rollover GTC/IOC và API Service (hiện mới là thiết kế; baseline code chỉ có FIFO, giá làm tròn `round(…, 2)` và trừ trực tiếp vào `Order.amount`).
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
