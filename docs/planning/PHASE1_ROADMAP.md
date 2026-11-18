# Kế hoạch và Phân công Chi tiết Giai đoạn 1 (10/2026 – 11/2026)

**Đề tài:** Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain  
**Đơn vị:** Khoa Điện toán và Công nghệ số năng lượng - Trường Đại học Điện Lực  
**Chủ nhiệm đề tài:** Đặng Xuân Huy  
**Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh  

---

## 1. Mục tiêu Giai đoạn 1
- Hoàn thành báo cáo tổng quan lý thuyết về thị trường carbon tự nguyện (VCM), tiêu chuẩn tín chỉ (Gold Standard, Verra) và công nghệ Blockchain.
- Khảo sát và lựa chọn nền tảng Blockchain (Polygon/Ethereum testnet), chuẩn token ERC-1155, giải pháp lưu trữ IPFS và cơ chế Đấu giá kép.
- Định hình kiến trúc hệ thống sơ bộ (bao gồm cả mô hình Multi-Agent System).
- Báo cáo tiến độ và thông qua ý kiến với GVHD.

---

## 2. Bảng Phân công Trách nhiệm Chi tiết

| Thành viên | MSV & Lớp | Chuyên đề phụ trách | Đầu ra cụ thể (Deliverables) | AI Sub-agent hỗ trợ tương ứng |
| :--- | :--- | :--- | :--- | :--- |
| **Đặng Xuân Huy** (Chủ nhiệm) | 23810310007<br>D18CNPM1 | **Điều phối, Định hình Bài toán & Tổng hợp**<br>• Lập kế hoạch, quản lý tiến độ nhóm.<br>• Viết mục tiêu, phạm vi và tính cấp thiết.<br>• Tổng hợp và biên tập báo cáo Giai đoạn 1. | • Bản đặc tả phạm vi đề tài (Scope Document).<br>• Báo cáo tổng quan hoàn chỉnh Giai đoạn 1.<br>• Slide báo cáo tiến độ với GVHD. | `scientific-research-writer` |
| **Ngô Văn Thắng** | 23810310401<br>D18CNPM1 | **Nghiệp vụ Thị trường Carbon & Tiêu chuẩn Quốc tế**<br>• Nghiên cứu quy trình cấp phát tín chỉ (Verra VCS, Gold Standard).<br>• Phân tích lộ trình thị trường carbon tại Việt Nam (QĐ 06/QĐ-TTg).<br>• Phân tích vấn đề trùng lặp tín chỉ (Double Spending/Counting). | • Chuyên đề 1: *"Tổng quan thị trường carbon tự nguyện và cơ chế phòng chống trùng lặp tín chỉ"*.<br>• Sơ đồ quy trình nghiệp vụ thực tế. | `fullstack-web3-engineer` |
| **Nguyễn Hoàng Đức** | 23810310060<br>D18CNPM1 | **Công nghệ Blockchain & Lưu trữ IPFS**<br>• So sánh mạng thử nghiệm (Polygon Amoy vs Ethereum Sepolia).<br>• Phân tích ưu nhược điểm ERC-20 vs ERC-721 vs ERC-1155.<br>• Khảo sát giải pháp lưu trữ ngoài chuỗi (Pinata IPFS). | • Chuyên đề 2: *"Khảo sát giải pháp Blockchain, chuẩn ERC-1155 và lưu trữ IPFS cho tín chỉ carbon"*.<br>• Ma trận so sánh công nghệ (Trade-off matrix). | `smart-contract-auditor` |
| **Nguyễn Bảo Phi** | 23810310017<br>D18CNPM1 | **Cơ chế Đấu giá kép & Mô hình Kinh tế**<br>• Nghiên cứu giải thuật Đấu giá kép (Continuous / Periodic Double Auction).<br>• Nghiên cứu cơ chế xác định giá thị trường ($k$-double auction rule).<br>• Đánh giá mô hình Off-chain matching vs On-chain matching. | • Chuyên đề 3: *"Nghiên cứu cơ chế đấu giá kép và giải thuật khớp lệnh tối ưu trong thị trường carbon"*.<br>• Báo cáo đánh giá thuật toán khớp lệnh. | `auction-algorithm-specialist` |

---

## 3. Lịch trình Theo tuần (Timeline)

- **Tuần 1 - 3 (01/10 – 21/10):**
  - Thu thập tài liệu, mỗi thành viên viết dự thảo báo cáo chuyên đề của mình.
  - Họp nhóm hàng tuần đánh giá tài liệu thu thập được.
- **Tuần 4 - 5 (22/10 – 05/11):**
  - Thảo luận nội bộ, bảo vệ quan điểm lựa chọn công nghệ (chốt dùng ERC-1155 và cơ chế khớp lệnh ngoài chuỗi).
  - Thử nghiệm các script mẫu trong thư mục `system_agents/`.
- **Tuần 6 - 7 (06/11 – 20/11):**
  - Ghép nối các chuyên đề thành một Báo cáo tổng quan hoàn chỉnh.
  - Đọc chéo và phản biện nội bộ để chỉnh sửa lỗi diễn đạt và số liệu.
- **Tuần 8 (21/11 – 30/11):**
  - Nộp báo cáo cho TS. Nguyễn Thị Hồng Khánh xin nhận xét.
  - Chỉnh sửa lần cuối và nghiệm thu Giai đoạn 1.
