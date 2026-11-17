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
     NEXT_PUBLIC_AMOY_RPC_URL="https://polygon-amoy.gateway.tenderly.co"
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
     * **Nút 2: "Nhận 100 EVCC (#101)"** $\to$ Gọi `EvccFaucet.claim()` để chuyển 100 tCO₂e đã đúc trên `CarbonCredit1155.sol` (Token ID: 101 - Rừng Tây Bắc Vintage 2026). `mintProjectLot` chỉ tạo lô một lần và yêu cầu `VERIFIER_ROLE`.
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

- **17/11/2026 · T.2** Modal faucet trên navbar có nút nhận 10.000 MockUSDC và 100 EVCC #101. Faucet EVCC cấp từ số dư của lô đã đúc, một lượt mỗi ví, vì `mintProjectLot` yêu cầu verifier và chỉ tạo lô #101 một lần. Đã kiểm tra lệnh mint MockUSDC bằng mô phỏng Amoy và chạy bytecode hai luồng trên EVM cục bộ.
- **Nghiệm thu MockUSDC** Ví thử `0xF6dD…B5d5` nhận 10.000 MockUSDC trên Amoy, số dư tăng từ 100.000 lên 110.000 tại block `53080025`. [Biên nhận MockUSDC](https://amoy.polygonscan.com/tx/0x5c5f6de5c2d6248c52772b134a6636a4d7415be0e3341178be03b2ab5e553bf2)
- **Còn chờ nghiệm thu EVCC #101** Đức đã nạp 1.000 EVCC vào faucet `0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED`. Frontend đọc hợp đồng EVCC liên kết và tồn kho #101 trước khi gọi `claim()`. Cần xác nhận giao dịch trên web và đối chiếu mức tăng 100 EVCC. [Biên nhận nạp faucet](https://amoy.polygonscan.com/tx/0xafd2b6c47daa6132902a350f6a9ee3dd100486c2dbf70908cdccd4e086efe17d)
- **17/11/2026 · T.4** Đã dựng bốn mockup theo SRS và xuất ảnh PNG 2880 × 2000 px cùng nguồn SVG tại [thư mục wireframes](../wireframes/README.md). Còn chờ nhập vào Figma Design và xác minh Huy mở được link xem trước khi tích hoàn thành.
