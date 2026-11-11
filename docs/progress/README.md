# HỆ THỐNG THEO DÕI TIẾN ĐỘ & NHẬT KÝ KỸ THUẬT HÀNG NGÀY
## DAILY PROGRESS & ENGINEERING DECISION LOGS

> **Cơ chế vận hành:** Kênh thông tin duy nhất (**Single Source of Truth - SSOT**) do **Chủ nhiệm đề tài Đặng Xuân Huy (Lead Architect)** trực tiếp duy trì và cập nhật liên tục trên nhánh `main`.  
> **Mục đích:** Ghi nhận minh bạch, chi tiết toàn bộ các thay đổi kỹ thuật (dù là nhỏ nhất) trong ngày, các quyết định kiến trúc (ADR), trạng thái tài liệu, tiến độ mã nguồn và phân công hành động cho từng thành viên trong nhóm nghiên cứu (**Đức, Phi, Thắng**) cùng Giảng viên hướng dẫn (**TS. Nguyễn Thị Hồng Khánh**).

---

## 📊 BẢNG DASHBOARD TIẾN ĐỘ TỔNG THỂ (GIAI ĐOẠN 2)

| Hạng mục Phân hệ | Thành viên phụ trách | Trạng thái hiện tại | Sản phẩm bàn giao chính | Bản cập nhật mới nhất |
| :--- | :--- | :---: | :--- | :---: |
| **Kiến trúc & SRS (IEEE 830)** | **Đặng Xuân Huy** | 🟢 **HOÀN THÀNH VƯỢT TIẾN ĐỘ** | `docs/SRS_DOCUMENT.md`<br/>`docs/ADR_001_...md` | 10/11/2026 |
| **Thuật toán Đấu giá & API Engine** | **Nguyễn Bảo Phi** | 🟡 **ĐANG TRIỂN KHAI** | `session_engine.py`<br/>`api_service.py` (FastAPI) | 10/11/2026 |
| **Hợp đồng Thông minh (Solidity v2)** | **Nguyễn Hoàng Đức** | 🟡 **ĐANG TRIỂN KHAI** | `contracts/CarbonDoubleAuction.sol`<br/>Test Hardhat đo Gas | 10/11/2026 |
| **Web3 Frontend & DApp UI/UX** | **Ngô Văn Thắng** | 🟡 **ĐANG TRIỂN KHAI** | `docs/METADATA_SCHEMA.json`<br/>Figma Wireframe 4 Portal | 10/11/2026 |

---

## 📅 MỤC LỤC NHẬT KÝ THEO NGÀY (CHRONOLOGICAL INDEX)

*Thư mục nhật ký được đánh số theo chuẩn ISO `YYYY-MM-DD` để dễ dàng sắp xếp theo thời gian trên máy tính và GitHub.*

| Ngày ghi nhận | Tiêu đề tóm tắt nội dung | Thành viên thực hiện | Liên kết chi tiết |
| :---: | :--- | :---: | :---: |
| **10/11/2026** | **Khóa 4 thông số kiến trúc (ADR-001), ban hành hồ sơ SRS IEEE 830 hoàn chỉnh, đồng bộ kiến trúc v2.0 và hiệu chỉnh đề cương học thuật Nhiệm vụ 3.** | Đặng Xuân Huy | [Xem chi tiết](2026-11-10/README.md) |
| *Ngày tiếp theo...* | *(Sẽ được cập nhật liên tục khi có phát sinh công việc mới)* | Đặng Xuân Huy | *Đang chờ* |

---

## 🛠️ QUY CHUẨN ĐỊNH DẠNG BẢN GHI NHẬT KÝ (LOGGING STANDARD & TEMPLATE)

Khi có ngày làm việc mới, Chủ nhiệm đề tài sẽ tạo thư mục mới `docs/progress/YYYY-MM-DD/` kèm file `README.md` theo cấu trúc chuẩn sau:

```markdown
# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY [DD/MM/YYYY]

## 1. MỤC TIÊU TRỌNG TÂM TRONG NGÀY
- [Liệt kê các mục tiêu chính cần giải quyết]

## 2. CHI TIẾT CÁC THAY ĐỔI TRONG NGÀY (THAY ĐỔI DÙ LÀ NHỎ NHẤT)
- **Tệp tạo mới:** [Đường dẫn file & Tóm tắt mục đích]
- **Tệp chỉnh sửa:** [Đường dẫn file & Các dòng/logic được sửa]
- **Thay đổi về mặt Lý thuyết / Học thuật:** [Nếu có]
- **Thay đổi về mặt Kiến trúc / Tham số hệ thống:** [Nếu có]
- **Quy chuẩn dữ liệu & Giao thức:** [Nếu có]

## 3. TÁC ĐỘNG TỚI TỪNG THÀNH VIÊN VÀ NHIỆM VỤ TIẾP THEO
- **Nguyễn Hoàng Đức (Smart Contract):** [Cần chú ý gì từ thay đổi này, việc cần làm]
- **Nguyễn Bảo Phi (Algorithm):** [Cần chú ý gì từ thay đổi này, việc cần làm]
- **Ngô Văn Thắng (Frontend):** [Cần chú ý gì từ thay đổi này, việc cần làm]

## 4. GHI CHÚ BẢN COMMIT VÀ TRẠNG THÁI GIT
- **Nhánh phát triển:** [Nhánh làm việc / main]
- **Commit SHA:** [Mã commit]
- **Pull Request liên quan:** [Số PR / link]
```

---
*Tài liệu này là quy chuẩn thống nhất nội bộ của nhóm NCKH Sinh viên Trường Đại học Điện Lực (EPU).*
