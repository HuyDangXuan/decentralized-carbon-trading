# HỆ THỐNG THEO DÕI TIẾN ĐỘ & NHẬT KÝ KỸ THUẬT HÀNG NGÀY
## DAILY PROGRESS & ENGINEERING DECISION LOGS

> **Cơ chế vận hành:** Kênh thông tin duy nhất (**Single Source of Truth - SSOT**) do **Chủ nhiệm đề tài Đặng Xuân Huy (Lead Architect)** trực tiếp duy trì và cập nhật liên tục trên nhánh `main`.  
> **Mục đích:** Ghi nhận minh bạch, chi tiết toàn bộ các thay đổi kỹ thuật (dù là nhỏ nhất) trong ngày, các quyết định kiến trúc (ADR), trạng thái tài liệu, tiến độ mã nguồn và phân công hành động cho từng thành viên trong nhóm nghiên cứu (**Đức, Phi, Thắng**) cùng Giảng viên hướng dẫn (**TS. Nguyễn Thị Hồng Khánh**).

---

## 📊 BẢNG DASHBOARD TIẾN ĐỘ TỔNG THỂ (GIAI ĐOẠN 2)

| Hạng mục Phân hệ | Thành viên phụ trách | Trạng thái hiện tại | Sản phẩm bàn giao chính | Bản cập nhật mới nhất |
| :--- | :--- | :---: | :--- | :---: |
| **Kiến trúc & SRS (IEEE 830)** | **Đặng Xuân Huy** | 🟢 **HOÀN THÀNH VƯỢT TIẾN ĐỘ** | `docs/SRS_DOCUMENT.md`<br/>`docs/ADR_001_...md` | 17/11/2026 |
| **Hợp đồng Thông minh (Solidity v2)** | **Nguyễn Hoàng Đức** | 🟢 **HOÀN THÀNH TOÀN DIỆN V2 & AMOY** | `CarbonDoubleAuction.sol`, `EvccFaucet.sol`<br/>Benchmark Gas Amoy (`BENCHMARK_RESULTS_AMOY.json`) | 17/11/2026 |
| **Thuật toán Đấu giá & API Engine** | **Nguyễn Bảo Phi** | 🟢 **HOÀN THÀNH V2 & BOT AMOY** | `session_engine.py`, `settlement_submitter.py`<br/>Tx On-chain Amoy, `docs/THREAT_MODELING.md` | 17/11/2026 |
| **Web3 Frontend & DApp UI/UX** | **Ngô Văn Thắng** | 🟢 **HOÀN THÀNH WEB3 & MOCKUPS** | DApp Amoy, `FaucetModal.tsx`<br/>Bộ Mockup Figma 4 phân hệ (`docs/wireframes/`) | 17/11/2026 |

---

## 📅 MỤC LỤC NHẬT KÝ THEO NGÀY (CHRONOLOGICAL INDEX)

*Thư mục nhật ký được đánh số theo chuẩn ISO `YYYY-MM-DD` để dễ dàng sắp xếp theo thời gian trên máy tính và GitHub.*

| Ngày ghi nhận | Tiêu đề tóm tắt nội dung | Thành viên thực hiện | Liên kết chi tiết |
| :---: | :--- | :---: | :---: |
| **17/11/2026** | **Tổng kết kỹ thuật Sprint tích hợp (12/11 – 17/11/2026): Deploy Polygon Amoy, Benchmark Gas thực tế (>52% savings), Bot Submitter chạy thành công giao dịch thật trên Amoy, Faucet Modal và Bộ Mockup Figma 4 phân hệ hoàn thiện.** | Đặng Xuân Huy | [Xem chi tiết](2026-11-17/README.md) |
| **11/11/2026** | **Hợp nhất toàn diện 3 phân hệ (Smart Contract v2, Matching Engine v2, Frontend Web3) vào main; giải quyết triệt để xung đột Git và kiểm thử tích hợp chéo thành công.** | Đặng Xuân Huy | [Xem chi tiết](2026-11-11/README.md) |
| **10/11/2026** | **Khóa 4 thông số kiến trúc (ADR-001), ban hành hồ sơ SRS IEEE 830 hoàn chỉnh, đồng bộ kiến trúc v2.0 và hiệu chỉnh đề cương học thuật Nhiệm vụ 3.** | Đặng Xuân Huy | [Xem chi tiết](2026-11-10/README.md) |
| *18/11/2026* | *(Kế hoạch: Tổ chức phiên Demo Liên thông Nội bộ nhóm 4 bên qua Google Meet)* | Toàn nhóm | [Kế hoạch Demo](../KE_HOACH_DEMO_NOI_BO_18_11.md) |

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
