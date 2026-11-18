# 📊 ĐỀ CƯƠNG CHI TIẾT BÀI TRÌNH CHIẾU BÁO CÁO TIẾN ĐỘ GIAI ĐOẠN 2
## SLIDE PRESENTATION ACADEMIC OUTLINE (20 SLIDES)
### ĐỀ TÀI: HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON MINH BẠCH VÀ HIỆU QUẢ TRÊN NỀN TẢNG BLOCKCHAIN

- **Đơn vị thực hiện:** Nhóm nghiên cứu sinh viên Khoa Công nghệ Thông tin – Trường Đại học Điện Lực (EPU)
- **Chủ nhiệm đề tài / Báo cáo viên:** Đặng Xuân Huy (MSV: 23810310007 - Lớp D18CNPM1)
- **Thành viên nghiên cứu:** Nguyễn Hoàng Đức, Nguyễn Bảo Phi, Ngô Văn Thắng
- **Giảng viên hướng dẫn khoa học:** TS. Nguyễn Thị Hồng Khánh
- **Thời điểm báo cáo:** Tháng 11/2026
- **Tài liệu nguồn tham chiếu:**
  + Hồ sơ đặc tả yêu cầu phần mềm IEEE 830: [`docs/SRS_DOCUMENT.md`](SRS_DOCUMENT.md)
  + Báo cáo quyết định kiến trúc: [`docs/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md`](ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md)
  + Đặc tả Động cơ Khớp lệnh & Lý thuyết trò chơi: [`docs/MATCHING_ENGINE_SPEC.md`](MATCHING_ENGINE_SPEC.md)
  + Đặc tả Hợp đồng Thông minh & Benchmark Gas: [`docs/SMART_CONTRACT_SPEC.md`](SMART_CONTRACT_SPEC.md)
  + Hồ sơ Mô hình Đe dọa An ninh: [`docs/THREAT_MODELING.md`](THREAT_MODELING.md)
  + Bộ thiết kế Wireframe Figma 4 phân hệ: [`docs/wireframes/README.md`](wireframes/README.md)

---

## MỤC LỤC CẤU TRÚC 20 SLIDE BÁO CÁO

```
PHẦN 1: BỐI CẢNH NGHIÊN CỨU & KIẾN TRÚC HỆ THỐNG (Slide 1 – 3)
  ├── Slide 1: Trang bìa & Giới thiệu đề tài nghiên cứu
  ├── Slide 2: Bài toán Thị trường Carbon Tự nguyện (VCM) & Động lực nghiên cứu
  └── Slide 3: Kiến trúc Tổng thể Lai (Hybrid Off-chain MAS & On-chain Settlement)

PHẦN 2: ĐẶC TẢ YÊU CẦU & CHUẨN HÓA DỮ LIỆU (Slide 4 – 7)
  ├── Slide 4: Quyết định Kiến trúc Cốt lõi (ADR-001) & Ma trận Yêu cầu IEEE 830
  ├── Slide 5: Chuẩn hóa Dữ liệu Tín chỉ Carbon (ERC-1155, Verra/GS & Buffer Pool 15%)
  ├── Slide 6: Hệ thống Đa tác tử (Multi-Agent System) & Dòng chảy Khớp lệnh
  └── Slide 7: Cơ chế Định tuyến Lệnh Không tốn Gas (Gasless Order Routing via EIP-712)

PHẦN 3: LÝ THUYẾT TRÒ CHƠI & THUẬT TOÁN ĐẤU GIÁ (Slide 8 – 10)
  ├── Slide 8: Cơ chế Đấu giá Kép Đồng nhất (Uniform k-Double Auction Mechanism)
  ├── Slide 9: Phân tích Tổn thất Xã hội (Deadweight Loss) & Định lý Hội tụ O(1/m²)
  └── Slide 10: Quy tắc Phá hòa Cân bằng: Phương pháp Hamilton & Thuật toán age_prorata

PHẦN 4: HỢP ĐỒNG THÔNG MINH & THỰC NGHIỆM BLOCKCHAIN (Slide 11 – 13)
  ├── Slide 11: Thiết kế Smart Contract v2 & Kiến trúc 7 Chốt chặn Bảo mật
  ├── Slide 12: Cơ chế Thanh toán Nguyên tử T+0 & Khối Batch Settlement Try-Catch
  └── Slide 13: Kết quả Benchmark Gas Thực tế trên Polygon Amoy Testnet (Tiết kiệm >52%)

PHẦN 5: GIAO DIỆN NGƯỜI DÙNG & TÍNH MINH BẠCH MRV (Slide 14 – 16)
  ├── Slide 14: Kiến trúc Giao diện Web3 DApp: 4 Cổng Phân hệ Chuyên biệt
  ├── Slide 15: Trải nghiệm Sàn Giao dịch: Sổ lệnh & Biểu đồ Độ sâu Thời gian thực
  └── Slide 16: Quy trình Đo đạc - Báo cáo - Thẩm tra (MRV) & Tiêu hủy ESG On-chain

PHẦN 6: AN TOÀN BẢO MẬT & ĐÁNH GIÁ THỰC NGHIỆM (Slide 17 – 18)
  ├── Slide 17: Phân tích Mô hình Đe dọa Bảo mật (STRIDE) & Giải pháp Chống MEV
  └── Slide 18: Kết quả Kiểm thử Liên thông Toàn trình (End-to-End On-chain Proofs)

PHẦN 7: KẾ HOẠCH GIAI ĐOẠN 3 & TỔNG KẾT (Slide 19 – 20)
  ├── Slide 19: Kế hoạch Triển khai Giai đoạn 3 & Định hướng Bài báo Khoa học
  └── Slide 20: Tổng kết Giá trị Đề tài, Lời cảm ơn & Phiên Hỏi - Đáp (Q&A)
```

---

## NỘI DUNG CHI TIẾT TỪNG SLIDE TRÌNH CHIẾU

---

### 🟢 SLIDE 1: TRANG BÌA & GIỚI THIỆU ĐỀ TÀI NGHIÊN CỨU
- **Tiêu đề Slide:** BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU KHOA HỌC GIAI ĐOẠN 2  
  *Đề tài:* **Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain**
- **Mục tiêu học thuật:** Xác lập tư cách khoa học, giới thiệu nhóm nghiên cứu, cơ quan chủ quản và giảng viên hướng dẫn.
- **Bố cục trình bày trực quan:**
  + Logo Trường Đại học Điện Lực (EPU) góc trên bên trái.
  + Khung định danh trang trọng: Bộ môn Kỹ thuật Phần mềm / Khoa Công nghệ Thông tin.
  + Huy hiệu đánh dấu tiến độ: `GIAI ĐOẠN 2: THIẾT KẾ KIẾN TRÚC, XÂY DỰNG MÃ NGUỒN & THỰC NGHIỆM TESTNET`.
- **Nội dung trọng tâm:**
  + **Chủ nhiệm đề tài:** Đặng Xuân Huy (MSV: 23810310007) – *Lead Architect & Coordinator*
  + **Thành viên nghiên cứu:**
    * Nguyễn Hoàng Đức (MSV: 23810310060) – *Smart Contract & On-chain Settlement*
    * Nguyễn Bảo Phi (MSV: 23810310017) – *Auction Algorithm & Game Theory*
    * Ngô Văn Thắng (MSV: 23810310401) – *Fullstack Web3 & UI/UX Design*
  + **Giảng viên hướng dẫn:** TS. Nguyễn Thị Hồng Khánh
  + **Thời gian báo cáo:** Tháng 11/2026
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Kính thưa TS. Nguyễn Thị Hồng Khánh cùng toàn thể Hội đồng khoa học. Hôm nay nhóm nghiên cứu sinh viên trường Đại học Điện Lực xin phép được báo cáo kết quả thực hiện Giai đoạn 2 của đề tài 'Hệ thống giao dịch tín chỉ carbon minh bạch và hiệu quả trên nền tảng Blockchain'. Trong giai đoạn vừa qua, nhóm đã hoàn thiện trọn vẹn kiến trúc v2, cài đặt thành công lõi đấu giá số nguyên ngoài chuỗi, triển khai toàn diện hợp đồng thông minh lên testnet Polygon Amoy và xây dựng DApp Web3 tương tác trực quan."*

---

### 🟢 SLIDE 2: BÀI TOÁN THỊ TRƯỜNG CARBON TỰ NGUYỆN (VCM) & ĐỘNG LỰC NGHIÊN CỨU
- **Tiêu đề Slide:** THỰC TRẠNG THỊ TRƯỜNG CARBON TỰ NGUYỆN (VCM) & BỐI CẢNH THIẾT KẾ
- **Mục tiêu học thuật:** Luận giải tính cấp thiết khoa học và thực tiễn, phân tích 4 nút thắt cổ chai lớn của thị trường carbon truyền thống hiện nay.
- **Bố cục trình bày trực quan:** Sơ đồ so sánh dạng bảng đối sánh hoặc 4 khối cảnh báo (Problem Cards) chỉ ra các điểm yếu chết người của VCM truyền thống:
  ```
  [Tính thanh khoản phân mảnh] ──> Khó hình thành giá thị trường chuẩn xác
  [Gian lận & Đếm trùng lặp]   ──> Thiếu cơ chế theo dõi MRV và tiêu hủy bất biến
  [Chi phí trung gian cao]     ──> 15% - 30% giá trị thất thoát vào môi giới OTC
  [Tắc nghẽn phí Gas Blockchain]──> Đặt/hủy lệnh trực tiếp on-chain gây tốn kém
  ```
- **Nội dung trọng tâm:**
  + **Đặc thù thị trường:** Tín chỉ carbon không hoàn toàn đồng nhất (non-fungible attributes: xuất xứ, loại hình công nghệ, năm phát hành vintage) nhưng vẫn cần thanh khoản quy mô lớn.
  + **Nút thắt tính toán:** Mô hình AMM truyền thống (như Uniswap x*y=k) không phù hợp cho tài sản biến động chậm và lệnh rời rạc; mô hình Sổ lệnh On-chain hoàn toàn (Fully on-chain CLOB) gây lãng phí hàng triệu USD tiền phí gas vô ích cho việc cập nhật lệnh.
  + **Định hướng giải pháp:** Xây dựng cơ chế Sàn giao dịch lai (Hybrid Architecture) kết hợp sức mạnh thuật toán kinh tế ngoài chuỗi và tính bất biến, minh bạch của công nghệ sổ cái phân tán.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Thị trường tín chỉ carbon tự nguyện toàn cầu đang phát triển bùng nổ hướng tới mục tiêu Net Zero 2050. Tuy nhiên, các sàn giao dịch hiện tại đối mặt với nghịch lý: nếu giao dịch OTC truyền thống thì thiếu minh bạch và chi phí trung gian cắt cổ lên tới 30%; còn nếu đưa toàn bộ lên blockchain thì chi phí gas cho việc tạo và hủy lệnh sẽ làm tê liệt toàn hệ thống. Đây chính là động lực thôi thúc nhóm đề xuất kiến trúc giao dịch lai tối ưu."*

---

### 🟢 SLIDE 3: KIẾN TRÚC TỔNG THỂ LAI (HYBRID OFF-CHAIN MAS & ON-CHAIN SETTLEMENT)
- **Tiêu đề Slide:** KIẾN TRÚC HỆ THỐNG LAI (HYBRID SYSTEM ARCHITECTURE)
- **Mục tiêu học thuật:** Trình bày mô hình phân lớp rõ ràng, phân định ranh giới tính toán giữa Off-chain Multi-Agent System và On-chain Smart Contracts.
- **Bố cục trình bày trực quan:** Biểu đồ kiến trúc 3 tầng (3-Tier Layered Architecture):
  ```
  +-------------------------------------------------------------------------+
  |  TẦNG ỨNG DỤNG (WEB3 DAPP) - Next.js, Wagmi v2, Viem, MetaMask EIP-6963  |
  +-------------------------------------------------------------------------+
                                 │ EIP-712 Signed Orders (REST / WebSocket)
                                 ▼
  +-------------------------------------------------------------------------+
  |  TẦNG ĐỘNG CƠ KHỚP LỆNH NGOÀI CHUỖI (OFF-CHAIN MAS MATCHING ENGINE)     |
  |  • FastAPI Gateway (Xác thực chữ ký, Quản lý Sổ lệnh OrderBook)         |
  |  • Thuật toán Đấu giá kép Đồng nhất k-DA & Phá hòa Hamilton age_prorata |
  |  • Settlement Submitter Bot (Xử lý Pre-flight, Đóng gói Batch Trades)   |
  +-------------------------------------------------------------------------+
                                 │ batchSettleTrades() calldata (Web3.py)
                                 ▼
  +-------------------------------------------------------------------------+
  |  TẦNG HỢP ĐỒNG THÔNG MINH ON-CHAIN (POLYGON AMOY TESTNET - CHAIN 80002) |
  |  • CarbonDoubleAuction.sol: 7 Chốt chặn Bảo mật, Atomic Swap T+0        |
  |  • CarbonCredit1155.sol: Packed Storage 3 slot, Quỹ rủi ro Buffer 15%   |
  |  • MockUSDC.sol: Token thanh toán chuẩn ERC-20 (6 decimals)             |
  +-------------------------------------------------------------------------+
  ```
- **Nội dung trọng tâm:**
  + **Tách biệt nhiệm vụ (Separation of Concerns):** Toàn bộ khâu thu thập lệnh, kiểm tra định dạng và khớp lệnh thực hiện ngoài chuỗi với độ trễ dưới 100ms; Smart contract chỉ đóng vai trò Trọng tài thanh toán tối cao (Supreme Settlement Arbiter).
  + **Tính nguyên tử (Atomicity):** Việc hoán đổi giữa tiền thanh toán (USDC) và tín chỉ carbon (EVCC) diễn ra đồng thời trong 1 giao dịch, loại bỏ rủi ro đối tác (Counterparty Risk).
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Kiến trúc của chúng tôi được thiết kế theo nguyên lý: 'Tính toán phức tạp để ngoài chuỗi, Xác thực chân lý đặt trên chuỗi'. Người dùng ký lệnh miễn phí ngoài chuỗi qua chuẩn EIP-712. Động cơ MAS thực hiện tối ưu hóa phúc lợi xã hội và chỉ gửi một giao dịch đóng gói thanh toán lên Polygon Amoy. Cơ chế này đảm bảo tốc độ cao như sàn tập trung nhưng vẫn an toàn tuyệt đối như hợp đồng thông minh."*

---

### 🟢 SLIDE 4: QUYẾT ĐỊNH KIẾN TRÚC CỐT LÕI (ADR-001) & MA TRẬN YÊU CẦU IEEE 830
- **Tiêu đề Slide:** ĐẶC TẢ YÊU CẦU PHẦN MỀM (IEEE 830) & QUYẾT ĐỊNH ADR-001
- **Mục tiêu học thuật:** Khẳng định tính chuẩn mực công nghệ phần mềm qua 4 quyết định kiến trúc bất biến và 15 yêu cầu chức năng (FR-01 đến FR-15).
- **Bố cục trình bày trực quan:** Bảng ma trận đối soát quyết định kỹ thuật và hệ thống yêu cầu chức năng cốt lõi:
  | Quyết định Kiến trúc (ADR-001) | Lựa chọn Công nghệ | Cơ sở Kỹ thuật & Khoa học |
  | :--- | :--- | :--- |
  | **Cơ chế thị trường (D1)** | Đấu giá kép định kỳ ($k$-DA) | Gom thanh khoản phân mảnh, giảm thiểu biến động giá |
  | **Chuẩn Token hóa (D2)** | Bán phần ERC-1155 | Gom nhóm tín chỉ tương đương (fungible pools) theo vintage |
  | **Chuẩn Ký Lệnh (D3)** | Gasless EIP-712 | Người dùng không tốn gas khi đặt lệnh hoặc sửa lệnh |
  | **Mạng lưới Thực thi (D4)** | Polygon Amoy L2 | Chi phí gas cực thấp ($< 0.001\$$), băng thông block cao |
- **Nội dung trọng tâm:**
  + **Ma trận yêu cầu chức năng:** Phân loại rõ từ FR-01 $\to$ FR-04 (Quản lý danh mục & Nộp hồ sơ MRV), FR-05 $\to$ FR-08 (Thẩm tra VVB & Mint token), FR-09 $\to$ FR-12 (Khớp lệnh $k$-DA & Thanh toán lô), FR-13 $\to$ FR-15 (Tiêu hủy ESG & Chứng chỉ minh bạch).
  + **Yêu cầu phi chức năng then chốt (NFRs):** Thời gian phản hồi API $< 200\text{ms}$ (NFR-01), Chi phí gas thanh toán $< 85,000\text{ gas/lệnh}$ trong batch (NFR-02), Tính toàn vẹn 100% không cho phép double-spending (NFR-03).
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Để dự án đi đúng quỹ đạo kỹ thuật, nhóm đã ban hành tài liệu SRS chuẩn IEEE 830 dài 51 trang cùng Bản quyết định kiến trúc ADR-001. Việc lựa chọn chuẩn ERC-1155 thay vì ERC-20 hay ERC-721 đơn thuần là bước đi then chốt, cho phép quản lý hàng trăm lô tín chỉ khác nhau trong cùng một hợp đồng, đồng thời tích hợp sẵn cơ chế trích lập quỹ dự phòng rủi ro."*

---

### 🟢 SLIDE 5: CHUẨN HÓA DỮ LIỆU TÍN CHỈ CARBON (ERC-1155, VERRA/GS & BUFFER POOL 15%)
- **Tiêu đề Slide:** ĐẶC TẢ SIÊU DỮ LIỆU TÍN CHỈ & QUỸ DỰ PHÒNG RỦI RO (BUFFER POOL)
- **Mục tiêu học thuật:** Trình bày cấu trúc dữ liệu on-chain tối ưu và cơ chế bảo đảm an toàn sinh thái theo chuẩn quốc tế Verra VCS và Gold Standard.
- **Bố cục trình bày trực quan:**
  + Sơ đồ Packed Storage 3 slot của struct `CreditLot` trong Solidity:
    ```
    Slot 0: [ uint256 totalMinted (32 bytes) ]
    Slot 1: [ uint256 retiredAmount (32 bytes) ]
    Slot 2: [ address projectOwner (20B) | uint16 vintage (2B) | uint8 standard (1B) | uint16 bufferRateBps (2B) | bool isActive (1B) ]
    ```
  + Biểu đồ tròn minh họa phân bổ đúc tín chỉ: 85% lưu hành thị trường, 15% tự động khóa vào Buffer Pool Vault.
- **Nội dung trọng tâm:**
  + **Tối ưu hóa Storage On-chain:** Gom cụm biến giúp tiết kiệm 20,000 gas (1 lần SLOAD/SSTORE) cho mỗi thao tác truy vấn trạng thái lô tín chỉ.
  + **Cơ chế Quỹ dự phòng Buffer Pool:** Khi thẩm tra viên ký duyệt đúc 100,000 tCO2e, hợp đồng tự động chuyển 15,000 tCO2e vào Vault dự phòng rủi ro bất khả kháng (cháy rừng, sâu bệnh), chỉ cấp 85,000 tCO2e cho chủ dự án lưu thông trên sàn.
  + **Định dạng JSON Schema v2:** Tích hợp đầy đủ trường dữ liệu MRV, liên kết IPFS CID bất biến và mã định danh theo chuẩn quốc tế.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Tính toàn vẹn môi trường là yếu tố sống còn của tín chỉ carbon. Hợp đồng CarbonCredit1155 của chúng tôi bắt buộc cài đặt cơ chế Buffer Pool tự động từ 10% đến 20%. Nếu dự án lâm nghiệp gặp rủi ro thiên tai, lượng tín chỉ tổn thất sẽ được bù đắp từ quỹ dự phòng này, bảo vệ quyền lợi tuyệt đối cho người mua."*

---

### 🟢 SLIDE 6: HỆ THỐNG ĐA TÁC TỬ (MULTI-AGENT SYSTEM) & DÒNG CHẢY KHỚP LỆNH
- **Tiêu đề Slide:** MÔ HÌNH HỆ THỐNG ĐA TÁC TỬ (MAS) NGOÀI CHUỖI
- **Mục tiêu học thuật:** Trình bày cấu trúc điều phối phân tán của các tác tử phần mềm trong việc thu thập, xác thực và tổ chức các phiên đấu giá định kỳ.
- **Bố cục trình bày trực quan:** Sequence Diagram mô tả dòng chảy thông điệp giữa các tác tử:
  ```mermaid
  sequenceDiagram
    autonumber
    actor Trader as Nhà Giao Dịch
    participant API as Gateway Agent (FastAPI)
    participant Engine as Auction Agent (session_engine)
    participant Submitter as Submitter Bot Agent
    participant Chain as Blockchain (Polygon Amoy)

    Trader->>API: Gửi lệnh ký EIP-712 (POST /orders)
    API->>API: Xác thực chữ ký & Nonce, nạp vào Memory OrderBook
    Note over API,Engine: Hết thời gian phiên gom lệnh (Batch Window)
    API->>Engine: Kích hoạt phiên khớp (POST /sessions/run)
    Engine->>Engine: Sắp xếp đường cung-cầu, tính P* & phân bổ Hamilton
    Engine-->>API: Trả về MatchResult[] & Cập nhật trạng thái lệnh
    Submitter->>API: Lấy danh sách giao dịch cần thanh toán
    Submitter->>Chain: Pre-flight check & gọi batchSettleTrades()
    Chain-->>Submitter: Phát sinh Event TradeSettled
    Submitter->>API: Xác nhận thanh toán (POST /settlements/confirm)
  ```
- **Nội dung trọng tâm:**
  + **Gateway Agent:** Tiếp nhận hàng nghìn kết nối đồng thời, duy trì WebSocket feed cập nhật độ sâu thị trường cho DApp.
  + **Auction Agent:** Quản lý vòng đời lệnh qua các trạng thái: `NEW` $\to$ `ROLLED_OVER` (tối đa 3 phiên đối với lệnh GTC) $\to$ `FILLED` / `EXPIRED` / `CANCELLED`.
  + **Submitter Bot Agent:** Đóng vai trò cầu nối an toàn, đảm bảo mọi kết quả tính toán đều được ghi nhận chuẩn xác lên blockchain.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Kiến trúc Đa tác tử MAS cho phép hệ thống chia nhỏ trách nhiệm xử lý: Gateway Agent chuyên lo giao tiếp tốc độ cao với người dùng, Auction Agent tập trung giải bài toán tối ưu kinh tế, còn Submitter Bot chuyên trách tương tác blockchain an toàn. Mô hình này giúp hệ thống đạt độ sẵn sàng cao và dễ dàng mở rộng quy mô."*

---

### 🟢 SLIDE 7: CƠ CHẾ ĐỊNH TUYẾN LỆNH KHÔNG TỐN GAS (GASLESS ORDER ROUTING VIA EIP-712)
- **Tiêu đề Slide:** ĐẶC TẢ CẤU TRÚC LỆNH EIP-712 & CƠ CHẾ BẢO VỆ CHỮ KÝ
- **Mục tiêu học thuật:** Phân tích cấu trúc dữ liệu định kiểu có cấu trúc (Typed Structured Data), Domain Separator và cơ chế chống tấn công Replay chéo chuỗi.
- **Bố cục trình bày trực quan:**
  + Cấu trúc dữ liệu Struct `Order` trong Solidity và TypeScript:
    ```solidity
    struct Order {
        address trader;      // Địa chỉ ví người đặt lệnh
        uint8 orderType;     // 0 = BID (Mua), 1 = ASK (Bán)
        uint256 tokenId;     // Mã lô tín chỉ carbon
        uint256 amount;      // Số lượng tCO2e (đơn vị số nguyên)
        uint256 pricePerUnit;// Giá giới hạn (micro-USDC, 6 decimals)
        uint256 nonce;       // Số đếm chống phát lại
        uint256 deadline;    // Hạn hiệu lực của chữ ký (Unix timestamp)
    }
    ```
  + Bảng thông số Domain Separator bất biến: `name: "EPU Carbon Double Auction"`, `version: "2.0"`, `chainId: 80002`, `verifyingContract: "0x6Ee8...c46f"`.
- **Nội dung trọng tâm:**
  + **Trải nghiệm người dùng Gasless:** Nhà giao dịch không cần có sẵn token POL trong ví để đặt lệnh hoặc sửa lệnh; chữ ký được thực hiện hoàn toàn off-chain qua ví cá nhân.
  + **Bảo vệ toàn vẹn chữ ký:** Áp dụng chuẩn EIP-712 ngăn chặn triệt để hình thức tấn công lừa ký chuỗi mù (Blind Signing); người dùng thấy rõ khối lượng và giá trước khi bấm ký.
  + **Loại bỏ chữ ký s cao (Malleability Protection):** Hợp đồng bắt buộc kiểm tra $s \le \text{secp256k1n}/2$ theo chuẩn OpenZeppelin ECDSA.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Điểm sáng trong trải nghiệm người dùng của chúng tôi là cơ chế Gasless Order. Bằng cách áp dụng EIP-712, doanh nghiệp có thể đặt hàng chục lệnh mua bán mỗi ngày mà không tốn một đồng phí mạng nào. Chữ ký chỉ thực sự được nộp lên chuỗi khi hai lệnh đã khớp thành công."*

---

### 🟢 SLIDE 8: CƠ CHẾ ĐẤU GIÁ KÉP ĐỒNG NHẤT (UNIFORM $k$-DOUBLE AUCTION MECHANISM)
- **Tiêu đề Slide:** MÔ HÌNH TOÁN HỌC ĐẤU GIÁ KÉP ĐỒNG NHẤT ($k$-DA)
- **Mục tiêu học thuật:** Trình bày thuật toán xác định điểm giao cắt cung - cầu, tối đa hóa thặng dư xã hội (Gains from Trade) và quy tắc định giá đồng nhất.
- **Bố cục trình bày trực quan:** Đồ thị kinh tế học kinh điển biểu diễn đường Cầu (giảm dần) và đường Cung (tăng dần) giao nhau tại vùng giá cân bằng $[p_{\min}^*, p_{\max}^*]$:
  ```
     Giá (USDC)
        ▲
     14 ┤  ● (Bid 1: 14)
     12 ┤  │     ● (Bid 2: 12)  ── Vùng thặng dư thương mại
     11 ┼──┼─────┼───────★ P* = 11.0 (Clearing Price)
     10 ┤  │     │  ▲ (Ask 2: 10)
      8 ┤  │  ▲ (Ask 1: 8)
        └──┴─────┴───────┴──────► Khối lượng Q* (tCO2e)
           0    50      100
  ```
- **Nội dung trọng tâm:**
  + **Nguyên lý khớp lệnh:**
    * Sắp xếp các lệnh Mua (Bids) theo thứ tự ưu tiên: Giá cao xếp trước, cùng giá ưu tiên lệnh đến trước (FIFO).
    * Sắp xếp các lệnh Bán (Asks): Giá thấp xếp trước, cùng giá ưu tiên lệnh đến trước.
  + **Công thức xác định giá khớp đồng nhất ($k$-DA Pricing Rule):**
    $$P^*(k) = (1 - k) \cdot p_{\text{ask}}^{\text{marginal}} + k \cdot p_{\text{bid}}^{\text{marginal}} \quad (k \in [0, 1])$$
    Trong đó $k = 0.5$ đại diện cho cơ chế chia đều thặng dư giữa bên mua và bên bán (Split-the-Difference).
  + **Chuẩn hóa số nguyên:** Toàn bộ phép tính trên engine đều sử dụng số nguyên vi mô (`micro-USDC`) kết hợp quy tắc làm tròn ngân hàng `half_even`, triệt tiêu hoàn toàn sai số dấu phẩy động khi chuyển giao cho smart contract.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Thay vì để người mua và người bán khớp lệnh riêng lẻ theo giá đặt gây thiệt hại cho người đến sau, cơ chế k-DA gom toàn bộ lệnh trong phiên và tìm ra một mức giá chung duy nhất P*. Tại mức giá này, thặng dư kinh tế của toàn thị trường đạt cực đại và mọi bên tham gia đều được hưởng lợi."*

---

### 🟢 SLIDE 9: PHÂN TÍCH TỔN THẤT XÃ HỘI (DEADWEIGHT LOSS) & ĐỊNH LÝ HỘI TỤ $O(1/m^2)$
- **Tiêu đề Slide:** CƠ SỞ KINH TẾ HỌC: ĐỊNH LÝ HỘI TỤ CHATTERJEE-SAMUELSON & RUSTICHINI
- **Mục tiêu học thuật:** Chứng minh cơ sở lý thuyết trò chơi của cơ chế $k$-DA và kết quả thực nghiệm mô phỏng độ tiêu giảm tổn thất xã hội khi thị trường mở rộng quy mô.
- **Bố cục trình bày trực quan:**
  + Đồ thị Log-Log biểu diễn mối quan hệ giữa Mất mát hiệu quả (Deadweight Loss) và số lượng người tham gia thị trường $m \in \{4, 8, 16, 32, 64\}$.
  + Bảng đối chiếu giữa lý thuyết giải tích và số liệu thực nghiệm đo đạc từ module `system_agents/matching_engine/simulation/`:
    | Quy tắc Giá | Hệ số dốc lý thuyết [RSW94] | Độ dốc đo đạc thực nghiệm | Đánh giá hội tụ |
    | :--- | :---: | :---: | :--- |
    | **Marginal ($k=0.5$)** | $-2.00$ ($O(1/m^2)$) | $-1.79 \pm 0.05$ | Tiệm cận lý thuyết chặt chẽ |
    | **$k$-DA Uniform ($k=1.0$)** | $-2.00$ ($O(1/m^2)$) | $-2.25 \pm 0.06$ | Hội tụ siêu bậc ở $m \le 32$ |
    | **Pairwise Benchmark** | $-1.00$ ($O(1/m)$) | $-0.95 \pm 0.02$ | Khớp chính xác với mô hình cơ sở |
- **Nội dung trọng tâm:**
  + **Định lý Chatterjee & Samuelson (1983):** Phân tích trạng thái cân bằng Bayes-Nash trong thị trường song phương; giải tích chứng minh tổn thất hiệu quả tỷ lệ với $\frac{1}{6}$ thặng dư tối đa.
  + **Định lý Rustichini, Satterthwaite & Williams (1994):** Chứng minh khi số lượng người tham gia thị trường tăng ($m \to \infty$), các nhà giao dịch buộc phải chào giá tiệm cận giá trị thực (Truthful Bidding), và tổn thất hiệu quả tiêu giảm với tốc độ bậc hai $O(1/m^2)$.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Chúng tôi không chỉ viết code mà còn chứng minh tính đúng đắn khoa học bằng mô phỏng thực nghiệm. Kết quả đo đạc trên 64 tác nhân đã tái hiện chính xác định lý kinh tế học của Rustichini: khi thị trường carbon có nhiều người tham gia, chiến lược trả giá gian lận sẽ tự động bị loại trừ và thị trường đạt hiệu quả tuyệt đối."*

---

### 🟢 SLIDE 10: QUY TẮC PHÁ HÒA CÂN BẰNG: PHƯƠNG PHÁP HAMILTON & THUẬT TOÁN `age_prorata`
- **Tiêu đề Slide:** THUẬT TOÁN PHÂN BỔ TỶ LỆ KẾT HỢP TUỔI LỆNH (`age_prorata`)
- **Mục tiêu học thuật:** Trình bày giải pháp công bằng xã hội giải quyết triệt để bài toán chia lẻ hàng hóa (Indivisibility) khi lượng cung và lượng cầu tại mức giá $P^*$ không cân bằng hoàn hảo.
- **Bố cục trình bày trực quan:** Sơ đồ khối 3 bước của thuật toán Hamilton (Largest Remainder Method) tích hợp trọng số tuổi lệnh:
  ```
  [1. Tính Hạn ngạch Cơ sở] ──> quota_i = (amount_i * weight_i / total_weighted) * Q_available
  [2. Phân bổ Phần nguyên]  ──> assigned_i = floor(quota_i) (Đảm bảo số nguyên tCO2e)
  [3. Phân chia Phần dư]    ──> Sắp xếp theo remainder_i giảm dần, phá hòa bằng FIFO seq
  ```
- **Nội dung trọng tâm:**
  + **Khắc phục bất cập của Pro-rata cổ điển:** Thuật toán pro-rata truyền thống thường tạo ra các phần lẻ thập phân không thể chuyển giao trên hợp đồng thông minh; `age_prorata` bảo toàn tính nguyên tử của số lượng token ($1\text{ tCO2e} = 1\text{ đơn vị}$).
  + **Khuyến khích cung cấp thanh khoản sớm (Anti-Sniping):** Các lệnh đặt sớm có tuổi lệnh (age) cao hơn sẽ nhận trọng số ưu tiên khi phân chia phần dư còn lại, ngăn chặn hành vi bot chèn lệnh giây cuối.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Khi khối lượng chào mua lớn hơn khối lượng chào bán tại mức giá P*, làm thế nào để phân chia công bằng mà không bị lẻ đơn vị token? Nhóm đã áp dụng phương pháp phân bổ lớn nhất của Hamilton kết hợp trọng số tuổi lệnh. Nhờ đó, người đặt lệnh sớm được thưởng phần dư, vừa công bằng vừa loại bỏ hoàn toàn hiện tượng bot chen ngang."*

---

### 🟢 SLIDE 11: THIẾT KẾ SMART CONTRACT V2 & KIẾN TRÚC 7 CHỐT CHẶN BẢO MẬT
- **Tiêu đề Slide:** THIẾT KẾ HỢP ĐỒNG THÔNG MINH V2 & 7 CHỐT CHẶN BẢO MẬT ON-CHAIN
- **Mục tiêu học thuật:** Phân tích kiến trúc an ninh phòng thủ chiều sâu (Defense-in-Depth) trong hợp đồng `CarbonDoubleAuction.sol`.
- **Bố cục trình bày trực quan:** Mô hình 7 tầng phòng thủ liên hoàn trước khi thực thi chuyển tiền và tín chỉ:
  ```
  [LỆNH NỘP VÀO]
        │
        ▼ 1. Xác thực Chữ ký EIP-712 của cả 2 bên (ECDSA.recover)
        ▼ 2. Kiểm tra Thời hạn Hiệu lực (deadline >= block.timestamp)
        ▼ 3. Kiểm tra Hợp thức Cặp lệnh (cùng tokenId, đúng chiều, trader khác nhau)
        ▼ 4. Kiểm tra Biên độ Giá (ask.price <= clearingPrice <= bid.price)
        ▼ 5. Kiểm tra Khối lượng Khớp CỦA CẢ HAI BÊN (filledAmount + match <= amount)
        ▼ 6. Kiểm tra Trạng thái Hủy Lệnh (!cancelledOrders)
        ▼ 7. Chống Nộp Trùng Giao dịch (keccak256 tất định không dùng block.number)
        │
  [THỰC THI HOÁN ĐỔI NGUYÊN TỬ T+0]
  ```
- **Nội dung trọng tâm:**
  + **Vá dứt điểm lỗ hổng Đ2:** Kiểm tra lũy kế `filledAmount` cho cả bên mua và bên bán, ngăn chặn hoàn toàn việc bán khống vượt quá số lượng đã ký.
  + **Chống Wash Trading:** Cấm giao dịch giữa các ví có cùng chủ sở hữu nhằm tạo thanh khoản ảo.
  + **ReentrancyGuard & Custom Errors:** Tiết kiệm gas và bảo vệ chống tấn công tái nhập trên mọi hàm thanh toán.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Smart contract v2 của chúng tôi được xây dựng với phương châm 'Zero Trust'. Mỗi cặp lệnh trước khi được chuyển đổi tài sản đều phải vượt qua 7 chốt chặn kiểm tra nghiêm ngặt. Dù bot submitter ngoài chuỗi có bị tấn công hay gửi nhầm dữ liệu, hợp đồng thông minh vẫn tự động từ chối và bảo toàn 100% tài sản cho người dùng."*

---

### 🟢 SLIDE 12: CƠ CHẾ THANH TOÁN NGUYÊN TỬ T+0 & KHỐI BATCH SETTLEMENT TRY-CATCH
- **Tiêu đề Slide:** CƠ CHẾ BATCH SETTLEMENT CHỐNG NGHẼN MẠNG & BẢO VỆ DoS
- **Mục tiêu học thuật:** Trình bày giải pháp kỹ thuật bọc khối gọi ngoại vi (`try/catch` wrapper) giúp thực thi hàng loạt giao dịch mà không bị tắc nghẽn bởi một lệnh lỗi đơn lẻ.
- **Bố cục trình bày trực quan:** Sơ đồ giải thuật hàm `batchSettleTrades`:
  ```solidity
  for (uint256 i = 0; i < trades.length; i++) {
      try this.executeSettlementExternal(trades[i]) {
          emit TradeSettled(...);
      } catch Error(string memory reason) {
          emit SettlementFailed(tradeHash, reason);
      } catch {
          emit SettlementFailed(tradeHash, "Unknown low-level failure");
      }
  }
  ```
- **Nội dung trọng tâm:**
  + **Giải quyết điểm nghẽn DoS:** Nếu một người mua cố tình rút hết tiền thanh toán USDC trước giờ khớp lệnh, trong mô hình thông thường toàn bộ batch 50 lệnh sẽ bị revert. Cơ chế `try/catch` độc lập của nhóm cô lập hoàn toàn lệnh lỗi, đảm bảo 49 lệnh hợp lệ còn lại vẫn được thanh toán thành công.
  + **Thanh toán nguyên tử T+0 (Atomic Swap):** Tiền USDC được chuyển từ ví Buyer sang Seller và tín chỉ EVCC được chuyển từ Seller sang Buyer trong cùng 1 transaction, không phát sinh bất kỳ độ trễ lưu ký nào.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Điểm cải tiến vượt bậc trong phiên bản v2 là cơ chế Batch Settlement cách ly lỗi. Bằng cách gọi qua wrapper external có try/catch, nếu có một người dùng quỵt tiền rút số dư trước, hợp đồng chỉ bỏ qua lệnh đó và ghi nhận lỗi, toàn bộ các lệnh chân chính khác trong lô vẫn được thực thi bình thường mà không bị ảnh hưởng."*

---

### 🟢 SLIDE 13: KẾT QUẢ BENCHMARK GAS THỰC TẾ TRÊN POLYGON AMOY TESTNET (TIẾT KIỆM >52%)
- **Tiêu đề Slide:** DỮ LIỆU ĐO LƯỜNG GAS THỰC TẾ TRÊN POLYGON AMOY (CHAIN ID 80002)
- **Mục tiêu học thuật:** Công bố kết quả thực nghiệm đo đạc on-chain chính thức, chứng minh tính kinh tế vượt trội của cơ chế thanh toán theo lô.
- **Bố cục trình bày trực quan:** Biểu đồ cột so sánh Gas tiêu thụ trung bình trên mỗi cặp lệnh giữa các cấu hình Batch:
  ```
  Chi phí Gas / Cặp lệnh
    300k ┤  ██ 286,145 gas (Đơn lẻ - Baseline)
    250k ┤  ██
    200k ┤  ██
    150k ┤  ██            ██ 152,677 (Batch 5: -46.6%)
    100k ┤  ██            ██            ██ 142,095 (Batch 10: -50.3%)
     50k ┤  ██            ██            ██            ██ 136,793 (Batch 20: -52.2%)
      0k └──┴─────────────┴─────────────┴─────────────┴────────► Cấu hình
  ```
- **Nội dung trọng tâm:**
  + Bảng đối soát Transaction Hash thực tế trên PolygonScan (dữ liệu từ `docs/BENCHMARK_RESULTS_AMOY.json`):
    * **Mint 100k tCO2e:** 309,894 gas (Tx: `0x700306...23c191`) – Chi phí: $0.0108$ POL ($\approx 0.004\$$)
    * **Settle 1 cặp đơn lẻ:** 286,145 gas (Tx: `0x96b795...fb82fe`) – Chi phí: $0.0100$ POL
    * **Batch 20 cặp lệnh:** 2,735,854 gas $\implies$ **136,793 gas/lệnh** (Tx: `0x5fc657...51e68`) – **Tiết kiệm 52.2%**
    * **Tiêu hủy ESG:** 66,365 gas (Tx: `0x007c64...4e128e`) – Chi phí: $0.0023$ POL
  + **Đánh giá tiêu chí NFR-02:** Mặc dù chi phí gas trên mạng testnet Polygon Amoy cao hơn EVM local do chi phí ấm slot lưu trữ, mức tiết kiệm $52.2\%$ khẳng định tính ưu việt của giải pháp kỹ thuật.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Nhóm đã triển khai hợp đồng và đo lường trực tiếp trên mạng Polygon Amoy thật chứ không chỉ dừng lại ở mô phỏng. Kết quả thực nghiệm với 20 cặp lệnh cho thấy cơ chế Batch Settlement giúp giảm hơn 52% lượng gas tiêu thụ. Với chi phí chỉ khoảng 0.004 USD cho một lần phát hành lô tín chỉ, hệ thống hoàn toàn sẵn sàng cho việc thương mại hóa thực tế."*

---

### 🟢 SLIDE 14: KIẾN TRÚC GIAO DIỆN WEB3 DAPP: 4 CỔNG PHÂN HỆ CHUYÊN BIỆT
- **Tiêu đề Slide:** THIẾT KẾ TRẢI NGHIỆM NGƯỜI DÙNG: BỘ 4 CỔNG PHÂN HỆ DAPP
- **Mục tiêu học thuật:** Trực quan hóa kiến trúc tương tác đa vai trò bám sát phân quyền RBAC và quy trình nghiệp vụ thị trường carbon.
- **Bố cục trình bày trực quan:** Lưới 4 ảnh chụp Mockup độ phân giải cao từ thư mục `docs/wireframes/`:
  ```
  +-----------------------------------+-----------------------------------+
  | 1. CỔNG CHỦ DỰ ÁN (PROJECT OWNER) | 2. CỔNG THẨM TRA VIÊN (VVB AUDIT) |
  | • Soạn thảo PDD, đẩy MRV lên IPFS | • Kiểm tra SHA-256 & CID tài liệu |
  | • Theo dõi tỷ lệ trích Buffer 15% | • Ký duyệt đúc tín chỉ on-chain   |
  +-----------------------------------+-----------------------------------+
  | 3. CỔNG SÀN GIAO DỊCH (TRADING)   | 4. CỔNG TIÊU HỦY ESG (RETIREMENT) |
  | • Sổ lệnh, Depth Chart, Đặt lệnh  | • Đốt tín chỉ vĩnh viễn           |
  | • Đồng hồ đếm ngược phiên đấu giá | • Xuất Giấy chứng nhận có mã QR   |
  +-----------------------------------+-----------------------------------+
  ```
- **Nội dung trọng tâm:**
  + **Phân quyền người dùng rõ rệt:** Giao diện tự động thích ứng theo vai trò ví kết nối (Project Developer, Verifier, Corporate Buyer, Trader).
  + **Chuẩn thiết kế công nghiệp:** Thiết kế trên Figma theo tỷ lệ 1440x1000px chuẩn desktop, hỗ trợ Dark Mode tối ưu cho các sàn giao dịch tài chính chuyên nghiệp.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Để phục vụ đa dạng các đối tượng trong hệ sinh thái tín chỉ carbon, bạn Thắng đã thiết kế 4 cổng phân hệ chuyên biệt. Từ chủ rừng nộp hồ sơ, kiểm toán viên quốc tế thẩm định, nhà đầu tư giao dịch đến các tập đoàn tiêu hủy tín chỉ để làm báo cáo ESG – tất cả đều được tích hợp trên một nền tảng Web3 thống nhất."*

---

### 🟢 SLIDE 15: TRẢI NGHIỆM SÀN GIAO DỊCH: SỔ LỆNH & BIỂU ĐỒ ĐỘ SÂU THỜI GIAN THỰC
- **Tiêu đề Slide:** PHÂN HỆ SÀN GIAO DỊCH & CÔNG NGHỆ WEBSOCKET REAL-TIME
- **Mục tiêu học thuật:** Phân tích kỹ thuật đồng bộ trạng thái sổ lệnh và biểu diễn trực quan độ sâu thị trường (Market Depth) phục vụ ra quyết định đầu tư.
- **Bố cục trình bày trực quan:** Ảnh chụp chi tiết mockup `docs/wireframes/03-trading-floor.png` làm nổi bật 3 khu vực:
  + Khu vực Đặt lệnh (Order Form): Lựa chọn BID/ASK, số lượng tCO2e, giá limit và loại lệnh GTC/IOC.
  + Khu vực Trực quan (Depth Chart): Biểu đồ diện tích xanh - đỏ biểu diễn khối lượng tích lũy mua và bán theo mức giá.
  + Khu vực Sổ lệnh & Đồng hồ phiên: Bảng giá khớp dự kiến $P^*$ và thời gian đếm ngược tới phiên khớp lệnh tiếp theo.
- **Nội dung trọng tâm:**
  + **Hiệu năng cập nhật:** Ứng dụng kênh truyền WebSocket `WS /ws/orderbook/{tokenId}` truyền phát chênh lệch sổ lệnh (Delta updates) với tần số 10Hz, độ trễ hiển thị dưới 50ms.
  + **Trải nghiệm ký mượt mà:** Tích hợp Wagmi v2 và thư viện Viem, hỗ trợ tự động gợi ý giá trần/giá sàn theo biên độ an toàn từ Oracle.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Màn hình sàn giao dịch mang lại cảm giác chuyên nghiệp như các sàn tài chính quốc tế. Biểu đồ độ sâu thị trường được vẽ theo thời gian thực qua WebSocket. Đặc biệt, đồng hồ đếm ngược phiên đấu giá giúp người tham gia biết chính xác thời điểm các lệnh được gom lại để khớp, tạo sự minh bạch tuyệt đối về thời gian."*

---

### 🟢 SLIDE 16: QUY TRÌNH ĐO ĐẠC - BÁO CÁO - THẨM TRA (MRV) & TIÊU HỦY ESG ON-CHAIN
- **Tiêu đề Slide:** TÍNH MINH BẠCH MRV & XÁC NHẬN TIÊU HỦY TÍN CHỈ VĨNH VIỄN
- **Mục tiêu học thuật:** Trình bày giải pháp loại bỏ triệt để vấn đề gian lận "Rửa xanh" (Greenwashing) và gian lận đếm hai lần (Double Counting) thông qua bằng chứng mật mã học bất biến.
- **Bố cục trình bày trực quan:**
  + Quy trình đính kèm mã băm SHA-256 của báo cáo kiểm định MRV vào IPFS và lưu trữ trực tiếp trên hợp đồng `CarbonCredit1155`.
  + Ảnh chụp mockup `docs/wireframes/04-esg-retirement.png` với mẫu Giấy chứng nhận Tiêu hủy Bù đắp Carbon (Certificate of Retirement) có mã QR trỏ thẳng tới transaction trên PolygonScan Amoy (`0x007c64...4e128e`).
- **Nội dung trọng tâm:**
  + **Bất biến hóa MRV:** Báo cáo kiểm định của bên thứ ba (VVB) sau khi thẩm định được tạo hàm băm băm bất biến; bất kỳ hành vi sửa đổi dữ liệu phát thải nào cũng sẽ làm sai lệch mã băm on-chain.
  + **Cơ chế Đốt vĩnh viễn (Permanent Burn):** Hàm `retireCarbonCredit` thực hiện chuyển token về địa chỉ `0x000...000` và giảm vĩnh viễn nguồn cung lưu hành của lô tín chỉ, đồng thời phát sinh sự kiện ghi nhận tên doanh nghiệp thụ hưởng để phục vụ kiểm toán ESG quốc tế.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Điểm yếu lớn nhất của thị trường carbon truyền thống là tình trạng bán một tín chỉ cho nhiều người. Hệ thống của chúng tôi giải quyết triệt để vấn đề này: khi doanh nghiệp muốn bù đắp phát thải, tín chỉ sẽ bị tiêu hủy vĩnh viễn trên chuỗi và hợp đồng xuất ngay một chứng chỉ ESG có mã QR kiểm toán công khai, không ai có thể làm giả hay dùng lại."*

---

### 🟢 SLIDE 17: PHÂN TÍCH MÔ HÌNH ĐE DỌA BẢO MẬT (STRIDE) & GIẢI PHÁP CHỐNG MEV
- **Tiêu đề Slide:** ĐÁNH GIÁ AN NINH HỆ THỐNG KIẾN TRÚC LAI (THREAT MODELING)
- **Mục tiêu học thuật:** Trình bày kết quả nghiên cứu an toàn thông tin chuyên sâu từ tài liệu `docs/THREAT_MODELING.md`, áp dụng mô hình phân loại STRIDE cho hệ thống lai Off-chain/On-chain.
- **Bố cục trình bày trực quan:** Bảng đối sánh 4 mối đe dọa an ninh nguy hiểm nhất và giải pháp kỹ thuật đã cài đặt trong mã nguồn:
  | Vector Tấn công | Mô tả Nguy cơ | Giải pháp Kỹ thuật Đã Triển khai |
  | :--- | :--- | :--- |
  | **Operator Front-running** | Người vận hành sàn chèn lệnh riêng hưởng lợi | Cam kết hàm băm trạng thái sổ lệnh (State Commitment Hash) |
  | **MEV Searcher Arbitrage** | Bot blockchain chèn giao dịch trước batch | Khóa quyền gọi thanh toán qua `SETTLEMENT_OPERATOR_ROLE` |
  | **Rò rỉ Khóa Ví Bot** | Kẻ tấn công chiếm đoạt quyền ví Submitter | Hợp đồng chỉ cho phép thanh toán theo chữ ký, không cho rút quỹ |
  | **Spam Lệnh Tích Tuổi** | Kẻ gian tạo ví rác spam lệnh để chiếm ưu thế Hamilton | Ràng buộc khối lượng tối thiểu và giới hạn số lần đảo sổ (max rollover = 3) |
- **Nội dung trọng tâm:**
  + **Tách biệt ví Operator:** Nghiêm cấm dùng ví Deployer cho bot; mỗi thành viên tự tạo ví riêng và chỉ được cấp quyền thanh toán hữu hạn.
  + **Phòng chống DoS từ Hook ERC-1155:** Bot tự động kiểm tra và bỏ qua các địa chỉ ví là hợp đồng thông minh nếu chưa có xác minh an toàn để tránh việc đối tác kích hoạt mã độc làm cạn kiệt gas của cả batch.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Một sàn giao dịch tiền tệ phi tập trung không thể thiếu phân tích an ninh. Nhóm đã thực hiện mô hình hóa đe dọa bảo mật theo chuẩn STRIDE. Chúng tôi đã lường trước các kịch bản tấn công như MEV bot, rò rỉ khóa hay spam lệnh, và cài đặt sẵn các chốt chặn phòng thủ tương ứng ngay từ tầng mã nguồn."*

---

### 🟢 SLIDE 18: KẾT QUẢ KIỂM THỬ LIÊN THÔNG TOÀN TRÌNH (END-TO-END ON-CHAIN PROOFS)
- **Tiêu đề Slide:** KIỂM THỬ TÍCH HỢP TOÀN TRÌNH & MINH CHỨNG THỰC NGHIỆM
- **Mục tiêu học thuật:** Báo cáo các chỉ số kiểm thử tự động toàn diện và minh chứng giao dịch thanh toán thực tế thành công trên mạng Polygon Amoy ngày 17/11/2026.
- **Bố cục trình bày trực quan:**
  + Bảng chỉ số kiểm thử phần mềm tự động (Test Automation Matrix):
    * **Matching Engine Test Suite:** **101/101 tests PASS** (Bao gồm test API, lõi số nguyên, mô phỏng và Submitter bot)
    * **Smart Contract Test Suite:** **14/14 tests PASS** (Hardhat local test coverage 100% cho 7 chốt chặn)
    * **Web3 Frontend & Schema:** **24/24 tests PASS** (14 tests UI Vitest + 10 tests Metadata validation)
  + Minh chứng giao dịch Settlement trực tiếp đầu tiên trên Amoy:
    ```
    Transaction Hash: 0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8
    Block Number:     53,082,140
    Gas Used:         275,741 gas
    Status:           SUCCESS (Event TradeSettled Emitted)
    Transfers:        Buyer nhận 5 EVCC (#101), Seller nhận 50 USDC
    ```
- **Nội dung trọng tâm:**
  + Khắc phục triệt để lỗi PoA middleware trên chuỗi Polygon Amoy trong Web3.py.
  + Script kiểm thử toàn trình `scripts/test_e2e_integration.py` tự động hóa liên thông 5 bước hoạt động hoàn hảo.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Để chứng minh hệ thống hoạt động thực chất, ngày 17/11 vừa qua nhóm đã kích hoạt thành công phiên giao dịch thật đầu tiên trên mạng Polygon Amoy với Transaction Hash công khai. Toàn bộ 139 bài kiểm thử tự động trên cả 3 phân hệ đều đạt tỷ lệ vượt qua 100%, khẳng định độ tin cậy và tính ổn định vượt trội của mã nguồn."*

---

### 🟢 SLIDE 19: KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN 3 & ĐỊNH HƯỚNG BÀI BÁO KHOA HỌC
- **Tiêu đề Slide:** KẾ HOẠCH NGHIÊN CỨU GIAI ĐOẠN 3 & ĐẦU RA KHOA HỌC
- **Mục tiêu học thuật:** Vạch rõ lộ trình phát triển trong giai đoạn tiếp theo hướng tới nghiệm thu đề tài cấp trường và công bố bài báo khoa học chuẩn quốc tế.
- **Bố cục trình bày trực quan:** Sơ đồ lộ trình phát triển (Gantt Chart / Roadmap) từ tháng 12/2026 đến tháng 04/2027:
  ```
  [12/2026]: Hoàn thiện tích hợp DApp với Oracle giá ngoài chuỗi (Chainlink)
  [01/2027]: Triển khai mạng thử nghiệm nội bộ quy mô lớn (Stress Test 1,000 TPS)
  [02/2027]: Soạn thảo bản thảo bài báo khoa học (Manuscript Draft)
  [03/2027]: Thử nghiệm ứng dụng thực tế với số liệu dự án năng lượng tái tạo tại VN
  [04/2027]: Báo cáo Nghiệm thu Chính thức Đề tài NCKH Sinh viên Cấp Trường
  ```
- **Nội dung trọng tâm:**
  + **Mục tiêu công bố bài báo:** Đăng ký công bố 01 bài báo khoa học tại Hội nghị quốc tế hoặc Tạp chí chuyên ngành uy tín (Scopus/Web of Science hoặc Tạp chí Khoa học & Công nghệ ĐH Điện Lực) với chủ đề: *"A Hybrid Multi-Agent and Blockchain-Based Double Auction Mechanism for Transparent Voluntary Carbon Credit Trading"*.
  + **Nâng cấp công nghệ:** Thử nghiệm giải pháp Zero-Knowledge Proofs (zk-SNARKs) để bảo mật danh tính doanh nghiệp và mức giá bỏ thầu nhạy cảm mà vẫn đảm bảo tính toán đúng đắn.
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Bước sang Giai đoạn 3, nhóm sẽ tập trung vào hai nhiệm vụ chiến lược: thứ nhất là nâng cao hiệu năng chịu tải của hệ thống qua kiểm thử áp lực; thứ hai là hoàn thiện bản thảo bài báo khoa học dựa trên những kết quả thực nghiệm lý thuyết trò chơi và số liệu đo đạc blockchain đã tích lũy được."*

---

### 🟢 SLIDE 20: TỔNG KẾT GIÁ TRỊ ĐỀ TÀI, LỜI CẢM ƠN & PHIÊN HỎI - ĐÁP (Q&A)
- **Tiêu đề Slide:** TỔNG KẾT & PHIÊN THẢO LUẬN (Q&A)
- **Mục tiêu học thuật:** Khái quát lại các đóng góp nổi bật của đề tài, bày tỏ lòng tri ân sâu sắc tới người hướng dẫn và mở phiên trao đổi chuyên môn với Hội đồng khoa học.
- **Bố cục trình bày trực quan:**
  + Tóm lược 3 giá trị đóng góp cốt lõi:
    1. **Đóng góp Lý thuyết:** Xác lập và kiểm chứng thực nghiệm mô hình $k$-DA giảm thiểu tổn thất xã hội với tốc độ $O(1/m^2)$ trong giao dịch tín chỉ carbon.
    2. **Đóng góp Kỹ thuật:** Thiết kế kiến trúc lai MAS - Blockchain tối ưu hóa gas ($>52\%$), giải quyết bài toán nan giải giữa chi phí và tính minh bạch.
    3. **Đóng góp Ứng dụng:** Xây dựng trọn vẹn sản phẩm DApp Web3 trực quan, có thể triển khai thí điểm thực tế ngay cho các dự án lâm nghiệp và năng lượng sạch.
  + Thông tin liên hệ và liên kết mã nguồn mở:
    * **GitHub Repository:** `HuyDangXuan/Blockchain-NCKH`
    * **Email liên hệ:** `dangxuanhuy.epu@gmail.com`
- **Lời thuyết minh gợi ý (Speaker Notes):**
  > *"Nhóm nghiên cứu xin trân trọng cảm ơn sự định hướng khoa học tận tình của TS. Nguyễn Thị Hồng Khánh cùng sự ủng hộ của Khoa CNTT - Trường ĐH Điện Lực trong suốt thời gian qua. Chúng em xin kính mời cô và Hội đồng đưa ra những câu hỏi, nhận xét quý báu để nhóm tiếp tục hoàn thiện đề tài tốt hơn nữa. Em xin trân trọng cảm ơn!"*

---
*Tài liệu đề cương slide báo cáo này là căn cứ chính thức để thiết kế bộ slide trình chiếu `.pptx` cho buổi báo cáo tiến độ Giai đoạn 2.*
