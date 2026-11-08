# Các vấn đề cần trao đổi — phần Matching Engine (Nguyễn Bảo Phi)

Cập nhật: 08/11/2026. Nguồn: đối chiếu `docs/MATCHING_ENGINE_SPEC.md` với `docs/SMART_CONTRACT_SPEC.md` của Đức (branch `docs/smart-contract-spec`, commit `3194bad`), review chéo bằng model khác, và chạy thử code `system_agents/matching_engine/`. Mỗi mục ghi **bằng chứng** để người nhận kiểm lại được. Nhãn: `NOT VERIFIED` = chưa có bằng chứng độc lập.

## 1. Với Đức (smart contract, EIP-712)

| # | Vấn đề | Bằng chứng | Đề xuất / câu hỏi | Mức |
|---|---|---|---|---|
| Đ1 | **Đơn vị `amount`** mâu thuẫn: kg CO2e hay tCO2e (chênh 1000 lần). | Spec của Đức §3.2 ghi `kg CO2e`; báo cáo GĐ1 ghi 1 token = 1 tCO2e; `CarbonCredit1155.sol` trên `main` không nêu. | Chốt một đơn vị cho cả hợp đồng, engine, mô phỏng, UI. | Cao |
| Đ2 | Kiểm `filledAmount` chỉ nêu cho **phía bid**. | Spec Đức §3.3, bước 3: `filledAmount[bidId] + matchAmount <= bidOrder.amount`. | Kiểm cả `askOrder`; nếu không, ask có thể bị khớp vượt `amount` qua nhiều phiên. | Cao |
| Đ3 | **Đơn vị `pricePerUnit`**: "wei USDC" không rõ. | Spec Đức §3.2 comment ở `pricePerUnit`; USDC thật có 6 chữ số thập phân, token test có thể khác. | Ghi rõ token thanh toán, số thập phân, và tick giá. Engine cần số nguyên và công thức làm tròn của giá khớp. | Cao |
| Đ4 | **Hướng làm tròn `clearingPrice`**. Hợp đồng revert `PriceMismatch` nếu ra ngoài [ask, bid]. | Spec Đức §3.3 bước 2. Baseline `auction_agent.py` làm tròn 2 chữ số và có thể ra ngoài khoảng (ask=10.001, bid=10.004, k=0 → 10.0). | Thống nhất: làm tròn xuống trên số nguyên đủ bảo đảm trong [ask, bid]. | Cao |
| Đ5 | `time_in_force` (GTC/IOC) **không nằm trong struct được ký**. | Spec Đức §3.2 `ORDER_TYPEHASH`. | Thêm `timeInForce` vào struct được ký, hoặc chấp nhận đó chỉ là tùy chọn của engine (ghi rõ trong tài liệu người dùng). | Trung bình |
| Đ6 | **Ngữ nghĩa `incrementNonce`**: vô hiệu hóa mọi lệnh cũ hay chỉ một lệnh? Lệnh GTC đang nằm trong sổ khi người dùng tăng nonce thì sao? | Spec Đức §3.4: chỉ có chữ ký hàm `incrementNonce()`. | Mô tả hành vi; engine sẽ đọc lại nonce ngay trước khi gửi. | Trung bình |
| Đ7 | **Ai được gọi `cancelOrder`**? Spec chỉ nêu giao diện. | Spec Đức §3.4. | Chỉ `trader` của lệnh; thêm vào spec. | Trung bình |
| Đ8 | `matchAmount = 0` có bị từ chối không? Pro-rata có thể sinh phần chia bằng 0. | Spec Matching §5.2, §6.1. | Hợp đồng revert khi `matchAmount == 0`, engine bỏ qua các lần khớp bằng 0. | Thấp |
| Đ9 | **Quyền gọi `settleMatchedTrade`**: `onlyMatchingAgent` (code `main`) hay ai cũng gọi được vì chữ ký đã xác minh on-chain? | Code `CarbonDoubleAuction.sol` trên `main`; spec Đức không nói. | Nếu ai cũng gọi được, engine ngừng hoạt động không làm tắc settlement; đổi lại thứ tự giao dịch phụ thuộc người gọi (MEV). Cần quyết định có chủ ý. | Trung bình |
| Đ10 | **`orderId = keccak256(trader, nonce, timestamp)`**: `timestamp` do ai cung cấp? Engine cần `orderId` duy nhất trước khi nhận lệnh. | Spec Đức §3.2, comment của `orderId`. | Client tính và ký; engine từ chối `orderId` trùng. | Thấp |
| Đ11 | **`contracts/` trên `main` chưa theo spec mới**: không có thanh toán ERC-20, không xác minh chữ ký. Branch `docs/smart-contract-spec` chưa merge. | `contracts/CarbonDoubleAuction.sol` trên `main` chỉ gọi `safeTransferFrom` của token carbon. | Kế hoạch cập nhật code và thứ tự merge; spec Matching đã bám theo spec mới. | Trung bình |
| Đ12 | Số liệu gas (112k, 145k, 920k) **chưa được benchmark thực** (`NOT VERIFIED`). Engine dùng nó để chọn kích thước batch. | Spec Đức §5. | Khi có testnet, đo lại và gửi bảng số liệu thật. | Thấp |

## 2. Với Huy (chủ nhiệm: phạm vi, SRS/UML, Google Doc)

| # | Vấn đề | Bằng chứng | Đề xuất | Mức |
|---|---|---|---|---|
| H1 | **Câu chữ nhiệm vụ 3 trên Google Doc** ("so sánh social welfare giữa k = 0, 0.5, 1 để tìm tham số tối ưu") sẽ không cho kết quả: với khai giá trung thực, welfare **bằng nhau** với mọi k. | `run_experiment.py a`, kết quả ở `system_agents/matching_engine/simulation/results/exp_a_*` (90 cặp n × seed, tính lại độc lập, reviewer model khác xác nhận). Đây là hệ quả đại số của công thức giá (`buyer_share = 1 − k`), nên chỉ là kiểm tra đúng đắn, không phải phát hiện. | Đổi thành: (A) kiểm tra đúng đắn + cách chia thặng dư theo k khi khai trung thực; (B) đo mất phúc lợi khi người tham gia khai giá chiến lược (đã có B1 mỏ neo và B2 quét cường độ; chưa có cân bằng thị trường nhiều lệnh). | Cao |
| H5 | **Kết quả thí nghiệm B2 dễ bị đọc sai.** efficiency ≈ 0,92–0,94 và "không tăng theo n" là hệ quả của chiến lược cố định, không phải cân bằng. | Spec Matching §9.5. | Không trích các con số này như kết luận về thị trường chiến lược; chỉ trình bày là độ nhạy với cường độ khai giá. Mẫu giữa các n lồng nhau và engine định giá theo từng cặp (không phải giá đồng nhất) cũng phải ghi trong báo cáo. | Trung bình |
| H2 | Các quyết định thiết kế **cần nhóm/GVHD chốt** (spec Matching §11): độ dài phiên đấu giá; tie-break mặc định (`age_prorata` hay `fifo`); giá theo cặp hay giá chung của phiên; giới hạn rollover của lệnh GTC. | Spec Matching §5.2, §7, §11. | Họp nhóm chốt trước tuần 3 để API Service thiết kế theo đó. | Cao |
| H3 | **SRS/UML** cần phản ánh vòng đời lệnh và rollover: trạng thái `NEW → … → ROLLED_OVER`, use case đặt/hủy lệnh, phiên đấu giá, thông báo kết quả. | Spec Matching §4, §6, §8. | Dùng sơ đồ trạng thái §4 làm đầu vào cho Activity/Sequence Diagram. | Trung bình |
| H4 | Báo cáo chung nên ghi rõ **mức chứng cứ**: hệ số Chatterjee–Samuelson (k = 0,5: 1/12, 2/3, 1/4, 2/3) có hai nguồn arXiv và suy ra dạng đóng cho mọi k, nhưng **chưa đọc bài gốc (1983)**; nguồn [R1] chưa đọc toàn văn; một nguồn thứ cấp nêu "1/6" không khớp với suy ra của nhóm (9/32 và 27/32). | Spec Matching §9.1, §12. | Không trích hệ số hay con số 1/6 vào báo cáo chung trước khi có bài gốc. | Trung bình |

## 3. Với Thắng (nghiệp vụ carbon, Metadata, DApp/UI)

| # | Vấn đề | Bằng chứng | Đề xuất | Mức |
|---|---|---|---|---|
| T1 | **Lớp tín chỉ nào được khớp với nhau?** Engine chỉ khớp lệnh cùng `token_id` và không đánh giá tính thay thế. Cần quy tắc nghiệp vụ: những lô khác vintage/dự án có coi là cùng lớp không. | Spec Matching §3.3. | Thắng đưa tiêu chí `eligibility`; nếu cần gộp nhiều `token_id` thì engine phải đổi. | Trung bình |
| T2 | **Wireframe "Trading Floor"** cần dữ liệu từ API của engine. | Spec Matching §8.2–§8.3 (REST + WebSocket). | Đối chiếu các màn hình với endpoint/sự kiện đã đặc tả; đơn vị giá và khối lượng hiển thị phải theo kết luận Đ1, Đ3. | Trung bình |
| T3 | `METADATA_SCHEMA.json` phải nêu rõ cách suy ra "lớp tín chỉ" từ metadata (project type, vintage, standard) để sổ lệnh và UI lọc được. | Spec Matching §3.3. | Thêm trường/quy ước nhóm lô. | Thấp |

## 4. Việc của chính Phi chưa xong (không phụ thuộc bên nào)
- Đọc **bài gốc** Chatterjee–Samuelson (1983) và Satterthwaite–Williams (1989) để xác minh hệ số; nguồn hiện có chỉ là thứ cấp và phép tính số.
- Tìm phản ứng tối ưu (ε-equilibrium) ngay trong thị trường nhiều lệnh nhiều đơn vị và kiểm định dự đoán mất hiệu quả O(1/m²) bằng mẫu độc lập giữa các n; hiện B2 chỉ quét cường độ khai giá ngoại sinh.
- Đối chiếu câu trả lời của Argon (mức suy nghĩ "Cao") với bài gốc trước khi dùng; `docs/MATCHING_ENGINE_SPEC.md` §9.
- Cài `age_prorata`, rollover và API Service (Giai đoạn 3); viết test case và threat modeling (tuần 5–8).
