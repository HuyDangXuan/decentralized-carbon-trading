---
name: benchmark-evaluation-specialist
description: Chuyên sâu về Kiểm thử tải & Thực nghiệm. Viết script đo lường chi phí Gas thực tế, thông lượng TPS, thời gian khớp lệnh và trực quan hóa số liệu thành biểu đồ khoa học (Matplotlib/Seaborn). Hỗ trợ cả nhóm.
---

# Benchmark Evaluation Specialist (Hỗ trợ Cả Nhóm)

Kỹ năng này trao quyền cho trợ lý AI Antigravity hỗ trợ nhóm nghiên cứu thực hiện các bài đo kiểm thực nghiệm, đánh giá hiệu năng hệ thống và trực quan hóa số liệu phục vụ báo cáo khoa học.

## Khi nào kích hoạt kỹ năng này?
- Khi viết script Hardhat/Foundry đo lường lượng gas thực tế on-chain trên mạng Polygon Amoy testnet.
- Khi đo lường thông lượng giao dịch (TPS) và độ trễ khớp lệnh của Matching Engine.
- Khi thực hiện kiểm thử tải với các kịch bản mô phỏng nhiều tác tử đồng thời (`market_maker_agent.py`).
- Khi vẽ biểu đồ so sánh chi phí gas (Single trade vs Batch settlement) bằng Matplotlib/Seaborn.

## Các Chỉ Số Đánh Giá Chính (Key Performance Indicators)
1. **Chi phí Gas on-chain:** Đo lường cho các hàm `mintCarbonCredit`, `settleMatchedTrade`, `batchSettleTrades`, `retireCarbonCredit`. Mục tiêu: $<100k$ gas/giao dịch khi gom lô.
2. **Thông lượng Khớp lệnh (Off-chain TPS):** Tốc độ xử lý hàng ngàn lệnh mua/bán trong một chu kỳ phiên (5 phút).
3. **Độ Trễ Thanh Quyết Toán (Settlement Latency):** Thời gian từ khi phiên kết thúc đến khi giao dịch được xác thực và hoàn tất trên Blockchain.
4. **Hiệu Quả Phân Bổ (Allocative Efficiency):** So sánh tổng thặng dư thực tế đạt được so với thặng dư tối ưu lý thuyết ($>90\%$).
