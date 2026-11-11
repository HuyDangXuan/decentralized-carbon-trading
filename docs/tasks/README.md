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
| **Nguyễn Hoàng Đức** | Smart Contract & On-chain Settlement (Polygon Amoy) | [`TASK_DUC_SMART_CONTRACT.md`](TASK_DUC_SMART_CONTRACT.md) | 🟡 **ĐANG THỰC HIỆN** |
| **Nguyễn Bảo Phi** | Matching Engine, FastAPI Service & Game Theory | [`TASK_PHI_AUCTION_ENGINE.md`](TASK_PHI_AUCTION_ENGINE.md) | 🟡 **ĐANG THỰC HIỆN** |
| **Ngô Văn Thắng** | Web3 Frontend DApp, Metadata Schema & UI/UX Figma | [`TASK_THANG_FRONTEND_WEB3.md`](TASK_THANG_FRONTEND_WEB3.md) | 🟡 **ĐANG THỰC HIỆN** |
| **Đặng Xuân Huy** | Lead Architect, Kiểm thử E2E, Slide & Báo cáo GVHD | [`TASK_HUY_LEAD_COORDINATION.md`](TASK_HUY_LEAD_COORDINATION.md) | 🟡 **ĐANG THỰC HIỆN** |

---

## 📊 BẢNG KANBAN TỔNG THỂ TIẾN ĐỘ SPRINT (12/11 – 20/11/2026)

| Mã Task | Hạng mục công việc chi tiết | Phụ trách | Hạn chót | Trạng thái | Sản phẩm bàn giao |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Đ.1** | Cài đặt môi trường `npm install` & Chạy test Hardhat local | Đức | 12/11 | [ ] Chưa xong | 100% tests `CarbonTrading.test.js` pass |
| **Đ.2** | Deploy 3 Smart Contracts lên mạng Polygon Amoy Testnet | Đức | 14/11 | [ ] Chưa xong | 3 Contract verified trên PolygonScan |
| **Đ.3** | Tạo tệp `docs/DEPLOYED_ADDRESSES.md` cấp địa chỉ cho nhóm | Đức | 14/11 | [ ] Chưa xong | Tệp `docs/DEPLOYED_ADDRESSES.md` |
| **Đ.4** | Đo lường và cập nhật Benchmark Gas thực tế trên Amoy | Đức | 16/11 | [ ] Chưa xong | Cập nhật Mục 5 `SMART_CONTRACT_SPEC.md` |
| **P.1** | Viết Bot Settlement Submitter (`settlement_submitter.py`) | Phi | 15/11 | [ ] Chưa xong | Module nộp `batchSettleTrades` on-chain |
| **P.2** | Mở rộng Thí nghiệm C đo lường Deadweight Loss ($m > 16$) | Phi | 17/11 | [ ] Chưa xong | Đồ thị log-log $O(1/m^2)$ trong `simulation/` |
| **P.3** | Biên soạn Tài liệu Đe dọa Bảo mật `docs/THREAT_MODELING.md` | Phi | 18/11 | [ ] Chưa xong | Tệp `docs/THREAT_MODELING.md` hoàn chỉnh |
| **P.4** | Đọc bài báo gốc & Chuẩn hóa học thuật $k$-DA vs Marginal | Phi | 20/11 | [ ] Chưa xong | Cập nhật `docs/MATCHING_ENGINE_SPEC.md` |
| **T.1** | Nhận địa chỉ Contract từ Đức và cấu hình `frontend/.env.local` | Thắng | 15/11 | [ ] Chưa xong | DApp kết nối ví MetaMask mạng Amoy |
| **T.2** | Xây dựng Modal Faucet MockUSDC & Mint thử trên UI | Thắng | 16/11 | [ ] Chưa xong | Component `FaucetModal.tsx` trên giao diện |
| **T.3** | Kiểm thử luồng Form đặt lệnh $\to$ Ký EIP-712 $\to$ Vẽ Depth Chart | Thắng | 18/11 | [ ] Chưa xong | Đặt lệnh hiển thị Depth Chart $< 1$s |
| **T.4** | Hoàn thiện Bộ thiết kế Wireframe Figma 4 phân hệ DApp | Thắng | 20/11 | [ ] Chưa xong | Thư mục `docs/wireframes/` & Link Figma |
| **H.1** | Viết script kiểm thử toàn trình `scripts/test_e2e_integration.py` | Huy | 17/11 | [ ] Chưa xong | Script test 5 bước khép kín tự động |
| **H.2** | Triệu tập và chủ trì phiên Demo Liên thông Nội bộ nhóm | Huy | 18/11 | [ ] Chưa xong | Biên bản họp Google Meet & Test log |
| **H.3** | Biên soạn Slide Báo cáo Tiến độ Giai đoạn 2 (15 - 20 trang) | Huy | 20/11 | [ ] Chưa xong | File `docs/SLIDE_BAO_CAO_GIAI_DOAN_2.pptx` |
| **H.4** | Duy trì nhật ký tiến độ hàng ngày và báo cáo với GVHD | Huy | Hàng ngày | [⏳] Đang làm | `docs/progress/` cập nhật liên tục |

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
