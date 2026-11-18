# 📚 HỆ THỐNG QUẢN TRỊ TÀI LIỆU DỰ ÁN (PROJECT DOCUMENTATION SYSTEM)
## ĐỀ TÀI NCKH: HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON MINH BẠCH VÀ HIỆU QUẢ TRÊN NỀN TẢNG BLOCKCHAIN

> **Chủ nhiệm đề tài / Lead Architect:** Đặng Xuân Huy  
> **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh  
> **Khoa Công nghệ Thông tin - Trường Đại học Điện Lực (EPU)**

---

## 🧭 BẢN ĐỒ TÀI LIỆU & PHÂN TẦNG THƯ MỤC (DOCUMENTATION MAP)

Toàn bộ tài liệu kỹ thuật, kiến trúc, đặc tả, kế hoạch và báo cáo của dự án được phân cấp chặt chẽ theo 10 phân nhóm chuyên biệt. **Tuyệt đối không lưu file markdown tự do trực tiếp tại thư mục gốc `docs/`.**

```
docs/
├── architecture/     # Kiến trúc hệ thống, ADR, sơ đồ luồng & từ điển dữ liệu
├── specs/            # Đặc tả yêu cầu phần mềm (SRS), hợp đồng, engine & bảo mật
├── integration/      # Hướng dẫn tích hợp, API samples, địa chỉ contract & bot
├── planning/         # Kế hoạch sprint, roadmap, kịch bản demo nội bộ
├── reports/          # Báo cáo tổng quan giai đoạn, slide thuyết trình
├── discussions/      # Lưu vết trao đổi kỹ thuật, lịch sử trạng thái nghiên cứu
├── tasks/            # Quản trị giao việc cá nhân (chia theo từng ngày giao YYYY-MM-DD)
├── progress/         # Nhật ký tiến độ thực hiện hàng ngày (YYYY-MM-DD)
├── wireframes/       # Bản vẽ thiết kế giao diện DApp Figma (PNG & SVG)
└── examples/         # Mẫu dữ liệu JSON theo chuẩn quốc tế (Verra VCS, Gold Standard)
```

---

## 🗂️ CHI TIẾT DANH MỤC TÀI LIỆU THEO TỪNG PHÂN TẦNG

### 1. Kiến trúc & Thiết kế Hệ thống (`docs/architecture/`)
* Chứa các tài liệu định hình kiến trúc tổng thể, quyết định công nghệ quan trọng và mô hình dữ liệu:
  * [`SYSTEM_ARCHITECTURE.md`](architecture/SYSTEM_ARCHITECTURE.md): Kiến trúc tổng thể 4 tầng (Application, Agent & Engine, Settlement, Consensus).
  * [`ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md`](architecture/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md): 4 quyết định kiến trúc then chốt (EIP-712, Batch Settlement, Định giá Marginal, Rollover 3 phiên).
  * [`USER_FLOWS.md`](architecture/USER_FLOWS.md): Luồng người dùng chi tiết (Project Developer, Verifier VVB, Trader, ESG Corporate).
  * [`DATA_DICTIONARY.md`](architecture/DATA_DICTIONARY.md): Từ điển dữ liệu chuẩn hóa cho metadata tín chỉ carbon và các trường on-chain.

### 2. Đặc tả Kỹ thuật Chuyên sâu (`docs/specs/`)
* Chứa các bản đặc tả chính thức có giá trị nghiệm thu kỹ thuật và đối chiếu khoa học:
  * [`SRS_DOCUMENT.md`](specs/SRS_DOCUMENT.md): Hồ sơ Đặc tả Yêu cầu Phần mềm chuẩn IEEE 830-1998 (FR-01 đến FR-15, NFR-01 đến NFR-05).
  * [`SMART_CONTRACT_SPEC.md`](specs/SMART_CONTRACT_SPEC.md): Đặc tả kỹ thuật Smart Contracts (ERC-1155, Double Auction, 7 chốt chặn an toàn).
  * [`MATCHING_ENGINE_SPEC.md`](specs/MATCHING_ENGINE_SPEC.md): Đặc tả thuật toán khớp lệnh phân bổ Hamilton, lý thuyết $k$-DA và mô phỏng Game Theory.
  * [`THREAT_MODELING.md`](specs/THREAT_MODELING.md): Mô hình hóa đe dọa bảo mật, phân tích rủi ro MEV, Front-running và giải pháp phòng thủ.

### 3. Tích hợp Hệ thống & Hướng dẫn Vận hành (`docs/integration/`)
* Hướng dẫn liên thông giữa các phân hệ, mẫu tích hợp và địa chỉ triển khai:
  * [`DEPLOYED_ADDRESSES.md`](integration/DEPLOYED_ADDRESSES.md): Danh bạ địa chỉ Smart Contracts chính thức trên mạng Polygon Amoy Testnet.
  * [`FRONTEND_INTEGRATION.md`](integration/FRONTEND_INTEGRATION.md): Hướng dẫn kết nối Frontend Next.js với Web3 Wagmi và Matching Engine.
  * [`FRONTEND_API_SAMPLES.md`](integration/FRONTEND_API_SAMPLES.md): Tập mẫu JSON request/response và WebSocket payload phục vụ Frontend.
  * [`SETTLEMENT_SUBMITTER_GUIDE.md`](integration/SETTLEMENT_SUBMITTER_GUIDE.md): Cẩm nang cấu hình và vận hành Bot thanh toán tự động (`settlement_submitter.py`).
  * [`OPERATOR_WALLET_REQUEST.md`](integration/OPERATOR_WALLET_REQUEST.md): Quy trình cấp quyền và quản lý an toàn ví Operator on-chain.
  * [`HUONG_DAN_SU_DUNG_SUB_AGENTS.md`](integration/HUONG_DAN_SU_DUNG_SUB_AGENTS.md): Hướng dẫn phối hợp các AI Sub-agents chuyên trách trong nhóm.

### 4. Kế hoạch & Quản trị Sprint (`docs/planning/`)
* Lộ trình phát triển, phân công công việc chi tiết và kịch bản diễn tập:
  * [`PHASE1_ROADMAP.md`](planning/PHASE1_ROADMAP.md): Lộ trình tổng thể Giai đoạn 1 và mục tiêu giai đoạn.
  * [`KE_HOACH_PHAN_CONG_NHIEM_VU_CHI_TIET_SPRINT_TICH_HOP.md`](planning/KE_HOACH_PHAN_CONG_NHIEM_VU_CHI_TIET_SPRINT_TICH_HOP.md): Kế hoạch phân công nhiệm vụ Sprint Tích hợp Hệ thống (12/11 – 20/11/2026).
  * [`KE_HOACH_DEMO_NOI_BO_18_11.md`](planning/KE_HOACH_DEMO_NOI_BO_18_11.md): Kịch bản chi tiết 5 bước tổ chức phiên Demo liên thông nội bộ ngày 18/11/2026.
  * `KE_HOACH_PHAN_CHIA_CONG_VIEC_GIAI_DOAN_2.docx`: Bản Word lưu hồ sơ khoa học kế hoạch Giai đoạn 2.

### 5. Báo cáo & Tài liệu Học thuật (`docs/reports/`)
* Các sản phẩm phục vụ báo cáo với Giảng viên hướng dẫn và Hội đồng nghiệm thu:
  * [`BAO_CAO_TONG_QUAN_GIAI_DOAN_1.md`](reports/BAO_CAO_TONG_QUAN_GIAI_DOAN_1.md): Báo cáo tổng kết toàn diện kết quả nghiên cứu Giai đoạn 1.
  * [`SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md`](reports/SLIDE_BAO_CAO_GIAI_DOAN_2_OUTLINE.md): Đề cương chi tiết 20 Slide thuyết trình báo cáo tiến độ Giai đoạn 2.
  * `BAO_CAO_PHAN_TICH_LICH_SU_GIT_VA_VAN_DE_MATCHING_ENGINE.docx`: Tài liệu phân tích chuyên sâu giải quyết xung đột mã nguồn.

### 6. Trao đổi Kỹ thuật & Lưu vết Nghiên cứu (`docs/discussions/`)
* Nơi lưu trữ biên bản các cuộc họp kỹ thuật, ghi chú hiện trạng giải quyết vấn đề:
  * [`PHI_STATUS_2026-11-17.md`](discussions/PHI_STATUS_2026-11-17.md): Nhật ký rà soát tiến độ và các câu hỏi kỹ thuật của kỹ sư Matching Engine.
  * [`VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md`](discussions/VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md): Bảng đối soát các vấn đề kỹ thuật Đ1–Đ13, H1–H10, T1–T3.
  * [`TIEN_TRINH_MATCHING_ENGINE.md`](discussions/TIEN_TRINH_MATCHING_ENGINE.md): Lịch sử cải tiến thuật toán và kiến trúc Engine.

### 7. Quản lý Giao việc Cá nhân (`docs/tasks/`)
* Quản trị nhiệm vụ cụ thể của từng thành viên theo từng đợt Sprint:
  * [`tasks/README.md`](tasks/README.md): Bảng điều khiển Kanban tổng thể của nhóm.
  * [`tasks/2026-11-12/`](tasks/2026-11-12/): Gói giao việc Sprint tích hợp Amoy (giao ngày 12/11/2026) — **Đã nghiệm thu 100%**.

### 8. Nhật ký Tiến độ Hàng ngày (`docs/progress/`)
* Lưu vết thay đổi mã nguồn, kết quả test và nhật ký làm việc từng ngày theo chuẩn Lead Architect:
  * [`progress/README.md`](progress/README.md): Bảng mục lục tiến độ xuyên suốt dự án.
  * `progress/YYYY-MM-DD/README.md`: Nhật ký chi tiết của từng ngày.

### 9. Thiết kế Giao diện UI/UX (`docs/wireframes/`)
* Chứa link Figma chính thức và 8 file bản vẽ (4 PNG độ phân giải 2880x2000, 4 SVG vector) cho 4 phân hệ Web3 DApp.

### 10. Lược đồ Dữ liệu & Mẫu Quốc tế (`docs/` & `docs/examples/`)
* [`METADATA_SCHEMA.json`](METADATA_SCHEMA.json): Lược đồ chuẩn xác thực JSON Schema cho metadata tín chỉ carbon trên IPFS.
* [`BENCHMARK_RESULTS_AMOY.json`](BENCHMARK_RESULTS_AMOY.json): Số liệu đo lường gas thực tế trên mạng Polygon Amoy Testnet.
* `examples/`: Các mẫu JSON thực tế (`example_verra_vcs.json`, `example_gold_standard.json`).

---

## 📜 QUY TẮC BẮT BUỘC KHI VIẾT VÀ QUẢN TRỊ TÀI LIỆU (DOCS RULES)

Để giữ gìn cấu trúc tài liệu khoa học, chuyên nghiệp và tránh tình trạng phân mảnh, mọi thành viên trong nhóm và các AI Agent hỗ trợ **bắt buộc phải tuân thủ nghiêm ngặt 5 quy tắc vàng sau**:

### 🚫 Quy tắc 1: CẤM tạo file Markdown trực tiếp ở thư mục gốc `docs/`
* Mọi file tài liệu mới phát sinh **bắt buộc** phải được xếp vào đúng 1 trong các thư mục con tương ứng (`architecture/`, `specs/`, `integration/`, `planning/`, `reports/`, `discussions/`).
* Thư mục gốc `docs/` chỉ chứa duy nhất file điều hướng `README.md`, schema gốc `METADATA_SCHEMA.json` và file số liệu `BENCHMARK_RESULTS_AMOY.json`.

### 📦 Quy tắc 2: Quy chuẩn Giao việc & Đóng gói Task (`docs/tasks/`)
* Khi bắt đầu một đợt giao việc mới:
  1. Lead Architect tạo thư mục con mang tên ngày giao task: `docs/tasks/YYYY-MM-DD/`.
  2. Tạo các file giao việc cho từng thành viên: `TASK_<TEN_THANH_VIEN>_<PHAN_HE>.md`.
* Khi hoàn thành một Sprint:
  1. Kiểm tra nghiệm thu, tích dấu `- [x] Hoàn thành`.
  2. Toàn bộ file task nằm trọn trong thư mục ngày giao đó, không để file task trôi nổi ở ngoài.
  3. Cập nhật bảng Kanban tại `docs/tasks/README.md`.

### 📅 Quy tắc 3: Quy chuẩn Nhật ký Tiến độ (`docs/progress/`)
* Khi hoàn thành công việc trong ngày, Lead Architect chạy script tự động:
  ```bash
  python scripts/log_daily_progress.py
  ```
* File nhật ký luôn nằm tại `docs/progress/YYYY-MM-DD/README.md` và tự động cập nhật vào bảng tổng kết `docs/progress/README.md`.

### 🔤 Quy tắc 4: Quy chuẩn Đặt tên File & Tiêu đề
* Tài liệu đặc tả kỹ thuật, kiến trúc, báo cáo: Dùng chữ in hoa cách nhau bằng dấu gạch dưới (`UPPER_SNAKE_CASE.md`), ví dụ: `SRS_DOCUMENT.md`, `SYSTEM_ARCHITECTURE.md`.
* Nhật ký, phân công theo thời gian: Dùng định dạng ISO `YYYY-MM-DD`.
* Tiêu đề tài liệu: Bắt buộc có biểu tượng emoji nhận diện, tiêu đề cấp 1 (`#`) ghi rõ tên tài liệu, tiêu đề cấp 2 (`##`) ghi tên phân hệ/đề tài.

### 🔗 Quy tắc 5: Quy chuẩn Liên kết & Trích dẫn (Cross-referencing)
* Khi tham chiếu giữa các tài liệu trong `docs/`, luôn dùng đường dẫn tương đối chính xác (relative path). Ví dụ:
  * Từ `specs/SRS_DOCUMENT.md` trỏ sang ADR: `[ADR-001](../architecture/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md)`.
  * Từ `specs/SRS_DOCUMENT.md` trỏ sang địa chỉ contract: `[DEPLOYED_ADDRESSES](../integration/DEPLOYED_ADDRESSES.md)`.
* Sau khi tạo tài liệu mới, người tạo **phải cập nhật link** vào bảng mục lục trong chính file `docs/README.md` này.

---
*Quy chuẩn này được áp dụng chính thức và có hiệu lực từ ngày 18/11/2026 đối với toàn bộ thành viên đề tài NCKH.*
