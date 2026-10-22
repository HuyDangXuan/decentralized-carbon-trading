# CarbonChain: Hệ thống Giao dịch Tín chỉ Carbon Minh bạch trên nền tảng Blockchain

> **Đề tài Nghiên cứu Khoa học Sinh viên - ĐH Điện Lực (2026 - 2027)**  
> **Chủ nhiệm đề tài:** Đặng Xuân Huy  
> **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh  
> **Thành viên nghiên cứu:** Đặng Xuân Huy, Ngô Văn Thắng, Nguyễn Hoàng Đức, Nguyễn Bảo Phi  

---

## 📌 Tổng quan Dự án

Dự án kết hợp giữa **Công nghệ Blockchain (ERC-1155, Smart Contracts)**, **Lưu trữ phi tập trung (IPFS)**, và **Hệ Đa Tác Tử (Multi-Agent System - MAS)** nhằm giải quyết các bài toán lớn nhất của thị trường carbon tự nguyện (VCM):
1. **Thiếu minh bạch & Trùng lặp tín chỉ (Double Spending/Double Counting)**: Giải quyết bằng hợp đồng thông minh chuẩn ERC-1155 và cơ chế đốt token (Burn on Retirement).
2. **Kém thanh khoản & Định giá thiếu hiệu quả**: Giải quyết bằng **Cơ chế đấu giá kép (Continuous/Periodic Double Auction)** và tác tử khớp lệnh tự động.
3. **Chi phí Gas và nghẽn mạng**: Ứng dụng mô hình **Off-chain Matching, On-chain Settlement** (Khớp lệnh ngoài chuỗi - Xác thực và thanh quyết toán trên chuỗi).

---

## 🏛️ 1. Hướng 1: Các Sub-Agent trong Kiến trúc Hệ thống (System Architecture)

Thư mục `system_agents/` chứa các tác tử phần mềm tự hành phục vụ vận hành thị trường:

1. **`matching_engine` (Auction & Matching Agent):**  
   Thu thập sổ lệnh (Orderbook) gồm lệnh Mua (Bid) và Bán (Ask), giải bài toán tối ưu hóa thị trường theo cơ chế Đấu giá kép (*k-Double Auction* hoặc *Mid-price*), xuất chứng thực khớp lệnh để gửi lên Smart Contract.
2. **`simulation_agent` (Market Simulation / Market Maker Agent):**  
   Mô phỏng hàng ngàn tác tử giao dịch đại diện cho các doanh nghiệp phát thải và dự án xanh (theo thuật toán Zero-Intelligence Plus hoặc Adaptive Bidding). Rất quan trọng cho phần đánh giá thực nghiệm.
3. **`mrv_agent` (MRV & Project Verification Agent):**  
   Kiểm định hồ sơ đo lường, báo cáo và thẩm tra (MRV) từ các dự án giảm phát thải, tính toán hash, lưu trữ metadata lên IPFS và phê duyệt phát hành token.
4. **`oracle_agent` (Carbon Oracle & Price Monitor):**  
   Cung cấp dữ liệu giá carbon tham chiếu từ các thị trường quốc tế, cảnh báo biến động bất thường và hành vi thao túng giá.
5. **`retirement_agent` (Retirement & ESG Compliance Agent):**  
   Theo dõi nghĩa vụ bù đắp carbon định kỳ của các doanh nghiệp, kích hoạt giao dịch hủy tín chỉ và xuất chứng nhận ESG bất biến.

---

## 🤖 2. Hướng 2: Các AI Sub-Agent Hỗ trợ Nhóm Nghiên cứu (Development Workflow)

Đã được cài đặt sẵn trong môi trường trợ lý Antigravity để nhóm có thể triệu hồi (`invoke_subagent`):

| Tên Sub-Agent | Thành viên phụ trách | Vai trò hỗ trợ |
| :--- | :--- | :--- |
| **`smart-contract-auditor`** | **Nguyễn Hoàng Đức** | Viết code Solidity ERC-1155, tối ưu gas, audit bảo mật (Reentrancy, Front-running). |
| **`auction-algorithm-specialist`** | **Nguyễn Bảo Phi** | Thiết kế giải thuật đấu giá kép, mô hình kinh tế toán, tối ưu thanh khoản. |
| **`fullstack-web3-engineer`** | **Ngô Văn Thắng** | Lập trình DApp (Next.js/React), kết nối ví MetaMask (Ethers.js/Viem), tích hợp IPFS Pinata. |
| **`scientific-research-writer`** | **Đặng Xuân Huy** | Soạn thảo báo cáo NCKH chuẩn IMRaD, trích dẫn BibTeX, viết bản thảo bài báo hội nghị. |
| **`benchmark-evaluation-specialist`** | **Cả nhóm** | Giả lập testnet, đo lường chi phí Gas, TPS, độ trễ và trực quan hóa biểu đồ (Matplotlib/Seaborn). |

---

## 📂 Cấu trúc Thư mục Dự án

```text
Blockchain/
├── contracts/                  # Smart Contracts (Solidity ERC-1155 & Auction)
│   ├── CarbonCredit1155.sol    # Token hóa tín chỉ carbon theo lô (vintage)
│   └── CarbonDoubleAuction.sol # Thanh quyết toán lệnh đấu giá on-chain
├── system_agents/              # Hệ Đa Tác Tử (Multi-Agent System)
│   ├── matching_engine/        # Auction Matching Engine (Python)
│   ├── simulation_agent/       # Bot mô phỏng giao dịch thị trường
│   ├── mrv_agent/              # Giám sát & Xác thực hồ sơ IPFS
│   ├── oracle_agent/           # Tác tử giám sát giá & cảnh báo
│   └── retirement_agent/       # Tác tử bù đắp & hủy tín chỉ
├── docs/                       # Tài liệu thiết kế & Báo cáo NCKH
│   ├── SYSTEM_ARCHITECTURE.md  # Sơ đồ kiến trúc & luồng xử lý
│   └── PHASE1_ROADMAP.md       # Chi tiết phân công công việc Giai đoạn 1
├── scripts/                    # Scripts deploy & benchmark
├── tests/                      # Kiểm thử hợp đồng & giải thuật
└── README.md
```

---

## 🚀 Hướng dẫn Bắt đầu Nhanh

1. **Khởi chạy mô phỏng Đấu giá kép:**
   ```bash
   cd system_agents/matching_engine
   python -m venv venv
   # Kích hoạt venv và cài đặt dependencies
   python auction_agent.py
   ```

2. **Chạy mô phỏng tác tử thị trường (Simulation Bots):**
   ```bash
   cd system_agents/simulation_agent
   python market_maker_agent.py
   ```
