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
| `SKIPPED` | Không gửi: payload sai hoặc kiểm tra trước thất bại (hết hạn, đã hủy on-chain, nonce thấp hơn, `tradeHash` đã dùng, vượt khối lượng đã ký, chữ ký không khớp, bên mua thiếu số dư hoặc allowance, bên bán thiếu tín chỉ hoặc chưa `setApprovalForAll`, bên mua có mã) |
| `FAILED` | Biết chắc trade không được thanh toán: hợp đồng bỏ qua trong `try/catch` (số dư hoặc allowance thay đổi sau lần kiểm trước, hook ERC-1155 từ chối, hoặc chạy với `--no-funds-check`), hoặc giao dịch bị revert |
| `UNKNOWN` | Đã gửi giao dịch nhưng không xác định được kết quả (hết giờ chờ biên nhận, lỗi mạng sau khi gửi, event không khớp). Giao dịch có thể vẫn được đào: dùng `--recover-tx` bên dưới, không chạy lại phiên |

Các trade đã `SETTLED` ở batch trước luôn được báo cho engine, kể cả khi batch sau gặp lỗi.

Giao dịch `batchSettleTrades` vẫn thành công khi có trade lỗi bên trong; bot chỉ dựa vào event, không dựa vào trạng thái giao dịch.

## Chuẩn bị chạy trên Amoy (làm một lần)

1. Cài thư viện: `pip install -r system_agents/matching_engine/requirements.txt`.
2. Tạo ví Operator riêng (không dùng ví deployer):
   ```
   python scripts/new_operator_wallet.py
   ```
   Lệnh chỉ in địa chỉ ví; khóa riêng được ghi vào `.env` ở gốc repo (file đã nằm trong `.gitignore`, không commit).
3. Gửi địa chỉ ví cho Đức để cấp `SETTLEMENT_OPERATOR_ROLE` (`grantRole`), và nạp POL từ faucet Amoy cho ví này để trả gas.

### Dùng chung trong nhóm: mỗi người tự tạo ví Operator của mình

- **Không commit, không đẩy `.env` hoặc khóa riêng lên git.** Repo này công khai; khóa đã lên GitHub là coi như lộ vĩnh viễn (lịch sử git không xóa được). Ví giữ `SETTLEMENT_OPERATOR_ROLE` thì ai có khóa cũng ký được `batchSettleTrades`; lộ khóa thì Đức phải thu hồi role.
- Thành viên nào cần chạy bot thì chạy bước 2 ở trên để tạo ví riêng, gửi **địa chỉ** (không phải khóa) cho Đức cấp role, rồi xin POL (faucet Polygon Amoy hoặc nhờ Đức).
- Khi demo, một người chạy bot trên máy của mình; các thành viên khác dùng API và frontend, không cần khóa.
- Nếu buộc phải chuyển khóa, gửi riêng tư cho đúng người, không qua git hay kênh chung.
4. Địa chỉ hợp đồng lấy từ `docs/DEPLOYED_ADDRESSES.md` (do Đức bàn giao).

## Chạy

Biến môi trường: `SETTLEMENT_OPERATOR_PRIVATE_KEY` (bắt buộc), `AUCTION_CONTRACT_ADDRESS` (hoặc `--contract`), `AMOY_RPC_URL` (tùy chọn), `MATCHING_API_KEY` (đặt giá trị này cho cả API và bot để bảo vệ `/sessions/run`, `/sessions/{id}/trades`, `/settlements/confirm`; không đặt thì các endpoint đó mở công khai, chỉ dùng khi chạy thử cục bộ).

```
cd system_agents/matching_engine
uvicorn api_service:app --port 8000          # cửa sổ 1: API, đặt AUCTION_CONTRACT_ADDRESS trước khi chạy
python settlement_submitter.py --session-id 1 --dry-run   # chỉ kiểm tra trước, không gửi giao dịch
python settlement_submitter.py --session-id 1             # nộp thật, in TxHash
```

Khi có trade `UNKNOWN`, bot in sẵn lệnh khôi phục. Lệnh này không gửi giao dịch nào: nó đọc event `TradeSettled` của giao dịch đã đào rồi báo engine các trade của phiên đã được thanh toán:

```
python settlement_submitter.py --session-id 1 --recover-tx 0x<tx_hash>
```

Mã thoát: 0 khi mọi trade `SETTLED` hoặc `SKIPPED` và engine đã ghi nhận; 1 khi có trade `FAILED`/`UNKNOWN`, lỗi giao dịch, hoặc engine không ghi nhận được; 2 khi thiếu cấu hình.

Trước khi gửi, bot bỏ qua (`SKIPPED`) các trade có chữ ký s cao (hợp đồng từ chối) và các trade hết hạn trong vòng 60 giây (có thể hết hạn trước khi block được đào).

Bot còn kiểm các điều kiện mà hợp đồng chỉ phát hiện khi chuyển token. Số dư và allowance được cộng dồn theo từng bên trong cùng lần chạy, nên bên mua chỉ đủ tiền cho một trong hai trade thì trade thứ hai bị bỏ:
- Bên mua: số dư và allowance token thanh toán, tối thiểu `matchAmount × clearingPrice` cộng các trade trước đó của họ.
- Bên bán: số dư tín chỉ của `tokenId` và quyền `setApprovalForAll` cho hợp đồng đấu giá.
- Bên mua có mã (hợp đồng hoặc EOA ủy quyền theo EIP-7702): bị bỏ qua mặc định, vì hook `onERC1155Received` của họ có thể đốt hết gas của batch (xem `docs/THREAT_MODELING.md`, mục 5.5). Cờ `--allow-contract-traders` cho phép lại.
- Cờ `--no-funds-check` tắt phần kiểm số dư và allowance; dùng để thử đường `FAILED` hoặc khi RPC đọc token chậm. Kiểm mã của bên mua vẫn chạy.

Kết quả kiểm là ảnh chụp tại thời điểm đọc: trader vẫn có thể rút allowance giữa lúc kiểm và lúc đào block, khi đó trade lộ ra là `FAILED`.

## Kiểm thử

- Test đơn vị: `python -m unittest discover` trong `system_agents/matching_engine` (không cần mạng).
- End-to-end trên Hardhat cục bộ (chainId 80002), từ gốc repo, sau `npm ci`:
  ```
  python system_agents/matching_engine/e2e_hardhat/run_e2e.py
  ```
  Kịch bản: batch 2 trade thành công, nộp lại bị bỏ qua, `--recover-tx`, trade thiếu allowance bị bỏ trước khi gửi (`SKIPPED`) và, với `--no-funds-check`, bị hợp đồng bỏ qua (`FAILED`), bên mua có mã (giả lập EIP-7702 bằng `hardhat_setCode`) bị bỏ qua mặc định và `FAILED` khi cho phép.

## Giới hạn đã biết

- Kiểm số dư và allowance chỉ là ảnh chụp trước khi gửi; hợp đồng không khóa tài sản nên trader vẫn có thể rút giữa chừng (trade thành `FAILED`, mục 5.6 của `docs/THREAT_MODELING.md`). Bot chưa đặt giới hạn gas riêng cho từng trade (cần sửa hợp đồng: `try this.executeSettlementExternal{gas: ...}`) và chưa tránh dùng `estimateGas` khi batch có bên mua có mã được cho phép bằng `--allow-contract-traders`.
- `tradeHash` của hợp đồng không có `sessionId`: khớp lại đúng cặp lệnh, đúng khối lượng và giá ở phiên sau bị hợp đồng từ chối (`TradeAlreadyExecuted`); bot phát hiện qua `executedTrades` và đặt `SKIPPED`. Cần Đức xem xét (xem `docs/THREAT_MODELING.md`, mục 3.2).
- Engine chưa có trạng thái `PENDING_SETTLEMENT` (spec mục 4): `filled_amount` là khối lượng đã khớp, `settled_amount` là phần có bằng chứng on-chain; hai số có thể lệch.
- Đã chạy thật trên Amoy một phiên một trade (17/11/2026, mục dưới). Chưa thử trên chuỗi: batch nhiều trade, trade `FAILED`, hết giờ chờ biên nhận, `--recover-tx`.

## Kết quả chạy thật trên Amoy (17/11/2026)

Cấu hình: hợp đồng `CarbonDoubleAuction` `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`, `MockUSDC` `0xe35681b0882d533458d22B344268642136ebD813`, `CarbonCredit1155` `0x851978601b47a61B8aF3bcC1707B689Fbc977697` (theo `docs/DEPLOYED_ADDRESSES.md` của Đức). Ví Operator `0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE` (đã có `SETTLEMENT_OPERATOR_ROLE`, xác minh bằng `hasRole` trả về true).

Kịch bản: hai ví thử, bên mua `0xA4405ECe027f9C0585764b97b3E96dA947b52E7d` (50.000 MockUSDC) và bên bán `0x485ed29E56A57c59ca817554950C4C19EB00aF0c` (50 tín chỉ lô 101), do Đức cấp tài sản. Hai bên approve cho hợp đồng; engine nhận lệnh mua 5 đơn vị giá 11 USDC và lệnh bán 5 đơn vị giá 9 USDC (chữ ký EIP-712), khớp 5 đơn vị ở giá 10 USDC.

| Bước | Kết quả |
| --- | --- |
| `--dry-run` | 1 trade sẽ gửi, 0 bị bỏ |
| Gửi thật | TxHash `0x9619ff0b986145c8c2c2ce7e49c49f4fe639fbf2faa42b2a88d64a050bca75b8`, `status` 1, gas 275.741, event `TradeSettled`, trade `SETTLED`, engine ghi nhận |
| Số dư trên chain sau đó | Bên mua: USDC 50.000 → 49.950, tín chỉ 0 → 5. Bên bán: tín chỉ 50 → 45, USDC 0 → 50 |

Lỗi tìm thấy khi chạy thật và đã sửa: Amoy là chuỗi PoA (`extraData` 104 byte) nên web3 báo `ExtraDataLengthError` khi đọc block; `Web3Chain.from_rpc` giờ bật `ExtraDataToPOAMiddleware`. Test local dùng chuỗi giả nên không bắt được lỗi này. Bot dừng ở bước khởi động, chưa gửi giao dịch nào khi lỗi.

Lưu ý khi chạy lại: bot đọc khóa từ biến môi trường, không tự đọc `.env`. RPC `poly-amoy-testnet.api.pocket.network` (mặc định) chưa được kiểm; lần chạy dùng `https://polygon-amoy-bor-rpc.publicnode.com`. Engine giữ phiên trong bộ nhớ nên khởi động lại thì số phiên về 1; do `tradeHash` không có `sessionId`, nộp lại đúng cặp lệnh, khối lượng và giá sẽ bị từ chối.
