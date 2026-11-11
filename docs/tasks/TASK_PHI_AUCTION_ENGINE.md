# 📋 BẢNG GIAO VIỆC CÁ NHÂN: NGUYỄN BẢO PHI
## PHÂN HỆ: MATCHING ENGINE, FASTAPI SERVICE & GAME THEORY SIMULATION

* **Người phụ trách:** Nguyễn Bảo Phi (MSV: 23810310017 - Lớp D18CNPM1)
* **Vai trò:** Auction Algorithm Engineer & Game Theory Specialist
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 20/11/2026
* **Nhánh làm việc khuyến nghị:** `feat/phi-settlement-submitter-bot`
* **Người giao việc & Nghiệm thu:** Đặng Xuân Huy (Chủ nhiệm đề tài)

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### 🔲 Task P.1: Xây dựng Bot Settlement Submitter (`settlement_submitter.py`)
* **Hạn chót:** **15/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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

#### 🔲 Task P.2: Mở rộng Thí nghiệm C đo lường Deadweight Loss ($m > 16$)
* **Hạn chót:** **17/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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

#### 🔲 Task P.3: Biên soạn Tài liệu Phân tích Đe dọa Bảo mật (`docs/THREAT_MODELING.md`)
* **Hạn chót:** **18/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  Tạo tệp mới `docs/THREAT_MODELING.md` phân tích chuyên sâu các nguy cơ bảo mật đối với cơ chế khớp lệnh ngoài chuỗi (Off-chain Matching, On-chain Settlement):
  1. *Nguy cơ 1 (Operator Front-running):* Người vận hành Engine chèn lệnh riêng hoặc thay đổi thứ tự khớp ngoài chuỗi $\to$ Giải pháp: Cơ chế cam kết hàm băm công khai (Commit-Reveal / Batch Hash publication).
  2. *Nguy cơ 2 (MEV Searcher Arbitrage):* Thợ đào/bot chèn giao dịch trước khi `batchSettleTrades` được ghi vào block $\to$ Giải pháp: Quyền gọi chỉ định `SETTLEMENT_OPERATOR_ROLE`.
  3. *Nguy cơ 3 (Rò rỉ Private Key của Submitter Bot):* Bot bị chiếm quyền điều khiển $\to$ Giải pháp: Hợp đồng giới hạn quyền ví bot chỉ được gọi thanh toán, không được rút tiền/chuyển token.
  4. *Nguy cơ 4 (Spam lệnh GTC rác không khóa tài sản):* Người dùng tạo ví miễn phí spam lệnh tích tuổi $\to$ Giải pháp: Khối lượng tối thiểu (Min Order Size) và biên độ giá (Price Collars) từ Oracle.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tệp `docs/THREAT_MODELING.md` hoàn chỉnh theo chuẩn bảo mật hệ thống thông tin.

---

#### 🔲 Task P.4: Chuẩn hóa Học thuật từ Bài báo gốc & Chốt các điểm H4, H7, H8
* **Hạn chót:** **20/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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
- Ngày ...:
- Tiến độ:
- Vấn đề phát sinh (nếu có):
```
