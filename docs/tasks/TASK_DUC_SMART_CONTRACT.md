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
* **Trạng thái:** `- [ ] Chưa hoàn thành`
* **Mô tả công việc:**
  1. Cài đặt các thư viện phụ thuộc bằng lệnh: `npm install` tại thư mục gốc của repository.
  2. Biên dịch hợp đồng: `npx hardhat compile` (đảm bảo không còn warning nghiêm trọng).
  3. Chạy toàn bộ bài test: `npx hardhat test`.
* **Tiêu chí nghiệm thu (Acceptance Criteria):**
  * Tất cả các kịch bản kiểm thử trong `test/CarbonTrading.test.js` đạt trạng thái **PASS 100%** (xác thực trọn vẹn 7 chốt chặn bảo mật).

---

#### 🔲 Task Đ.2: Cấu hình & Deploy 3 Hợp đồng lên Polygon Amoy Testnet
* **Hạn chót:** **14/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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
    1. `MockUSDC.sol` (6 decimals).
    2. `CarbonCredit1155.sol` (Packed storage, Buffer pool).
    3. `CarbonDoubleAuction.sol` (EIP-712 settlement).

---

#### 🔲 Task Đ.3: Biên soạn Tài liệu Địa chỉ Hợp đồng `docs/DEPLOYED_ADDRESSES.md`
* **Hạn chót:** **14/11/2026**
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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
* **Trạng thái:** `- [ ] Chưa hoàn thành`
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
- Ngày ...:
- Tiến độ:
- Vấn đề phát sinh (nếu có):
```
