# Mẫu dữ liệu API Matching Engine cho frontend (bàn giao cho Thắng)

Người viết: Phi, 17/11/2026. Mọi mẫu dưới đây được **sinh từ chính engine** (`api_service.py`, 103 test pass), dùng khóa mẫu công khai không có tài sản, thời gian giả lập `now = 1800000000`. Địa chỉ hợp đồng là `CarbonDoubleAuction` trên Amoy: `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`.

## Chạy engine cho frontend

```
cd system_agents/matching_engine
set AUCTION_CONTRACT_ADDRESS=0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f   # bắt buộc, nếu quên engine từ chối mọi chữ ký
set MATCHING_API_KEY=<khóa admin, chỉ cho /sessions/run, /sessions/window>
set CORS_ALLOW_ORIGINS=http://localhost:3000                            # origin của frontend, nhiều origin cách nhau bằng dấu phẩy
uvicorn api_service:app --port 8000
```

CORS mặc định chỉ cho `http://localhost:3000` và `http://127.0.0.1:3000`. Phương thức cho phép: GET, POST, DELETE, OPTIONS; header: `Content-Type`, `X-API-Key`. Khóa admin **không** đặt trong frontend.

## Quy ước

- `orderType`: 0 = mua (BID), 1 = bán (ASK). `time_in_force`: `GTC` (còn hiệu lực qua các phiên) hoặc `IOC` (khớp ngay trong phiên, phần dư bị hủy).
- `pricePerUnit`: micro-USDC mỗi tCO2e (1 USDC = 1.000.000). `amount`: số nguyên tCO2e. `deadline`, `nonce`: số nguyên (giây UNIX cho deadline).
- `orderId`: chuỗi `0x` + 64 ký tự hex (bytes32), frontend tự sinh ngẫu nhiên, không trùng. Engine lưu chữ thường.
- Chữ ký EIP-712 (`signTypedData`) phải đúng `domain`, `types`, `message` ở mục 3. Chữ ký phải ở dạng s thấp (ethers/viem mặc định đã đúng); s cao bị engine từ chối vì hợp đồng cũng từ chối.

## 1. Trạng thái phiên: `GET /api/v1/sessions/current`

Chưa đặt giờ đóng (luôn mở):

```json
{
  "next_session_id": 1,
  "last_session_id": 0,
  "status": "open",
  "closes_at": null
}
```

Sau khi admin đặt giờ đóng bằng `POST /api/v1/sessions/window` (header `X-API-Key`, body `{"closes_at": <UNIX giây>}`; `null` để bỏ giờ đóng). `status` thành `closed` khi qua `closes_at`:

```json
{
  "next_session_id": 2,
  "last_session_id": 1,
  "status": "open",
  "closes_at": 1800000600
}
```

Lưu ý: engine **chưa tự chạy phiên** và chưa từ chối lệnh mới khi `status = closed`; `status` hiện chỉ để hiển thị. Việc chạy phiên vẫn do admin gọi `POST /api/v1/sessions/run`.

## 2. Gửi lệnh: `POST /api/v1/orders`

Body (lệnh mua, đã ký):

```json
{
  "order": {
    "orderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
    "trader": "0x19E7E376E7C213B7E7e7e46cc70A5dD086DAff2A",
    "orderType": 0,
    "tokenId": 101,
    "amount": 5,
    "pricePerUnit": 11000000,
    "nonce": 1,
    "deadline": 1800086400
  },
  "signature": "0x0a77dc1e3c5a3da36e5ef546c985d35161bfa42cf731031c9c3bb141f0a92cf70c2fa4d871cfa3fc3d85f8406fc8cd74d03e874f6e3f3ce6601fdc9a9ef4fb281b",
  "time_in_force": "GTC"
}
```

Phản hồi `201`:

```json
{
  "status": 201,
  "body": {
    "orderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
    "status": "NEW"
  }
}
```

Lỗi chữ ký (HTTP 401):

```json
{
  "detail": "invalid signature"
}
```

Các lỗi khác: 400 sai cấu trúc hoặc `deadline` đã qua, 409 `orderId` trùng. Xem lệnh: `GET /api/v1/orders/<orderId>`:

```json
{
  "orderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
  "trader": "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a",
  "orderType": 0,
  "tokenId": 101,
  "amount": 5,
  "pricePerUnit": 11000000,
  "deadline": 1800086400,
  "time_in_force": "GTC",
  "status": "FILLED",
  "remaining_amount": 0,
  "filled_amount": 5,
  "rollover_count": 0,
  "settled_amount": 0
}
```

(`FILLED` là đã khớp trong engine; `settled_amount` chỉ tăng khi bot xác nhận có `TradeSettled` on-chain.)

## 3. Dữ liệu ký EIP-712

```json
{
  "domain": {
    "name": "EPU Carbon Double Auction",
    "version": "2.0",
    "chainId": 80002,
    "verifyingContract": "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f"
  },
  "types": {
    "Order": [
      {
        "name": "orderId",
        "type": "bytes32"
      },
      {
        "name": "trader",
        "type": "address"
      },
      {
        "name": "orderType",
        "type": "uint8"
      },
      {
        "name": "tokenId",
        "type": "uint256"
      },
      {
        "name": "amount",
        "type": "uint128"
      },
      {
        "name": "pricePerUnit",
        "type": "uint128"
      },
      {
        "name": "nonce",
        "type": "uint256"
      },
      {
        "name": "deadline",
        "type": "uint256"
      }
    ]
  },
  "primaryType": "Order",
  "message": {
    "orderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
    "trader": "0x19E7E376E7C213B7E7e7e46cc70A5dD086DAff2A",
    "orderType": 0,
    "tokenId": 101,
    "amount": 5,
    "pricePerUnit": 11000000,
    "nonce": 1,
    "deadline": 1800086400
  }
}
```

Khớp với `DEPLOYED_ADDRESSES.md` mục 3.1. Ví dụ với ethers v6: `signer.signTypedData(domain, types, message)`.

## 4. Sổ lệnh theo mức giá: `GET /api/v1/orderbook/<tokenId>`

`bids` giảm dần theo giá, `asks` tăng dần; mỗi dòng là một mức giá với tổng khối lượng còn lại và số lệnh:

```json
{
  "bids": [
    {
      "price": 11000000,
      "amount": 5,
      "orders": 1
    }
  ],
  "asks": []
}
```

Sổ rỗng khi không còn lệnh: `{"bids": [], "asks": []}`.

## 5. WebSocket: `ws://<host>:8000/ws/orderbook/<tokenId>`

Khi kết nối, engine gửi ảnh chụp sổ lệnh:

```json
{
  "event": "orderbook.snapshot",
  "tokenId": 101,
  "data": {
    "bids": [],
    "asks": []
  }
}
```

Mỗi khi sổ lệnh đổi (có lệnh mới, hủy, hoặc sau khi chạy phiên) engine gửi `orderbook.update`:

```json
{
  "event": "orderbook.update",
  "tokenId": 101,
  "data": {
    "bids": [
      {
        "price": 11000000,
        "amount": 5,
        "orders": 1
      }
    ],
    "asks": []
  }
}
```

Khi chạy phiên (`POST /sessions/run`) mỗi cặp khớp gửi `match.executed` (trạng thái `pending`: chưa có bằng chứng settlement on-chain), rồi một `orderbook.update` mới:

```json
{
  "event": "match.executed",
  "sessionId": 1,
  "status": "pending",
  "data": {
    "bidOrderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
    "askOrderId": "0xb2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2",
    "tokenId": 101,
    "amount": 5,
    "clearingPrice": 10000000
  }
}
```

```json
{
  "event": "orderbook.update",
  "tokenId": 101,
  "data": {
    "bids": [],
    "asks": []
  }
}
```

Kết quả của `POST /api/v1/sessions/run` (admin):

```json
{
  "session_id": 1,
  "matches": [
    {
      "bidOrderId": "0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
      "askOrderId": "0xb2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2",
      "tokenId": 101,
      "amount": 5,
      "clearingPrice": 10000000
    }
  ]
}
```

## Chưa kiểm chứng

- Mẫu ký ở trên do Python (`eth_account`) tạo. **Chưa thử với chữ ký sinh từ frontend thật**; nhờ Thắng gửi một lệnh đã ký để đối chiếu.
- Chưa có phiên tự động đóng/mở theo giờ và chưa chặn lệnh khi `closed` (xem mục 1).
