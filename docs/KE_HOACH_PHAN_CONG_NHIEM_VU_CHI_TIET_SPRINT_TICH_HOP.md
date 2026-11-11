# KẾ HOẠCH PHÂN CÔNG NHIỆM VỤ VÀ TRIỂN KHAI SPRINT TÍCH HỢP HỆ THỐNG
## GIAI ĐOẠN 2: TỪ THIẾT KẾ ĐỘC LẬP SANG VẬN HÀNH LIÊN THÔNG END-TO-END
*(Thời gian thực hiện: Từ ngày 12/11/2026 đến ngày 20/11/2026)*

---

### THÔNG TIN ĐỀ TÀI & NHÓM NGHIÊN CỨU
* **Cơ quan chủ quản:** Trường Đại học Điện Lực (EPU) – Khoa Điện toán và Công nghệ số Năng lượng
* **Tên đề tài:** Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain
* **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh (Bộ môn Hệ thống thông tin)
* **Chủ nhiệm đề tài:** Đặng Xuân Huy – Lớp D18CNPM1 (MSV: 23810310007)
* **Nhóm sinh viên nghiên cứu:**
  1. Nguyễn Hoàng Đức (MSV: 23810310060) – Smart Contract Engineer
  2. Nguyễn Bảo Phi (MSV: 23810310017) – Auction Algorithm Engineer
  3. Ngô Văn Thắng (MSV: 23810310401) – Fullstack Web3 & Frontend Engineer
* **Mã nguồn dự án (GitHub):** https://github.com/HuyDangXuan/decentralized-carbon-trading.git (Nhánh chính: `main`)

---

## I. BỐI CẢNH & MỤC TIÊU CỐT LÕI CỦA SPRINT

### 1. Bối cảnh
Tính đến ngày 11/11/2026, nhóm nghiên cứu đã hoàn thành một khối lượng công việc rất lớn và **vượt tiến độ kế hoạch 1 – 2 tuần**:
* Đã ban hành Quyết định Kiến trúc **ADR-001** và Tài liệu Đặc tả Yêu cầu Phần mềm chuẩn quốc tế **IEEE Std 830-1998** (`docs/SRS_DOCUMENT.md`).
* Đã hợp nhất hoàn chỉnh mã nguồn của cả 3 phân hệ độc lập vào nhánh `main` (commit `8eaf0b4`):
  * **Tầng Smart Contract:** Hợp đồng `CarbonDoubleAuction.sol` v2 với 7 chốt chặn bảo mật và batch settlement, `CarbonCredit1155.sol`, `MockUSDC.sol`.
  * **Tầng Matching Engine:** Nhân `session_engine.py` số nguyên, thuật toán phá hòa Hamilton `age_prorata`, giá $k$-DA uniform, và server FastAPI `api_service.py`.
  * **Tầng DApp Frontend:** Metadata Schema v2 (`docs/METADATA_SCHEMA.json`), hook ký gasless EIP-712 và client kết nối API REST/WebSocket.

### 2. Mục tiêu Sprint (12/11 – 20/11/2026)
Chuyển đổi từ trạng thái **"mã nguồn tồn tại độc lập trên cùng một nhánh"** sang trạng thái **"vận hành liên thông khép kín (End-to-End)"**:
1. Triển khai (Deploy) hợp đồng lên mạng thử nghiệm **Polygon Amoy Testnet** và đo gas thực tế.
2. Xây dựng **Bot Settlement Submitter** để tự động đưa kết quả khớp lệnh từ Matching Engine nộp lên Blockchain.
3. Kết nối giao diện DApp Web3 với Smart Contract trên Polygon Amoy và API Service của Matching Engine.
4. Chạy kịch bản kiểm thử toàn trình End-to-End thành công và hoàn thiện hồ sơ slide báo cáo giữa kỳ với GVHD.

---

## II. SƠ ĐỒ DÒNG CHẢY PHỐI HỢP CÔNG VIỆC LIÊN PHÂN HỆ

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIẾN TRÌNH TÍCH HỢP SPRINT                              │
└────────────────────────────────────────────────────────────────────────────────────────┘

  [NGUYỄN HOÀNG ĐỨC]                                          [NGUYỄN BẢO PHI]
  (Smart Contract)                                            (Matching Engine)
         │                                                           │
         ├────── 14/11: Deploy Polygon Amoy                          │
         │       (Địa chỉ Contract & ABI chuẩn)                      │
         │                                                           │
         ├─── Địa chỉ Contract ───┐                                  │
         │                        ▼                                  │
         │               [NGÔ VĂN THẮNG]                             │
         │               (Web3 Frontend)                             │
         │                      │                                    │
         │                      ├──── 18/11: Ký EIP-712 Form         │
         │                      │     Gửi Order vào FastAPI ────────►│
         │                      │                                    ├──── 15/11: Viết Submitter Bot
         │                      │                                    │     Lấy MatchResult[]
         │                      ▼                                    ▼
         │             [TEST GIAO DIỆN UI]               [CALL SETTLE ON-CHAIN]
         │             (Figma 4 Portal)                  (batchSettleTrades)
         │                      │                                    │
         └──────────────────────┼────────────────────────────────────┘
                                ▼
                        [ĐẶNG XUÂN HUY]
                      (Lead Architect)
                                │
                                ├──── 17/11: Viết script Test E2E khép kín
                                ├──── 18/11: Họp Demo Liên thông Nội bộ nhóm
                                └──── 20/11: Slide Báo cáo & Hồ sơ Nghiệm thu GVHD
```

---

## III. BẢN PHÂN CÔNG NHIỆM VỤ CHI TIẾT THEO TỪNG THÀNH VIÊN

### 1. NGUYỄN HOÀNG ĐỨC – SMART CONTRACT ENGINEER
* **Vai trò:** Chịu trách nhiệm toàn diện về Tầng Thanh Quyết toán On-chain (Settlement Layer), độ an toàn của hợp đồng và tối ưu hóa chi phí Gas.

| Mã việc | Nhiệm vụ kỹ thuật chi tiết | Tệp phụ trách / Lệnh thực thi | Hạn chót | Tiêu chí nghiệm thu (Acceptance Criteria) |
| :---: | :--- | :--- | :---: | :--- |
| **Đ.1** | **Cài đặt môi trường & Chạy Local Test** | `hardhat.config.js`<br/>`package.json` | **12/11/2026** | Chạy `npm install` và `npx hardhat test` đạt **100% test pass** trên môi trường local (không lỗi compile, không thiếu thư viện OpenZeppelin v5). |
| **Đ.2** | **Cấu hình & Deploy lên Polygon Amoy** | `scripts/deploy_contracts.js`<br/>`.env` | **14/11/2026** | Deploy thành công 3 hợp đồng lên testnet Amoy:<br/>1. `MockUSDC.sol`<br/>2. `CarbonCredit1155.sol`<br/>3. `CarbonDoubleAuction.sol`<br/>Mã nguồn được verify thành công trên PolygonScan Amoy. |
| **Đ.3** | **Biên soạn Bảng Địa chỉ Hợp đồng** | `docs/DEPLOYED_ADDRESSES.md` *(Tạo mới)* | **14/11/2026** | Tạo tài liệu ghi rõ:<br/>- Địa chỉ 3 contract và link PolygonScan tương ứng.<br/>- Hướng dẫn nhận POL testnet và MockUSDC faucet.<br/>- Cấp quyền `SETTLEMENT_OPERATOR_ROLE` cho địa chỉ ví bot submitter. |
| **Đ.4** | **Đo lường & Cập nhật Benchmark Gas thật** | `test/CarbonTrading.test.js`<br/>`docs/SMART_CONTRACT_SPEC.md` | **16/11/2026** | Đo số liệu gas thực tế trên Amoy cho:<br/>- Mint 1 lô tín chỉ carbon.<br/>- Khớp 1 cặp lệnh Atomic Swap T+0.<br/>- Khớp theo lô (Batch) 5, 10, 20 cặp lệnh.<br/>Thay thế hoàn toàn số liệu ước tính `112k/145k/920k` tại Mục 5 của Spec. |

* **Sản phẩm bàn giao:** File `docs/DEPLOYED_ADDRESSES.md` và bảng thông số Gas thực tế.
* **Người nhận bàn giao:** Thắng (lấy địa chỉ cho Frontend) và Phi (lấy địa chỉ cho bot thanh toán).

---

### 2. NGUYỄN BẢO PHI – AUCTION ALGORITHM ENGINEER
* **Vai trò:** Chịu trách nhiệm về Bộ khớp lệnh Đấu giá kép (Matching Engine), tính đúng đắn toán học, API Service và Bot nộp giao dịch on-chain.

| Mã việc | Nhiệm vụ kỹ thuật chi tiết | Tệp phụ trách / Lệnh thực thi | Hạn chót | Tiêu chí nghiệm thu (Acceptance Criteria) |
| :---: | :--- | :--- | :---: | :--- |
| **P.1** | **Xây dựng Bot Settlement Submitter** | `system_agents/matching_engine/settlement_submitter.py` *(Tạo mới)* | **15/11/2026** | Xây dựng module Python tự động:<br/>- Lấy danh sách `MatchResult[]` từ phiên đấu giá của `api_service.py`.<br/>- Đóng gói đúng cấu trúc struct `MatchedTrade[]` on-chain.<br/>- Sử dụng `web3.py` hoặc `eth-account` ký giao dịch từ ví có quyền Operator để gọi hàm `batchSettleTrades`. |
| **P.2** | **Mở rộng Thí nghiệm C (Deadweight Loss)** | `system_agents/matching_engine/simulation/run_experiment_c.py` | **17/11/2026** | Chạy mô phỏng tổn thất hiệu quả kinh tế với số lượng người tham gia lớn hơn ($m \in \{16, 32, 64\}$) và kịch bản nhiều đơn vị (multi-unit); xuất biểu đồ log-log chứng minh độ dốc $O(1/m^2)$. |
| **P.3** | **Biên soạn Tài liệu Phân tích Đe dọa Bảo mật** | `docs/THREAT_MODELING.md` *(Tạo mới)* | **18/11/2026** | Phân tích 4 mối nguy bảo mật:<br/>1. Operator Front-running lệnh ngoài chuỗi.<br/>2. Miner/Searcher MEV chèn thứ tự giao dịch.<br/>3. Rò rỉ private key của ví Settlement Submitter.<br/>4. Spam lệnh GTC rác nhằm tích tuổi lệnh/vét phần dư.<br/>Đưa ra các cơ chế phòng vệ tương ứng. |
| **P.4** | **Chuẩn hóa Học thuật từ Bài báo gốc** | `docs/MATCHING_ENGINE_SPEC.md` | **20/11/2026** | Đọc toàn văn Chatterjee & Samuelson (1983) và Rustichini et al. (1994) nhằm chốt chuẩn hóa thuật ngữ $k$-DA vs Marginal Clearing Price (điểm H7) và giải quyết nghi vấn số liệu 1/6 (điểm H4). |

* **Sản phẩm bàn giao:** Module `settlement_submitter.py` chạy ổn định, tài liệu `docs/THREAT_MODELING.md` và kết quả Thí nghiệm C mở rộng.
* **Người nhận bàn giao:** Huy (phối hợp chạy kiểm thử tích hợp E2E).

---

### 3. NGÔ VĂN THẮNG – FULLSTACK WEB3 & FRONTEND ENGINEER
* **Vai trò:** Chịu trách nhiệm về Giao diện Người dùng (DApp UI/UX), Thiết kế Wireframe/Figma, Tích hợp Ví Web3 và Chuẩn hóa Siêu dữ liệu IPFS.

| Mã việc | Nhiệm vụ kỹ thuật chi tiết | Tệp phụ trách / Lệnh thực thi | Hạn chót | Tiêu chí nghiệm thu (Acceptance Criteria) |
| :---: | :--- | :--- | :---: | :--- |
| **T.1** | **Cấu hình DApp với Contract Polygon Amoy** | `frontend/.env.local`<br/>`frontend/src/web3/config.ts` | **15/11/2026** | Nhận địa chỉ Contract từ Đức $\to$ Cấu hình vào file `.env.local`. Người dùng kết nối ví MetaMask, chuyển mạng sang Polygon Amoy thành công, đọc được số dư MockUSDC và token EVCC. |
| **T.2** | **Thêm Nút Faucet & Mint Thử nghiệm trên UI** | `frontend/src/components/FaucetModal.tsx` *(Tạo mới)* | **16/11/2026** | Xây dựng modal/nút bấm trên giao diện cho phép ví người dùng tự Faucet 10,000 MockUSDC và đúc thử 100 tCO2e để hội đồng nghiệm thu/GVHD dễ dàng test trực tiếp trên trình duyệt mà không cần CLI. |
| **T.3** | **Kiểm thử Luồng Đặt lệnh & Vẽ Sổ lệnh** | `frontend/src/components/TradingFloor.tsx`<br/>`frontend/src/services/matchingApi.ts` | **18/11/2026** | Kiểm tra luồng tương tác thực tế:<br/>Nhập form đặt lệnh $\to$ Ký thông điệp EIP-712 gasless trên MetaMask $\to$ Gửi HTTP POST tới API của Phi $\to$ Nhận thông báo WebSocket cập nhật biểu đồ độ sâu (Depth Chart) trong $< 1$ giây. |
| **T.4** | **Hoàn thành Bộ Wireframe Figma 4 Phân hệ** | Thư mục `docs/wireframes/`<br/>*(Kèm đường link Figma)* | **20/11/2026** | Hoàn thành thiết kế bản vẽ chi tiết cho 4 phân hệ DApp:<br/>1. Project Developer Portal (Nộp PDD & MRV).<br/>2. Verifier/VVB Portal (Kiểm toán độc lập & ký duyệt).<br/>3. Trading Floor (Sổ lệnh, biểu đồ giá khớp, đặt lệnh).<br/>4. ESG Retirement Portal (Kích hoạt hủy & cấp chứng chỉ). |

* **Sản phẩm bàn giao:** Ứng dụng Next.js chạy mượt mà (`npm run dev`) và link bản vẽ Figma 4 phân hệ hoàn chỉnh.
* **Người nhận bàn giao:** Huy (kiểm thử giao diện và đưa hình ảnh vào Slide/Báo cáo).

---

### 4. ĐẶNG XUÂN HUY – LEAD ARCHITECT & PROJECT MANAGER
* **Vai trò:** Điều phối chung toàn dự án, thiết kế kiến trúc hệ thống, kiểm thử liên thông End-to-End, tổng hợp hồ sơ học thuật và báo cáo với GVHD.

| Mã việc | Nhiệm vụ kỹ thuật chi tiết | Tệp phụ trách / Lệnh thực thi | Hạn chót | Tiêu chí nghiệm thu (Acceptance Criteria) |
| :---: | :--- | :--- | :---: | :--- |
| **H.1** | **Xây dựng Script Kiểm thử End-to-End** | `scripts/test_e2e_integration.py` *(Tạo mới)* | **17/11/2026** | Viết script tự động hóa kịch bản hoàn chỉnh 5 bước:<br/>1. Khởi tạo 2 ví thử nghiệm Buyer và Seller.<br/>2. Sinh và ký 2 lệnh đối ứng chuẩn EIP-712.<br/>3. Gửi lệnh vào FastAPI Service.<br/>4. Kích hoạt phiên khớp lệnh $k$-DA.<br/>5. Bot submitter nộp on-chain và kiểm tra số dư thay đổi chuẩn xác. |
| **H.2** | **Tổ chức Phiên Demo Tích hợp Nội bộ** | Họp trực tuyến Google Meet | **18/11/2026** | Triệu tập toàn bộ 4 thành viên, chạy thử luồng demo hoàn chỉnh từ Web3 Frontend $\to$ FastAPI Matching Engine $\to$ Smart Contract Amoy. Ghi nhận lỗi phát sinh và xử lý ngay. |
| **H.3** | **Biên soạn Slide Báo cáo Tiến độ Giai đoạn 2** | `docs/SLIDE_BAO_CAO_GIAI_DOAN_2.pptx` | **20/11/2026** | Soạn slide báo cáo (15 – 20 trang) bám sát các sản phẩm của nhóm: Kiến trúc hệ thống, quyết định ADR-001, các cải tiến toán học của $k$-DA, kết quả đo gas thực tế và ảnh chụp giao diện DApp. |
| **H.4** | **Duy trì Nhật ký Tiến độ & Báo cáo GVHD** | `docs/progress/`<br/>`scripts/log_daily_progress.py` | **Hàng ngày** | Chạy công cụ log tiến độ hàng ngày, chuẩn bị hồ sơ minh chứng đầy đủ phục vụ buổi báo cáo tiến độ định kỳ với TS. Nguyễn Thị Hồng Khánh. |

* **Sản phẩm bàn giao:** Script kiểm thử E2E, slide báo cáo Giai đoạn 2 và biên bản nghiệm thu nội bộ.
* **Người nhận bàn giao:** Giảng viên hướng dẫn (TS. Nguyễn Thị Hồng Khánh) và Hội đồng khoa học.

---

## IV. BẢNG MỐC THỜI GIAN THEO NGÀY (TIMELINE & MILESTONES)

```
┌──────────────┬────────────────────────────────────────────────────────────────────────┐
│ Ngày         │ Cột mốc hoàn thành trọng tâm                                           │
├──────────────┼────────────────────────────────────────────────────────────────────────┤
│ 12/11/2026   │ Đức chạy npm install và hoàn thành 100% test pass Hardhat local.       │
│ 14/11/2026   │ Đức deploy thành công 3 contract lên Amoy, xuất DEPLOYED_ADDRESSES.md. │
│ 15/11/2026   │ Phi hoàn thành Bot Settlement Submitter; Thắng cấu hình xong .env DApp.│
│ 16/11/2026   │ Đức đo gas thực tế trên Amoy; Thắng làm xong nút Faucet/Mint trên UI.  │
│ 17/11/2026   │ Phi mở rộng Thí nghiệm C (m>16); Huy viết script test E2E.             │
│ 18/11/2026   │ Nhóm tổ chức họp Demo liên thông nội bộ; Thắng test xong form đặt lệnh.│
│ 20/11/2026   │ BÀN GIAO TOÀN DIỆN: Thắng nộp Figma, Phi nộp Threat Modeling,          │
│              │ Huy nộp Slide Báo cáo & Báo cáo GĐ2 gửi GVHD.                          │
└──────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## V. QUY ĐỊNH KỶ LUẬT KỸ THUẬT VÀ QUY TRÌNH GIT

Để tránh tình trạng xung đột và vỡ mã nguồn trên nhánh `main`:
1. **Nguyên tắc làm việc trên nhánh phụ:**
   * Mỗi thành viên khi làm tính năng mới phải tạo nhánh riêng bám theo mã việc, ví dụ:
     * Đức: `feat/duc-deploy-amoy-gas-benchmark`
     * Phi: `feat/phi-settlement-submitter-bot`
     * Thắng: `feat/thang-faucet-ui-figma-integration`
     * Huy: `feat/huy-e2e-testing-slides`
2. **Kiểm thử trước khi tạo Pull Request:**
   * Phải chạy bài test cục bộ đảm bảo không bị lỗi hồi quy:
     * Smart contract: `npx hardhat test`
     * Matching engine: `python -m unittest discover system_agents/matching_engine/ -p "test_*.py"`
     * Metadata: `python -m unittest tests/test_metadata.py`
3. **Quy chuẩn thông điệp Commit (Conventional Commits):**
   * Định dạng chuẩn: `feat(...)`, `fix(...)`, `docs(...)`, `test(...)`.
   * Ví dụ: `feat(contract): deploy contracts to polygon amoy testnet`.
4. **Quyền phê duyệt và Hợp nhất:**
   * Mọi Pull Request bắt buộc phải do **Chủ nhiệm đề tài Đặng Xuân Huy** review và merge vào `main`. Tuyệt đối không tự ý push trực tiếp lên `main` nếu chưa kiểm thử chéo.

---
*Kế hoạch này được ban hành chính thức trên kho lưu trữ của dự án và có hiệu lực thực thi ngay đối với toàn bộ thành viên nhóm nghiên cứu.*
