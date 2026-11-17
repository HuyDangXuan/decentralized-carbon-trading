# 📋 BẢNG GIAO VIỆC CÁ NHÂN: NGUYỄN HOÀNG ĐỨC
## PHÂN HỆ: SMART CONTRACT & ON-CHAIN SETTLEMENT LAYER (POLYGON AMOY)

* **Người phụ trách:** Nguyễn Hoàng Đức (MSV: 23810310060 - Lớp D18CNPM1)
* **Vai trò:** Smart Contract Architect & Engineer
* **Thời gian thực hiện Sprint:** Từ ngày 12/11/2026 đến ngày 16/11/2026
* **Nhánh làm việc khuyến nghị:** `feat/duc-deploy-amoy-gas-benchmark`
* **Người giao việc & Nghiệm thu:** Đặng Xuân Huy (Chủ nhiệm đề tài)

---

### DANH SÁCH NHIỆM VỤ CẦN THỰC HIỆN

#### 🔲 Task Đ.1: Cài đặt môi trường `npm install` & Chạy Local Test Hardhat
* **Hạn chót:** **12/11/2026**
* **Trạng thái:** `- [x] Đã hoàn thành (14/14 Test Cases PASS 100%, gas đạt 67,750 gas/lệnh < 85k chuẩn NFR-02)`
* **Mô tả công việc:**
  1. Cài đặt các thư viện phụ thuộc bằng lệnh: `npm install` tại thư mục gốc của repository.
  2. Biên dịch hợp đồng: `npx hardhat compile` (đảm bảo không còn warning nghiêm trọng).
  3. Chạy toàn bộ bài test: `npx hardhat test`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tất cả các kịch bản kiểm thử trong `test/CarbonTrading.test.js` đạt trạng thái **PASS 100%** (xác thực trọn vẹn 7 chốt chặn bảo mật).

---

#### 🔲 Task Đ.2: Cấu hình & Deploy 3 Hợp đồng lên Polygon Amoy Testnet
* **Hạn chót:** **14/11/2026**
* **Trạng thái:** `- [x] Đã hoàn thành (12/11/2026 - Deploy thành công 3 hợp đồng, vượt tiến độ 2 ngày)`
* **Mô tả công việc:**
  1. Chuẩn bị ví MetaMask có sẵn token POL mạng Amoy Testnet (nhận từ faucet https://faucet.polygon.technology/).
  2. Cấu hình biến môi trường trong file `.env`: `AMOY_RPC_URL`, `PRIVATE_KEY`, `POLYGONSCAN_API_KEY`.
  3. Chạy script triển khai:
     ```bash
     npx hardhat run scripts/deploy_contracts.js --network amoy
     ```
  4. Xác minh (verify) mã nguồn 3 hợp đồng trên PolygonScan Amoy.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Cả 3 hợp đồng sau được deploy thành công và hiển thị trạng thái Contract Verified trên PolygonScan:
    1. `MockUSDC.sol` (6 decimals): `0xe35681b0882d533458d22B344268642136ebD813`
    2. `CarbonCredit1155.sol` (Packed storage, Buffer pool): `0x851978601b47a61B8aF3bcC1707B689Fbc977697`
    3. `CarbonDoubleAuction.sol` (EIP-712 settlement): `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`

---

#### 🔲 Task Đ.3: Biên soạn Tài liệu Địa chỉ Hợp đồng `docs/DEPLOYED_ADDRESSES.md`
* **Hạn chót:** **14/11/2026**
* **Trạng thái:** `- [x] Đã hoàn thành (12/11/2026 - Tạo tệp docs/DEPLOYED_ADDRESSES.md bàn giao Thắng & Phi)`
* **Mô tả công việc:**
  Tạo tệp mới `docs/DEPLOYED_ADDRESSES.md` lưu trữ thông tin triển khai chính thức gồm:
  - Bảng địa chỉ 3 hợp đồng trên Polygon Amoy Testnet kèm đường link trực tiếp trên PolygonScan.
  - Hướng dẫn nhận POL testnet và lệnh mint thử MockUSDC faucet.
  - Phân quyền: Cấp quyền `SETTLEMENT_OPERATOR_ROLE` cho địa chỉ ví bot thanh toán của Phi.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tệp `docs/DEPLOYED_ADDRESSES.md` được commit lên Git và bàn giao trực tiếp cho **Thắng** (làm Frontend) và **Phi** (làm Submitter bot).

---

#### 🔲 Task Đ.4: Đo lường & Cập nhật Benchmark Gas Thực tế trên Polygon Amoy
* **Hạn chót:** **16/11/2026**
* **Trạng thái:** `- [x] Đã hoàn thành (13/11/2026 - Đo lường thành công 6 kịch bản on-chain có TxHash PolygonScan)`
* **Mô tả công việc:**
  1. Chạy các giao dịch thực tế trên Polygon Amoy để đo lường chính xác lượng gas tiêu thụ:
     * Chi phí gas khi mint 1 lô tín chỉ carbon (`CarbonCredit1155.sol`).
     * Chi phí gas khi thanh toán 1 cặp lệnh đơn lẻ (`settleMatchedTrade`).
     * Chi phí gas khi thanh toán theo lô: Batch 5 cặp, Batch 10 cặp, Batch 20 cặp (`batchSettleTrades`).
  2. Tính toán lượng gas trung bình cho mỗi cặp lệnh khi chạy Batch và tỷ lệ tiết kiệm gas (kỳ vọng $> 60\%$).
  3. Cập nhật bảng dữ liệu đo được vào **Mục 5 (Đánh giá Hiệu năng & Chi phí Gas)** trong file `docs/SMART_CONTRACT_SPEC.md` để thay thế hoàn toàn các con số lý thuyết phỏng đoán `112k/145k/920k` (giải quyết dứt điểm vấn đề **Đ12**).
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Bảng số liệu gas có đính kèm Transaction Hash trên Amoy làm minh chứng khoa học trong tài liệu Spec.

---

### NHẬT KÝ & GHI CHÚ CÁ NHÂN CỦA ĐỨC
*(Đức hãy ghi chú các khó khăn, lỗi gặp phải hoặc tiến độ hàng ngày vào phần này rồi commit lên Git)*

```markdown
- Ngày 12/11/2026:
  - Hoàn thành Task Đ.1: 14/14 test cases PASS 100%, gas batch settlement đạt 67,750 gas/cặp lệnh (< 85,000 gas chuẩn NFR-02).
  - Hoàn thành Task Đ.2: Cấu hình ví MetaMask thành công, nhận 1.0 POL faucet và deploy thành công cả 3 hợp đồng lên mạng Polygon Amoy Testnet (vượt tiến độ 2 ngày so với deadline 14/11).
  - Hoàn thành Task Đ.3: Biên soạn xong tệp docs/DEPLOYED_ADDRESSES.md chứa toàn bộ địa chỉ contract, cấu hình RPC và hướng dẫn tích hợp chi tiết bàn giao cho Thắng (Frontend) và Phi (Matching Bot).

- Ngày 13/11/2026:
  - Hoàn thành Task Đ.4: Chạy thành công script scripts/benchmark_amoy_gas.js đo lường 6 kịch bản giao dịch thực tế trên Polygon Amoy Testnet.
  - Kết quả đo lường thực nghiệm:
    + Mint lô tín chỉ (100k tCO2e): 309,894 gas (Tx: 0x700306...23c191)
    + Settle 1 cặp lệnh đơn lẻ: 286,145 gas (Tx: 0x96b795...fb82fe)
    + Batch 5 cặp lệnh: 763,384 gas (TB: 152,677 gas/lệnh, tiết kiệm 46.6% - Tx: 0x35df68...787187)
    + Batch 10 cặp lệnh: 1,420,946 gas (TB: 142,095 gas/lệnh, tiết kiệm 50.3% - Tx: 0xd49960...5c8b4)
    + Batch 20 cặp lệnh: 2,735,854 gas (TB: 136,793 gas/lệnh, tiết kiệm 52.2% - Tx: 0x5fc657...51e68)
    + Tiêu hủy tín chỉ (50 tCO2e): 66,365 gas (Tx: 0x007c64...4e128e)
  - Cập nhật bảng dữ liệu thực nghiệm có kèm 6 link PolygonScan vào Mục 5 file docs/SMART_CONTRACT_SPEC.md, giải quyết dứt điểm tồn tại Đ12.
```
