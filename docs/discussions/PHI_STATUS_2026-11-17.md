# Tình hình công việc của Phi (cập nhật 17/11/2026)

Nhánh làm việc: `feat/phi-settlement-submitter-bot`, đã push lên `origin/auction-algorithm-engineer` (theo xác nhận của Huy: push ở nhánh hiện tại). Test engine: 101 test OK (chạy 17/11/2026, thư viện theo `system_agents/matching_engine/requirements.txt`).

## Đã xong (đã commit)

| Nhiệm vụ | Sản phẩm | Ghi chú |
| --- | --- | --- |
| P.1 Bot settlement | `system_agents/matching_engine/settlement_submitter.py`, test, `docs/SETTLEMENT_SUBMITTER_GUIDE.md` | Test local và e2e pass. **Đã chạy thật trên Amoy 17/11/2026**: 1 trade `SETTLED`, TxHash `0x9619ff0b…75b8`, số dư hai ví khớp. Chi tiết: `docs/SETTLEMENT_SUBMITTER_GUIDE.md`, mục "Kết quả chạy thật trên Amoy". |
| P.3 Threat modeling | `docs/THREAT_MODELING.md` | Đã qua review độc lập, các phát hiện đã tự kiểm trước khi tích hợp. |
| P.4 Chuẩn hóa theo paper | `docs/MATCHING_ENGINE_SPEC.md` | H4 xong; **H7**: Huy đã phê duyệt Phương án A (chuẩn hóa tên kỹ thuật là `marginal` theo ADR-001); **H8**: Huy đã xác nhận vòng đời GTC tối đa 3 phiên (`max_rollover = 2`). |
| P.2 Thực nghiệm C mở rộng | `export_strategies_c.py`, `run_experiment_c_multiunit.py`, `results/exp_c_*`, spec §9.5 | Xem giới hạn bên dưới. |

## P.2 vẫn đang chạy thử (sẽ cập nhật ở phiên sau)

Phi vẫn đang chạy thử Thực nghiệm C ở các mức tham số khác (m, k, số kịch bản, số vòng lặp) để có output chuẩn nhất. Các số liệu P.2 dưới đây là kết quả tạm thời, **chưa phải bản chốt**; bản chốt (kèm CSV thô và độ dốc đã tái tính) sẽ được cập nhật ở phiên sau.

## Giới hạn của P.2 (cần ghi khi trích dẫn)

- k = 1: m đến 64. Độ dốc log-log: `pair` −0,95 ± 0,02, `marginal` −1,79 ± 0,05, `kda` −2,25 ± 0,06 (chỉ m = 4…32; `kda` phẳng ở m ≥ 32 và m = 64 không hội tụ).
- k = 0,5: chỉ trích dẫn đến m = 16 (độ dốc ≈ −2,1). Ở m ≥ 32 tìm cân bằng không hội tụ; tăng kịch bản và vòng lặp không sửa được; nguyên nhân chưa rõ (UNKNOWN).
- Nhiều đơn vị mỗi lệnh chỉ là kiểm tra độ bền (áp chiến lược một đơn vị), không phải cân bằng nhiều đơn vị.
- Oracle `max_amount = 1`: `marginal` và `kda` khớp loss một đơn vị; `pair` lệch 1–9% ở m = 8, 16 do luật hòa giá (chiến lược phẳng), không phải lỗi.
- CSV thô từng cấu hình m = 32, 64 và k = 0,5 đã mất. Các độ dốc m = 2…64 **NOT VERIFIED** cho đến khi chạy lại.

## Bot chạy thật trên Amoy (17/11/2026)

- Đức đã cấp `SETTLEMENT_OPERATOR_ROLE` cho ví Operator, chuyển POL, đưa địa chỉ hợp đồng (`docs/DEPLOYED_ADDRESSES.md`) và cấp tài sản cho hai ví thử. Phi đã xác minh bằng `hasRole` và số dư trên chain.
- Phiên thử: khớp 5 đơn vị ở giá 10 USDC, giao dịch `batchSettleTrades` thành công (gas 275.741), event `TradeSettled`, số dư bên mua và bên bán thay đổi đúng.
- Lỗi tìm thấy khi chạy thật và đã sửa (commit `2a4c3bf`): thiếu middleware PoA, bot không đọc được block Amoy.
- Giới hạn: mới chạy một phiên một trade. Chưa thử batch nhiều trade, trade lỗi, hết giờ chờ biên nhận, `--recover-tx` trên chuỗi thật.

## Cần Huy / Đức xác nhận (mới)

| Việc | Chờ ai | Chi tiết |
| --- | --- | --- |
| Gas thực tế | Đức | `batchSettleTrades` cho 1 trade tốn 275.741 gas trên Amoy. Đức đối chiếu với benchmark gas của Đ.4 (`docs/SMART_CONTRACT_SPEC.md`); nếu lệch nhiều thì cần xem lại. |
| Ví Operator | Đức | Ví `0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE` hiện giữ `SETTLEMENT_OPERATOR_ROLE`; xác nhận chỉ cấp cho ví này (không dùng ví deployer cho bot) và quy trình thu hồi role nếu lộ khóa. |
| Script `scripts/setup_operator_bot.js` của Đức | Đức | Phi mới đọc phần cấp role, chưa đọc kỹ phần còn lại; cần Đức xác nhận script không cấp quyền nào khác ngoài `SETTLEMENT_OPERATOR_ROLE`. |
| Luồng demo 18/11 | Huy | Bot cần engine API chạy sẵn (`AUCTION_CONTRACT_ADDRESS`, `MATCHING_API_KEY`) và hai bên có tài sản + allowance. Huy xác nhận ai chạy engine trong buổi demo và ví nào làm bên mua, bên bán. |
| Phiên engine | Huy | Engine giữ phiên trong bộ nhớ; khởi động lại thì số phiên về 1. Cần Huy quyết định có lưu phiên xuống DB không, vì `tradeHash` chưa có `sessionId` (xem bên dưới). |

## Đang chờ

| Việc | Chờ ai | Trạng thái |
| --- | --- | --- |
| H7 A/B, H8 | Huy | ✅ **Đã giải quyết (17/11/2026)**: Huy (Lead Architect) chốt Phương án A cho H7 (xác nhận tên gọi kỹ thuật chính thức là `marginal`, giữ nguyên công thức ADR-001 $P^* = \lfloor(b_M + s_M)/2\rfloor$ và `PRICING_RULE = "marginal"`); xác nhận H8 (vòng đời GTC tối đa 3 phiên, `max_rollover = 2` tương ứng 3 phiên). |
| H10 | Huy | ✅ Huy đã xác nhận tiếp tục push ở nhánh hiện tại. |
| Deadline P.3 (18/11 hay 20/11), tổng thể (20/11 hay 25/11) | Huy | Kế hoạch ghi hai mốc khác nhau. |
| Lỗi hợp đồng: `cancelOrder` kiểm soát truy cập, `tradeHash` thiếu `sessionId`, giới hạn gas từng trade, tách ví Operator khỏi deployer, tên sự kiện cũ trong SRS | Đức | Đã ghi trong `docs/THREAT_MODELING.md` và guide của bot. |

## Việc của Phi / Claude

1. Chờ Huy và Đức trả lời các mục ở bảng "Cần Huy / Đức xác nhận".
2. Thử bot với batch nhiều trade và các trường hợp lỗi trên Amoy.
3. Tùy chọn: chạy lại P.2 để có CSV thô m = 32, 64 (mất nhiều giờ).
