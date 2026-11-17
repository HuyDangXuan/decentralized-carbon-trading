# Yêu cầu cấp quyền cho ví Operator (bot Settlement Submitter, Task P.1)

Gửi: Đức. Từ: Phi. Mạng: Polygon Amoy.

## Địa chỉ ví Operator

```
0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE
```

Ví tạo riêng cho bot, không dùng ví deployer. Khóa riêng chỉ nằm ở máy của Phi, không chia sẻ.

## Đề nghị Đức giúp

1. Cấp `SETTLEMENT_OPERATOR_ROLE` cho địa chỉ trên bằng `grantRole` trên hợp đồng `CarbonDoubleAuction` (Amoy).
2. Gửi địa chỉ hợp đồng `CarbonDoubleAuction` đã deploy trên Amoy (và địa chỉ token thanh toán, tín chỉ ERC-1155 nếu khác), để ghi vào `docs/DEPLOYED_ADDRESSES.md`.
3. Chuyển giúp **0,1 POL (Amoy)** vào địa chỉ ví trên để trả gas. Faucet công khai đòi ví có ETH thật trên Mainnet nên Phi không tự nạp được.
4. Báo lại mã giao dịch `grantRole` (và giao dịch chuyển POL) để Phi kiểm tra bằng `hasRole` và số dư.

## Phi sẽ làm sau khi có quyền

- Chạy bot với `--dry-run` (chỉ đọc chain), rồi nộp thật một phiên nhỏ.
- Đối chiếu event `TradeSettled` trên chain với báo cáo của bot và báo kết quả cho nhóm.

## Ghi chú liên quan (đã ghi trong `docs/THREAT_MODELING.md`, `docs/SETTLEMENT_SUBMITTER_GUIDE.md`)

- Bot chưa đặt giới hạn gas riêng cho từng trade (cần sửa hợp đồng).
- `tradeHash` thiếu `sessionId` (mục 3.2 của `docs/THREAT_MODELING.md`), cần Đức xem xét.
