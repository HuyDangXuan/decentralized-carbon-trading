# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY 10/11/2026
## SPRINT ALIGNMENT, BAN HÀNH SRS CHUẨN IEEE 830 & ĐỒNG BỘ KIẾN TRÚC GIAI ĐOẠN 2

- **Ngày thực hiện:** 10/11/2026 (Thứ Ba)
- **Người chủ trì cập nhật:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Thành viên tham gia phối hợp:** Nguyễn Hoàng Đức, Nguyễn Bảo Phi, Ngô Văn Thắng
- **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh
- **Trạng thái nhánh Git:** Đã tích hợp hoàn chỉnh và đẩy lên `main` (Merge Pull Request #2)

---

## 1. MỤC TIÊU TRỌNG TÂM ĐÃ ĐẠT ĐƯỢC TRONG NGÀY
1. **Giải quyết dứt điểm tồn tại H2:** Chủ trì cuộc họp kỹ thuật Sprint Alignment, biểu quyết và khóa chính thức 4 thông số kiến trúc của Bộ khớp lệnh đấu giá kép định kỳ (PDA).
2. **Giải quyết dứt điểm tồn tại H1 & H5:** Sửa đổi câu chữ học thuật Nhiệm vụ 3 trên kế hoạch Giai đoạn 2 và Google Docs, loại bỏ sai lầm lý thuyết về "so sánh Welfare khi trung thực", thay bằng phân tích phân bổ thặng dư (Surplus Split) và tổn thất hiệu quả (Deadweight Loss) dưới Bayesian-Nash Equilibrium.
3. **Giải quyết dứt điểm tồn tại H3:** Biên soạn hồ sơ Đặc tả Yêu cầu Phần mềm (SRS) chuẩn quốc tế **IEEE Std 830-1998** và thiết kế 4 sơ đồ UML hoàn chỉnh (đặc biệt là State Machine vòng đời lệnh và Sequence Diagram luồng 3 bên).
4. **Đồng bộ hóa toàn bộ kho lưu trữ Git:** Rà soát lịch sử commit của 4 nhánh, kết hợp tài liệu `MATCHING_ENGINE_SPEC.md` từ nhánh algorithm, tạo nhánh riêng, khởi tạo PR #2 và hợp nhất an toàn vào `main`.

---

## 2. CHI TIẾT TỪNG THAY ĐỔI KỸ THUẬT (DÙ LÀ NHỎ NHẤT)

### 2.1 Các tệp tạo mới (New Files Created)

1. **`docs/SRS_DOCUMENT.md` (51 KB - Bản đặc tả chính thức):**
   - Tuân thủ cấu trúc chuẩn **IEEE Std 830-1998** gồm 7 chương: Giới thiệu, Mô tả tổng quan, Giao diện ngoại vi, 15 Yêu cầu chức năng (**FR-01 đến FR-15**), 11 Yêu cầu phi chức năng (**NFR-01 đến NFR-11**), và Bộ sơ đồ UML Mermaid.
   - **State Machine Diagram:** Bổ sung chu trình trạng thái lệnh đầy đủ: `NEW -> ACTIVE -> PARTIALLY_FILLED -> ROLLED_OVER -> EXPIRED / CANCELLED`.
   - **Sequence Diagram:** Luồng tương tác 3 bên chuẩn xác: `Trader ký EIP-712 -> REST API Matching Agent -> OrderBook -> Session Engine -> Settlement Submitter -> Smart Contract`.
   - **Use Case Diagram & Activity Diagram:** Toàn bộ tiến trình gom lệnh, khớp $k$-DA, phá hòa Hamilton và thanh quyết toán on-chain.

2. **`docs/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md` (10.7 KB - Quyết định kiến trúc):**
   - Biên bản cuộc họp Sprint Alignment ghi nhận biểu quyết của 4 thành viên khóa 4 thông số:
     - **Chu kỳ phiên:** 5 phút cho Testnet demo (Polygon Amoy) và 15 phút cho Thực tế (Mainnet/Pilot).
     - **Quy tắc phá hòa:** Áp dụng `age_prorata` kết hợp thuật toán phần dư lớn nhất Largest Remainder (Hamilton method), triệt tiêu hoàn toàn sai lệch làm tròn số nguyên token.
     - **Quy tắc giá:** Chuyển đổi dứt điểm sang quy tắc giá đồng nhất toàn phiên $k$-DA (`kda` uniform clearing price), xóa bỏ cơ chế khớp theo cặp (`pair`).
     - **Giới hạn rollover:** Lệnh GTC tự động chuyển sang `EXPIRED` sau tối đa 3 phiên liên tiếp để bảo vệ vốn nhà đầu tư.

3. **`docs/BAO_CAO_PHAN_TICH_LICH_SU_GIT_VA_VAN_DE_MATCHING_ENGINE.docx` (52 KB):**
   - Tài liệu Word phân tích chi tiết toàn bộ lịch sử commit trên repo, đối soát 15 vấn đề (Đ1 đến Đ15, H1 đến H6, T1 đến T3) và giải pháp hành động cụ thể cho từng thành viên.

4. **`system_agents/generate_git_and_matching_issues_docx.py` (56 KB):**
   - Script mã nguồn Python tự động sinh file Word báo cáo phân tích đối soát kỹ thuật.

5. **`docs/progress/README.md` & `docs/progress/2026-11-10/README.md`:**
   - Hệ thống theo dõi tiến độ và nhật ký kỹ thuật hàng ngày do Chủ nhiệm đề tài quản lý trực tiếp trên `main`.

6. **`scripts/log_daily_progress.py` (Script tự động hóa CLI):**
   - Công cụ dòng lệnh Python hỗ trợ quét Git changes, tự động tạo cấu trúc thư mục ngày, cập nhật dashboard và push lên `main` chỉ bằng 1 lệnh `python scripts/log_daily_progress.py --push`.

7. **`.gemini/skills/lead-architect-progress-logger/SKILL.md` (AI Sub-Agent độc quyền cho Huy):**
   - Kỹ năng AI ảo tự động hóa việc ghi nhận tiến độ, kiểm tra spec và đồng bộ tài liệu kiến trúc.

---

### 2.2 Các tệp chỉnh sửa (Modified Files)

1. **`docs/HUONG_DAN_SU_DUNG_SUB_AGENTS.md`:**
   - Bổ sung AI Sub-Agent thứ 7 `lead-architect-progress-logger` vào sơ đồ Mermaid, bảng phân công 2.1 và mẫu câu lệnh Prompt Mẫu 7.

2. **`docs/SYSTEM_ARCHITECTURE.md`:**
   - Cập nhật phiên bản 2.0: Tích hợp mô hình lai **Off-chain Intelligence (FastAPI MAS), On-chain Trust (Polygon Amoy)**.
   - Bổ sung 4 quyết định kiến trúc từ ADR-001.
   - Thêm sơ đồ Mermaid luồng 3 bên và máy trạng thái lệnh.
   - Chuẩn hóa đơn vị đo lường: `MockUSDC` (6 decimals - Micro-USDC, nghiêm cấm dùng `wei USDC`) và Tín chỉ ERC-1155 ($1 \text{ token} = 1 \text{ tCO}_2\text{e}$ với decimals = 0).

2. **`system_agents/generate_work_division_docx.py`:**
   - Sửa đổi dòng 169 (Bảng RACI mục 7): *"Viết script mô phỏng thực nghiệm: phân bổ thặng dư (Surplus Split) & tổn thất hiệu quả (Deadweight Loss)"*.
   - Sửa đổi dòng 253 (Nhiệm vụ 3 của Nguyễn Bảo Phi): Cập nhật 2 mục tiêu khoa học chuẩn tắc:
     - Đo lường phân bổ thặng dư kinh tế giữa bên mua ($\text{buyer\_share} = 1 - k$) và bên bán ($\text{seller\_share} = k$) khi khai giá trung thực.
     - Mô phỏng và đo lường tổn thất hiệu quả (Deadweight Loss) dưới Bayesian-Nash Equilibrium trên các quy mô thị trường $m$ khác nhau theo lý thuyết Rustichini et al. (1994).

3. **`docs/KE_HOACH_PHAN_CHIA_CONG_VIEC_GIAI_DOAN_2.docx`:**
   - Chạy lại script Python để xuất file Word kế hoạch Giai đoạn 2 mới nhất chứa toàn bộ nội dung học thuật đã chỉnh sửa.

---

### 2.3 Thay đổi về Lý thuyết & Học thuật (Theoretical & Mathematical Refinements)
- **Khắc phục lỗi ngụy biện về Welfare:** Làm rõ theo định lý Myerson-Satterthwaite (1983): Khi các bên trung thực, tổng thặng dư xã hội $W = \sum (v_b - v_s)$ hoàn toàn độc lập với mức giá khớp $P^*$. Mọi $k \in [0, 1]$ đều đem lại cùng mức Welfare tối đa $100\%$. Tham số $k$ chỉ có vai trò phân chia tỷ lệ thặng dư giữa người mua và người bán.
- **Xác lập mô hình tổn thất hiệu quả:** Tổn thất chỉ xuất hiện khi người chơi hành vi chiến lược (Strategic Bidding). Tốc độ tiêu giảm tổn thất của quy tắc giá phiên $k$-DA đạt $O(1/m^2)$, vượt trội so với quy tắc khớp cặp $O(1/m)$.
- **Thuật toán Hamilton (Largest Remainder):** Áp dụng công thức phần nguyên sàn $a_i = \lfloor q_i^{\text{ideal}} \rfloor$, phần dư $r_i = q_i^{\text{ideal}} - a_i$, và phân bổ $R = Q_{\text{pool}} - \sum a_i$ token còn lại cho các lệnh có $r_i$ lớn nhất.

---

### 2.4 Thay đổi về Giao diện & Kiến trúc Hệ thống (Architectural & Interface Changes)
- **Chuẩn hóa chữ ký EIP-712 Gasless:** Người dùng đặt lệnh chỉ cần ký cấu trúc dữ liệu trên ví MetaMask, không mất gas on-chain.
- **7 Chốt chặn bảo mật bắt buộc trong Smart Contract (`CarbonDoubleAuction.sol`):**
  1. Xác thực chữ ký EIP-712 cả 2 bên.
  2. Kiểm tra `block.timestamp <= deadline`.
  3. Cùng `tokenId`, đúng loại lệnh, khác địa chỉ ví (chống wash trading).
  4. Mức giá khớp $P^*$ nằm trong dải $[P_{\text{ask}}, P_{\text{bid}}]$.
  5. Hạn mức lũy kế $\text{filledAmount} + \text{matchAmount} \le \text{amount}$ cho cả 2 bên.
  6. Chưa bị hủy (`!cancelledOrders`).
  7. Chống nộp trùng (`!executedTrades[tradeHash]`).
- **Thanh toán theo lô (Batch Settlement):** Gom 10 - 20 cặp lệnh vào một giao dịch gọi hàm `batchSettleTrades`, giảm hơn 60% chi phí gas so với thanh toán lẻ.

---

## 3. TÁC ĐỘNG TỚI TỪNG THÀNH VIÊN VÀ NHIỆM VỤ TIẾP THEO

### 3.1 Đối với Nguyễn Hoàng Đức (Smart Contract Engineer)
- **Tác động:** Không tự thiết kế tùy tiện storage layout và logic settlement nữa; bám sát 100% tài liệu `docs/SRS_DOCUMENT.md` mục **FR-11, FR-12**.
- **Nhiệm vụ cần thực hiện:**
  1. Viết code Solidity v2 cho `CarbonDoubleAuction.sol` và `CarbonCredit1155.sol` trên nhánh `docs/smart-contract-spec`.
  2. Bổ sung đầy đủ 7 chốt chặn bảo mật trong hàm `batchSettleTrades`.
  3. Viết bộ kiểm thử Hardhat/Foundry đo lượng gas thực tế ($< 100k$ gas/lệnh).
  4. Xuất file ABI chuẩn (chứa đúng kiểu dữ liệu Micro-USDC và uint128) bàn giao cho Thắng.
- **Hạn chót:** 20/11/2026.

### 3.2 Đối với Nguyễn Bảo Phi (Auction Algorithm Engineer)
- **Tác động:** Toàn bộ các nghi vấn kỹ thuật Phi nêu ra trong tài liệu đối soát đã được Chủ nhiệm đề tài giải quyết và đưa vào tài liệu kiến trúc chính thức.
- **Nhiệm vụ cần thực hiện:**
  1. Thay thế mã nguồn cũ `system_agents/matching_engine/auction_agent.py` bằng logic của `session_engine.py` (kích hoạt mặc định $k$-DA và Hamilton tie-breaking theo **FR-07, FR-08**).
  2. Dựng Mock API Service bằng FastAPI theo đặc tả **FR-15** (`POST /api/v1/orders`, `DELETE /api/v1/orders/{id}`, `GET /api/v1/orderbook/{tokenId}`, `POST /api/v1/sessions/run`).
  3. Mở rộng thực nghiệm toán học đo lường Surplus Split và Deadweight Loss với $m > 16$ theo câu chữ mới của Nhiệm vụ 3.
- **Hạn chót:** 25/11/2026.

### 3.3 Đối với Ngô Văn Thắng (Web3 Frontend Engineer)
- **Tác động:** Giao diện DApp chuyển hướng sang tương tác với API Service của Phi thay vì tương tác trực tiếp on-chain khi đặt lệnh; hiển thị chu kỳ phiên đấu giá.
- **Nhiệm vụ cần thực hiện:**
  1. Cập nhật file `docs/METADATA_SCHEMA.json` bổ sung các trường phân khúc tín chỉ (Vintage, Project Class, Buffer Rate) và chuẩn hóa decimals = 0 (tCO2e).
  2. Hoàn thiện Wireframe Figma 4 phân hệ DApp theo hạn nộp 20/11/2026.
  3. Bổ sung vào giao diện Trading Floor: Đồng hồ đếm ngược phiên đấu giá (5 phút trên Testnet / 15 phút trên Mainnet) và bảng lịch sử hiển thị trạng thái lệnh (`ROLLED_OVER`, `EXPIRED`).
- **Hạn chót:** 30/11/2026.

---

## 4. GHI CHÚ BẢN COMMIT VÀ TRẠNG THÁI GIT

- **Nhánh phát triển:** `feature/huy-lead-architect-srs-uml` $\to$ đã hợp nhất vào `main`.
- **Commit chính:**
  - `d518cfa`: `feat(lead-architect): add SRS IEEE 830, ADR-001, updated system architecture and Phase 2 alignment`
  - `591b50c`: `Merge remote-tracking branch 'origin/main' into feature/huy-lead-architect-srs-uml`
  - `304675e`: `Merge pull request #2 from HuyDangXuan/feature/huy-lead-architect-srs-uml`
- **Trạng thái nhánh `main`:** Đồng bộ tuyệt đối với remote `origin/main`, cây commit sạch, không có xung đột.

---
*Bản ghi nhật ký này được lưu trữ vĩnh viễn trên nhánh main của repository và phục vụ công tác nghiệm thu NCKH.*
