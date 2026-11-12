# 📋 BẢNG GIAO VIỆC CÁ NHÂN: NGÔ VĂN THẮNG
## PHÂN HỆ: FULLSTACK WEB3 DAPP, METADATA SCHEMA & UI/UX FIGMA

* **Người phụ trách:** Ngô Văn Thắng (MSV: 23810310401 - Lớp D18CNPM1)
* **Vai trò:** Fullstack Web3 Developer & UI/UX Designer
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 20/11/2026
* **Nhánh làm việc khuyến nghị:** `feat/thang-faucet-ui-figma`
* **Người giao việc & Nghiệm thu:** Đặng Xuân Huy (Chủ nhiệm đề tài)

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### 🔲 Task T.1: Cấu hình DApp kết nối Contract thực tế trên Polygon Amoy
* **Hạn chót:** **15/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Nhận địa chỉ 3 hợp đồng (`MockUSDC`, `CarbonCredit1155`, `CarbonDoubleAuction`) từ tệp `docs/DEPLOYED_ADDRESSES.md` của Đức.
  2. Tạo/cập nhật file `frontend/.env.local`:
     ```env
     NEXT_PUBLIC_AMOY_RPC_URL="https://rpc-amoy.polygon.technology"
     NEXT_PUBLIC_CARBON_AUCTION_ADDRESS="0x..."
     NEXT_PUBLIC_CARBON_CREDIT_ADDRESS="0x..."
     NEXT_PUBLIC_MOCK_USDC_ADDRESS="0x..."
     NEXT_PUBLIC_MATCHING_API_URL="http://localhost:8000"
     ```
  3. Kiểm tra file `frontend/src/web3/config.ts` đảm bảo Wagmi v2 kết nối đúng mạng Polygon Amoy (ChainId: 80002).
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Khởi động `npm run dev`, mở trình duyệt kết nối ví MetaMask chuyển mạng Amoy: DApp đọc và hiển thị chính xác số dư token `EVCC` và số dư `MockUSDC` từ blockchain thật.

---

#### 🔲 Task T.2: Xây dựng Modal Faucet MockUSDC & Mint Thử nghiệm trên UI
* **Hạn chót:** **16/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Tạo component mới: `frontend/src/components/FaucetModal.tsx`.
  2. Cung cấp giao diện trực quan với 2 nút bấm tiện ích:
     * **Nút 1: "Nhận 10,000 MockUSDC"** $\to$ Gọi hàm `mint(msg.sender, 10_000 * 10^6)` trên contract `MockUSDC.sol`.
     * **Nút 2: "Đúc thử 100 tCO2e"** $\to$ Gọi hàm đúc mẫu trên `CarbonCredit1155.sol` (Token ID: 101 - Rừng Tây Bắc Vintage 2026).
  3. Thêm nút kích hoạt Modal này trên Header/Navbar của DApp.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Người dùng thử nghiệm, GVHD hoặc Hội đồng nghiệm thu có thể tự bấm nút nhận token testnet ngay trên web mà không cần dùng lệnh CLI phức tạp.

---

#### 🔲 Task T.3: Kiểm thử Luồng Đặt lệnh & Vẽ Biểu đồ Độ sâu (Depth Chart)
* **Hạn chót:** **18/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Khởi chạy song song:
     * Server FastAPI của Phi: `uvicorn system_agents.matching_engine.api_service:app --port 8000`.
     * Ứng dụng Next.js: `npm run dev`.
  2. Kiểm thử dòng chảy thực tế trên màn hình `TradingFloor.tsx`:
     * Nhập Form: Loại lệnh (BID/ASK), Khối lượng (tCO2e), Mức giá (USDC).
     * Bấm "Đặt lệnh" $\to$ MetaMask hiển thị cửa sổ ký EIP-712 Typed Data Gasless.
     * Sau khi ký xong, DApp tự động gửi `POST /api/v1/orders` tới FastAPI.
     * Kiểm tra kênh WebSocket: Biểu đồ độ sâu sổ lệnh (`DepthChart.tsx`) và danh sách sổ lệnh cập nhật lệnh mới trong vòng $< 1$ giây.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Luồng đặt lệnh ngoài chuỗi hoạt động trơn tru không lỗi console, hiển thị đầy đủ thông báo Toast thành công.

---

#### 🔲 Task T.4: Hoàn thiện Bộ Thiết kế Wireframe / Mockup Figma 4 Phân hệ DApp
* **Hạn chót:** **20/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Hoàn thiện bản vẽ thiết kế giao diện đồ họa chi tiết (UI/UX Mockups) trên Figma cho 4 cổng phân hệ chính của DApp (theo cam kết tại RACI Matrix Giai đoạn 2):
     * **Phân hệ 1 (Project Developer Portal):** Giao diện nộp hồ sơ PDD, đăng tải báo cáo MRV lên IPFS, theo dõi đúc tín chỉ.
     * **Phân hệ 2 (Verifier/VVB Portal):** Cổng thẩm tra độc lập dành cho kiểm toán viên xem xét hồ sơ và ký xác nhận on-chain.
     * **Phân hệ 3 (Trading Floor Portal):** Sàn giao dịch với Sổ lệnh OrderBook trực quan, biểu đồ giá khớp $k$-DA và lịch sử khớp lệnh.
     * **Phân hệ 4 (ESG Retirement Portal):** Khu vực doanh nghiệp thực hiện tiêu hủy tín chỉ vĩnh viễn và xuất giấy chứng nhận ESG có mã QR truy xuất on-chain.
  2. Xuất các ảnh chụp màn hình chất lượng cao vào thư mục `docs/wireframes/` và đính kèm đường link Figma có quyền xem vào file `docs/wireframes/README.md`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Bộ bản vẽ Figma hoàn chỉnh 4 phân hệ được bàn giao cho Huy để đưa vào Slide và Hồ sơ Báo cáo tiến độ GĐ2 gửi GVHD.

---

### NHẬT KÝ & GHI CHÚ CÁ NHÂN CỦA THẮNG
*(Thắng hãy ghi chú tiến độ giao diện hoặc các khó khăn gặp phải vào phần này rồi commit lên Git)*

```markdown
- Ngày ...:
- Tiến độ:
- Vấn đề phát sinh (nếu có):
```

- **12/11/2026 · T.1** Đã cấu hình ba địa chỉ Polygon Amoy và bổ sung hiển thị số dư EVCC theo token ID cùng MockUSDC theo địa chỉ ví. Số dư MockUSDC dùng 6 chữ số thập phân.
- **Kiểm tra** 14 bài kiểm thử frontend, 10 bài kiểm thử metadata, TypeScript, lint và production build đều đạt. Chrome dùng đầu nối ví giả lập với RPC Amoy thật hiển thị 0 EVCC cho token 101 và 10.000.000 MockUSDC, khớp kết quả đọc độc lập tại block 52674033 của ví triển khai công khai.
- **Nghiệm thu còn lại** Kết nối MetaMask thật trên Polygon Amoy và đối chiếu số dư của tài khoản đang kết nối. T.1 giữ trạng thái chờ xác nhận lượt kiểm tra này.
