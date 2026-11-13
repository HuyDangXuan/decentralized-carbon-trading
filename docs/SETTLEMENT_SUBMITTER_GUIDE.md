# Hướng dẫn chạy Bot Settlement Submitter (Task P.1)

Bot đưa kết quả khớp lệnh của một phiên từ Matching Engine lên `CarbonDoubleAuction.batchSettleTrades` trên Polygon Amoy. Mã nguồn: `system_agents/matching_engine/settlement_submitter.py`.

## Luồng

```
Trader --POST /orders (EIP-712)--> API (api_service.py) --run_session--> MatchResult[]
Bot  --GET /sessions/{id}/trades--> hai lệnh đã ký + khối lượng + giá  (cần X-API-Key nếu API đặt admin_key)
Bot  --kiểm tra trước (đọc chain)--> batchSettleTrades (ví Operator ký)
Bot  --đọc event TradeSettled từng trade--> POST /settlements/confirm --> engine ghi settled_amount
```

Trạng thái mỗi trade trong báo cáo của bot:

| Trạng thái | Ý nghĩa |
| --- | --- |
| `SETTLED` | Có event `TradeSettled` trên chuỗi |
| `SKIPPED` | Không gửi: payload sai hoặc kiểm tra trước thất bại (hết hạn, đã hủy on-chain, nonce thấp hơn, `tradeHash` đã dùng, vượt khối lượng đã ký, chữ ký không khớp) |
| `FAILED` | Đã gửi nhưng hợp đồng bỏ qua trade trong `try/catch` (thường thiếu allowance hoặc số dư) |

Giao dịch `batchSettleTrades` vẫn thành công khi có trade lỗi bên trong; bot chỉ dựa vào event, không dựa vào trạng thái giao dịch.

## Chuẩn bị chạy trên Amoy (làm một lần)

1. Cài thư viện: `pip install -r system_agents/matching_engine/requirements.txt`.
2. Tạo ví Operator riêng (không dùng ví deployer):
   ```
   python scripts/new_operator_wallet.py
   ```
   Lệnh chỉ in địa chỉ ví; khóa riêng được ghi vào `.env` ở gốc repo (file đã nằm trong `.gitignore`, không commit).
3. Gửi địa chỉ ví cho Đức để cấp `SETTLEMENT_OPERATOR_ROLE` (`grantRole`), và nạp POL từ faucet Amoy cho ví này để trả gas.
4. Địa chỉ hợp đồng lấy từ `docs/DEPLOYED_ADDRESSES.md` (do Đức bàn giao).

## Chạy

Biến môi trường: `SETTLEMENT_OPERATOR_PRIVATE_KEY` (bắt buộc), `AUCTION_CONTRACT_ADDRESS` (hoặc `--contract`), `AMOY_RPC_URL` (tùy chọn), `MATCHING_API_KEY` (đặt giá trị này cho cả API và bot để bảo vệ `/sessions/run`, `/sessions/{id}/trades`, `/settlements/confirm`; không đặt thì các endpoint đó mở công khai, chỉ dùng khi chạy thử cục bộ).

```
cd system_agents/matching_engine
uvicorn api_service:app --port 8000          # cửa sổ 1: API, đặt AUCTION_CONTRACT_ADDRESS trước khi chạy
python settlement_submitter.py --session-id 1 --dry-run   # chỉ kiểm tra trước, không gửi giao dịch
python settlement_submitter.py --session-id 1             # nộp thật, in TxHash
```

Mã thoát: 0 khi mọi trade `SETTLED` hoặc `SKIPPED`; 1 khi có trade `FAILED` hoặc lỗi giao dịch; 2 khi thiếu cấu hình.

## Kiểm thử

- Test đơn vị: `python -m unittest discover` trong `system_agents/matching_engine` (không cần mạng).
- End-to-end trên Hardhat cục bộ (chainId 80002), từ gốc repo, sau `npm ci`:
  ```
  python system_agents/matching_engine/e2e_hardhat/run_e2e.py
  ```
  Kịch bản: batch 2 trade thành công, nộp lại bị bỏ qua, trade thiếu allowance bị phát hiện `FAILED`.

## Giới hạn đã biết

- Bot chưa kiểm số dư và allowance trước khi gửi; trade thiếu allowance chỉ lộ ra sau khi gửi (`FAILED`).
- `tradeHash` của hợp đồng không có `sessionId`: khớp lại đúng cặp lệnh, đúng khối lượng và giá ở phiên sau bị hợp đồng từ chối (`TradeAlreadyExecuted`); bot phát hiện qua `executedTrades` và đặt `SKIPPED`. Cần Đức xem xét (xem `docs/THREAT_MODELING.md`, mục 3.2).
- Engine chưa có trạng thái `PENDING_SETTLEMENT` (spec mục 4): `filled_amount` là khối lượng đã khớp, `settled_amount` là phần có bằng chứng on-chain; hai số có thể lệch.
- Chưa chạy trên Amoy thật cho tới khi ví Operator được cấp quyền.
