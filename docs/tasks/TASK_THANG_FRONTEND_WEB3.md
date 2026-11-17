# 📋 BẢNG GIAO VIỆC CÁ NHÂN: NGÔ VĂN THẮNG
## PHÂN HỆ: FULLSTACK WEB3 DAPP, METADATA SCHEMA & UI/UX FIGMA

* **Người phụ trách:** Ngô Văn Thắng (MSV: 23810310401 - Lớp D18CNPM1)
* **Vai trò:** Fullstack Web3 Developer & UI/UX Designer
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 20/11/2026
* **Nhánh làm việc khuyến nghị:** `feat/thang-faucet-ui-figma`
* **Người giao việc & Nghiệm thu:** Đặng Xuân Huy (Chủ nhiệm đề tài)

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### ✅ Task T.1: Cấu hình DApp kết nối Contract thực tế trên Polygon Amoy
* **Hạn chót:** **15/11/2026**
* **Trạng thái:** `- [x] Hoàn thành`
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
     * Từ thư mục gốc, chạy FastAPI của Phi với `python -m uvicorn --app-dir system_agents/matching_engine api_service:app --port 8000`. Xem cấu hình địa chỉ hợp đồng trong [hướng dẫn frontend](../../frontend/README.md#đặt-lệnh-và-biểu-đồ-độ-sâu-t3).
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
- **Lỗi kết nối MetaMask** Ưu tiên MetaMask do trình duyệt công bố qua EIP-6963, hỗ trợ cách phát hiện cũ và hướng dẫn mở đúng trình duyệt khi không có tiện ích. Đã kiểm tra trường hợp có ví khác, thiếu MetaMask và hủy yêu cầu kết nối. Hai số dư vẫn khớp với RPC Amoy khi dùng đầu nối giả lập.
- **Nghiệm thu T.1** Chrome kết nối tiện ích MetaMask thật trên Polygon Amoy (chain ID 80002). Sau khi đổi RPC mặc định của DApp sang Tenderly, bảng điều khiển hiển thị **0 EVCC (token #101)** và **0 MockUSDC**. Kết quả khớp với hai lệnh `balanceOf` đọc độc lập tại block `52676023`; MockUSDC có 6 chữ số thập phân. Không cần ký hoặc gửi giao dịch để đối chiếu.
- **17/11/2026 · T.2** Modal faucet trên navbar có nút nhận 10.000 MockUSDC và 100 EVCC #101. Faucet EVCC cấp từ số dư của lô đã đúc, một lượt mỗi ví, vì `mintProjectLot` yêu cầu verifier và chỉ tạo lô #101 một lần. Đã kiểm tra lệnh mint MockUSDC bằng mô phỏng Amoy và chạy bytecode hai luồng trên EVM cục bộ.
- **Nghiệm thu MockUSDC** Ví thử `0xF6dD…B5d5` nhận 10.000 MockUSDC trên Amoy, số dư tăng từ 100.000 lên 110.000 tại block `53080025`. [Biên nhận MockUSDC](https://amoy.polygonscan.com/tx/0x5c5f6de5c2d6248c52772b134a6636a4d7415be0e3341178be03b2ab5e553bf2)
- **Còn chờ nghiệm thu EVCC #101** Đức đã nạp 1.000 EVCC vào faucet `0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED`. Frontend đọc hợp đồng EVCC liên kết và tồn kho #101 trước khi gọi `claim()`. Cần xác nhận giao dịch trên web và đối chiếu mức tăng 100 EVCC. [Biên nhận nạp faucet](https://amoy.polygonscan.com/tx/0xafd2b6c47daa6132902a350f6a9ee3dd100486c2dbf70908cdccd4e086efe17d)
- **17/11/2026 · T.3** Frontend đọc `ORDER_TYPEHASH` và `userNonces()` trên Amoy, ký theo mẫu đang triển khai, gửi `POST /api/v1/orders` qua proxy Next.js và cập nhật Depth Chart bằng dữ liệu mức giá từ WebSocket của Phi.
- **Kiểm thử cục bộ T.3** Chrome dùng ví thử tự ký EIP-712, kết nối Next.js và FastAPI thật trên máy. Hai lệnh BID/GTC và ASK/IOC đều được API tiếp nhận với HTTP 201. Tab thứ hai cập nhật biểu đồ sau 498 ms và 366 ms kể từ lúc gửi POST, không có lỗi console. TypeScript, ESLint và 20 bài kiểm thử frontend đều đạt.
- **Điều kiện nghiệm thu T.3** Cần xác nhận ký bằng MetaMask thật và ghi bằng chứng trên web. Khớp phiên trong FastAPI hiện chạy thủ công. GTC/IOC do Matching Engine xử lý, còn mẫu chữ ký trên Amoy hiện tại chỉ ràng buộc hạn lệnh theo `deadline` và chưa ký `timeInForce` như SRS.
- **17/11/2026 · T.4** Đã dựng bốn mockup theo SRS và xuất ảnh PNG 2880 × 2000 px cùng nguồn SVG tại [thư mục wireframes](../wireframes/README.md). Còn chờ nhập vào Figma Design và xác minh Huy mở được link xem trước khi tích hoàn thành.
