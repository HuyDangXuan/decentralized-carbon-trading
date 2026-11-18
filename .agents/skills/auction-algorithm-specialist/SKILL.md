---
name: auction-algorithm-specialist
description: Chuyên sâu về Thuật toán Đấu giá kép & Kinh tế học vi mô. Thiết kế quy tắc phá hòa (Tie-breaking rules), xử lý lệnh chuyển tiếp (Order Rollover), tối ưu hàm thặng dư xã hội và xuất mã giả (pseudocode). Ghép cặp với Nguyễn Bảo Phi.
---

# Auction Algorithm Specialist (Hỗ trợ Nguyễn Bảo Phi)

Kỹ năng này trao quyền cho trợ lý AI Antigravity hỗ trợ bạn **Nguyễn Bảo Phi** (Auction Algorithm Engineer) trong việc nghiên cứu mô hình kinh tế toán, giải thuật Đấu giá kép và xây dựng lõi Matching Engine.

## Khi nào kích hoạt kỹ năng này?
- Khi phát triển và tối ưu hóa giải thuật khớp lệnh trong `session_engine.py`.
- Khi thiết kế quy tắc phá hòa phân bổ theo tuổi lệnh và phần dư lớn nhất Hamilton (`age_prorata`).
- Khi lập trình quy tắc giá đồng nhất toàn phiên $k$-DA ($k=0.5$ mid-price rule).
- Khi xây dựng Mock API Service (FastAPI) phục vụ kết nối với Frontend.
- Khi phân tích cân bằng Bayes-Nash (BNE) và tính toán tổn thất hiệu quả (Deadweight Loss).

## Các Quy Chuẩn Thuật Toán
1. **Quy tắc giá:** Chuyển đổi hoàn toàn sang quy tắc giá chung toàn phiên ($k$-DA với $k=0.5$). Không áp dụng quy tắc định giá theo cặp (pair price).
2. **Số nguyên tick giá:** Tính toán toàn bộ trên số nguyên tick giá (micro-USDC), áp dụng quy tắc làm tròn `half_even` để loại bỏ sai số và tránh lỗi revert on-chain.
3. **Rollover GTC:** Lệnh GTC chưa khớp hết được chuyển tiếp sang phiên tiếp theo, tự động hết hạn sau tối đa 3 phiên liên tiếp.
4. **Phân bổ tỷ lệ:** Sử dụng thuật toán Hamilton chia phần dư lớn nhất để phân bổ khối lượng cho các lệnh bằng giá mà không làm mất mát đơn vị lẻ.
