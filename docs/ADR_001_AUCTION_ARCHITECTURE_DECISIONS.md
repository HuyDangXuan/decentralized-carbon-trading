# KIẾN TRÚC & QUYẾT ĐỊNH THIẾT KẾ (ARCHITECTURE DECISION RECORD)
## ADR-001: Khóa 4 Thông số Kiến trúc Cốt lõi cho Bộ Khớp lệnh Đấu giá kép Định kỳ (Periodic Double Auction)

- **Mã tài liệu:** ADR-001
- **Trạng thái:** ACCEPTED (ĐÃ PHÊ DUYỆT & ÁP DỤNG CHÍNH THỨC)
- **Ngày quyết định:** 10/11/2026
- **Chủ trì & Phê duyệt:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Thành viên tham gia biểu quyết:**
  - Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
  - Nguyễn Bảo Phi (Auction Algorithm Engineer)
  - Nguyễn Hoàng Đức (Smart Contract Engineer)
  - Ngô Văn Thắng (Fullstack Web3 & Frontend Engineer)
- **Dự án:** Sàn giao dịch Tín chỉ Carbon Phi tập trung ứng dụng Hệ Đa Tác tử (Multi-Agent System) trên nền tảng Blockchain – Trường Đại học Điện Lực (EPU)

---

### 1. Bối cảnh & Vấn đề Kỹ thuật (Context & Problem Statement)

Trong quá trình phân tích lịch sử Git và đối soát chéo giữa các tài liệu kỹ thuật Giai đoạn 1 và bản phác thảo Giai đoạn 2 (được ghi nhận tại vấn đề tồn tại **H2**), nhóm nghiên cứu phát hiện sự thiếu đồng bộ và chưa thống nhất giữa 4 thành viên về 4 thông số kiến trúc nền tảng của Bộ khớp lệnh (Matching Engine):
1. **Chu kỳ phiên (Call Duration):** Mã nguồn cũ chạy khớp lệnh liên tục hoặc không xác định độ dài chu kỳ tích lũy lệnh.
2. **Quy tắc phá hòa (Tie-breaking):** Chưa chốt giữa phương án ưu tiên thời gian thuần túy (FIFO), chia tỷ lệ Pro-rata, hay kết hợp tuổi lệnh (`age_prorata`). Nguy cơ làm tròn số nguyên gây sai lệch tổng khối lượng khớp.
3. **Quy tắc định giá:** Mã nguồn cũ `auction_agent.py` dùng cơ chế định giá theo từng cặp (`pair`), trong khi thực nghiệm toán học của Nguyễn Bảo Phi chỉ ra rằng quy tắc giá chung của toàn phiên (`kda`) có đặc tính hội tụ kinh tế vượt trội $O(1/m^2)$.
4. **Vòng đời lệnh chưa khớp (Order Rollover):** Lệnh GTC (Good-Til-Cancelled) chưa có giới hạn chuyển tiếp, dẫn đến tình trạng treo lệnh vĩnh viễn trên sổ lệnh ngoài chuỗi, gây quá tải bộ nhớ và rủi ro trượt giá cho nhà đầu tư.

Chủ nhiệm đề tài Đặng Xuân Huy đã triệu tập cuộc họp kỹ thuật **Sprint Alignment** nhằm thảo luận, bỏ phiếu dân chủ và ban hành quyết định kiến trúc chính thức.

---

### 2. Chi tiết 4 Quyết định Kiến trúc Đã Thống nhất (Architecture Decisions)

#### Quyết định 1: Chu kỳ phiên đấu giá định kỳ (Periodic Double Auction Session Duration)
- **Quy định chính thức:**
  - **Môi trường Testnet / Demo nghiệm thu:** **$T_{\text{session}} = 5 \text{ phút}$** (300 giây).
    - *Giai đoạn gom lệnh (Order Collection Phase):* 4 phút 30 giây (270 giây).
    - *Giai đoạn đóng sổ & khớp lệnh (Freeze & Matching Phase):* 15 giây.
    - *Giai đoạn gửi thanh quyết toán On-chain (Settlement Phase):* 15 giây.
  - **Môi trường Thực tế (Mainnet / Pilot Production):** **$T_{\text{session}} = 15 \text{ phút}$** (900 giây).
    - *Giai đoạn gom lệnh:* 14 phút (840 giây).
    - *Giai đoạn đóng sổ & khớp lệnh:* 30 giây.
    - *Giai đoạn xác nhận khối on-chain:* 30 giây.
- **Cơ sở kỹ thuật:**
  - Chu kỳ 5 phút trên Testnet Polygon Amoy đảm bảo thời gian đủ ngắn để hội đồng nghiệm thu quan sát trực quan luồng gom lệnh -> khớp -> thanh toán on-chain mà không phải chờ đợi lâu, nhưng đủ dài để tránh nghẽn mạng và tiết kiệm chi phí RPC.
  - Chu kỳ 15 phút trên thực tế mô phỏng chính xác nhịp độ thị trường tín chỉ carbon (thị trường tài sản giao dịch phi tập trung tần suất thấp - low frequency trading, khối lượng lớn), cho phép tích tụ đủ độ sâu thanh khoản (Liquidity Pooling) để triệt tiêu chênh lệch giá (bid-ask spread).

---

#### Quyết định 2: Quy tắc phá hòa đa tiêu chí `age_prorata` kết hợp phần dư lớn nhất (Hamilton Method)
- **Quy định chính thức:**
  Áp dụng quy tắc kết hợp **`age_prorata`** cho các lệnh cùng mức giá thanh toán biên ($P_{\text{clearing}}$):
  1. **Bước 1 (Phân nhóm theo thâm niên - Age Grouping):** Ưu tiên các lệnh đã tồn tại từ các phiên trước (lệnh được Rollover) so với các lệnh mới vào sổ ở phiên hiện tại.
  2. **Bước 2 (Chia tỷ lệ Pro-rata):** Trong cùng một nhóm tuổi, khối lượng khớp lý tưởng của lệnh $i$ được chia theo tỷ lệ khối lượng còn lại $q_i$:
     $$q_i^{\text{ideal}} = Q_{\text{match\_pool}} \times \frac{q_i}{\sum_{j} q_j}$$
  3. **Bước 3 (Làm tròn số nguyên bằng thuật toán Hamilton / Largest Remainder):**
     - Để bảo toàn tuyệt đối đơn vị nguyên vẹn của tín chỉ ($1 \text{ token} = 1 \text{ tCO}_2\text{e}$), cấm dùng hàm `round()` số học thông thường.
     - Tính phần nguyên sàn (floor): $a_i = \lfloor q_i^{\text{ideal}} \rfloor$.
     - Tính phần thập phân dư: $r_i = q_i^{\text{ideal}} - a_i$.
     - Tính số token dư thừa chưa chia: $R = Q_{\text{match\_pool}} - \sum a_i$.
     - Sắp xếp các lệnh theo $r_i$ giảm dần (nếu $r_i$ bằng nhau, áp dụng tiêu chí phụ FIFO - lệnh nộp sớm hơn được ưu tiên).
     - Phân bổ thêm $1$ token cho $R$ lệnh đầu danh sách có $r_i$ lớn nhất.
- **Cơ sở kỹ thuật:**
  - Đảm bảo $\sum q_i^{\text{allocated}} \equiv Q_{\text{match\_pool}}$ tuyệt đối, không thiếu và không thừa dù chỉ 1 token.
  - Chống tình trạng "cá mập" chèn ép lệnh nhỏ: lệnh lớn nhận được khối lượng tương ứng, nhưng lệnh nhỏ nộp sớm vẫn được bảo vệ quyền lợi.

---

#### Quyết định 3: Quy tắc giá đồng nhất toàn phiên $k$-DA (`kda`)
- **Quy định chính thức:**
  - **Chính thức loại bỏ quy tắc khớp theo cặp (`pair`)** trong mã nguồn cũ.
  - Chuyển sang **quy tắc giá cân bằng duy nhất ($k$-DA Uniform Clearing Price)** cho toàn bộ các giao dịch thành công trong phiên:
    $$P^* = k \cdot b_M + (1 - k) \cdot s_M$$
    - Trong đó: $b_M$ là giá của lệnh mua biên cuối cùng được khớp; $s_M$ là giá của lệnh bán biên cuối cùng được khớp ($b_M \ge s_M$).
    - Tham số mặc định hệ thống: $k = 0.5$ (Mid-price uniform clearing):
      $$P^* = \frac{b_M + s_M}{2}$$
- **Cơ sở kỹ thuật:**
  - *Tính công bằng (Fairness & Non-discrimination):* Tất cả người mua và người bán thành công trong cùng một phiên đều được hưởng cùng một mức giá thanh toán duy nhất $P^*$.
  - *Tốc độ hội tụ hiệu quả cao:* Theo nghiên cứu giải tích của Rustichini, Satterthwaite & Williams (1994), quy tắc $k$-DA uniform price có tổn thất hiệu quả kinh tế tiêu giảm với tốc độ $O(1/m^2)$ (trong khi quy tắc pair chỉ đạt $O(1/m)$).
  - *Tiết kiệm gas on-chain:* Smart contract chỉ cần nhận một tham số `clearingPrice` cho toàn bộ lô lệnh thay vì phải lưu từng mức giá riêng lẻ cho từng cặp.

---

#### Quyết định 4: Giới hạn chuyển tiếp lệnh (Rollover Limit) cho lệnh GTC
- **Quy định chính thức:**
  - Thiết lập tham số cấu hình: **`MAX_ROLLOVER_SESSIONS` = 3 phiên** (có thể cấu hình tối đa đến 5 phiên tùy loại tài sản).
  - Trường dữ liệu mới trong cấu trúc quản lý lệnh nội bộ: `rollover_count: int` (khởi tạo bằng 0 khi lệnh ở trạng thái `NEW`).
  - **Quy tắc chuyển trạng thái khi kết thúc phiên:**
    - Nếu lệnh khớp $100\%$ khối lượng: Chuyển sang `FILLED`.
    - Nếu lệnh chưa khớp hết:
      - Tăng `rollover_count += 1`.
      - Nếu `rollover_count >= MAX_ROLLOVER_SESSIONS`: Tự động chuyển lệnh sang trạng thái **`EXPIRED`** và đẩy ra khỏi Sổ lệnh активных.
      - Nếu `rollover_count < MAX_ROLLOVER_SESSIONS`: Giữ lại phần dư `remaining_amount` trên sổ lệnh, chuyển trạng thái nội bộ thành **`ROLLED_OVER`**, kích hoạt lại trong phiên kế tiếp với độ tuổi được bảo lưu (giúp hưởng ưu tiên `age_prorata`).
    - Lệnh có cờ `time_in_force = IOC` (Immediate-Or-Cancel): Không áp dụng rollover, phần chưa khớp lập tức chuyển sang `CANCELLED`.
- **Cơ sở kỹ thuật:**
  - Tránh ô nhiễm bộ nhớ RAM và suy giảm hiệu năng sổ lệnh do các lệnh "rác" hoặc các lệnh đặt giá quá phi thực tế (stale orders) bị treo hàng tuần.
  - Bảo vệ nhà đầu tư khỏi rủi ro thị trường thay đổi đột ngột (market shift) khiến lệnh cũ bị khớp ở mức giá bất lợi ngoài ý muốn.

---

### 3. Phân công Nhiệm vụ Thực thi & Bàn giao (Action Items)

| Thành viên | Nhiệm vụ thực thi | File mã nguồn / Tài liệu phụ trách | Hạn chót |
| :--- | :--- | :--- | :--- |
| **Đặng Xuân Huy** | Cập nhật tài liệu đặc tả SRS IEEE 830; Vẽ lại sơ đồ UML State Machine & Sequence Diagram; Sửa đề cương học thuật Google Docs. | `docs/SRS_DOCUMENT.md`<br/>`docs/SYSTEM_ARCHITECTURE.md` | 15/11/2026 |
| **Nguyễn Bảo Phi** | Tích hợp thuật toán `kda`, `age_prorata` Hamilton và bộ đếm `rollover_count` vào `session_engine.py`; Đóng gói mock API FastAPI. | `system_agents/matching_engine/auction_agent.py`<br/>`system_agents/matching_engine/session_engine.py` | 20/11/2026 |
| **Nguyễn Hoàng Đức** | Cập nhật struct thanh toán on-chain nhận `clearingPrice` chung; triển khai kiểm tra `filledAmount` và `deadline`. | `contracts/CarbonDoubleAuction.sol`<br/>`test/CarbonAuction.test.ts` | 20/11/2026 |
| **Ngô Văn Thắng** | Cập nhật Frontend hiển thị đồng hồ đếm ngược phiên (5 phút / 15 phút); hiển thị trạng thái lệnh (`ROLLED_OVER`, `EXPIRED`). | `frontend/src/components/AuctionTimer.tsx`<br/>`frontend/src/components/OrderHistory.tsx` | 25/11/2026 |

---
*Tài liệu này là quyết định kỹ thuật ràng buộc có hiệu lực tức thì đối với toàn bộ thành viên nhóm nghiên cứu.*
