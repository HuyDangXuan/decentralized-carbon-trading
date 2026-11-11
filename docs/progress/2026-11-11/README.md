# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY 11/11/2026
## HỢP NHẤT TOÀN DIỆN 3 PHÂN HỆ VÀO MAIN & KIỂM THỬ TÍCH HỢP HỆ THỐNG GIAI ĐOẠN 2

- **Ngày thực hiện:** 11/11/2026 (Thứ Tư)
- **Người chủ trì cập nhật:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Thành viên tham gia phối hợp:** Nguyễn Hoàng Đức, Nguyễn Bảo Phi, Ngô Văn Thắng
- **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh
- **Trạng thái nhánh Git:** Toàn bộ 3 nhánh tính năng (`docs/smart-contract-spec`, `auction-algorithm-engineer`, `feature/thang-web3-frontend-integration`) đã được hợp nhất thành công 100% vào `main`. Cây commit sạch sẽ, không có xung đột, hệ thống kiểm thử toàn vẹn (47/47 tests Matching Engine pass, 10/10 tests Metadata pass).

---

## 1. MỤC TIÊU TRỌNG TÂM ĐÃ ĐẠT ĐƯỢC TRONG NGÀY
1. **Hợp nhất Tầng Hợp đồng Thông minh (Smart Contract Layer):** Chấp thuận và merge an toàn Pull Request #4 từ nhánh `docs/smart-contract-spec` của Nguyễn Hoàng Đức, đưa toàn bộ mã nguồn Solidity v2, 7 chốt chặn bảo mật, cơ chế Batch Settlement và bộ test Hardhat lên `main`.
2. **Hợp nhất Tầng Thuật toán & API (Matching Engine Layer):** Chấp thuận và merge an toàn Pull Request #5 từ nhánh `auction-algorithm-engineer` của Nguyễn Bảo Phi, tích hợp nhân khớp lệnh số nguyên `session_engine.py`, `auction_agent.py` bám sát ADR-001 và dịch vụ FastAPI Service.
3. **Giải quyết triệt để xung đột Git & Hợp nhất Tầng Giao diện (Frontend Web3 Layer):** Khắc phục lỗi `modify/delete conflict` thông qua kỹ thuật revert-revert an toàn (commit `4326258`), hợp nhất thành công mã nguồn DApp Next.js, Web3 EIP-712 hooks, client `matchingApi.ts` và Metadata Schema v2 của Ngô Văn Thắng (commit `fe9446f` qua merge commit `8eaf0b4`).
4. **Kiểm tra tính toàn vẹn hệ thống chéo (Cross-layer Verification):** Chạy kiểm thử tự động toàn diện trên nhánh `main`: 47 bài test Matching Engine đạt chuẩn 100% (0.096s); 10 bài test ràng buộc Metadata đạt chuẩn 100% (0.675s).
5. **Cập nhật hồ sơ tài liệu đối soát:** Cập nhật tệp Word `docs/BAO_CAO_PHAN_TICH_LICH_SU_GIT_VA_VAN_DE_MATCHING_ENGINE.docx` (60 đoạn văn, 5 bảng biểu lớn, ma trận RACI) phục vụ nghiệm thu học thuật.

---

## 2. CHI TIẾT TỪNG THAY ĐỔI KỸ THUẬT (DÙ LÀ NHỎ NHẤT)

### 2.1 Tầng Smart Contract (Nguyễn Hoàng Đức — PR #4 / commit `c2d89ec`)
- **`contracts/CarbonDoubleAuction.sol` (Viết mới hoàn toàn theo kiến trúc v2):**
  - Kế thừa OpenZeppelin v5: `EIP712`, `ECDSA`, `SafeERC20`, `ReentrancyGuard`, `AccessControl`.
  - Triển khai đầy đủ **7 Chốt chặn bảo mật** theo đúng khuyến nghị:
    1. Xác thực chữ ký EIP-712 của cả hai bên (`_verifyOrderSignature`).
    2. Kiểm tra thời hạn hiệu lực `deadline >= block.timestamp` (custom error `SignatureExpired`).
    3. Kiểm tra tính hợp thức cặp lệnh: cùng `tokenId`, đúng vai trò `bid=0 & ask=1`, khác địa chỉ ví `bid.trader != ask.trader` (chống Wash Trading), `matchAmount > 0`.
    4. Kiểm tra dải giá khớp: `ask.pricePerUnit <= clearingPrice <= bid.pricePerUnit`.
    5. **Kiểm tra `filledAmount` cho CẢ HAI BÊN** (vá lỗ hổng chí mạng Đ2 bỏ quên bên bán).
    6. Kiểm tra trạng thái hủy lệnh `!cancelledOrders`.
    7. Chống nộp trùng `tradeHash` tất định: `keccak256(abi.encodePacked(bid.orderId, ask.orderId, matchAmount, clearingPrice))` (không dùng `block.number` theo đúng lưu ý Đ15).
  - Tính năng **Batch Settlement** (`batchSettleTrades`): Gom nhiều cặp lệnh trong 1 giao dịch, sử dụng `try/catch` qua hàm external wrapper để DoS protection (1 lệnh lỗi không làm tắc nghẽn toàn batch).
- **`contracts/CarbonCredit1155.sol`:**
  - Packed Storage Layout 3 slot tối ưu hóa gas on-chain.
  - Quỹ dự phòng rủi ro Buffer Pool Vault (10% - 20%) tự động trích lập khi mint lô tín chỉ.
  - Cơ chế phân quyền RBAC: Admin, Verifier/VVB, ProjectOwner, AuctionContract.
  - Chức năng tiêu hủy vĩnh viễn (Permanent Retirement) phục vụ mục đích báo cáo ESG.
- **`contracts/MockUSDC.sol`:** Chuẩn hóa token thanh toán ERC-20 với 6 chữ số thập phân (`decimals = 6`), loại bỏ hoàn toàn sự mơ hồ "wei USDC".
- **Hạ tầng kiểm thử & ABI:**
  - Thiết lập Hardhat + TypeScript (`hardhat.config.js`, `tsconfig.json`).
  - Viết bộ test `test/CarbonTrading.test.js` (450 dòng test kiểm tra trọn vẹn 7 chốt chặn và đo gas).
  - Xuất trọn bộ ABI chuẩn sang thư mục `contracts/abis/` (`CarbonCredit1155.json`, `CarbonDoubleAuction.json`, `MockUSDC.json`, `index.ts`).

### 2.2 Tầng Matching Engine & Thuật toán Đấu giá (Nguyễn Bảo Phi — PR #5 / commit `867b606` & `c04fab1`)
- **Chuyển dịch nhân xử lý sang `session_engine.py`:**
  - Đưa engine số nguyên thuần túy ra làm lõi xử lý chính thức trong `system_agents/matching_engine/`.
  - Phân bổ theo quy tắc `age_prorata` kết hợp thuật toán phần dư lớn nhất Largest Remainder (Hamilton method), phần dư bằng nhau phá hòa bằng FIFO `seq` do engine cấp.
- **Tái cấu trúc `auction_agent.py`:**
  - Viết lại làm wrapper số nguyên trên `session_engine.py`, quản lý vòng đời lệnh bám sát ADR-001: `NEW`, `ROLLED_OVER`, `FILLED`, `EXPIRED`, `CANCELLED`.
  - Bộ đếm `rollover_count`: Lệnh GTC sống tối đa 3 phiên liên tiếp (`rollover_count >= 3` tự động chuyển sang `EXPIRED`).
  - Khắc phục triệt để lỗi của baseline cũ: Không trừ trực tiếp vào thuộc tính bộ nhớ (dùng `remaining_amount` nội bộ) và từ chối các mức giá float lẻ gây lỗi on-chain (thay bằng số nguyên tick giá và `half_even`).
- **Xây dựng Dịch vụ API hoàn chỉnh (`api_service.py`):**
  - Sử dụng framework **FastAPI**, tích hợp xác thực chữ ký EIP-712 gasless qua thư viện `eth-account`.
  - Đầy đủ các endpoint REST: `POST /api/v1/orders` (tiếp nhận lệnh), `DELETE /api/v1/orders/{orderId}` (hủy lệnh ngoài chuỗi), `GET /api/v1/orderbook/{tokenId}` (lấy sổ lệnh), `POST /api/v1/sessions/run` (kích hoạt khớp lệnh).
  - Kênh WebSocket feed `WS /ws/orderbook/{tokenId}` truyền phát độ sâu sổ lệnh theo thời gian thực.
- **Kiểm thử & Cơ sở học thuật:**
  - Thêm 30 bài test hồi quy trong `test_api_service.py` và `test_auction_agent.py`. Tổng cộng 47/47 tests chạy qua sạch sẽ.
  - Cập nhật tài liệu đối soát `docs/VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md` với các mục thảo luận mới: H7 (phân biệt giá marginal vs kda), H8 (cách đếm rollover 3 phiên), H9 (thời hạn bàn giao).

### 2.3 Tầng Frontend Web3 & Siêu dữ liệu (Ngô Văn Thắng — commit `b0ef2ce` & `fe9446f` / Merge commit `8eaf0b4`)
- **Chuẩn hóa `docs/METADATA_SCHEMA.json` v2:**
  - Bổ sung nhóm thuộc tính phân loại và gom nhóm thanh khoản (Credit Fungibility): `asset_class`, `standard_category`, `vintage_window`, `is_fungible_pool`, `fungibility_group_id`.
  - Khóa chặt đơn vị: `unit: "tCO2e"` (decimals=0), `price_unit: "USDC"` (decimals=6), buffer rate từ 10% đến 20%.
  - Bổ sung bộ từ điển dữ liệu hoàn chỉnh: `docs/DATA_DICTIONARY.md`, `docs/FRONTEND_INTEGRATION.md`, `docs/USER_FLOWS.md`, và các tệp mẫu `example_verra_vcs.json`, `example_gold_standard.json`.
  - Viết công cụ và kiểm thử tự động: `scripts/validate_metadata.py`, `tests/test_metadata.py` (10/10 tests pass).
- **Phát triển Tầng Giao diện Web3 DApp (`frontend/`):**
  - Hook ký EIP-712 gasless `useEIP712Order.ts` tương thích 100% với struct `Order` v2 và contract của Đức.
  - Module client `matchingApi.ts` giao tiếp REST và WebSocket với FastAPI Service của Phi (`POST /api/v1/orders`, `WS /ws/orderbook/{tokenId}`).
  - Xây dựng component giao diện `TradingFloor.tsx`, biểu đồ độ sâu sổ lệnh `DepthChart.tsx`.

### 2.4 Quản trị Kiến trúc & Git Workflow (Đặng Xuân Huy)
- **Xử lý kỹ thuật giải quyết xung đột Git:**
  - Thực hiện dry-run merge test phát hiện trước lỗi `modify/delete conflict` do commit revert cũ `49463c9`.
  - Áp dụng kỹ thuật revert-revert chuẩn của Git (commit `4326258`) để khôi phục cấu trúc thư mục `frontend/`, sau đó merge sạch sẽ commit `fe9446f` của Thắng.
- **Bảo toàn tài liệu học thuật:** Cập nhật tệp Word `docs/BAO_CAO_PHAN_TICH_LICH_SU_GIT_VA_VAN_DE_MATCHING_ENGINE.docx` tích hợp đầy đủ giải pháp cho 4 thành viên.

---

## 3. TÁC ĐỘNG TỚI TỪNG THÀNH VIÊN VÀ NHIỆM VỤ TIẾP THEO

### 3.1 Đối với Nguyễn Hoàng Đức (Smart Contract Engineer)
- **Tác động:** Mã nguồn Solidity v2 đã được tích hợp lên `main`.
- **Nhiệm vụ cần thực hiện ngay:**
  1. Chạy `npm install` để cài đặt dependencies trên root repository.
  2. Cấu hình private key ví thử nghiệm và RPC Polygon Amoy trong `hardhat.config.js`.
  3. Chạy lệnh deploy: `npx hardhat run scripts/deploy_contracts.js --network amoy`.
  4. Xuất địa chỉ contract đã deploy bàn giao cho Thắng (Frontend `.env`) và Phi (Bot Submitter).
- **Hạn chót:** 15/11/2026.

### 3.2 Đối với Nguyễn Bảo Phi (Auction Algorithm Engineer)
- **Tác động:** Nhân `session_engine.py` và FastAPI Service đã hoạt động ổn định trên `main`.
- **Nhiệm vụ cần thực hiện tiếp theo:**
  1. Mở rộng Thí nghiệm C đo lường Deadweight Loss với thị trường nhiều đơn vị và số lượng người tham gia lớn ($m > 16$).
  2. Tìm đọc toàn văn bài báo gốc Chatterjee & Samuelson (1983) và Rustichini et al. (1994) để hoàn thiện cơ sở lý thuyết.
  3. Soạn thảo tài liệu phân tích mối đe dọa bảo mật `docs/THREAT_MODELING.md`.
  4. Xây dựng Settlement Submitter bot tự động lấy `MatchResult[]` gọi hàm `batchSettleTrades` của Đức trên Polygon Amoy.
- **Hạn chót:** 20/11/2026.

### 3.3 Đối với Ngô Văn Thắng (Web3 Frontend Engineer)
- **Tác động:** Toàn bộ mã nguồn DApp và Metadata Schema đã được hợp nhất vào `main`.
- **Nhiệm vụ cần thực hiện tiếp theo:**
  1. Nhận địa chỉ Contract trên mạng Amoy từ Đức và cập nhật vào file `frontend/.env.local`.
  2. Hoàn thiện bộ thiết kế Wireframe / Mockup Figma cho 4 phân hệ Web3 DApp (Chủ dự án, VVB, Sàn giao dịch, ESG Retirement) bám sát hạn nộp 20/11.
  3. Khởi chạy `npm run dev` trong `frontend/` để kiểm thử giao diện đặt lệnh trực quan kết nối với server FastAPI của Phi.
- **Hạn chót:** 20/11/2026.

---

## 4. GHI CHÚ BẢN COMMIT VÀ TRẠNG THÁI GIT

- **Nhánh phát triển:** `main` (đồng bộ hoàn hảo với `origin/main`).
- **Các commit hợp nhất then chốt:**
  - `a7ac992`: `Merge pull request #4 from HuyDangXuan/docs/smart-contract-spec` (Tích hợp Smart Contract v2 của Đức).
  - `dd6f7e0`: `Merge pull request #5 from HuyDangXuan/auction-algorithm-engineer` (Tích hợp Matching Engine v2 & FastAPI của Phi).
  - `4326258`: `Revert "revert: undo frontend integration from PR #3"` (Khôi phục trạng thái frontend chuẩn bị cho merge).
  - `8eaf0b4`: `Merge remote-tracking branch 'origin/feature/thang-web3-frontend-integration'` (Tích hợp Frontend Web3 & Metadata v2 của Thắng).
- **Trạng thái nhánh `main`:** Cây commit sạch sẽ, không có uncommitted changes, 100% tests vượt qua.

---
*Bản ghi nhật ký này được lưu trữ vĩnh viễn trên nhánh main của repository và phục vụ công tác nghiệm thu NCKH.*
