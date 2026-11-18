# 📋 BẢNG GIAO VIỆC CÁ NHÂN: NGUYỄN BẢO PHI
## PHÂN HỆ: MATCHING ENGINE, FASTAPI SERVICE & GAME THEORY SIMULATION

* **Người phụ trách:** Nguyễn Bảo Phi (MSV: 23810310017 - Lớp D18CNPM1)
* **Vai trò:** Auction Algorithm Engineer & Game Theory Specialist
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 20/11/2026
* **Nhánh làm việc khuyến nghị:** `feat/phi-settlement-submitter-bot`
* **Người giao việc & Nghiệm thu:** Đặng Xuân Huy (Chủ nhiệm đề tài)

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### ✅ Task P.1: Xây dựng Bot Settlement Submitter (`settlement_submitter.py`)
* **Hạn chót:** **15/11/2026**
* **Trạng thái:** `- [x] Hoàn thành (17/11/2026)`. Đã chạy thật trên Polygon Amoy: 1 trade `SETTLED`, TxHash `0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8`, số dư hai ví khớp. Chi tiết: `docs/SETTLEMENT_SUBMITTER_GUIDE.md` (mục "Kết quả chạy thật trên Amoy").
* **Mô tả công việc:**
  1. Tạo tệp mới: `system_agents/matching_engine/settlement_submitter.py`.
  2. Xây dựng logic tự động kết nối giữa Matching Engine và Smart Contract của Đức:
     - Lấy danh sách kết quả khớp lệnh `MatchResult[]` từ phiên đấu giá của `api_service.py`.
     - Chuyển đổi định dạng sang mảng các struct `MatchedTrade[]` theo đúng ABI của `CarbonDoubleAuction.sol`.
     - Sử dụng thư viện `web3.py` hoặc `eth-account` kết nối RPC Polygon Amoy, ký transaction từ địa chỉ ví Operator (đã được cấp quyền `SETTLEMENT_OPERATOR_ROLE`).
     - Gọi hàm `batchSettleTrades(MatchedTrade[] calldata trades)`.
  3. Lắng nghe Event `TradeSettled` và `BatchSettlementCompleted` trên blockchain để cập nhật trạng thái lệnh trong Engine sang `SETTLED`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Chạy bot thực hiện thành công ít nhất 1 giao dịch Batch Settlement thật trên mạng Polygon Amoy và in ra Transaction Hash.

---

#### ✅ Task P.2: Mở rộng Thí nghiệm C đo lường Deadweight Loss ($m > 16$)
* **Hạn chót:** **17/11/2026**
* **Trạng thái:** `- [x] Hoàn thành (Nghiệm thu 18/11/2026)`. Lead Architect nghiệm thu chấp nhận bảng số liệu thực nghiệm $m \le 64$ ($k=1$), kiểm tra mở rộng đa đơn vị và biểu đồ log-log hiện tại cho báo cáo Giai đoạn 2. Hiện tượng đường cong tiệm cận phẳng ở $m \ge 32$ được phân tích trong mục Thảo luận học thuật (Finite Sample Limitations); việc chạy lại mô phỏng dài giờ để cập nhật bài báo quốc tế sẽ tiếp tục ở Giai đoạn 3.
* **Mô tả công việc:**
  1. Nâng cấp script `system_agents/matching_engine/simulation/run_experiment_c.py`:
     - Mở rộng quy mô số lượng người tham gia thị trường $m \in \{16, 32, 64\}$.
     - Mô phỏng kịch bản lệnh đa đơn vị (multi-unit orders) ngoài kịch bản 1 đơn vị hiện tại.
     - Kiểm tra chéo bằng thuật toán tìm cân bằng độc lập khác để củng cố độ tin cậy khoa học.
  2. Xuất biểu đồ log-log quan hệ giữa Mất mát Hiệu quả xã hội (Deadweight Loss) và quy mô thị trường $m$.
  3. Cập nhật bảng số liệu và biểu đồ vào thư mục `simulation/results/` và Mục 9.5 của `docs/MATCHING_ENGINE_SPEC.md`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Biểu đồ thực nghiệm chứng minh tổn thất hiệu quả tiêu giảm với tốc độ xấp xỉ $O(1/m^2)$ dưới quy tắc giá $k$-DA uniform, đóng góp minh chứng quan trọng cho bài báo khoa học.

---

#### ✅ Task P.3: Biên soạn Tài liệu Phân tích Đe dọa Bảo mật (`docs/THREAT_MODELING.md`)
* **Hạn chót:** **18/11/2026**
* **Trạng thái:** `- [x] Hoàn thành (17/11/2026)`. Đã qua review độc lập, các phát hiện đã tự kiểm bằng mã trước khi tích hợp. Các lỗi hợp đồng nêu trong tài liệu (`cancelOrder`, `tradeHash`, giới hạn gas từng trade) cần Đức xem xét.
* **Mô tả công việc:**
  Tạo tệp mới `docs/THREAT_MODELING.md` phân tích chuyên sâu các nguy cơ bảo mật đối với cơ chế khớp lệnh ngoài chuỗi (Off-chain Matching, On-chain Settlement):
  1. *Nguy cơ 1 (Operator Front-running):* Người vận hành Engine chèn lệnh riêng hoặc thay đổi thứ tự khớp ngoài chuỗi $\to$ Giải pháp: Cơ chế cam kết hàm băm công khai (Commit-Reveal / Batch Hash publication).
  2. *Nguy cơ 2 (MEV Searcher Arbitrage):* Thợ đào/bot chèn giao dịch trước khi `batchSettleTrades` được ghi vào block $\to$ Giải pháp: Quyền gọi chỉ định `SETTLEMENT_OPERATOR_ROLE`.
  3. *Nguy cơ 3 (Rò rỉ Private Key của Submitter Bot):* Bot bị chiếm quyền điều khiển $\to$ Giải pháp: Hợp đồng giới hạn quyền ví bot chỉ được gọi thanh toán, không được rút tiền/chuyển token.
  4. *Nguy cơ 4 (Spam lệnh GTC rác không khóa tài sản):* Người dùng tạo ví miễn phí spam lệnh tích tuổi $\to$ Giải pháp: Khối lượng tối thiểu (Min Order Size) và biên độ giá (Price Collars) từ Oracle.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tệp `docs/THREAT_MODELING.md` hoàn chỉnh theo chuẩn bảo mật hệ thống thông tin.

---

#### ✅ Task P.4: Chuẩn hóa Học thuật từ Bài báo gốc & Chốt các điểm H4, H7, H8
* **Hạn chót:** **20/11/2026**
* **Trạng thái:** `- [x] Hoàn thành (Nghiệm thu 18/11/2026)`. Lead Architect đã phê duyệt chính thức Phương án A cho H7 (giữ công thức ADR-001 $P^* = \lfloor(b_M + s_M)/2\rfloor$ chuẩn hóa tên kỹ thuật `marginal`); H8 xác nhận vòng đời lệnh GTC tối đa 3 phiên (`max_rollover=2`, `rollover_count >= 3` $\to$ `EXPIRED`). H4 đã giải quyết xong với nguồn [CS83] và [RSW94].
* **Mô tả công việc:**
  1. Tìm đọc toàn văn bài báo gốc của Chatterjee & Samuelson (1983) và Rustichini, Satterthwaite & Williams (1994).
  2. Chuẩn hóa định nghĩa toán học giữa quy tắc giá `marginal` (lệnh biên đã khớp) và `kda` (lệnh kế tiếp chưa khớp) theo điểm **H7**.
  3. Xác nhận tính đúng đắn của con số giải tích 1/6 so với 9/32 theo điểm **H4**.
  4. Cập nhật giải thích chính thức vào Mục 7 và Mục 12 của `docs/MATCHING_ENGINE_SPEC.md`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tài liệu Spec loại bỏ hoàn toàn các nhãn "chưa đọc bài gốc" và sẵn sàng trích dẫn vào Báo cáo đề tài chính thức.

---

### NHẬT KÝ & GHI CHÚ CÁ NHÂN CỦA PHI
*(Phi hãy ghi chú tiến độ thực nghiệm hoặc các lỗi gặp phải vào phần này rồi commit lên Git)*

```markdown
- Ngày 13/11/2026:
- Tiến độ:
  - P.1: `settlement_submitter.py` đã xong và chạy thật trên node Hardhat cục bộ (chainId 80002) bằng `system_agents/matching_engine/e2e_hardhat/run_e2e.py`: batch 2 trade SETTLED, nộp lại bị bỏ qua, trade thiếu allowance bị phát hiện FAILED. Thêm 22 test (tổng 69 test ở matching_engine). CHƯA chạy trên Amoy: cần ví Operator có POL và được Đức cấp SETTLEMENT_OPERATOR_ROLE (hướng dẫn: docs/SETTLEMENT_SUBMITTER_GUIDE.md).
  - P.2: đã có bộ kiểm chéo độc lập `simulation/equilibrium_crosscheck.py` (13 test). Ở m=2 và m=4 nó xếp nghiệm của find_equilibrium vào loại cân bằng xấp xỉ (exploitability 0,002-0,005; khai thật là 0,036-0,071). Các lần chạy m=32, m=64, kịch bản nhiều đơn vị, biểu đồ log-log và mục 9.5 của spec: chưa làm (để sau).
  - P.3: docs/THREAT_MODELING.md là bản nháp; mỗi biện pháp "đã có trong mã" đã đối chiếu file:dòng; chưa có review độc lập.
  - P.4: đã đọc [R4] toàn văn và [RSW94] bản DP tr. 1–16/45; đã cập nhật spec §7, §9.1, §9.6, §12 và H4/H7. H4 xong (9/32, 27/32, 1/6 đều có nguồn). H7: k-DA của bài là `kda`, không phải công thức ADR (`marginal`); chờ Huy chọn đổi tên hay đổi mặc định. Còn: đọc phần sau của [RSW94] (chứng minh, mục 4), [R1] chưa đọc toàn văn, H8 đã code theo ADR chờ Huy xác nhận.
- Vấn đề phát sinh (nếu có):
  - Contract: `cancelOrder` không kiểm tra người gọi (ai cũng hủy được lệnh của người khác); `tradeHash` không có sessionId nên khớp lại cùng cặp lệnh, khối lượng và giá ở phiên sau bị bỏ qua im lặng; `batchSettleTrades` nuốt lỗi từng trade (bot đọc event để biết). Cần báo Đức.
  - Tiêu chí P.2 "O(1/m^2)": số liệu sơ bộ chưa ủng hộ cho mọi quy tắc giá (k=1, pair: độ dốc khoảng -0,96); báo cáo theo số liệu thật.
  - Engine chưa có PENDING_SETTLEMENT: filled_amount (đã khớp) có thể lớn hơn settled_amount (có bằng chứng on-chain).

- Ngày 17/11/2026:
- Tiến độ:
  - P.1: ĐÃ CHẠY THẬT TRÊN AMOY. Đức cấp SETTLEMENT_OPERATOR_ROLE, POL, địa chỉ hợp đồng, tài sản cho hai ví thử. Dry-run: 1 trade sẽ gửi. Gửi thật: TxHash 0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8, status 1, gas 275.741, event TradeSettled, số dư bên mua/bán đổi đúng. Lỗi tìm thấy khi chạy thật và đã sửa: thiếu middleware PoA (ExtraDataLengthError). Chưa thử batch nhiều trade, trade lỗi, --recover-tx trên chuỗi thật.
  - P.2: m đến 64 (k=1), nhiều đơn vị (kiểm tra độ bền), log-log, spec 9.5. Oracle q=1: marginal/kda khớp, pair lệch 1–9% do luật hòa giá. Số liệu còn tạm thời (xem trạng thái P.2).
  - P.3: đã review độc lập và tích hợp.
  - API cho frontend: file mẫu JSON `docs/FRONTEND_API_SAMPLES.md` (đã đối chiếu với schema phiên và CORS của Huy/Thắng trên main).
- Vấn đề phát sinh:
- Ngày 18/11/2026:
- Nghiệm thu & Chốt kỹ thuật chính thức từ Lead Architect (Đặng Xuân Huy):
  - P.1: Đạt nghiệm thu 100%. Ghi nhận thành công settlement on-chain trên Amoy.
  - P.2: Chấp nhận kết quả mô phỏng m <= 64 (k=1) và biểu đồ log-log hiện tại cho báo cáo Giai đoạn 2; các giới hạn mẫu hữu hạn được thảo luận chi tiết trong báo cáo; chạy mở rộng bổ sung cho paper sẽ dời sang Giai đoạn 3.
  - P.3: Đạt nghiệm thu 100%. Tài liệu THREAT_MODELING.md hoàn chỉnh.
  - P.4: Đạt nghiệm thu 100%. Chính thức phê duyệt Phương án A (chuẩn hóa tên `marginal` cho H7) và vòng đời 3 phiên GTC cho H8.
  - Demo 18/11: Phi phụ trách chạy FastAPI (:8000) và Settlement Submitter Bot theo đúng KE_HOACH_DEMO_NOI_BO_18_11.md.
  - Trạng thái phiên: Tạm thời giữ In-Memory cho Demo, ghi nhận lưu persistence và bổ sung sessionId vào tradeHash ở Sprint 3.
  - TỔNG KẾT: Hoàn thành 100% toàn bộ 4 nhiệm vụ (P.1 - P.4).
```
