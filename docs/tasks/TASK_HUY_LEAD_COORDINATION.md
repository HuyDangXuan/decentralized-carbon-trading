# 📋 BẢNG GIAO VIỆC CÁ NHÂN: ĐẶNG XUÂN HUY
## PHÂN HỆ: LEAD ARCHITECT, KIỂM THỬ END-TO-END & BÁO CÁO NGHIỆM THU

* **Người phụ trách:** Đặng Xuân Huy (MSV: 23810310007 - Lớp D18CNPM1)
* **Vai trò:** Chủ nhiệm đề tài & Kiến trúc sư trưởng (Lead Architect)
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 20/11/2026
* **Nhánh làm việc khuyến nghị:** `main` hoặc `feat/huy-e2e-testing-slides`
* **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### 🔲 Task H.1: Xây dựng Script Kiểm thử Toàn trình End-to-End (`test_e2e_integration.py`)
* **Hạn chót:** **17/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  Tạo tệp mới `scripts/test_e2e_integration.py` tự động hóa kịch bản kiểm thử khép kín 5 bước liên thông cả 3 phân hệ:
  1. *Bước 1:* Sinh 2 ví thử nghiệm Buyer và Seller bằng `eth-account`, faucet MockUSDC cho Buyer và đúc token EVCC cho Seller.
  2. *Bước 2:* Ký 2 lệnh đối ứng EIP-712 (Buyer đặt mua giá 12 USDC, Seller đặt bán giá 10 USDC cho 50 tCO2e).
  3. *Bước 3:* Đẩy cả 2 lệnh vào server FastAPI của Phi qua `POST /api/v1/orders`.
  4. *Bước 4:* Gọi `POST /api/v1/sessions/run` kích hoạt phiên khớp lệnh $k$-DA (kỳ vọng giá khớp $P^* = 11$ USDC).
  5. *Bước 5:* Chạy bot submitter của Phi gọi hàm `batchSettleTrades` trên hợp đồng của Đức trên Polygon Amoy $\to$ Kiểm tra số dư on-chain: Buyer nhận đúng 50 EVCC, Seller nhận đúng 550 USDC.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Script chạy thông suốt từ đầu đến cuối không bị revert on-chain và in ra bảng tổng kết kết quả khớp lệnh thành công.

---

#### 🔲 Task H.2: Tổ chức & Chủ trì Phiên Demo Liên thông Nội bộ nhóm
* **Hạn chót:** **18/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Triệu tập cuộc họp trực tuyến Google Meet với đầy đủ 4 thành viên.
  2. Phân công chạy thử:
     * Thắng mở màn hình DApp Next.js kết nối MetaMask.
     * Phi mở log server FastAPI và bot Submitter.
     * Đức mở giao diện PolygonScan theo dõi các transaction `TradeSettled`.
  3. Thao tác trực tiếp một phiên giao dịch thực tế trên trình duyệt từ đặt lệnh đến thanh toán on-chain.
  4. Ghi nhận các lỗi phát sinh, chốt biên bản nghiệm thu nội bộ.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Toàn bộ 4 thành viên thống nhất hệ thống chạy ổn định và sẵn sàng cho buổi báo cáo với GVHD.

---

#### 🔲 Task H.3: Biên soạn Slide Báo cáo Tiến độ Giai đoạn 2 (`docs/SLIDE_BAO_CAO_GIAI_DOAN_2.pptx`)
* **Hạn chót:** **20/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  Soạn thảo bài trình chiếu PowerPoint (15 – 20 slide) phục vụ buổi báo cáo tiến độ với TS. Nguyễn Thị Hồng Khánh và Hội đồng khoa học:
  - *Slide 1-3:* Mục tiêu đề tài, bài toán VCM và kiến trúc tổng thể lai (Off-chain MAS, On-chain Settlement).
  - *Slide 4-7:* Quyết định kiến trúc ADR-001, các yêu cầu chức năng cốt lõi (FR-01 đến FR-15) trong tài liệu SRS IEEE 830.
  - *Slide 8-10:* Thuật toán Đấu giá kép $k$-DA uniform, phá hòa Hamilton `age_prorata` và kết quả mô phỏng Deadweight Loss $O(1/m^2)$.
  - *Slide 11-13:* Thiết kế Smart Contract v2: 7 chốt chặn bảo mật, Batch Settlement và số liệu benchmark gas thực tế trên Polygon Amoy.
  - *Slide 14-16:* Trực quan hóa giao diện DApp 4 phân hệ (Figma mockups) và video/ảnh demo luồng đặt lệnh gasless EIP-712.
  - *Slide 17-18:* Kế hoạch triển khai Giai đoạn 3 (Tích hợp thực tế và chuẩn bị bài báo khoa học).
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tệp Slide hoàn chỉnh, định dạng chuyên nghiệp chuẩn học thuật được lưu tại `docs/SLIDE_BAO_CAO_GIAI_DOAN_2.pptx`.

---

#### 🔲 Task H.4: Duy trì Hệ thống Nhật ký Tiến độ Hàng ngày & Báo cáo GVHD
* **Hạn chót:** **Hàng ngày**
* **Trạng thái:** `- [⏳] Đang thực hiện liên tục`
* **Mô tả công việc:**
  - Hàng ngày, chạy công cụ tự động `python scripts/log_daily_progress.py --push` hoặc ra lệnh cho agent AI để cập nhật thư mục `docs/progress/`.
  - Giám sát tiến độ tick task `[x]` của Đức, Phi, Thắng trên thư mục `docs/tasks/`.
  - Định kỳ tổng hợp báo cáo tiến độ bằng văn bản gửi cho GVHD (TS. Nguyễn Thị Hồng Khánh).
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Thư mục `docs/progress/` luôn có bản ghi mới phản ánh trung thực toàn bộ diễn biến kỹ thuật của đề tài.

---

### NHẬT KÝ & GHI CHÚ CỦA CHỦ NHIỆM ĐỀ TÀI (HUY)

```markdown
- Ngày 11/11/2026: Đã hợp nhất toàn bộ 3 phân hệ vào main, khởi tạo hệ thống giao việc docs/tasks/ và chuẩn bị bước vào Sprint tích hợp liên thông.
```
