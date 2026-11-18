# Bàn giao metadata và tích hợp frontend của Ngô Văn Thắng

Phạm vi đối soát: T1/T3 về nhóm tín chỉ, T2 về EIP-712 và REST/WebSocket; README, ADR-001 và SRS trên main là mốc kỹ thuật. Bản báo cáo Word phản ánh trạng thái trước ADR nên một số ví dụ trong đó còn thiếu `timeInForce` và chưa khóa đơn vị. Frontend dùng cấu trúc mới của SRS, không tự sửa contract hoặc thuật toán của thành viên khác.

## Sản phẩm hiện có

- [Metadata schema](METADATA_SCHEMA.json), [từ điển dữ liệu](DATA_DICTIONARY.md), mẫu metadata trong [examples](examples/), và bộ kiểm tra schema/nghiệp vụ.
- [Luồng người dùng](USER_FLOWS.md). Đây là thiết kế luồng; không thay thế bàn giao Figma.
- Trading Floor theo một tokenId: sổ mua/bán và độ sâu từng lệnh, form limit GTC/IOC, đồng hồ dùng mốc thời gian server, các lệnh đã được API tiếp nhận trong lần mở trang, cập nhật bằng polling và WebSocket.
- Giá và khối lượng được giữ dạng chuỗi số nguyên khi truyền API; chuyển giá hiển thị bằng `parseUnits`/`formatUnits`, không dùng số thực để tính tiền.
- Ký `Order` gồm `timeInForce`; đọc nonce từ hợp đồng mỗi lần ký, không tăng nonce cục bộ. Nonce là thế hệ hủy hàng loạt, không phải bộ đếm tự tăng sau từng chữ ký.

## Cấu hình và chạy

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
# Điền địa chỉ đúng mạng từ lần deploy tương ứng.
npm run dev
```

Địa chỉ chưa cấu hình không được thay bằng zero address. Khi chưa có API, giao diện hiển thị mất kết nối; khi chưa có ABI/địa chỉ đấu giá, nút ký bị khóa. Không giả lập dữ liệu như thể giao dịch đã thành công. Việc gửi lệnh ngoài chuỗi không chuyển token hay USDC; cấp quyền và settlement là các bước riêng.

## Bàn giao cần nhận từ Đức

Chưa có build artifact Solidity v2 hoặc địa chỉ triển khai trong các nhánh đã đối soát. ABI đấu giá cũ đã được bỏ khỏi luồng ký; module ABI hiện là rỗng có cờ `AUCTION_ABI_READY = false`, không được gọi là ABI v2 đã deploy.

Khi nhận artifact Hardhat/Foundry thực:

```powershell
cd frontend
node scripts/import-auction-artifact.mjs <duong-dan-artifact.json> <ten-ham-doc-nonce>
```

Importer kiểm tra getter nonce `view(address) returns (uint256)` và getter `ORDER_TYPEHASH() view returns (bytes32)`, rồi nhập ABI thực. Tên getter nonce phải được Đức xác nhận; mặc định `nonces` chỉ là tên dự kiến. Hook kiểm tra bytecode và `ORDER_TYPEHASH` thực trên mạng trước khi ký, nên ABI sai hoặc contract chưa hỗ trợ `timeInForce` sẽ bị từ chối.

Domain: `name = EPU Carbon Double Auction`, `version = 2.0`, chainId đúng ví, verifyingContract đúng địa chỉ mạng. Chuỗi typehash:

```text
Order(bytes32 orderId,address trader,uint8 orderType,uint256 tokenId,uint128 amount,uint128 pricePerUnit,uint8 timeInForce,uint256 nonce,uint256 deadline)
```

`orderId` tuân FR-04: `keccak256(abi.encode(trader, orderType, tokenId, amount, pricePerUnit, nonce, deadline))`. Công thức hiện tại chưa chứa `timeInForce`; vì vậy hai lệnh trùng bảy trường này có cùng ID dù GTC/IOC khác nhau. API phải từ chối ID trùng, không ghi đè. Chữ ký vẫn ràng buộc GTC/IOC. Đây là điểm cần cả nhóm xác nhận nếu muốn cho phép hai lệnh đồng thời chỉ khác GTC/IOC.

ABI token carbon hiện còn là giao diện baseline. Các hàm mint/quản trị phải được đối soát với artifact token v2 trước khi sử dụng; chưa thể tuyên bố đã kiểm thử vòng đời mint–trade–retire trên testnet.

## Hợp đồng trao đổi API cần Phi xác nhận

Frontend dùng `/api/v1` theo SRS mới. Spec Matching cũ dùng `/v1`, `price`, `expiry` và tên sự kiện khác; không tự fallback POST sang endpoint khác để tránh gửi lặp lệnh. Các endpoint và bổ sung dữ liệu phiên dưới đây là giao diện frontend cần, chưa phải xác nhận backend đã triển khai.

| Method | Path | Mục đích |
|---|---|---|
| POST | `/api/v1/orders` | Nhận lệnh ký, phản hồi 201 với `order_id`, `status` |
| GET | `/api/v1/orders/{order_id}` | Cập nhật trạng thái một lệnh đã gửi |
| DELETE | `/api/v1/orders/{order_id}` | Client có hỗ trợ truyền chữ ký hủy; UI hủy chờ chốt thông điệp ký riêng |
| GET | `/api/v1/orderbook/{tokenId}` | `bids`, `asks`, giá khớp gần nhất nếu có |
| GET | `/api/v1/sessions/current?token_id=...` | Mốc phiên hiện tại để đếm ngược chính xác |
| WS | `/ws/orderbook/{tokenId}` | Báo thay đổi; frontend đọc lại REST để đồng bộ |

Request POST dùng `order_id`, `trader`, `order_type` (0/1), `token_id`, `amount`, `price_per_unit`, `time_in_force` (0=GTC, 1=IOC), `nonce`, `deadline`, `signature`, `chain_id`, `verifying_contract`. Các số uint trừ enum/chainId dùng chuỗi thập phân. API kiểm tra đúng chain/domain và cùng quy ước micro-USDC; không dùng `price` số thực theo USD.

Mỗi lệnh trả về có `order_id`, `trader`, `order_type`, `token_id`, `amount`, `remaining_amount`, `price_per_unit`, `status`; `rollover_count` tùy chọn. Client nhận snake_case hoặc camelCase và cả envelope `{success:true,data:...}`. Số nguyên vượt `Number.MAX_SAFE_INTEGER` phải truyền bằng chuỗi, nếu truyền số JSON sẽ bị từ chối.

Ví dụ phiên (giá trị chỉ minh họa):

```json
{"session_id":"demo-session","phase":"CALL","duration_seconds":300,"cutoff_at":2000000000,"phase_ends_at":2000000000}
```

Timestamp là Unix giây; `phase` thuộc CALL/MATCH/SETTLE; chu kỳ 300 hoặc 900 giây. Endpoint là cùng dịch vụ/mạng với các lệnh ký. Engine phải từ chối `chain_id`/`verifying_contract` khác mạng nó phục vụ. Khi không có mốc phiên tin cậy, frontend không tự tạo chu kỳ bằng đồng hồ máy để mở đặt lệnh.

Nếu API và frontend khác origin, backend cần cấu hình CORS cho origin frontend, header `Content-Type`, và các method GET/POST/DELETE/OPTIONS. Frontend không thể tự bỏ qua chính sách CORS của trình duyệt. Wagmi bật `ssr: true` để trạng thái ví không gây lệch HTML khi Next.js hydrate.

Sự kiện: `orderbook.update`, `match.executed`, `settlement.confirmed`, `settlement.failed`, `session.completed`, `price.update`. Có adapter cho tên underscore cũ của frontend. `FILLED` là khớp đủ, không đồng nghĩa `SETTLED_FINAL`. WebSocket không tự đánh dấu thanh toán; cập nhật REST là nguồn trạng thái. Khi timeout POST, frontend không tự retry; cần tra cứu ID trước khi gửi lại.

## Phạm vi fungibility

Tiêu chí nhóm: cùng `asset_class`, cùng `standard_category`, cùng khoảng `vintage_window`; `vintage_year` từng lô phải nằm trong khoảng. `fungibility_group_id` được tính theo cửa sổ để mọi lô cùng nhóm có cùng ID. Nhóm metadata dùng lọc/đánh giá eligibility. Lệnh hiện vẫn gắn đúng một tokenId; UI không tự nới điều kiện cùng tokenId mà contract đang yêu cầu. Khớp chéo tokenId là thay đổi Engine/settlement cần nhóm phê duyệt và kiểm thử riêng.

## Kiểm tra và giới hạn nghiệm thu

```powershell
# Tại thư mục gốc
python -m pip install -r requirements-dev.txt
python scripts/validate_metadata.py docs/examples/example_verra_vcs.json docs/examples/example_gold_standard.json
python -m unittest discover -s tests -v
# Tại frontend
npm test
npm run typecheck
npm run lint
npm run build
```

Bộ test kiểm tra dữ liệu sai, giới hạn số nguyên, ràng buộc chữ ký, payload API, lỗi/timeout, và dừng reconnect sau disconnect. Kiểm tra bằng mock hoặc trình duyệt local không thay thế E2E testnet. Cần ABI/deployment v2, API đang chạy và ví testnet để nghiệm thu ký → nhận lệnh → khớp → settlement. Wireframe Figma 4 portal cũng chưa có bằng chứng bàn giao trong repository.
