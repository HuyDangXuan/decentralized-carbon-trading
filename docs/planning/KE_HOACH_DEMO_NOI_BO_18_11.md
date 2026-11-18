# 🎯 KẾ HOẠCH TỔ CHỨC PHIÊN DEMO LIÊN THÔNG NỘI BỘ (18/11/2026)
## CHƯƠNG TRÌNH DIỄN TẬP VÀ NGHIỆM THU TÍCH HỢP HỆ THỐNG GIAI ĐOẠN 2
### ĐỀ TÀI: HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON MINH BẠCH VÀ HIỆU QUẢ TRÊN NỀN TẢNG BLOCKCHAIN

- **Thời gian diễn ra:** 08:30 – 10:30, Thứ Tư ngày 18/11/2026
- **Hình thức:** Họp trực tuyến qua Google Meet (Ghi hình toàn bộ quá trình demo)
- **Chủ trì & Điều phối:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Thành phần tham dự bắt buộc:**
  1. **Đặng Xuân Huy** (MSV: 23810310007) – *Chủ nhiệm đề tài / Lead Architect*
  2. **Nguyễn Hoàng Đức** (MSV: 23810310060) – *Smart Contract & On-chain Settlement Engineer*
  3. **Nguyễn Bảo Phi** (MSV: 23810310017) – *Auction Algorithm & Matching Engine Specialist*
  4. **Ngô Văn Thắng** (MSV: 23810310401) – *Fullstack Web3 Developer & UI/UX Designer*
- **Mục tiêu phiên họp:** Kiểm thử toàn trình liên thông 3 phân hệ (Frontend DApp $\leftrightarrow$ Matching Engine API $\leftrightarrow$ Smart Contracts trên Polygon Amoy Testnet), phát hiện và xử lý dứt điểm các lỗi phát sinh, ký biên bản nghiệm thu kỹ thuật nội bộ chuẩn bị báo cáo chính thức với TS. Nguyễn Thị Hồng Khánh.

---

## 1. PHÂN CÔNG VAI TRÒ & BỐ TRÍ MÀN HÌNH CHIA SẺ (SCREEN SHARE SETUP)

Để phiên demo diễn ra khoa học, minh bạch và mô phỏng chính xác luồng vận hành thực tế, 4 thành viên được phân bổ quyền hạn và màn hình giám sát chuyên biệt:

```
+-----------------------------------------------------------------------------------+
|                            HỘI NGHỊ GOOGLE MEET DEMO                              |
+-----------------------------------------------------------------------------------+
| [Màn hình 1 - Thắng]          | [Màn hình 2 - Phi]                                |
| • Next.js DApp (localhost:3000) | • Terminal 1: FastAPI Uvicorn Log (:8000)        |
| • MetaMask Wallet popups      | • Terminal 2: Bot Settlement Submitter Log        |
| • Trading Floor & Depth Chart | • JSON Payload / Sổ lệnh / $P^*$ Calculation       |
+--------------------------------+---------------------------------------------------+
| [Màn hình 3 - Đức]            | [Màn hình 4 - Huy (Chủ trì)]                      |
| • PolygonScan Amoy Explorer   | • Dashboard Điều phối Kịch bản                    |
| • Sự kiện TradeSettled        | • Script Kiểm thử E2E độc lập                     |
| • Biến động số dư On-chain    | • Biên bản Nghiệm thu Kỹ thuật & Ghi âm/Ghi hình  |
+--------------------------------+---------------------------------------------------+
```

### Chi tiết nhiệm vụ từng vị trí:
1. **Ngô Văn Thắng (Người thao tác người dùng - Trader Actor):**
   - Đóng vai trò Buyer và Seller thực hiện các thao tác từ góc nhìn người dùng cuối:
     * Nhận token thử nghiệm qua `FaucetModal.tsx`.
     * Nhập form đặt lệnh, thực hiện ký số EIP-712 Typed Data qua MetaMask (Gasless).
     * Theo dõi phản hồi thời gian thực trên Sổ lệnh (OrderBook) và Biểu đồ độ sâu (DepthChart).
     * Thao tác tiêu hủy tín chỉ ESG trên giao diện và tải chứng nhận hoàn thành có mã QR.
2. **Nguyễn Bảo Phi (Người giám sát Động cơ Khớp lệnh - Engine Operator):**
   - Đảm bảo dịch vụ FastAPI hoạt động thông suốt:
     * Trực tiếp theo dõi log tiếp nhận lệnh EIP-712 qua `POST /api/v1/orders`.
     * Kích hoạt phiên khớp lệnh qua `POST /api/v1/sessions/run`.
     * Trình chiếu thuật toán phân bổ Hamilton `age_prorata` và công thức xác định giá khớp đồng nhất $P^*$.
     * Khởi chạy bot `settlement_submitter.py` để lấy `MatchResult[]`, thực hiện pre-flight check và nộp giao dịch `batchSettleTrades` lên Polygon Amoy.
3. **Nguyễn Hoàng Đức (Người giám sát Hợp đồng Thông minh - Blockchain Auditor):**
   - Mở sẵn các tab trình duyệt tra cứu trên PolygonScan Amoy:
     * Giám sát hợp đồng đấu giá: `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`
     * Giám sát hợp đồng tín chỉ: `0x851978601b47a61B8aF3bcC1707B689Fbc977697`
     * Giám sát hợp đồng thanh toán: `0xe35681b0882d533458d22B344268642136ebD813`
     * Giám sát hợp đồng Faucet: `0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED`
   - Phân tích chi tiết Transaction Receipt: lượng gas thực tế tiêu thụ, trạng thái thực thi của 7 chốt chặn bảo mật, các Event `TradeSettled`, `BatchSettlementCompleted`, `CarbonCreditRetired`.
4. **Đặng Xuân Huy (Chủ tọa phiên Demo - Lead Coordinator):**
   - Điều khiển tiến trình cuộc họp theo đúng mốc thời gian quy định.
   - Ra lệnh kích hoạt từng bước kịch bản kiểm thử, kiểm tra chéo bằng script độc lập `scripts/test_e2e_integration.py`.
   - Ghi nhận lỗi (nếu có), xác nhận tiêu chí nghiệm thu và lập Biên bản hoàn thành.

---

## 2. CHECKLIST KIỂM TRA MÔI TRƯỜNG TRƯỚC PHIÊN DEMO (PRE-FLIGHT CHECKLIST)

*Tất cả 4 thành viên phải hoàn tất việc kiểm tra môi trường trước 08:15 ngày 18/11/2026:*

| STT | Hạng mục kiểm tra | Phụ trách | Giá trị cấu hình chuẩn | Trạng thái sẵn sàng |
| :---: | :--- | :---: | :--- | :---: |
| 1 | Mạng RPC Polygon Amoy | Toàn nhóm | `https://polygon-amoy.gateway.tenderly.co`<br/>Dự phòng: `https://poly-amoy-testnet.api.pocket.network` | [x] SẴN SÀNG |
| 2 | Chain ID & Currency | Toàn nhóm | `ChainId: 80002` (0x13882) - Native Gas: `POL` | [x] SẴN SÀNG |
| 3 | Contract `CarbonDoubleAuction` | Đức | `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f` | [x] ĐÃ DEPLOY |
| 4 | Contract `CarbonCredit1155` | Đức | `0x851978601b47a61B8aF3bcC1707B689Fbc977697` | [x] ĐÃ DEPLOY |
| 5 | Contract `MockUSDC` | Đức | `0xe35681b0882d533458d22B344268642136ebD813` | [x] ĐÃ DEPLOY |
| 6 | Contract `EvccFaucet` | Đức | `0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED` (Có 1,000 EVCC #101) | [x] ĐÃ DEPLOY |
| 7 | Ví Operator của Submitter Bot | Phi, Đức | Địa chỉ: `0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE`<br/>Quyền: `SETTLEMENT_OPERATOR_ROLE` = `true`<br/>Số dư: $\ge 0.5$ POL | [x] SẴN SÀNG |
| 8 | Ví thử nghiệm Buyer | Thắng, Huy | Địa chỉ ví MetaMask 1: Có $\ge 0.1$ POL, số dư MockUSDC | [x] SẴN SÀNG |
| 9 | Ví thử nghiệm Seller | Thắng, Huy | Địa chỉ ví MetaMask 2: Có $\ge 0.1$ POL, số dư EVCC #101 | [x] SẴN SÀNG |
| 10 | FastAPI Backend Server | Phi | Cổng 8000: Có biến `AUCTION_CONTRACT_ADDRESS` | [x] SẴN SÀNG |
| 11 | Web3 Next.js DApp | Thắng | Cổng 3000: `.env.local` cấu hình đúng các địa chỉ trên | [x] SẴN SÀNG |
| 12 | Script E2E Integration | Huy | `scripts/test_e2e_integration.py` sẵn sàng chạy | [x] SẴN SÀNG |

---

## 3. LỊCH TRÌNH VÀ KỊCH BẢN THỰC THI CHI TIẾT (DEMO SCENARIOS TIMELINE)

### ⏱️ TỔNG QUAN THỜI GIAN BIỂU (08:30 – 10:30)
- **08:30 – 08:45 (15 phút):** Khởi động phiên họp, đối soát Checklist môi trường, Huy phổ biến quy chế demo.
- **08:45 – 09:05 (20 phút):** Kịch bản 1 & 2 – Khởi tạo tài sản Faucet & Phiên giao dịch cơ sở $k$-DA.
- **09:05 – 09:30 (25 phút):** Kịch bản 3 – Khớp lệnh theo lô (Batch Settlement) & Đánh giá tiết kiệm gas.
- **09:30 – 09:50 (20 phút):** Kịch bản 4 – Kiểm thử 7 Chốt chặn bảo mật & Xử lý trường hợp ngoại lệ.
- **09:50 – 10:10 (20 phút):** Kịch bản 5 – Quy trình Tiêu hủy Tín chỉ (Retirement) & Cấp Chứng chỉ ESG On-chain.
- **10:10 – 10:30 (20 phút):** Thảo luận lỗi, thống nhất phương án hoàn thiện, ký Biên bản Nghiệm thu nội bộ.

---

### 🎬 CHI TIẾT 5 KỊCH BẢN KIỂM THỬ THỰC HÀNH

#### 📌 KỊCH BẢN 1: CẤP PHÁT TÀI SẢN QUA FAUCET TRÊN GIAO DIỆN (UI FAUCET CLAIM)
- **Mục tiêu:** Chứng minh người dùng mới có thể tự cấp vốn MockUSDC và EVCC thử nghiệm trực tiếp từ Web3 UI mà không cần can thiệp kỹ thuật dòng lệnh.
- **Các bước tiến hành:**
  1. Thắng mở trình duyệt Chrome, kết nối ví Buyer trên DApp Next.js (`http://localhost:3000`).
  2. Bấm vào nút **"Faucet"** trên thanh điều hướng Header $\to$ Modal `FaucetModal.tsx` mở ra.
  3. Bấm **"Nhận 10,000 MockUSDC"** $\to$ Ký xác nhận giao dịch trên MetaMask gọi hàm `mint` của hợp đồng `MockUSDC`.
  4. Chuyển sang ví Seller, bấm nút **"Nhận 100 EVCC (#101)"** $\to$ Xác nhận giao dịch gọi `EvccFaucet.claim()`.
  5. Đức quan sát PolygonScan xác nhận 2 giao dịch hoàn tất.
  6. Thắng kiểm tra số dư hiển thị trên thanh Header: Buyer có 10,000 USDC, Seller có 100 EVCC.
- **Kết quả kỳ vọng:** Số dư tài sản cập nhật chính xác trên DApp ngay sau khi block được đào.

---

#### 📌 KỊCH BẢN 2: PHIÊN KHỚP LỆNH CHUẨN $k$-DA VÀ ATOMIC SETTLEMENT T+0
- **Mục tiêu:** Trực quan hóa dòng chảy khép kín từ đặt lệnh EIP-712 gasless đến khớp lệnh ngoài chuỗi và thanh toán nguyên tử on-chain.
- **Các thông số kịch bản:**
  - Token giao dịch: Lô #101 (Rừng Tây Bắc 2026, đơn vị tCO2e).
  - Lệnh Mua (Buyer): Mua 50 tCO2e với giá tối đa **12.0 USDC/tCO2e** (Loại lệnh: GTC).
  - Lệnh Bán (Seller): Bán 50 tCO2e với giá tối thiểu **10.0 USDC/tCO2e** (Loại lệnh: GTC).
  - Hệ số giá: $k = 0.5$ (Quy tắc trung bình cộng chuẩn).
  - Kỳ vọng kết quả:
    + Giá khớp thanh toán đồng nhất: $P^* = 10.0 + 0.5 \times (12.0 - 10.0) = 11.0\text{ USDC}$.
    + Khối lượng khớp: $Q^* = 50\text{ tCO2e}$.
    + Tổng giá trị thanh toán: $50 \times 11.0 = 550\text{ USDC}$.
- **Các bước tiến hành:**
  1. **Bước 2.1 (Approve On-chain):** Buyer approve 550 USDC cho `CarbonDoubleAuction`; Seller gọi `setApprovalForAll(AuctionContract, true)` cho `CarbonCredit1155`.
  2. **Bước 2.2 (Đặt lệnh & Ký EIP-712):**
     - Thắng dùng ví Buyer nhập form: Buy 50 tCO2e @ 12 USDC $\to$ Bấm "Ký & Gửi lệnh" $\to$ MetaMask hiển thị bảng ký EIP-712 Typed Data $\to$ Ký thành công, không tốn gas.
     - Thắng chuyển ví Seller nhập form: Sell 50 tCO2e @ 10 USDC $\to$ Ký EIP-712 thành công.
  3. **Bước 2.3 (Nhận lệnh ngoài chuỗi):**
     - Phi trình chiếu log FastAPI: Nhận 2 lệnh, xác thực chữ ký `ECDSA.recover` trùng khớp địa chỉ ví, ghi nhận vào OrderBook.
     - Thắng trình chiếu giao diện: Biểu đồ độ sâu (DepthChart) và danh sách sổ lệnh cập nhật 2 lệnh mới $< 1$s qua WebSocket.
  4. **Bước 2.4 (Chạy phiên khớp lệnh):**
     - Phi gửi yêu cầu `POST /api/v1/sessions/run`.
     - Log engine hiển thị: Tính toán thặng dư tối đa, xác định $P^* = 11.0\text{ USDC}$, khối lượng 50 đơn vị, xuất `MatchResult`.
  5. **Bước 2.5 (Thanh toán On-chain qua Submitter Bot):**
     - Phi khởi chạy bot: `python settlement_submitter.py --session-id <ID>`.
     - Bot đọc RPC, thực hiện kiểm tra tiền gửi, gọi `batchSettleTrades`.
     - Transaction được đưa vào block mạng Amoy, in TxHash ra console.
  6. **Bước 2.6 (Kiểm toán On-chain):**
     - Đức mở link PolygonScan của TxHash:
       * Status: Success.
       * Bắt được event: `TradeSettled(tradeHash, buyer, seller, 101, 50, 11000000)`.
       * Biến động số dư: Buyer nhận đúng 50 EVCC, trừ 550 USDC; Seller nhận đúng 550 USDC, trừ 50 EVCC.
- **Kết quả kỳ vọng:** Giao dịch thành công nguyên tử T+0, không phát sinh chênh lệch số dư.

---

#### 📌 KỊCH BẢN 3: THANH TOÁN THEO LÔ (BATCH SETTLEMENT) & ĐO LƯỜNG TIẾT KIỆM GAS
- **Mục tiêu:** Chứng minh tính năng gom cụm thanh toán nhiều giao dịch cùng lúc (`batchSettleTrades`), bảo vệ mạng lưới chống nghẽn và đo lường tỷ lệ tiết kiệm gas thực tế $> 50\%$.
- **Các bước tiến hành:**
  1. Sử dụng script tự động sinh đồng thời 5 cặp lệnh đối ứng giữa các tài khoản thử nghiệm.
  2. Kích hoạt phiên đấu giá: Engine xuất mảng gồm 5 `MatchResult`.
  3. Bot Submitter đóng gói mảng 5 `MatchedTrade[]` và nộp trong duy nhất 1 giao dịch blockchain.
  4. Đức kiểm tra biên nhận giao dịch trên PolygonScan:
     - So sánh tổng gas tiêu thụ của Batch 5 ($\approx 763,000$ gas) với 5 giao dịch đơn lẻ ($5 \times 286,000 \approx 1,430,000$ gas).
     - Tính toán tỷ lệ tiết kiệm gas: $\frac{1,430,000 - 763,000}{1,430,000} \approx 46.6\% - 50\%$.
- **Kết quả kỳ vọng:** Cả 5 cặp lệnh đều được thanh toán an toàn trong 1 transaction, minh chứng số liệu khớp với bảng Benchmark của Đức.

---

#### 📌 KỊCH BẢN 4: THỬ NGHIỆM 7 CHỐT CHẶN BẢO MẬT & XỬ LÝ NGOẠI LỆ (SECURITY GATES TEST)
- **Mục tiêu:** Kiểm tra độ vững chắc của hệ thống trước các hành vi bất thường, tấn công gian lận hoặc lỗi người dùng.
- **Các tình huống kiểm thử cụ thể:**
  1. **Tình huống 4.1 (Wash Trading Detection):** Cố tình tạo 1 cặp lệnh mà địa chỉ Buyer trùng với Seller (`bid.trader == ask.trader`).
     - *Kỳ vọng:* Smart contract revert với lỗi bảo mật hoặc Bot Submitter chặn ngay từ khâu pre-flight check với trạng thái `SKIPPED`.
  2. **Tình huống 4.2 (Chữ ký Hết hạn - Signature Expired):** Gửi lệnh có `deadline < block.timestamp`.
     - *Kỳ vọng:* Bị từ chối on-chain với custom error `SignatureExpired`.
  3. **Tình huống 4.3 (Thiếu số dư hoặc Rút Allowance giữa chừng):** Bên mua rút cạn USDC trước khi bot nộp lệnh.
     - *Kỳ vọng:* Bot Submitter phát hiện và đánh dấu `SKIPPED`; nếu chạy cờ `--no-funds-check`, hàm `batchSettleTrades` sử dụng khối `try/catch` bỏ qua lệnh lỗi mà không làm đổ vỡ các lệnh hợp lệ khác trong batch.
  4. **Tình huống 4.4 (Chống nộp trùng - Replay Protection):** Cố tình nộp lại transaction của Kịch bản 2.
     - *Kỳ vọng:* Hợp đồng từ chối với lỗi `TradeAlreadyExecuted` do `tradeHash` tất định đã tồn tại trong mapping `executedTrades`.
- **Kết quả kỳ vọng:** Toàn bộ 7 chốt chặn bảo mật phản ứng chính xác theo thiết kế, hệ thống không bị crash hoặc thất thoát tài sản.

---

#### 📌 KỊCH BẢN 5: TIÊU HỦY TÍN CHỈ ESG & TRUY XUẤT CHỨNG NHẬN ON-CHAIN
- **Mục tiêu:** Trực quan hóa quy trình doanh nghiệp tiêu hủy tín chỉ để nhận Giấy chứng nhận Bù đắp Carbon vĩnh viễn (Permanent ESG Retirement).
- **Các bước tiến hành:**
  1. Thắng mở phân hệ **ESG Retirement Portal** trên giao diện DApp.
  2. Chọn lô tín chỉ đã sở hữu (#101), nhập số lượng cần tiêu hủy: 20 tCO2e.
  3. Nhập thông tin người thụ hưởng (Beneficiary): "Tập đoàn Điện lực Việt Nam - EVN" và mục đích: "Bù đắp phát thải Net Zero 2026".
  4. Bấm **"Xác nhận Tiêu hủy Vĩnh viễn"** $\to$ Ký giao dịch MetaMask gọi hàm `retireCarbonCredit` trên hợp đồng `CarbonCredit1155`.
  5. Đức kiểm tra PolygonScan:
     - Giao dịch hoàn tất, phát sinh sự kiện `CarbonCreditRetired(101, trader, 20, "EVN", timestamp)`.
     - Tổng cung lưu hành của lô 101 giảm tương ứng, số dư của ví bị đốt vĩnh viễn.
  6. Thắng kiểm tra màn hình: DApp hiển thị Giấy chứng nhận điện tử (Certificate of Retirement) kèm mã QR tra cứu trực tiếp giao dịch trên PolygonScan.
- **Kết quả kỳ vọng:** Luồng tiêu hủy thực thi minh bạch, đáp ứng trọn vẹn yêu cầu chức năng FR-12 và FR-13 của tài liệu SRS.

---

## 4. KẾ HOẠCH DỰ PHÒNG & XỬ LÝ SỰ CỐ KỸ THUẬT (CONTINGENCY & TROUBLESHOOTING)

Trong quá trình demo trực tiếp trên testnet công khai, các sự cố ngoại cảnh có thể phát sinh. Nhóm quy định phương án ứng phó chuẩn sau:

| Sự cố tiềm ẩn | Nguyên nhân gốc rễ | Phương án ứng phó tức thì (Action Plan) |
| :--- | :--- | :--- |
| **RPC Amoy bị nghẽn / Rate Limit** | Nhà cung cấp Pocket Network quá tải request | Thắng & Phi chuyển ngay sang Tenderly RPC: `https://polygon-amoy.gateway.tenderly.co` hoặc dRPC: `https://polygon-amoy.drpc.org`. |
| **Lỗi PoA Middleware trên Web3.py** | Cấu trúc khối Polygon Amoy có trường `extraData > 32 bytes` | Đảm bảo bot luôn chạy bản commit `2a4c3bf` đã tiêm sẵn `PoAMiddleware` vào Web3 provider. |
| **Phí Gas Amoy tăng đột biến** | Biến động mạng lưới khiến tx bị pending lâu | Đức hướng dẫn cấu hình tăng `maxFeePerGas` lên 35 Gwei và `maxPriorityFeePerGas` lên 30 Gwei trong script nộp bot. |
| **Giao dịch bị treo không có Receipt** | Timeout kết nối HTTP sau khi gửi tx | Tuyệt đối **không nộp lại phiên mới**. Sử dụng ngay lệnh cứu hộ của bot: `python settlement_submitter.py --session-id <ID> --recover-tx <TxHash>`. |
| **MetaMask từ chối kết nối** | Xung đột extension ví Web3 khác (Phantom, Rabby) | Thắng mở cửa sổ ẩn danh (Incognito) chỉ kích hoạt duy nhất MetaMask, hoặc sử dụng cơ chế EIP-6963 đã cài đặt trong mã nguồn. |

---

## 5. BIÊN BẢN NGHIỆM THU KỸ THUẬT NỘI BỘ (INTERNAL SIGN-OFF TEMPLATE)

*Cuối phiên họp, Chủ nhiệm đề tài và 3 thành viên sẽ cùng ký duyệt vào biên bản nghiệm thu dưới đây để lưu hồ sơ khoa học:*

```markdown
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
-------------------------

BIÊN BẢN NGHIỆM THU KỸ THUẬT LIÊN THÔNG NỘI BỘ (GIAI ĐOẠN 2)
Đề tài NCKH Sinh viên: "Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain"
Thời gian: ...h... ngày 18 tháng 11 năm 2026
Địa điểm: Phiên họp trực tuyến Google Meet

I. THÀNH PHẦN NGHIỆM THU:
1. Đặng Xuân Huy - Chủ nhiệm đề tài / Lead Architect (Chủ trì)
2. Nguyễn Hoàng Đức - Kỹ sư Smart Contract & On-chain Settlement
3. Nguyễn Bảo Phi - Kỹ sư Động cơ Khớp lệnh & Mô phỏng Game Theory
4. Ngô Văn Thắng - Kỹ sư Giao diện Web3 DApp & Thiết kế UI/UX

II. KẾT QUẢ ĐÁNH GIÁ 5 KỊCH BẢN KIỂM THỬ:
- Kịch bản 1 (Cấp phát tài sản Faucet UI):        [ ] ĐẠT   [ ] CHƯA ĐẠT
- Kịch bản 2 (Khớp lệnh k-DA & Settle T+0):      [ ] ĐẠT   [ ] CHƯA ĐẠT
- Kịch bản 3 (Batch Settlement tiết kiệm gas):   [ ] ĐẠT   [ ] CHƯA ĐẠT
- Kịch bản 4 (Kiểm tra 7 chốt chặn bảo mật):     [ ] ĐẠT   [ ] CHƯA ĐẠT
- Kịch bản 5 (Tiêu hủy tín chỉ ESG & Chứng nhận):[ ] ĐẠT   [ ] CHƯA ĐẠT

III. CÁC TỒN TẠI VÀ THỐNG NHẤT HƯỚNG KHẮC PHỤC:
...

IV. KẾT LUẬN CHUNG:
Hệ thống đạt / chưa đạt yêu cầu kỹ thuật để tổ chức báo cáo tiến độ với Giảng viên hướng dẫn TS. Nguyễn Thị Hồng Khánh.

CHỦ NHIỆM ĐỀ TÀI              CÁC THÀNH VIÊN THAM GIA ĐỒNG KÝ
(Ký, ghi rõ họ tên)           (Ký, ghi rõ họ tên)
  Đặng Xuân Huy               Nguyễn Hoàng Đức    Nguyễn Bảo Phi    Ngô Văn Thắng
```

---
*Tài liệu này là căn cứ tổ chức và điều hành chính thức cho phiên diễn tập 18/11/2026 của nhóm nghiên cứu.*
