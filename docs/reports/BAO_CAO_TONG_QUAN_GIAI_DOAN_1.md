# BÁO CÁO TỔNG QUAN VÀ THIẾT KẾ ĐỊNH HƯỚNG ĐỀ TÀI (GIAI ĐOẠN 1)

**ĐỀ TÀI:** HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON MINH BẠCH VÀ HIỆU QUẢ TRÊN NỀN TẢNG BLOCKCHAIN  
**Đơn vị:** Khoa Điện toán và Công nghệ số năng lượng – Trường Đại học Điện Lực  
**Chủ nhiệm đề tài:** Đặng Xuân Huy (MSV: 23810310007 – D18CNPM1)  
**Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh  
**Thành viên tham gia:** Ngô Văn Thắng, Nguyễn Hoàng Đức, Nguyễn Bảo Phi  
**Thời gian thực hiện Giai đoạn 1:** 10/2026 – 11/2026  

---

## MỤC LỤC TỔNG QUAN
1. [PHẦN 1: BÀI TOÁN NGHIÊN CỨU VÀ PHẠM VI ĐỀ TÀI (SCOPE)](#phần-1-bài-toán-nghiên-cứu-và-phạm-vi-đề-tài)
2. [PHẦN 2: TỔNG QUAN NGHIỆP VỤ THỊ TRƯỜNG CARBON VÀ VÒNG ĐỜI TÍN CHỈ](#phần-2-tổng-quan-nghiệp-vụ-thị-trường-carbon-và-vòng-đời-tín-chỉ)
3. [PHẦN 3: KHẢO SÁT VÀ ĐỀ XUẤT NỀN TẢNG BLOCKCHAIN, CHUẨN TOKEN VÀ LƯU TRỮ PHI TẬP TRUNG](#phần-3-khảo-sát-và-đề-xuất-nền-tảng-blockchain-chuẩn-token-và-lưu-trữ-phi-tập-trung)
4. [PHẦN 4: NGHIÊN CỨU CƠ CHẾ ĐẤU GIÁ KÉP (DOUBLE AUCTION) VÀ MÔ HÌNH XÁC ĐỊNH GIÁ](#phần-4-nghiên-cứu-cơ-chế-đấu-giá-kép-double-auction-và-mô-hình-xác-định-giá)
5. [PHẦN 5: KIẾN TRÚC TỔNG QUAN HỆ THỐNG (SYSTEM ARCHITECTURE OVERVIEW)](#phần-5-kiến-trúc-tổng-quan-hệ-thống)
6. [PHẦN 6: KẾT LUẬN GIAI ĐOẠN 1 VÀ KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN 2](#phần-6-kết-luận-giai-đoạn-1-và-kế-hoạch-triển-khai-giai-đoạn-2)

---

## PHẦN 1: BÀI TOÁN NGHIÊN CỨU VÀ PHẠM VI ĐỀ TÀI

### 1.1. Bối cảnh và Đặt vấn đề
Thị trường carbon tự nguyện (Voluntary Carbon Market – VCM) đang trở thành một trụ cột tài chính khí hậu toàn cầu, đóng vai trò then chốt trong nỗ lực đạt mục tiêu Phát thải ròng bằng không (Net Zero) vào năm 2050 theo Thỏa thuận Paris. Tuy nhiên, thị trường truyền thống đang bộc lộ những rào cản nghiêm trọng:
1. **Thiếu minh bạch và rủi ro gian lận (Double Spending / Double Counting):** Các sổ đăng ký tín chỉ hoạt động như những ốc đảo dữ liệu tập trung, dẫn đến nguy cơ một tín chỉ bị bán cho nhiều người hoặc được tính trùng vào cả cam kết quốc gia lẫn cam kết doanh nghiệp.
2. **Kém hiệu quả định giá và phân mảnh thanh khoản:** Đa phần giao dịch carbon hiện nay diễn ra qua phương thức thỏa thuận song phương (OTC) kín, chi phí hoa hồng môi giới cao (chiếm 15% – 30%), gây bất đối xứng thông tin nghiêm trọng.
3. **Quy trình thẩm định và lưu ký chậm chạp:** Thời gian hoàn tất bù trừ và chuyển đổi chủ sở hữu thường kéo dài từ vài ngày đến vài tuần.

Để giải quyết bài toán trên, đề tài đề xuất **Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain**, kết hợp giữa hợp đồng thông minh đa tài sản (ERC-1155), lưu trữ phi tập trung (IPFS), cơ chế Đấu giá kép tự động (Double Auction) và Hệ Đa Tác Tử (Multi-Agent System – MAS).

### 1.2. Xác định Phạm vi Đề tài (Scope of the Project)
Để đảm bảo tính khả thi cao trong thời gian nghiên cứu 06 tháng (10/2026 – 05/2027) của cấp đề tài NCKH sinh viên, phạm vi nghiên cứu được xác định rõ ràng trên 4 trục:

#### A. Phạm vi Nghiệp vụ và Loại hình Tín chỉ (Business & Asset Scope)
* **Đối tượng giao dịch:** Tín chỉ carbon thuộc thị trường tự nguyện (VCM), quy chuẩn 1 tín chỉ tương đương **1 tấn $CO_2$ quy đổi ($1\ \text{tCO}_2\text{e}$)**.
* **Chuẩn hóa phân loại:** Hệ thống hỗ trợ token hóa các tín chỉ phát sinh từ các loại hình dự án tiêu biểu tại Việt Nam:
  * Dự án lâm nghiệp và sử dụng đất (AFOLU / Trồng và bảo vệ rừng).
  * Dự án năng lượng tái tạo (Điện mặt trời, điện gió, thủy điện nhỏ).
  * Dự án tiết kiệm năng lượng công nghiệp và xử lý sinh khối.
* **Tiêu chuẩn tham chiếu:** Mô hình hóa các quy chuẩn thẩm định của **Verra (VCS)**, **Gold Standard (GS4GG)** và **Cơ chế Phát triển Sạch (CDM)** để thiết kế cấu trúc dữ liệu hồ sơ dự án.

#### B. Phạm vi Thị trường và Người tham gia (Market & Participant Scope)
* **Mô hình thị trường:** Mô phỏng thị trường carbon tự nguyện cho các doanh nghiệp và dự án tại Việt Nam theo định hướng lộ trình của Chính phủ (Nghị định 06/2022/NĐ-CP, Nghị định 119/2025/NĐ-CP và Quyết định 232/QĐ-TTg).
* **Các tác nhân tham gia:** 
  1. Chủ dự án giảm phát thải (Project Developers – Bên bán).
  2. Doanh nghiệp có nhu cầu bù trừ phát thải / thực hiện báo cáo ESG (End-Buyers – Bên mua).
  3. Đơn vị thẩm tra độc lập (Validation & Verification Bodies – VVB).
  4. Quản trị viên sổ đăng ký hệ thống (Registry Admin / Issuer).

#### C. Phạm vi Công nghệ và Kỹ thuật (Technical Scope)
* **Tầng Blockchain:** Triển khai trên mạng thử nghiệm tương thích EVM **Polygon Amoy Testnet** (thay thế cho Polygon Mumbai đã ngừng hoạt động), tận dụng phí giao dịch siêu thấp (<$0.01) và tốc độ giao dịch cao (~2-3s block time).
* **Chuẩn Token:** Chuẩn **ERC-1155 (Multi-Token Standard)** – quản lý bán phần (Semi-Fungible Tokens). Mỗi Token ID đại diện cho một đợt phát hành (Project ID + Vintage Year), cho phép giao dịch khối lượng lẻ và hỗ trợ chuyển nhượng hàng loạt (*safeBatchTransferFrom*) để tối ưu gas.
* **Lưu trữ ngoài chuỗi (Off-chain Storage):** Mạng **IPFS** kết hợp dịch vụ **Pinata** để ghim hồ sơ PDD, báo cáo MRV và chứng nhận phát thải dạng JSON/PDF, lưu trữ chuỗi băm nội dung (CID) bất biến vào Smart Contract.
* **Cơ chế thị trường:** Cơ chế **Đấu giá kép định kỳ (Periodic Double Auction)** với thuật toán xác định giá trung bình cân bằng thị trường (*$k$-Double Auction Rule* với $k=0.5$ Mid-price).
* **Kiến trúc thực thi:** Mô hình **Lai (Hybrid Architecture – Off-chain Matching, On-chain Settlement)**. Khớp lệnh và tính toán giá diễn ra ngoài chuỗi qua tác tử Auction Agent để tránh nghẽn mạng và tiết kiệm chi phí gas; kết quả khớp lệnh được đưa lên Smart Contract để thanh quyết toán nguyên tử (*Atomic Swap*).

#### D. Giới hạn Nghiên cứu (Research Delimitations)
* Đề tài **không** xây dựng thiết bị IoT đo đạc phát thải vật lý tại hiện trường; dữ liệu đo đạc MRV được chuẩn hóa thành tệp báo cáo số hóa mô phỏng.
* Đề tài **không** can thiệp vào thị trường carbon bắt buộc (ETS) của Nhà nước mà đóng vai trò là giải pháp công nghệ bổ trợ cho thị trường tự nguyện và sàn giao dịch thí điểm.
* Giao dịch tiền tệ thanh toán được mô phỏng thông qua đơn vị tiền mã hóa ổn định (Test ERC-20 Stablecoin / Native Token Testnet) trong khuôn khổ môi trường thử nghiệm.

---

## PHẦN 2: TỔNG QUAN NGHIỆP VỤ THỊ TRƯỜNG CARBON VÀ VÒNG ĐỜI TÍN CHỈ
*(Tổng hợp từ Báo cáo Chuyên đề của Thành viên Ngô Văn Thắng)*

### 2.1. Bản chất Thị trường Carbon Tự nguyện (VCM) và Lộ trình tại Việt Nam
* **Phân biệt CCM và VCM:** Trong khi Thị trường Bắt buộc (Compliance Carbon Market – CCM) vận hành theo cơ chế "Giới hạn và Giao dịch" (Cap-and-Trade) do Nhà nước áp đặt hạn ngạch, thì Thị trường Tự nguyện (VCM) vận hành theo cơ chế "Đường cơ sở và Tín chỉ" (Baseline-and-Credit), phục vụ doanh nghiệp có nhu cầu tự nguyện trung hòa carbon vì mục tiêu ESG, xuất khẩu và thương hiệu.
* **Lộ trình tại Việt Nam:** Được thể chế hóa qua Luật BVMT 2020 (Điều 139), Nghị định 06/2022/NĐ-CP (sửa đổi tại Nghị định 119/2025/NĐ-CP) và Quyết định 232/QĐ-TTg. Việt Nam đang trong giai đoạn triển khai thí điểm Sàn giao dịch carbon (HNX và VSDC phối hợp) từ giữa năm 2025 đến 2028, trước khi tiến tới vận hành chính thức toàn diện từ năm 2029.

### 2.2. So sánh Đối chiếu các Tiêu chuẩn Tín chỉ Quốc tế Uy tín

| Tiêu chí so sánh | Verra (VCS) | Gold Standard (GS4GG) | Cơ chế CDM (UNFCCC) |
| :--- | :--- | :--- | :--- |
| **Cơ quan quản lý** | Tổ chức phi lợi nhuận Verra (Mỹ) | Gold Standard Foundation (Thụy Sĩ) | Ban Chấp hành CDM thuộc LHQ |
| **Đơn vị tín chỉ** | VCU (Verified Carbon Unit) | GS VER (Verified Emission Reduction) | CER (Certified Emission Reduction) |
| **Đơn vị kiểm toán** | VVB độc lập | VVB phối hợp SustainCert | DOE do LHQ chỉ định |
| **Yêu cầu đồng lợi ích** | Khuyến khích (nhãn CCB, SD VISta) | **Bắt buộc** đóng góp $\ge 3$ mục tiêu UN SDGs | Tiêu chuẩn phát triển bền vững nước sở tại |
| **Lĩnh vực mũi nhọn** | Lâm nghiệp REDD+, AFOLU, công nghiệp | Năng lượng sạch, nước sạch, cộng đồng | Năng lượng tái tạo, xử lý rác, sinh khối |
| **Tính ứng dụng cho đề tài** | Chuẩn hóa cấu trúc Metadata dự án | Cấu trúc thuộc tính đồng lợi ích (Co-benefits) | Nguồn phương pháp luận tính toán Baseline |

### 2.3. Mô hình hóa 5 Giai đoạn Vòng đời Tín chỉ Carbon (End-to-End Lifecycle)
Vòng đời của tín chỉ được hệ thống hóa thành quy trình khép kín:
$$\text{Đăng ký (Registration)} \longrightarrow \text{Thẩm tra (V&V)} \longrightarrow \text{Phát hành (Issuance)} \longrightarrow \text{Giao dịch (Trading)} \longrightarrow \text{Hủy / Bù đắp (Retirement)}$$

1. **Giai đoạn 1 – Thiết kế & Đăng ký (Registration):** Chủ dự án lập Hồ sơ thiết kế (PDD), tính toán phát thải đường cơ sở và đưa lên danh mục thẩm định.
2. **Giai đoạn 2 – Thẩm tra & Xác minh (Validation & Verification):** Tổ chức độc lập (VVB) thẩm tra hồ sơ thiết kế, sau đó định kỳ kiểm toán số liệu giảm phát thải thực địa để ban hành Chứng thư xác minh.
3. **Giai đoạn 3 – Phê duyệt Cấp phát (Issuance):** Cơ quan quản lý rà soát báo cáo VVB, trích lập tỷ lệ dự phòng rủi ro (Buffer Pool, thường từ 10% đến 20% cho dự án rừng) và cấp phát tín chỉ gắn số sê-ri định danh.
4. **Giai đoạn 4 – Giao dịch Đấu giá kép (Trading):** Tín chỉ được đưa lên sàn đấu giá. Người mua và người bán gửi lệnh chào mua/chào bán để khớp lệnh tại mức giá thanh toán công bằng (*Clearing Price*).
5. **Giai đoạn 5 – Tiêu hủy Bù đắp (Retirement / Burning):** Khi người mua dùng tín chỉ để bù trừ phát thải khí nhà kính, tín chỉ sẽ bị khóa vĩnh viễn trên chuỗi (gọi hàm `_burn()`), sinh chứng chỉ bù đắp ESG bất biến có mã băm chứng thực.

### 2.4. Khắc phục 4 Điểm nghẽn của Thị trường Truyền thống bằng Blockchain

| Điểm nghẽn truyền thống | Bản chất hạn chế | Giải pháp kỹ thuật của Hệ thống đề xuất |
| :--- | :--- | :--- |
| **Trùng lặp tín chỉ (Double Spending/Counting)** | Sổ đăng ký phân mảnh, giao dịch ngầm OTC dẫn đến 1 tín chỉ bán cho nhiều bên hoặc bị kê khai hai lần. | Token hóa bằng chuẩn **ERC-1155**; cơ chế đồng thuận Blockchain triệt tiêu double-spending; hàm `retireCarbonCredit` thực thi đốt token vĩnh viễn khỏi tổng cung. |
| **Thiếu minh bạch & Nguy cơ "Tẩy xanh"** | Người mua không tiếp cận được hồ sơ gốc PDD, biên bản thẩm định VVB; cơ sở dữ liệu đóng dễ bị sửa đổi ngầm. | Toàn bộ hồ sơ PDD, ảnh viễn thám, chứng chỉ VVB được lưu trữ trên **IPFS**, tạo mã băm nội dung (CID) gán trực tiếp vào token URI on-chain. |
| **Định giá kém & Phân mảnh thanh khoản** | Giao dịch thỏa thuận riêng lẻ che giấu giá thực, thông tin bất đối xứng, thanh khoản thấp. | Áp dụng **Cơ chế Đấu giá kép (Double Auction)** gom sổ lệnh, khớp lệnh tự động và công khai giá thanh toán cân bằng thị trường (*Clearing Price*). |
| **Chi phí trung gian cao & Đối soát chậm** | Phí môi giới chiếm 15% – 30%; chu kỳ thanh toán bù trừ mất T+3 đến T+14 ngày. | Hợp đồng thông minh đóng vai trò ký quỹ tự động (**Escrow**) và thanh toán tức thì (**Atomic Settlement - T+0**) với chi phí gas cực thấp. |

---

## PHẦN 3: KHẢO SÁT VÀ ĐỀ XUẤT NỀN TẢNG BLOCKCHAIN, CHUẨN TOKEN VÀ LƯU TRỮ PHI TẬP TRUNG
*(Tổng hợp từ Báo cáo Chuyên đề của Thành viên Nguyễn Hoàng Đức)*

### 3.1. Phân tích Ma trận Đánh đổi (Trade-off Matrix) và Đề xuất Blockchain
Hệ thống giao dịch carbon đòi hỏi tần suất giao dịch cao (đăng ký, nộp lệnh bid/ask, khớp lệnh, chuyển nhượng và hủy). Việc lựa chọn nền tảng cần thỏa mãn 4 tiêu chí: Phí gas thấp, Tốc độ TPS/Finality nhanh, Môi trường Testnet ổn định và Tính tương thích với hệ sinh thái Tài chính Tái tạo (ReFi).

| Tiêu chí | Ethereum Sepolia | Polygon Amoy (Đề xuất) | Arbitrum Sepolia | Solana Devnet |
| :--- | :--- | :--- | :--- | :--- |
| **Phí Gas thực tế** | Rất cao ($2 – $30+) | **Cực thấp (< $0.01)** | Rất thấp ($0.02 – $0.1) | Cực thấp (< $0.001) |
| **Thông lượng (TPS) & Finality** | ~15 TPS (Finality 12–15 phút) | **~7,000 TPS lý thuyết (Finality 2–3s)** | ~40,000 TPS (< 1s) | ~65,000 TPS (~400ms) |
| **Hệ sinh thái Tooling EVM** | Chuẩn mực nhất (Hardhat/Foundry) | **Hoàn toàn tương thích EVM** | Hoàn toàn tương thích EVM | Riêng biệt (Rust/Anchor) |
| **Hệ sinh thái ReFi thực tế** | Chi phí quá cao cho giao dịch lẻ | **Dẫn đầu toàn cầu (Toucan, KlimaDAO)**| Đang mở rộng | Phát triển mảng DePIN |
| **Đánh giá lựa chọn** | Phù hợp test logic đơn thuần | **LỰA CHỌN TỐI ƯU SỐ 1** | Phương án dự phòng Rollup | Rào cản chuyển đổi chuẩn ERC |

> **Kết luận đề xuất:** Nhóm thống nhất lựa chọn mạng **Polygon Amoy Testnet**. Đây là giải pháp Layer 2/Sidechain tối ưu hóa chi phí vận hành, đồng thời bám sát thực tiễn công nghệ của các dự án ReFi hàng đầu thế giới.

### 3.2. Luận cứ Lựa chọn Chuẩn Token ERC-1155 (Multi-Token Standard)
Trong thị trường carbon, mỗi lô tín chỉ mang tính chất **Bán phần (Semi-Fungible)**:
* Các tín chỉ trong **cùng một lô** (cùng Dự án, cùng Niên độ phát hành - Vintage Year) là hoàn toàn đồng nhất và thay thế được cho nhau.
* Các tín chỉ thuộc **hai lô khác nhau** (ví dụ: Tín chỉ Rừng 2026 vs. Tín chỉ Điện mặt trời 2024) có chất lượng, phương pháp luận và mức giá định giá khác nhau nên không thể gộp chung.

**So sánh các chuẩn token:**
1. **ERC-20 (Fungible):** Thất bại trong việc thể hiện thuộc tính riêng biệt (Metadata, Vintage, Project ID) nếu chỉ dùng một hợp đồng; nếu triển khai mỗi lô một hợp đồng ERC-20 thì chi phí quản lý và deploy cực kỳ tốn kém.
2. **ERC-721 (Non-Fungible):** Mỗi token là duy nhất. Phù hợp cho chứng chỉ độc bản, nhưng khi giao dịch khối lượng lớn (ví dụ: mua 500 tín chỉ), ERC-721 phải duyệt qua 500 ID riêng biệt, gây bùng nổ chi phí gas.
3. **ERC-1155 (Đề xuất số 1):** 
   * Cho phép quản lý đồng thời vô số loại token trong cùng **một hợp đồng thông minh duy nhất**.
   * Mỗi `tokenId` đại diện cho một lô tín chỉ cụ thể: $\text{tokenId} = \text{uint256}(\text{keccak256}(\text{projectId, vintageYear}))$.
   * Số dư `balanceOf(user, tokenId)` đại diện cho số tấn $CO_2e$ sở hữu, hỗ trợ phân chia nhỏ linh hoạt.
   * Tính năng `safeBatchTransferFrom` cho phép chuyển nhượng nhiều loại tín chỉ trong một giao dịch duy nhất, tiết kiệm tối đa phí gas.

### 3.3. Giải pháp Lưu trữ Phi tập trung IPFS kết hợp Pinata
* **Tại sao không lưu on-chain?** Hồ sơ thiết kế (PDD), báo cáo kiểm kê MRV, ảnh viễn thám và chứng thư kiểm toán có dung lượng hàng chục Megabyte. Lưu trữ trên EVM sẽ tiêu tốn hàng nghìn USD tiền gas và gây phình to sổ cái (State Bloat).
* **Tại sao không lưu trên máy chủ tập trung (Cloud AWS/Google)?** Dễ gặp rủi ro máy chủ ngừng hoạt động (Single Point of Failure) hoặc dữ liệu bị chỉnh sửa ngầm, làm mất tính toàn vẹn.
* **Mô hình kiến trúc IPFS đề xuất:**
  * Toàn bộ tệp PDD và metadata JSON được đẩy lên mạng IPFS.
  * Mạng IPFS sinh chuỗi mã băm định danh nội dung bất biến **CID (Content Identifier)**. Nếu tệp tin bị thay đổi dù chỉ một bit, mã CID sẽ thay đổi hoàn toàn.
  * Chuỗi CID được lưu trực tiếp vào Smart Contract thông qua hàm `uri(tokenId)`.
  * Nhóm sử dụng dịch vụ **Pinata Pinning Service** để đảm bảo dữ liệu luôn được ghim cố định 24/7 trên các IPFS gateway chuyên dụng với tốc độ truy xuất CDN cao.

---

## PHẦN 4: NGHIÊN CỨU CƠ CHẾ ĐẤU GIÁ KÉP (DOUBLE AUCTION) VÀ MÔ HÌNH XÁC ĐỊNH GIÁ
*(Tổng hợp từ Báo cáo Chuyên đề của Thành viên Nguyễn Bảo Phi)*

### 4.1. Cơ sở Lý thuyết Đấu giá kép: Phân biệt 3 Quyết định Cốt lõi
Nghiên cứu chỉ ra rằng một cơ chế Đấu giá kép (Double Auction) hoàn chỉnh cần giải quyết đồng thời 3 quyết định độc lập:
1. **Thời điểm gom/xử lý lệnh:**
   * *Đấu giá liên tục (Continuous Double Auction - CDA):* Khớp lệnh ngay khi có lệnh đối ứng xuất hiện trong sổ lệnh. Phù hợp thị trường thanh khoản cực lớn nhưng dễ bị tấn công chạy trước lệnh (Front-running / MEV).
   * *Đấu giá theo phiên (Periodic / Frequent Batch Auction):* Gom toàn bộ lệnh hợp lệ trong một khoảng thời gian $\Delta t$ (cutoff snapshot), sau đó giải bài toán khớp lệnh đồng thời. Phương thức này triệt tiêu ưu thế cạnh tranh tốc độ của bot và giảm thiểu rủi ro front-running (theo nghiên cứu của Budish et al., 2015).
2. **Quy tắc phân bổ (Allocation / Matching):** Xác định lệnh mua nào được ghép với lệnh bán nào và khối lượng ghép là bao nhiêu.
3. **Quy tắc thanh toán (Payment / Pricing):** Xác định mức giá thanh toán cho mỗi đơn vị giao dịch.

### 4.2. Khảo sát các Công trình Học thuật Nền tảng và Nghiên cứu VCM

* **Smith (1962):** Nghiên cứu thực nghiệm kinh tế vi mô đầu tiên chứng minh cơ chế đấu giá hai phía nhanh chóng tiệm cận trạng thái cân bằng cạnh tranh hoàn hảo ngay cả khi người tham gia chỉ có thông tin cục bộ.
* **Budish, Cramton và Shim (2015):** Chứng minh cơ chế Đấu giá theo phiên rời rạc (Frequent Batch Auction) với một mức giá thanh toán chung vượt trội hơn CDA trong việc chống lại hành vi trục lợi chênh lệch tốc độ và rủi ro trượt giá.
* **McAfee (1992):** Thiết kế cơ chế đấu giá kép có chiến lược chi phối (Dominant Strategy Incentive Compatible - DSIC). McAfee chỉ ra rằng để đảm bảo người tham gia khai báo trung thực (Truthful Bidding) và không thâm hụt ngân sách, cơ chế có thể phải chấp nhận loại bỏ giao dịch biên thứ $k$ (đánh đổi giữa hiệu quả khối lượng và động cơ khai báo).
* **Segal-Halevi, Hassidim và Aumann (2018 - MUDA):** Mở rộng đấu giá kép cho bài toán nhiều đơn vị (Multi-unit) với hàm lợi ích biên giảm dần, chứng minh hai biến thể Lottery-MUDA (cân bằng ngân sách mạnh) và Vickrey-MUDA.
* **Liu và cộng sự (2026 - Applied Energy):** Nghiên cứu mới nhất ứng dụng Đấu giá kép tuần tự (Sequential Double Auction) trên nền tảng Hyperledger Fabric cho thị trường carbon tự nguyện tại Hoa Kỳ, chứng minh việc gom nhóm tín chỉ đồng nhất và đấu giá kép giúp tăng thanh khoản và giảm chi phí giao dịch đáng kể.

### 4.3. Giải thuật Khớp lệnh Hai Con Trỏ và Xác định Giá Thanh toán
Nhóm nghiên cứu thiết kế giải thuật khớp lệnh tham lam hai con trỏ tối ưu cho đợt đấu giá theo phiên:

```text
THUẬT TOÁN KHỚP LỆNH HAI CON TRỎ (GREEDY TWO-POINTER MATCHING):
1. Sắp xếp danh sách lệnh Mua (Bids) theo giá giảm dần:  P_bid[1] >= P_bid[2] >= ... >= P_bid[n]
2. Sắp xếp danh sách lệnh Bán (Asks) theo giá tăng dần: P_ask[1] <= P_ask[2] <= ... <= P_ask[m]
3. Khởi tạo con trỏ: i = 0 (phía mua), j = 0 (phía bán)
4. Lặp khi i < n và j < m:
     a. Nếu P_bid[i] < P_ask[j]: Dừng vòng lặp (Cung và Cầu không còn gặp nhau).
     b. Lượng khớp: q = min(remaining_bid[i], remaining_ask[j])
     c. Ghi nhận cặp khớp (Bid[i], Ask[j], q)
     d. Cập nhật lượng còn lại. Nếu lệnh nào hết lượng thì tăng con trỏ tương ứng.
Độ phức tạp: O(n log n + m log m) cho sắp xếp; O(n + m) cho quá trình duyệt khớp.
```

**Mô hình Xác định Giá Thanh toán ($k$-Double Auction Rule):**  
Giá thanh toán cho mỗi cặp khớp lệnh được tính theo công thức tổ hợp trọng số:
$$P^* = (1 - \alpha) \cdot P_{ask} + \alpha \cdot P_{bid} \quad \text{với } 0 \le \alpha \le 1$$
* Khi $\alpha = 0.5$ (**Mid-Price Rule**): Mức giá là trung điểm công bằng giữa giá chào mua và chào bán, chia đều thặng dư kinh tế cho cả hai phía thị trường.
* Trong trường hợp phiên đấu giá áp dụng mức giá đồng nhất (**Uniform Clearing Price**), hệ thống lấy trung điểm của khoảng giá cân bằng thị trường tại điểm giao nhau giữa đường cung và cầu: $P^* = \frac{P_{bid, k} + P_{ask, k}}{2}$, đảm bảo mọi lệnh thắng trong phiên đều thanh toán cùng một mức giá.

### 4.4. Đánh giá Khả thi Kỹ thuật: Lựa chọn Mô hình Lai (Hybrid Architecture)

Nhóm đã đối chiếu sâu sắc giữa hai mô hình triển khai:
1. **Mô hình Thuần On-chain (Full On-chain Matching):** Toàn bộ việc lưu sổ lệnh, sắp xếp và khớp lệnh chạy trong Smart Contract. 
   * *Hạn chế:* Thao tác sắp xếp mảng trong EVM tiêu tốn lượng gas khổng lồ; nếu số lượng lệnh lớn có thể vượt giới hạn Gas Limit của Block, dẫn đến nghẽn mạng và rủi ro bị khai thác MEV/Front-running.
2. **Mô hình Lai (Hybrid – Off-chain Matching, On-chain Settlement - Đề xuất của Nhóm):**
   * Người dùng ký số vào lệnh giao dịch (chuẩn EIP-712).
   * Tác tử **Auction Matching Agent** gom sổ lệnh và chạy giải thuật tối ưu ngoài chuỗi (Off-chain).
   * Sau khi chốt phiên, tác tử gửi danh sách kết quả khớp lệnh lên hợp đồng [`CarbonDoubleAuction.sol`](file:///e:/CODE/NCKH/Blockchain/contracts/CarbonDoubleAuction.sol) trên chuỗi.
   * Smart Contract chỉ làm nhiệm vụ kiểm tra chữ ký, xác thực tính toàn vẹn và thực thi hoán đổi nguyên tử (**Atomic Swap**) giữa Token ERC-1155 và Tiền ký quỹ.
   * *Ưu điểm:* Tiết kiệm đến hơn 90% chi phí gas, đạt thông lượng cao, hoàn toàn khả thi trên môi trường thực tế (tương tự kiến trúc đã được kiểm chứng của CoW Protocol và 0x Protocol).

---

## PHẦN 5: KIẾN TRÚC TỔNG QUAN HỆ THỐNG (SYSTEM ARCHITECTURE OVERVIEW)
*(Do Chủ nhiệm Đặng Xuân Huy tổng hợp và định hình thiết kế)*

### 5.1. Mô hình Kiến trúc Đa tầng (Multi-tier Architecture)
Hệ thống được thiết kế theo 4 tầng kiến trúc phân định trách nhiệm rõ ràng:

```mermaid
graph TD
    subgraph Layer1 ["1. TẦNG NGƯỜI DÙNG & GIAO DIỆN (Presentation Layer)"]
        UI1["Web3 DApp Dashboard<br/>(Next.js / TailwindCSS)"]
        UI2["Cổng Quản lý Dự án & Thẩm định<br/>(Dành cho Chủ dự án & VVB)"]
        UI3["Giao diện Sổ lệnh & Đấu giá kép<br/>(Orderbook & Trading View)"]
    end

    subgraph Layer2 ["2. TẦNG HỆ ĐA TÁC TỬ (Multi-Agent System Layer - MAS)"]
        MA["Auction & Matching Agent<br/>(Thuật toán Đấu giá kép & Khớp lệnh ngoài chuỗi)"]
        SA["Market Simulation Agent<br/>(Bot mô phỏng thanh khoản & Stress Test)"]
        MRV["MRV Verification Agent<br/>(Kiểm tra tính toàn vẹn hồ sơ & Hash SHA-256)"]
        ORA["Carbon Oracle Agent<br/>(Dải giá trần/sàn & Phát hiện thao túng)"]
        RET["Retirement Compliance Agent<br/>(Quản lý tiêu hủy & Cấp chứng chỉ ESG)"]
    end

    subgraph Layer3 ["3. TẦNG LƯU TRỮ PHI TẬP TRUNG (Decentralized Storage Layer)"]
        IPFS["Mạng IPFS & Dịch vụ Pinata<br/>(Lưu PDD, Báo cáo MRV, Chứng chỉ JSON/PDF)"]
        CID["Mã băm bất biến (Content Identifier - CID)"]
    end

    subgraph Layer4 ["4. TẦNG BLOCKCHAIN & THANH QUYẾT TOÁN (Blockchain & Settlement Layer)"]
        C1["CarbonCredit1155.sol<br/>(Quản lý Lô tín chỉ, Cấp phát & Tiêu hủy Token)"]
        C2["CarbonDoubleAuction.sol<br/>(Ký quỹ Escrow & Thanh toán Nguyên tử T+0)"]
    end

    UI1 <-->|Kết nối Ví Web3 / EIP-712| Layer2
    UI2 -->|Nộp hồ sơ PDD & Kiểm kê| MRV
    MRV -->|Ghim tài liệu & Lấy CID| IPFS
    IPFS --> CID
    CID -->|Gán vào Token URI| C1
    
    UI3 -->|Gửi lệnh Bid / Ask có chữ ký| MA
    ORA -.->|Kiểm tra dải giá an toàn| MA
    SA -.->|Bơm lệnh giả lập kiểm thử tải| MA
    
    MA -->|Submit kết quả khớp lệnh (Batch Matched)| C2
    C2 -->|Gọi hàm chuyển giao safeBatchTransferFrom| C1
    
    UI1 -->|Yêu cầu bù đắp CO2| RET
    RET -->|Gọi hàm retireCarbonCredit / burn| C1
```

### 5.2. Sự Phối hợp Giữa 5 Tác tử Hệ thống (MAS Integration)

1. **`MRV Verification Agent`:** Tiếp nhận hồ sơ số hóa từ chủ dự án, đối chiếu tính nhất quán của dữ liệu giảm phát thải, tính toán mã băm SHA-256, đẩy dữ liệu lên IPFS Pinata và cung cấp bằng chứng cho Quản trị viên ký lệnh `mintCarbonCredit()`.
2. **`Carbon Oracle Agent`:** Thu thập giá carbon tham chiếu quốc tế, xác lập biên độ giá an toàn (Price Corridor: trần/sàn). Bất kỳ lệnh mua/bán nào có giá vượt ngưỡng bất thường sẽ bị cảnh báo hoặc từ chối để chống thao túng giá.
3. **`Auction & Matching Agent`:** Đóng vai trò hạt nhân của sàn giao dịch. Thu thập các lệnh ký số hợp lệ trong phiên, loại bỏ các lệnh vi phạm, chạy giải thuật khớp lệnh tham lam hai con trỏ và xác định giá thanh toán $P^*$, sau đó đóng gói giao dịch gửi tới hợp đồng thanh quyết toán.
4. **`Market Simulation Agent`:** Tạo ra các tác tử giao dịch nhân tạo với các chiến lược định giá khác nhau (Zero-Intelligence Plus hoặc Adaptive Bidding), phục vụ quá trình thực nghiệm, đo kiểm thông lượng (TPS) và đánh giá độ ổn định của thị trường.
5. **`Retirement Compliance Agent`:** Tự động giám sát nghĩa vụ kiểm kê khí nhà kính của doanh nghiệp, kích hoạt thủ tục tiêu hủy on-chain và xuất chứng nhận bù đắp carbon chuẩn hóa có mã QR truy xuất.

### 5.3. Ma trận Phân quyền Truy cập (Role-Based Access Control - RBAC)

| Tác nhân | Vai trò on-chain | Quyền hạn nghiệp vụ |
| :--- | :--- | :--- |
| **Chủ dự án (Developer)** | `PROJECT_OWNER` | Đăng ký dự án, nộp báo cáo giám sát lên IPFS, ký lệnh chào bán (Ask). |
| **Đơn vị Thẩm định (VVB)** | `VERIFIER_ROLE` | Xác thực hồ sơ PDD, phê duyệt sản lượng giảm phát thải hợp lệ trên chuỗi. |
| **Cơ quan Quản lý (Issuer)**| `DEFAULT_ADMIN_ROLE` | Quản lý danh sách VVB, thực thi hàm cấp phát (Mint) tín chỉ ERC-1155. |
| **Doanh nghiệp Mua (Buyer)** | Mặc định (Public User) | Nạp tiền ký quỹ, ký lệnh chào mua (Bid), kích hoạt lệnh tiêu hủy (Retire/Burn). |
| **Hợp đồng Đấu giá** | `AUCTION_CONTRACT` | Nhận kết quả từ Matching Agent, chuyển token và thanh toán tiền tự động (Atomic). |

---

## PHẦN 6: KẾT LUẬN GIAI ĐOẠN 1 VÀ KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN 2

### 6.1. Đánh giá Mức độ Hoàn thành Mục tiêu Giai đoạn 1 (10/2026 – 11/2026)
* ✅ **Về mặt Lý thuyết & Nghiệp vụ:** Đã hệ thống hóa toàn diện cơ chế vận hành thị trường carbon tự nguyện (VCM), phân tích đối chiếu 3 tiêu chuẩn lớn (Verra, Gold Standard, CDM), chuẩn hóa quy trình 5 bước vòng đời tín chỉ và bám sát khung pháp lý tại Việt Nam.
* ✅ **Về mặt Công nghệ Nền tảng:** Đã đưa ra luận cứ kỹ thuật thuyết phục để lựa chọn mạng **Polygon Amoy Testnet**, chuẩn token đa tài sản **ERC-1155**, giải pháp lưu trữ phi tập trung **IPFS/Pinata**.
* ✅ **Về mặt Cơ chế Thị trường:** Đã làm rõ lý thuyết Đấu giá kép, giải thuật khớp lệnh hai con trỏ, quy tắc xác định giá $k$-Double Auction và lựa chọn kiến trúc lai (Off-chain Matching, On-chain Settlement).
* ✅ **Về mặt Kiến trúc & Định hình Hệ thống:** Đã xây dựng hoàn chỉnh mô hình kiến trúc đa tầng tích hợp Hệ Đa Tác Tử (MAS) và khởi tạo kho mã nguồn chuẩn hóa.

### 6.2. Kế hoạch Chi tiết Bước sang Giai đoạn 2 (11/2026 – 01/2027)
Giai đoạn 2 sẽ tập trung vào **Phân tích yêu cầu và Thiết kế chi tiết hệ thống**:
1. **Thiết kế chi tiết Smart Contracts:**
   * Hoàn thiện hợp đồng [`CarbonCredit1155.sol`](file:///e:/CODE/NCKH/Blockchain/contracts/CarbonCredit1155.sol) bổ sung cơ chế trích lập Quỹ dự phòng rủi ro (*Buffer Pool Vault*) và kiểm soát đa chữ ký (*Multi-signature*).
   * Hoàn thiện hợp đồng [`CarbonDoubleAuction.sol`](file:///e:/CODE/NCKH/Blockchain/contracts/CarbonDoubleAuction.sol) hỗ trợ xác thực chữ ký số ngoài chuỗi EIP-712 và thanh toán bằng Token chuẩn ERC-20 (Mock USDT/USDC).
2. **Xây dựng Tài liệu Đặc tả Yêu cầu Hệ thống (SRS):**
   * Chi tiết hóa Use Case, Activity Diagram và Sequence Diagram cho toàn bộ 5 giai đoạn nghiệp vụ.
   * Xây dựng từ điển dữ liệu (Data Dictionary) cho siêu dữ liệu Metadata trên IPFS.
3. **Thiết kế Giao diện Người dùng (UI/UX Mockup):**
   * Thiết kế Wireframe/Figma cho Web3 DApp: Dashboard theo dõi danh mục tín chỉ, bảng điều khiển nộp hồ sơ PDD của chủ dự án, giao diện sổ lệnh đấu giá kép và trang tra cứu chứng chỉ bù đắp ESG.
4. **Phối hợp Nghiên cứu & Giảng viên Hướng dẫn:**
   * Trình bày báo cáo tổng quan Giai đoạn 1 với TS. Nguyễn Thị Hồng Khánh để xin ý kiến định hướng trước khi bước vào lập trình lõi ở Giai đoạn 3.
