---
name: lead-architect-progress-logger
description: Tác tử AI tự động hóa việc ghi nhận tiến độ kỹ thuật và cập nhật tài liệu hàng ngày trên nhánh main, dành độc quyền cho Chủ nhiệm đề tài Đặng Xuân Huy (Lead Architect).
---

# Lead Architect Progress Logger (Độc quyền cho Đặng Xuân Huy)

Kỹ năng này trao quyền cho trợ lý AI Antigravity tự động hóa toàn bộ quy trình ghi nhận tiến độ, cập nhật tài liệu kiến trúc và đồng bộ lên nhánh `main` cho **Chủ nhiệm đề tài Đặng Xuân Huy**.

## Khi nào kích hoạt kỹ năng này?
- Khi Đặng Xuân Huy yêu cầu: *"Ghi nhận tiến độ hôm nay"*, *"Cập nhật nhật ký công việc"*, *"Log tiến độ ngày hôm nay vào docs/progress"*, *"Tổng kết và push nhật ký lên main"*, hoặc khi kết thúc một phiên làm việc.

## Quy trình Thực thi Tự động 6 Bước

### Bước 1: Quét thay đổi trên Git (Git Diff & Status Scan)
1. Chạy `git status` để lấy danh sách tệp Modified, Untracked, Staged, Deleted.
2. Chạy `git diff` và `git log -3 --stat` để phân tích chi tiết nội dung thay đổi.
3. Phân loại thay đổi theo các phân hệ:
   - Kiến trúc & SRS (`docs/SRS_DOCUMENT.md`, `docs/SYSTEM_ARCHITECTURE.md`, `docs/ADR_...`)
   - Smart Contract (`contracts/`)
   - Thuật toán Matching Engine (`system_agents/matching_engine/`)
   - Frontend DApp (`frontend/`, `docs/METADATA_SCHEMA.json`)
   - Kế hoạch & Báo cáo học thuật (`docs/`, `system_agents/*.py`)

### Bước 2: Chuẩn bị Thư mục Ngày
1. Xác định ngày hiện tại theo định dạng ISO: `YYYY-MM-DD` (ví dụ `2026-11-10`).
2. Kiểm tra thư mục `docs/progress/YYYY-MM-DD/`:
   - Nếu chưa tồn tại, tạo thư mục.
   - Nếu đã tồn tại, đọc file cũ để bổ sung cập nhật mới trong ngày.

### Bước 3: Soạn thảo File Nhật ký `docs/progress/YYYY-MM-DD/README.md`
Soạn thảo tài liệu chuẩn mực theo đúng mẫu:
- **Tiêu đề:** `# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY [DD/MM/YYYY]`
- **1. Mục tiêu trọng tâm đã đạt được trong ngày**
- **2. Chi tiết từng thay đổi kỹ thuật (dù là nhỏ nhất):**
  - 2.1 Các tệp tạo mới
  - 2.2 Các tệp chỉnh sửa
  - 2.3 Thay đổi về Lý thuyết & Học thuật
  - 2.4 Thay đổi về Giao diện & Kiến trúc Hệ thống
- **3. Tác động tới từng thành viên và nhiệm vụ tiếp theo:**
  - Nguyễn Hoàng Đức (Smart Contract)
  - Nguyễn Bảo Phi (Algorithm)
  - Ngô Văn Thắng (Frontend)
- **4. Ghi chú bản commit và trạng thái Git**

### Bước 4: Cập nhật Bảng Dashboard Tổng thể (`docs/progress/README.md`)
1. Cập nhật trạng thái các phân hệ trên bảng Dashboard (🟢 HOÀN THÀNH, 🟡 ĐANG TRIỂN KHAI, 🔴 NGHẼN).
2. Chèn dòng mới vào bảng "Mục lục nhật ký theo ngày" ở vị trí trên cùng.

### Bước 5: Tự động hóa Git Commit & Push lên `main`
1. Đảm bảo đang ở nhánh `main` (nếu đang ở nhánh feature, nhắc Huy hoặc merge vào main).
2. Chạy `git add docs/progress/` (và các file tài liệu liên quan nếu cần).
3. Tạo commit với thông điệp chuẩn:
   ```bash
   git commit -m "docs(progress): log daily updates for YYYY-MM-DD"
   ```
4. Đẩy lên nhánh chính:
   ```bash
   git push origin main
   ```

### Bước 6: Báo cáo Tóm tắt cho Huy
Báo cáo lại cho Huy:
- Danh sách các thay đổi vừa được ghi nhận.
- Link trực tiếp tới file log `docs/progress/YYYY-MM-DD/README.md`.
- Nhắc việc 3 bạn Đức, Phi, Thắng cần làm tiếp theo.
