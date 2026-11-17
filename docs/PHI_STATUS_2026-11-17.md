# Tình hình công việc của Phi (cập nhật 17/11/2026)

Nhánh: `feat/phi-settlement-submitter-bot`. Chưa push tại thời điểm viết file này. Test engine: 101 test OK (chạy 17/11/2026, thư viện theo `system_agents/matching_engine/requirements.txt`).

## Đã xong (đã commit)

| Nhiệm vụ | Sản phẩm | Ghi chú |
| --- | --- | --- |
| P.1 Bot settlement | `system_agents/matching_engine/settlement_submitter.py`, test, `docs/SETTLEMENT_SUBMITTER_GUIDE.md` | Test local và e2e pass. Chưa chạy trên Amoy thật. |
| P.3 Threat modeling | `docs/THREAT_MODELING.md` | Đã qua review độc lập, các phát hiện đã tự kiểm trước khi tích hợp. |
| P.4 Chuẩn hóa theo paper | `docs/MATCHING_ENGINE_SPEC.md` | H4 xong; H7 làm rõ tên; H7 A/B và H8 chờ Huy. |
| P.2 Thực nghiệm C mở rộng | `export_strategies_c.py`, `run_experiment_c_multiunit.py`, `results/exp_c_*`, spec §9.5 | Xem giới hạn bên dưới. |

## P.2 vẫn đang chạy thử (sẽ cập nhật ở phiên sau)

Phi vẫn đang chạy thử Thực nghiệm C ở các mức tham số khác (m, k, số kịch bản, số vòng lặp) để có output chuẩn nhất. Các số liệu P.2 dưới đây là kết quả tạm thời, **chưa phải bản chốt**; bản chốt (kèm CSV thô và độ dốc đã tái tính) sẽ được cập nhật ở phiên sau.

## Giới hạn của P.2 (cần ghi khi trích dẫn)

- k = 1: m đến 64. Độ dốc log-log: `pair` −0,95 ± 0,02, `marginal` −1,79 ± 0,05, `kda` −2,25 ± 0,06 (chỉ m = 4…32; `kda` phẳng ở m ≥ 32 và m = 64 không hội tụ).
- k = 0,5: chỉ trích dẫn đến m = 16 (độ dốc ≈ −2,1). Ở m ≥ 32 tìm cân bằng không hội tụ; tăng kịch bản và vòng lặp không sửa được; nguyên nhân chưa rõ (UNKNOWN).
- Nhiều đơn vị mỗi lệnh chỉ là kiểm tra độ bền (áp chiến lược một đơn vị), không phải cân bằng nhiều đơn vị.
- Oracle `max_amount = 1`: `marginal` và `kda` khớp loss một đơn vị; `pair` lệch 1–9% ở m = 8, 16 do luật hòa giá (chiến lược phẳng), không phải lỗi.
- CSV thô từng cấu hình m = 32, 64 và k = 0,5 đã mất. Các độ dốc m = 2…64 **NOT VERIFIED** cho đến khi chạy lại.

## Đang chờ

| Việc | Chờ ai | Trạng thái |
| --- | --- | --- |
| Chạy bot trên Amoy | Đức | Ví Operator `0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE` đã tạo, đang có 0,001 POL (chưa đủ). Cần cấp `SETTLEMENT_OPERATOR_ROLE`, chuyển khoảng 0,1 POL, và gửi địa chỉ hợp đồng. Yêu cầu: `docs/OPERATOR_WALLET_REQUEST.md`. |
| H7 A/B, H8, H10 | Huy | Chưa có trả lời. Huy đã xác nhận cứ push ở nhánh hiện tại. |
| Deadline P.3 (18/11 hay 20/11), tổng thể (20/11 hay 25/11) | Huy | Kế hoạch ghi hai mốc khác nhau. |
| Lỗi hợp đồng: `cancelOrder` kiểm soát truy cập, `tradeHash` thiếu `sessionId`, giới hạn gas từng trade, tách ví Operator khỏi deployer, tên sự kiện cũ trong SRS | Đức | Đã ghi trong `docs/THREAT_MODELING.md` và guide của bot. |

## Việc của Phi / Claude

1. Push nhánh lên `origin/feat/phi-settlement-submitter-bot` khi Phi đồng ý (không push `main`; Huy merge).
2. Sau khi Đức cấp role và có POL: chạy bot `--dry-run`, rồi một phiên nhỏ, đối chiếu event `TradeSettled`.
3. Tùy chọn: chạy lại P.2 để có CSV thô m = 32, 64 (mất nhiều giờ).
