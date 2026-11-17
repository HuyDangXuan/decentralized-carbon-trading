# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY 17/11/2026
## TỔNG HỢP TIẾN ĐỘ KỸ THUẬT SPRINT TÍCH HỢP LIÊN THÔNG (12/11/2026 – 17/11/2026)
### HOÀN THÀNH TRIỂN KHAI POLYGON AMOY, SETTLEMENT BOT, BENCHMARK GAS VÀ BỘ MOCKUP 4 PHÂN HỆ

- **Thời gian ghi nhận:** 17/11/2026 (Thứ Ba)
- **Chu kỳ Sprint:** Giai đoạn 2 - Sprint Tích hợp Liên thông Hệ thống (12/11/2026 – 20/11/2026)
- **Người chủ trì cập nhật:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Thành viên phối hợp:** Nguyễn Hoàng Đức (*Smart Contract*), Nguyễn Bảo Phi (*Matching Engine & Simulation*), Ngô Văn Thắng (*Web3 Frontend & UI/UX*)
- **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh
- **Kênh thông tin:** Single Source of Truth (SSOT) trên nhánh `main`

---

## 1. MỤC TIÊU TRỌNG TÂM ĐÃ ĐẠT ĐƯỢC (TỪ 12/11 ĐẾN 17/11/2026)

Trong giai đoạn từ ngày 12/11/2026 đến ngày 17/11/2026, toàn bộ nhóm nghiên cứu đã bám sát kế hoạch phân công Sprint tích hợp liên thông, đạt được những bước tiến mang tính bước ngoặt kỹ thuật:

1. **Triển khai toàn bộ Smart Contract v2 lên mạng thử nghiệm Polygon Amoy Testnet (Đức):**
   - Triển khai thành công 3 hợp đồng cốt lõi: `MockUSDC` (`0xe356...`), `CarbonCredit1155` (`0x8519...`), `CarbonDoubleAuction` (`0x6Ee8...`).
   - Đấu nối RBAC on-chain: cấp quyền `AUCTION_CONTRACT_ROLE` cho hợp đồng đấu giá trên hợp đồng tín chỉ, thiết lập quỹ dự phòng Buffer Pool Vault 15%.
   - Triển khai bổ sung hợp đồng `EvccFaucet` (`0xcD5D...`) và nạp 1,000 EVCC lot #101 phục vụ kiểm thử DApp và Faucet cho Hội đồng nghiệm thu.
   - Vượt tiến độ 2 ngày so với deadline giao việc (hoàn thành 12/11 thay vì 14/11).

2. **Thực hiện Benchmark Gas On-Chain thực tế trên Polygon Amoy (Đức):**
   - Thực hiện đo đạc 6 kịch bản giao dịch thực tế trên Polygon Amoy (ChainId 80002) với các giao dịch có TxHash minh chứng rõ ràng trên PolygonScan.
   - Chứng minh cơ chế Batch Settlement tiết kiệm gas vượt trội: Batch 5 tiết kiệm **46.6%**, Batch 10 tiết kiệm **50.3%**, Batch 20 tiết kiệm **52.2%** (đạt 136,793 gas/lệnh so với 286,145 gas/lệnh đơn lẻ). Thay thế hoàn toàn các ước lượng lý thuyết trước đây, giải quyết dứt điểm vấn đề **Đ12**.

3. **Xây dựng Bot Settlement Submitter & Chạy thành công giao dịch Settlement thực tế trên Polygon Amoy (Phi):**
   - Phát triển hoàn thiện module `system_agents/matching_engine/settlement_submitter.py` tích hợp kiểm tra an toàn tiền gửi (pre-flight checks), bảo vệ DoS, khôi phục giao dịch `--recover-tx`, xử lý phân quyền `SETTLEMENT_OPERATOR_ROLE`.
   - Khắc phục lỗi tương thích chuỗi Proof-of-Authority (PoA) trên Polygon Amoy bằng cách tiêm middleware PoA vào Web3.py.
   - **Thực hiện thành công giao dịch `batchSettleTrades` đầu tiên trên Polygon Amoy Testnet** vào ngày 17/11/2026 (TxHash: `0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8`), đối soát số dư Buyer và Seller biến động chính xác 100%.

4. **Nghiên cứu Game Theory & Hoàn thiện Hồ sơ Đe dọa Bảo mật (Phi):**
   - Mở rộng Thí nghiệm C đo lường Deadweight Loss với số lượng người tham gia thị trường $m$ lên tới 64 tác nhân, xây dựng module kiểm chứng chéo cân bằng Nash xấp xỉ `equilibrium_crosscheck.py`.
   - Chuẩn hóa nền tảng học thuật theo hai bài báo gốc Chatterjee & Samuelson (1983) và Rustichini, Satterthwaite & Williams (1994), làm rõ sự khác biệt giữa quy tắc giá `marginal` và `kda` uniform.
   - Hoàn thiện tài liệu chuyên sâu `docs/THREAT_MODELING.md` phân tích 8 vector tấn công và các chốt chặn phòng thủ đã kiểm chứng.

5. **Hoàn thiện Web3 DApp kết nối Polygon Amoy & Thiết kế Mockup Figma 4 Phân hệ (Thắng):**
   - Cấu hình DApp Next.js kết nối đa RPC trên Amoy, tích hợp hiển thị số dư EVCC lot 101 và MockUSDC thời gian thực, xử lý mượt mà kết nối ví MetaMask theo chuẩn EIP-6963.
   - Xây dựng component `FaucetModal.tsx` trên giao diện người dùng, thực hiện thành công giao dịch nhận MockUSDC testnet on-chain (TxHash: `0x5c5f6de5c...`).
   - Hoàn thành bộ thiết kế đồ họa chất lượng cao (UI/UX Mockups) cho 4 phân hệ DApp theo đúng cam kết chuẩn IEEE 830: Project Developer Portal, Verifier/VVB Portal, Trading Floor Portal, ESG Retirement Portal; xuất 4 file PNG độ phân giải 2880 × 2000 px và 4 vector SVG tại `docs/wireframes/`.

---

## 2. NHẬT KÝ CHI TIẾT THEO TỪNG NGÀY (DAILY CHRONOLOGY: 12/11 – 17/11/2026)

### 📅 Ngày 12/11/2026 (Thứ Năm)
* **Smart Contract Layer (Đức):**
  - Chạy `npm install` và biên dịch bộ hợp đồng Solidity v2 trên môi trường node Hardhat.
  - Chạy toàn bộ 14 test cases trong `test/CarbonTrading.test.js` đạt trạng thái PASS 100%, ghi nhận chi phí batch settlement đạt 67,750 gas/cặp lệnh trên EVM cục bộ.
  - Cấu hình ví deployer, nhận token POL mạng Amoy và triển khai thành công 3 hợp đồng lên Polygon Amoy Testnet (Chain ID 80002):
    + `MockUSDC`: `0xe35681b0882d533458d22B344268642136ebD813`
    + `CarbonCredit1155`: `0x851978601b47a61B8aF3bcC1707B689Fbc977697`
    + `CarbonDoubleAuction`: `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`
  - Soạn thảo tài liệu bàn giao `docs/DEPLOYED_ADDRESSES.md` cấp địa chỉ chính thức và hướng dẫn tích hợp cho Phi và Thắng.
* **Frontend Web3 Layer (Thắng):**
  - Nhận địa chỉ từ Đức, cấu hình `frontend/.env.local` kết nối mạng Amoy.
  - Cập nhật cơ chế phát hiện MetaMask qua EIP-6963 chống xung đột extension, thêm giao diện hiển thị số dư `EVCC` lot #101 và `MockUSDC` (6 decimals).
  - Kiểm thử đọc trạng thái on-chain thành công tại block `52674033` và `52676023`.

### 📅 Ngày 13/11/2026 (Thứ Sáu)
* **Smart Contract Layer (Đức):**
  - Xây dựng và thực thi script `scripts/benchmark_amoy_gas.js` trên mạng Polygon Amoy thật.
  - Đo lường thành công 6 kịch bản on-chain và lưu kết quả vào `docs/BENCHMARK_RESULTS_AMOY.json`:
    + Mint lô tín chỉ (100k tCO2e): 309,894 gas (Tx: `0x700306...23c191`)
    + Settle đơn lẻ: 286,145 gas (Tx: `0x96b795...fb82fe`)
    + Batch 5 cặp lệnh: 763,384 gas (Tx: `0x35df68...787187`, tiết kiệm 46.6%)
    + Batch 10 cặp lệnh: 1,420,946 gas (Tx: `0xd49960...5c8b4`, tiết kiệm 50.3%)
    + Batch 20 cặp lệnh: 2,735,854 gas (Tx: `0x5fc657...51e68`, tiết kiệm 52.2%)
    + Tiêu hủy tín chỉ bù đắp: 66,365 gas (Tx: `0x007c64...4e128e`)
  - Cập nhật số liệu thực nghiệm vào Mục 5 file `docs/SMART_CONTRACT_SPEC.md`, giải quyết dứt điểm tồn tại Đ12.
* **Matching Engine Layer (Phi):**
  - Xây dựng module bot `system_agents/matching_engine/settlement_submitter.py` phục vụ việc nộp kết quả khớp lệnh lên smart contract.
  - Chạy thử nghiệm thành công trên Hardhat node cục bộ (batch 2 trades SETTLED, nộp lại bị skip, trade thiếu allowance bị phát hiện). Viết 22 tests mới nâng tổng số test suite lên 69 tests.
  - Xây dựng bộ đánh giá độc lập `simulation/equilibrium_crosscheck.py` (13 tests) phục vụ kiểm chứng thực nghiệm C.
  - Soạn thảo bản nháp tài liệu phân tích mối nguy cơ bảo mật `docs/THREAT_MODELING.md`.
  - Đọc hai bài báo gốc của Chatterjee & Samuelson (1983) và Rustichini et al. (1994), làm rõ điểm H4 và H7 trong tài liệu đặc tả `docs/MATCHING_ENGINE_SPEC.md`.

### 📅 Ngày 14/11/2026 (Thứ Bảy)
* **Quản trị Kiến trúc & Bảo mật Tích hợp (Huy, Đức, Phi):**
  - Thống nhất cơ chế bảo mật cho ví bot Submitter: nghiêm cấm lưu private key trên Git repository; mỗi thành viên tự khởi tạo ví Operator riêng bằng công cụ `scripts/new_operator_wallet.py`.
  - Quy chuẩn phân quyền on-chain: hợp đồng `CarbonDoubleAuction` chỉ cho phép địa chỉ sở hữu role `SETTLEMENT_OPERATOR_ROLE` được quyền gọi hàm `batchSettleTrades`. Đức chuẩn bị script `scripts/setup_operator_bot.js`.
  - Lập quy hoạch cấp phát tài sản cho các ví thử nghiệm: lô tín chỉ carbon thử nghiệm ID 101 ("Rừng Tây Bắc 2026", tiêu chuẩn Verra VCS, buffer 15%).

### 📅 Ngày 15/11/2026 (Chủ Nhật)
* **Đồng bộ Liên thông Hệ thống (Huy, Thắng, Phi):**
  - Đánh giá khả năng tương thích API FastAPI và Web3 DApp: kiểm tra luồng định dạng chữ ký EIP-712 giữa frontend Wagmi/Viem và backend `eth-account`.
  - Khắc phục các sai lệch định dạng dữ liệu bigint/number giữa JavaScript và Python API.
  - Kiểm thử hồi quy toàn bộ hệ thống: 14 test cases Frontend Web3, 10 test cases Metadata Schema, 69 test cases Matching Engine đều đạt trạng thái PASS 100%.

### 📅 Ngày 16/11/2026 (Thứ Hai)
* **Phát triển Tiện ích Kiểm thử & Faucet (Đức, Thắng):**
  - Thắng lập trình component `FaucetModal.tsx` trên giao diện Web3 DApp, tích hợp nút nhận 10,000 MockUSDC và nhận 100 EVCC #101.
  - Đức xây dựng hợp đồng `contracts/EvccFaucet.sol` chuyên biệt để cấp phát an toàn 100 tCO2e/lần cho các ví thử nghiệm mà không vi phạm nguyên tắc kiểm toán VVB (`mintProjectLot` chỉ tạo lô một lần duy nhất).
  - Phi chạy các vòng lặp tính toán sâu cho Thí nghiệm C mô phỏng Deadweight Loss với số lượng người tham gia $m=32, 64$ và kịch bản lệnh nhiều đơn vị.

### 📅 Ngày 17/11/2026 (Thứ Ba)
* **Bứt phá Tích hợp & Kiểm thử Thực tế On-chain (Toàn nhóm):**
  - **Đức:**
    + Triển khai hợp đồng `EvccFaucet` lên Amoy tại `0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED` (commit `df3e8d2`).
    + Nạp 1,000 EVCC lot #101 vào Faucet (Tx: `0xafd2b6c...e17d`).
    + Chạy script `scripts/fund_phi_test_traders.js` nạp vốn MockUSDC và EVCC cho Buyer `0xA440...` và Seller `0x485e...`.
    + Cấp quyền `SETTLEMENT_OPERATOR_ROLE` cho ví Operator của Phi: `0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE`.
  - **Phi:**
    + Phát hiện và khắc phục lỗi `extraData` của chuỗi PoA trên mạng Polygon Amoy bằng cách tích hợp PoA middleware vào `Web3.py` (commit `2a4c3bf`).
    + **Thực hiện thành công giao dịch `batchSettleTrades` thực tế trên Polygon Amoy Testnet:**
      * TxHash: [`0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8`](https://amoy.polygonscan.com/tx/0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8)
      * Chi phí gas: 275,741 gas.
      * Trạng thái giao dịch: Thành công (`status = 1`), bắt được sự kiện `TradeSettled`.
      * Biến động tài sản on-chain: Buyer nhận 5 EVCC, trả 50 USDC; Seller nhận 50 USDC, chuyển 5 EVCC.
    + Xuất bản tài liệu `docs/PHI_STATUS_2026-11-17.md` tổng kết toàn diện tiến độ P.1, P.2, P.3, P.4.
  - **Thắng:**
    + Hoàn thành bộ bản vẽ thiết kế giao diện Figma Desktop cho 4 phân hệ CarbonChain (Task T.4): xuất 4 tệp ảnh PNG 2880 × 2000 px và 4 tệp vector SVG tại `docs/wireframes/` kèm tài liệu mô tả chi tiết `docs/wireframes/README.md`.
    + Kết nối DApp với hợp đồng `EvccFaucet`, thực hiện nghiệm thu nút nhận 10,000 MockUSDC trên Amoy (TxHash: `0x5c5f6de5c...553bf2`).
  - **Huy (Lead Architect):**
    + Review và hợp nhất toàn bộ các Pull Request tính năng vào nhánh `main` (PR #7, #8, #9, #10, #11).
    + Soạn thảo Kế hoạch Demo Nội bộ Nhóm ngày 18/11/2026 (`docs/KE_HOACH_DEMO_NOI_BO_18_11.md`).
    + Soạn thảo Đề cương Slide Báo cáo Giai đoạn 2 chuẩn học thuật (`docs/SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md`).
    + Cập nhật hệ thống Kanban và bảng giao việc cá nhân trong `docs/tasks/`.

---

## 3. BẢNG TỔNG HỢP CÁC TỆP THAY ĐỔI TRONG GIAI ĐOẠN 12/11 – 17/11/2026

### 3.1 Tệp tạo mới (New Files)
| Tệp phát sinh | Phân hệ / Tác giả | Mục đích kỹ thuật |
| :--- | :---: | :--- |
| `contracts/EvccFaucet.sol` | Smart Contract / Đức | Hợp đồng Faucet phân phối tín chỉ EVCC #101 an toàn cho người dùng thử nghiệm |
| `scripts/deploy_evcc_faucet.js` | Smart Contract / Đức | Script triển khai `EvccFaucet` lên Polygon Amoy |
| `scripts/mint_sample_lot.js` | Smart Contract / Đức | Script đúc mẫu lô tín chỉ 101 cho dự án Rừng Tây Bắc |
| `scripts/fund_phi_test_traders.js` | Smart Contract / Đức | Script cấp vốn MockUSDC và EVCC cho các ví kiểm thử của Phi |
| `scripts/setup_operator_bot.js` | Smart Contract / Đức | Script gán quyền `SETTLEMENT_OPERATOR_ROLE` cho ví Operator |
| `scripts/check_amoy_balance.js` | Smart Contract / Đức | Script truy vấn nhanh số dư POL, MockUSDC, EVCC trên mạng Amoy |
| `scripts/benchmark_amoy_gas.js` | Smart Contract / Đức | Script tự động hóa đo lường 6 kịch bản tiêu thụ gas trên Amoy |
| `scripts/new_operator_wallet.py` | Architecture / Phi, Huy | Công cụ sinh ví Operator an toàn không để lộ khóa riêng tư |
| `system_agents/matching_engine/settlement_submitter.py` | Matching Engine / Phi | Lõi bot Submitter nộp kết quả khớp lệnh lên on-chain với try-catch và pre-flight check |
| `system_agents/matching_engine/simulation/equilibrium_crosscheck.py` | Simulation / Phi | Bộ kiểm tra chéo cân bằng Nash độc lập đánh giá độ bền thuật toán |
| `system_agents/matching_engine/simulation/run_experiment_c_multiunit.py` | Simulation / Phi | Script mô phỏng Deadweight Loss đa đơn vị mở rộng tới $m=64$ |
| `docs/BENCHMARK_RESULTS_AMOY.json` | Smart Contract / Đức | Dữ liệu đo đạc gas thực nghiệm 6 kịch bản trên Polygon Amoy |
| `docs/DEPLOYED_ADDRESSES.md` | Smart Contract / Đức | Bảng lưu trữ địa chỉ hợp đồng và hướng dẫn đấu nối phân hệ |
| `docs/SETTLEMENT_SUBMITTER_GUIDE.md` | Matching Engine / Phi | Cẩm nang hướng dẫn vận hành, xử lý lỗi và cấu hình bot Submitter |
| `docs/THREAT_MODELING.md` | Security / Phi | Báo cáo phân tích mối đe dọa bảo mật hệ thống kiến trúc lai |
| `docs/PHI_STATUS_2026-11-17.md` | Progress / Phi | Báo cáo tổng kết trạng thái nhiệm vụ P.1, P.2, P.3, P.4 ngày 17/11 |
| `docs/wireframes/01-project-developer.png` & `.svg` | Frontend / Thắng | Mockup màn hình Cổng Chủ dự án (Project Developer Portal) |
| `docs/wireframes/02-verifier-vvb.png` & `.svg` | Frontend / Thắng | Mockup màn hình Cổng Kiểm toán viên (Verifier/VVB Portal) |
| `docs/wireframes/03-trading-floor.png` & `.svg` | Frontend / Thắng | Mockup màn hình Sàn giao dịch & Sổ lệnh (Trading Floor Portal) |
| `docs/wireframes/04-esg-retirement.png` & `.svg` | Frontend / Thắng | Mockup màn hình Tiêu hủy & Chứng nhận ESG (ESG Retirement Portal) |
| `docs/wireframes/README.md` | Frontend / Thắng | Tài liệu hướng dẫn đối soát và nhập bộ thiết kế vào Figma |
| `frontend/src/components/FaucetModal.tsx` | Frontend / Thắng | Component giao diện Modal nhận MockUSDC và EVCC tiện ích |
| `docs/KE_HOACH_DEMO_NOI_BO_18_11.md` | Coordination / Huy | Bản kế hoạch chi tiết buổi Demo liên thông nội bộ ngày 18/11/2026 |
| `docs/SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md` | Coordination / Huy | Đề cương 20 slide báo cáo tiến độ Giai đoạn 2 chuẩn học thuật |

### 3.2 Tệp chỉnh sửa quan trọng (Key Modified Files)
- `contracts/CarbonDoubleAuction.sol`: Bổ sung kiểm tra địa chỉ ví, tối ưu hóa cấu trúc dữ liệu thanh toán theo lô.
- `docs/SMART_CONTRACT_SPEC.md`: Cập nhật toàn bộ bảng số liệu gas thực nghiệm Mục 5 thay thế số liệu giả định cũ.
- `docs/MATCHING_ENGINE_SPEC.md`: Cập nhật Mục 7, 9, 12 chuẩn hóa cơ sở toán học theo [CS83] và [RSW94], giải quyết dứt điểm H4 và H7.
- `frontend/src/web3/config.ts` & `frontend/src/web3/contracts.ts`: Cập nhật địa chỉ Amoy và ABI EvccFaucet.
- `docs/tasks/TASK_DUC_SMART_CONTRACT.md`: Tích hoàn thành 100% các task Đ.1, Đ.2, Đ.3, Đ.4.
- `docs/tasks/TASK_THANG_FRONTEND_WEB3.md`: Cập nhật tiến độ hoàn thành T.1, chuẩn bị nghiệm thu T.2 và T.4.
- `docs/tasks/TASK_PHI_AUCTION_ENGINE.md`: Cập nhật tiến độ P.1, P.3, P.4 và ghi nhận kết quả thực nghiệm P.2.

---

## 4. TỔNG HỢP ĐỊA CHỈ & THÔNG SỐ TRIỂN KHAI CHÍNH THỨC TRÊN POLYGON AMOY

```yaml
Blockchain Network: Polygon Amoy Testnet
Chain ID: 80002 (Hex: 0x13882)
Currency: POL (Phí gas giao dịch)
RPC Gateway: https://polygon-amoy.gateway.tenderly.co / https://poly-amoy-testnet.api.pocket.network
Block Explorer: https://amoy.polygonscan.com

Smart Contracts:
  MockUSDC: "0xe35681b0882d533458d22B344268642136ebD813"
  CarbonCredit1155: "0x851978601b47a61B8aF3bcC1707B689Fbc977697"
  CarbonDoubleAuction: "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f"
  EvccFaucet: "0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED"

System Roles:
  Admin / Deployer: "0x6Ea660D087C90c8ff915E2646a5A282a53Cd8694"
  Settlement Operator (Bot): "0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE"

Test Wallets (Pre-funded):
  Buyer Ví: "0xA4405ECe027f9C0585764b97b3E96dA947b52E7d" (Số dư ban đầu: 50,000 MockUSDC)
  Seller Ví: "0x485ed29E56A57c59ca817554950C4C19EB00aF0c" (Số dư ban đầu: 50 EVCC #101)
```

---

## 5. TÁC ĐỘNG TỚI TỪNG THÀNH VIÊN VÀ NHIỆM VỤ TIẾP THEO

### 5.1 Nguyễn Hoàng Đức (Smart Contract Engineer)
- **Tác động:** Đã xuất sắc hoàn thành vượt tiến độ toàn bộ 4 nhiệm vụ được giao (Đ.1 - Đ.4).
- **Nhiệm vụ chuẩn bị phiên Demo 18/11:**
  1. Đảm bảo ví Deployer và ví Operator có đủ số dư POL để thực hiện các giao dịch live demo.
  2. Mở sẵn tab PolygonScan Amoy theo dõi hợp đồng `0x6Ee8...c46f` và `0x8519...7697`.
  3. Chuẩn bị sẵn sàng giải thích cơ chế 7 chốt chặn bảo mật và phân tích trực tiếp transaction hash khi bot submit lệnh thành công.

### 5.2 Nguyễn Bảo Phi (Auction Algorithm Engineer)
- **Tác động:** Đã đưa bot Submitter chạy thành công trên Amoy, hệ thống test engine đạt 101 tests pass.
- **Nhiệm vụ chuẩn bị phiên Demo 18/11:**
  1. Khởi động trước server FastAPI `api_service.py` trên cổng 8000, nạp biến môi trường contract Amoy.
  2. Đảm bảo bot `settlement_submitter.py` sẵn sàng nộp lệnh khi có kết quả khớp từ engine.
  3. Mở sẵn màn hình terminal hiển thị log khớp lệnh, log tính toán giá clearing $P^*$ và log nộp transaction on-chain.

### 5.3 Ngô Văn Thắng (Web3 Frontend Engineer)
- **Tác động:** Đã có bộ mockup wireframes 4 phân hệ chất lượng cao và giao diện DApp kết nối Amoy.
- **Nhiệm vụ chuẩn bị phiên Demo 18/11:**
  1. Nhập bộ vector SVG vào workspace Figma của nhóm, chia sẻ quyền xem (View access) cho Huy và nhóm.
  2. Mở giao diện DApp Next.js, kết nối ví MetaMask chuyển mạng Polygon Amoy để thực hiện thao tác trực tiếp:
     - Thao tác bấm nút nhận 10,000 MockUSDC và 100 EVCC từ Faucet Modal.
     - Thao tác nhập lệnh mua/bán trên giao diện Trading Floor, ký EIP-712 gasless và quan sát biểu đồ độ sâu cập nhật tức thì.

### 5.4 Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Nhiệm vụ trọng tâm ngày 18/11:**
  1. Chủ trì buổi Demo Liên thông Nội bộ nhóm lúc 08:30 sáng 18/11/2026 trên Google Meet.
  2. Điều phối các thành viên diễn tập theo đúng kịch bản 5 giai đoạn đã đề ra trong `docs/KE_HOACH_DEMO_NOI_BO_18_11.md`.
  3. Ghi chép biên bản nghiệm thu kỹ thuật nội bộ, tổng kết các điểm hoàn thiện cuối cùng trước khi báo cáo chính thức với TS. Nguyễn Thị Hồng Khánh.
  4. Chuyển hóa Đề cương Slide (`docs/SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md`) thành bộ Slide trình chiếu PowerPoint hoàn chỉnh `docs/SLIDE_BAO_CAO_GIAI_DOAN_2.pptx`.

---

## 6. GHI CHÚ BẢN COMMIT VÀ TRẠNG THÁI HỆ THỐNG TRÊN GIT

- **Nhánh hiện tại:** `main` (đồng bộ hoàn hảo với `origin/main`).
- **Commit HEAD:** `3bde0e3` (Merge PR #11 - hoàn tất hợp nhất toàn bộ mã nguồn của Thắng, Đức và Phi).
- **Trạng thái kiểm thử:**
  + Smart Contract: 14/14 tests Hardhat PASS.
  + Matching Engine & Submitter Bot: 101/101 tests Python PASS.
  + Metadata & Schema: 10/10 tests JSON Schema PASS.
  + Web3 Frontend: 14/14 tests Vitest & Build Production Next.js PASS.
- **Đánh giá chung:** Hệ thống đạt độ hoàn thiện cao, sẵn sàng 100% cho buổi Demo Liên thông Nội bộ 18/11/2026 và Báo cáo Nghiệm thu Giai đoạn 2.
