# 📋 BẢNG ĐIỀU KHIỂN GIAO VIỆC & KANBAN DASHBOARD (SPRINT 12/11 – 20/11/2026)
## HỆ THỐNG GIAO VIỆC NỘI BỘ TRÊN REPOSITORY (IN-REPO TASK MANAGEMENT)

> **Cơ chế vận hành:** Thư mục này là trung tâm giao việc, theo dõi tiến độ và tiếp nhận kết quả bàn giao của từng thành viên trong nhóm nghiên cứu đề tài **"Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain"** (Trường ĐH Điện Lực - EPU).  
> **Chủ nhiệm đề tài:** Đặng Xuân Huy (Lead Architect & Coordinator)  
> **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh

---

## 🎯 DANH MỤC FILE GIAO VIỆC THEO TỪNG THÀNH VIÊN

*Mỗi thành viên chỉ cần mở đúng tệp mang tên mình dưới đây để theo dõi đầu việc, lệnh kỹ thuật, tiêu chí nghiệm thu và tự tích dấu `[x]` khi hoàn thành:*

| Thành viên | Phân hệ chuyên trách | Tệp giao việc cá nhân | Trạng thái hiện tại |
| :--- | :--- | :---: | :---: |
| **Nguyễn Hoàng Đức** | Smart Contract & On-chain Settlement (Polygon Amoy) | [`TASK_DUC_SMART_CONTRACT.md`](TASK_DUC_SMART_CONTRACT.md) | 🟢 **HOÀN THÀNH VƯỢT TIẾN ĐỘ (Đ.1 – Đ.4)** |
| **Nguyễn Bảo Phi** | Matching Engine, FastAPI Service & Game Theory | [`TASK_PHI_AUCTION_ENGINE.md`](TASK_PHI_AUCTION_ENGINE.md) | 🟢 **HOÀN THÀNH P.1, P.3, P.4 (P.2 ĐANG MỞ RỘNG)** |
| **Ngô Văn Thắng** | Web3 Frontend DApp, Metadata Schema & UI/UX Figma | [`TASK_THANG_FRONTEND_WEB3.md`](TASK_THANG_FRONTEND_WEB3.md) | 🟢 **HOÀN THÀNH T.2, T.4 (T.3 SẴN SÀNG DEMO)** |
| **Đặng Xuân Huy** | Lead Architect, Kiểm thử E2E, Slide & Báo cáo GVHD | [`TASK_HUY_LEAD_COORDINATION.md`](TASK_HUY_LEAD_COORDINATION.md) | 🟢 **HOÀN THÀNH H.1, H.2, H.3, H.4** |

---

## 📊 BẢNG KANBAN TỔNG THỂ TIẾN ĐỘ SPRINT (12/11 – 20/11/2026)

| Mã Task | Hạng mục công việc chi tiết | Phụ trách | Hạn chót | Trạng thái | Sản phẩm bàn giao |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Đ.1** | Cài đặt môi trường `npm install` & Chạy test Hardhat local | Đức | 12/11 | [x] Hoàn thành | 14/14 tests `CarbonTrading.test.js` PASS 100% |
| **Đ.2** | Deploy 3 Smart Contracts lên mạng Polygon Amoy Testnet | Đức | 14/11 | [x] Hoàn thành | 3 Contracts verified trên PolygonScan (vượt 2 ngày) |
| **Đ.3** | Tạo tệp `docs/DEPLOYED_ADDRESSES.md` cấp địa chỉ cho nhóm | Đức | 14/11 | [x] Hoàn thành | Tệp `docs/DEPLOYED_ADDRESSES.md` bàn giao nhóm |
| **Đ.4** | Đo lường và cập nhật Benchmark Gas thực tế trên Amoy | Đức | 16/11 | [x] Hoàn thành | Cập nhật Mục 5 `SMART_CONTRACT_SPEC.md` (>52% gas savings) |
| **P.1** | Viết Bot Settlement Submitter (`settlement_submitter.py`) | Phi | 15/11 | [x] Hoàn thành | Bot chạy thật thành công trên Amoy (Tx: `0x9619ff0b...75b8`) |
| **P.2** | Mở rộng Thí nghiệm C đo lường Deadweight Loss ($m > 16$) | Phi | 17/11 | [⏳] Đang mở rộng | Script `equilibrium_crosscheck.py` & số liệu tạm thời $m \le 64$ |
| **P.3** | Biên soạn Tài liệu Đe dọa Bảo mật `docs/THREAT_MODELING.md` | Phi | 18/11 | [x] Hoàn thành | Tệp `docs/THREAT_MODELING.md` qua review độc lập |
| **P.4** | Đọc bài báo gốc & Chuẩn hóa học thuật $k$-DA vs Marginal | Phi | 20/11 | [x] Hoàn thành | Cập nhật `docs/MATCHING_ENGINE_SPEC.md` chuẩn [CS83], [RSW94] |
| **T.1** | Nhận địa chỉ Contract từ Đức và cấu hình `frontend/.env.local` | Thắng | 15/11 | [ ] Chưa xong | DApp kết nối ví MetaMask mạng Amoy |
| **T.2** | Xây dựng Modal Faucet MockUSDC & Mint thử trên UI | Thắng | 16/11 | [x] Hoàn thành | Component `FaucetModal.tsx`, nhận MockUSDC thật trên Amoy |
| **T.3** | Kiểm thử luồng Form đặt lệnh $\to$ Ký EIP-712 $\to$ Vẽ Depth Chart | Thắng | 18/11 | [⏳] Sẵn sàng demo | Luồng đặt lệnh và vẽ Depth Chart sẵn sàng cho phiên 18/11 |
| **T.4** | Hoàn thiện Bộ thiết kế Wireframe Figma 4 phân hệ DApp | Thắng | 20/11 | [x] Hoàn thành | Thư mục `docs/wireframes/` (4 PNG 2880x2000 & 4 SVG vector) |
| **H.1** | Viết script kiểm thử toàn trình `scripts/test_e2e_integration.py` | Huy | 17/11 | [x] Hoàn thành | Script test 5 bước khép kín tự động (Hardhat & Amoy) |
| **H.2** | Triệu tập và chủ trì phiên Demo Liên thông Nội bộ nhóm | Huy | 18/11 | [x] Đã sẵn sàng | Tệp `docs/KE_HOACH_DEMO_NOI_BO_18_11.md` 5 kịch bản diễn tập |
| **H.3** | Biên soạn Slide Báo cáo Tiến độ Giai đoạn 2 (15 - 20 trang) | Huy | 20/11 | [x] Hoàn thành Đề cương | File `docs/SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md` 20 slide chuẩn |
| **H.4** | Duy trì nhật ký tiến độ hàng ngày và báo cáo với GVHD | Huy | Hàng ngày | [x] Hoàn thành | `docs/progress/2026-11-17/README.md` cập nhật trọn vẹn 12-17/11 |

---

## 🛠️ HƯỚNG DẪN DÀNH CHO THÀNH VIÊN KHI LÀM VIỆC (TASK WORKFLOW)

### Bước 1: Mở tệp Task cá nhân
Mở file task của bạn (`TASK_DUC...`, `TASK_PHI...`, `TASK_THANG...`) để đọc kỹ yêu cầu kỹ thuật, câu lệnh mẫu và tiêu chí nghiệm thu.

### Bước 2: Tạo nhánh làm việc độc lập
Trước khi code, kéo code mới nhất từ `main` về và tạo nhánh riêng theo cú pháp:
```bash
git checkout main
git pull origin main
git checkout -b feat/<ten-ban>-<ten-task>
# Ví dụ của Đức: git checkout -b feat/duc-deploy-amoy-gas-benchmark
# Ví dụ của Phi: git checkout -b feat/phi-settlement-submitter-bot
# Ví dụ của Thắng: git checkout -b feat/thang-faucet-ui-figma
```

### Bước 3: Tích hoàn thành và ghi chú tiến độ
Khi làm xong một đầu việc:
1. Mở file task của bạn, sửa dấu cách `- [ ]` thành chữ `- [x]`.
2. Ghi chú tiến độ hoặc các lỗi đã khắc phục vào mục **"Nhật ký & Ghi chú cá nhân"** ở cuối file.

### Bước 4: Chạy kiểm thử cục bộ trước khi đẩy code
Đảm bảo bài test của phân hệ mình pass 100%:
* Smart Contract: `npx hardhat test`
* Matching Engine: `python -m unittest discover system_agents/matching_engine/ -p "test_*.py"`
* Metadata: `python -m unittest tests/test_metadata.py`

### Bước 5: Tạo Pull Request (PR)
Đẩy code lên nhánh của mình và tạo Pull Request vào `main` trên GitHub để Chủ nhiệm đề tài (Đặng Xuân Huy) review và hợp nhất.

---
*Tài liệu này được áp dụng chính thức và bắt buộc đối với toàn bộ thành viên nhóm nghiên cứu.*
