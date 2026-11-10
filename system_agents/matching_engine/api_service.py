"""
Mock API Service cho Matching Engine (SRS FR-15; docs/MATCHING_ENGINE_SPEC.md, mục 8).

Endpoint (tiền tố `/api/v1`):
- POST   /orders                     đặt lệnh, kèm chữ ký EIP-712 `Order` của trader
- DELETE /orders/{orderId}           hủy mềm ngoài chuỗi, kèm chữ ký EIP-712 `CancelRequest`
- GET    /orders/{orderId}           trạng thái lệnh
- GET    /orderbook/{tokenId}        độ sâu sổ lệnh
- POST   /sessions/run               kích hoạt một phiên khớp lệnh (cron job hoặc tác tử)
- GET    /sessions/current           số phiên kế tiếp
- GET    /sessions/{sessionId}/matches
- WS     /ws/orderbook/{tokenId}     snapshot khi kết nối, rồi orderbook.update / match.executed

Chạy thử:  uvicorn api_service:app --reload   (Swagger UI ở /docs)

Giới hạn của bản mock (chưa có trong spec hoặc chưa nối blockchain):
- Sổ lệnh nằm trong bộ nhớ; chưa có đồng hồ phiên 5/15 phút, phiên chạy khi gọi POST /sessions/run.
- Chữ ký `CancelRequest` (định dạng và domain) CHƯA được nhóm chốt; dùng cùng domain với `Order`.
- Chưa kiểm dải giá Oracle (mã 422), số dư/allowance, nonce và trạng thái hủy on-chain.
- `verifyingContract` lấy từ biến môi trường AUCTION_CONTRACT_ADDRESS (mặc định địa chỉ 0).
- `time_in_force` chưa nằm trong struct được ký (điểm Đ5 chưa chốt với Đức), nên người gửi
  lệnh không bị ràng buộc bởi chữ ký về GTC/IOC.
- POST /sessions/run mở công khai trừ khi truyền `admin_key` cho `create_app` (header X-API-Key).
"""

import os
import re
import time
from typing import Callable, Dict, Literal, Optional, Set, Tuple

from eth_account import Account
from eth_account.messages import encode_typed_data
from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from auction_agent import ACTIVE_STATUSES, DoubleAuctionAgent, OrderStatus
from order_book import Order, OrderType

UINT128_MAX = 2**128 - 1
UINT256_MAX = 2**256 - 1
BYTES32_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")

DOMAIN_NAME = "EPU Carbon Double Auction"
DOMAIN_VERSION = "2.0"
CHAIN_ID = 80002  # Polygon Amoy
ORDER_TYPES = {
    "Order": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "trader", "type": "address"},
        {"name": "orderType", "type": "uint8"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "amount", "type": "uint128"},
        {"name": "pricePerUnit", "type": "uint128"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}
CANCEL_TYPES = {
    "CancelRequest": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "cancelNonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}


class OrderPayload(BaseModel):
    orderId: str
    trader: str
    orderType: int = Field(description="0 = BID, 1 = ASK")
    tokenId: int = Field(ge=0, le=UINT256_MAX)
    amount: int = Field(gt=0, le=UINT128_MAX, description="số nguyên tCO2e")
    pricePerUnit: int = Field(gt=0, le=UINT128_MAX, description="micro-USDC mỗi tCO2e")
    nonce: int = Field(ge=0, le=UINT256_MAX)
    deadline: int = Field(gt=0, le=UINT256_MAX)


class PlaceOrderRequest(BaseModel):
    order: OrderPayload
    signature: str
    time_in_force: Literal["GTC", "IOC"] = "GTC"


class CancelOrderRequest(BaseModel):
    signature: str
    cancel_nonce: int = Field(ge=0, le=UINT256_MAX)
    deadline: int = Field(gt=0, le=UINT256_MAX)


class RunSessionRequest(BaseModel):
    tokenId: int = Field(ge=0, le=UINT256_MAX)


def _recover(domain: dict, types: dict, message: dict, signature: str) -> str:
    """Trả về địa chỉ (chữ thường) đã ký; ném ValueError nếu chữ ký sai định dạng."""
    try:
        signable = encode_typed_data(domain_data=domain, message_types=types, message_data=message)
        return Account.recover_message(signable, signature=signature).lower()
    except Exception as exc:  # thư viện ném nhiều loại lỗi khác nhau cho chữ ký hỏng
        raise ValueError(f"invalid signature: {exc}") from exc


class _ConnectionManager:
    def __init__(self) -> None:
        self._subs: Dict[int, Set[WebSocket]] = {}

    async def connect(self, token_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._subs.setdefault(token_id, set()).add(ws)

    def disconnect(self, token_id: int, ws: WebSocket) -> None:
        self._subs.get(token_id, set()).discard(ws)

    async def broadcast(self, token_id: int, message: dict) -> None:
        for ws in list(self._subs.get(token_id, ())):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(token_id, ws)


def create_app(
    agent: Optional[DoubleAuctionAgent] = None,
    verify_signatures: bool = True,
    contract_address: Optional[str] = None,
    admin_key: Optional[str] = None,
    now_fn: Callable[[], float] = time.time,
) -> FastAPI:
    agent = agent or DoubleAuctionAgent(now_fn=now_fn)
    domain = {
        "name": DOMAIN_NAME,
        "version": DOMAIN_VERSION,
        "chainId": CHAIN_ID,
        "verifyingContract": contract_address
        or os.environ.get("AUCTION_CONTRACT_ADDRESS", "0x" + "0" * 40),
    }
    used_cancel_nonces: Set[Tuple[str, int]] = set()
    manager = _ConnectionManager()
    app = FastAPI(title="CarbonChain Matching Engine API (mock)", version="0.1.0")
    app.state.agent = agent

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Spec mục 8.2: 400 cho sai cấu trúc/giá trị (422 dành cho giá ngoài dải Oracle)
        return JSONResponse(status_code=400, content={"detail": jsonable_errors(exc)})

    def jsonable_errors(exc: RequestValidationError) -> list:
        return [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]

    async def _push_book(token_id: int) -> None:
        await manager.broadcast(
            token_id, {"event": "orderbook.update", "tokenId": token_id, "data": agent.snapshot(token_id)}
        )

    def _order_view(order_id: str) -> dict:
        r = agent.get_order(order_id)
        o = r.order
        return {
            "orderId": o.order_id,
            "trader": o.trader_id,
            "orderType": 0 if o.order_type == OrderType.BID else 1,
            "tokenId": o.token_id,
            "amount": o.amount,
            "pricePerUnit": o.price,
            "deadline": o.deadline,
            "time_in_force": o.time_in_force,
            "status": r.status.value,
            "remaining_amount": r.remaining_amount,
            "filled_amount": r.filled_amount,
            "rollover_count": r.rollover_count,
        }

    @app.post("/api/v1/orders", status_code=201)
    async def place_order(req: PlaceOrderRequest) -> dict:
        p = req.order
        if not BYTES32_RE.match(p.orderId):
            raise HTTPException(400, "orderId must be 0x + 64 hex characters (bytes32)")
        if not ADDRESS_RE.match(p.trader):
            raise HTTPException(400, "trader must be an address (0x + 40 hex characters)")
        if p.orderType not in (0, 1):
            raise HTTPException(400, "orderType must be 0 (BID) or 1 (ASK)")
        if p.deadline <= now_fn():
            raise HTTPException(400, "deadline already passed")
        order_id = p.orderId.lower()
        trader = p.trader.lower()

        if verify_signatures:
            message = {
                "orderId": p.orderId, "trader": p.trader, "orderType": p.orderType,
                "tokenId": p.tokenId, "amount": p.amount, "pricePerUnit": p.pricePerUnit,
                "nonce": p.nonce, "deadline": p.deadline,
            }
            try:
                signer = _recover(domain, ORDER_TYPES, message, req.signature)
            except ValueError:
                raise HTTPException(401, "invalid signature")
            if signer != trader:
                raise HTTPException(401, "signature does not match trader")

        try:
            agent.get_order(order_id)
            raise HTTPException(409, "orderId already exists")
        except KeyError:
            pass

        order = Order(
            order_id=order_id,
            trader_id=trader,
            order_type=OrderType.BID if p.orderType == 0 else OrderType.ASK,
            token_id=p.tokenId,
            amount=p.amount,
            price=p.pricePerUnit,
            signature=req.signature,
            time_in_force=req.time_in_force,
            deadline=p.deadline,
        )
        agent.submit_order(order)
        await _push_book(p.tokenId)
        return {"orderId": order_id, "status": OrderStatus.NEW.value}

    @app.delete("/api/v1/orders/{order_id}")
    async def cancel_order(order_id: str, req: CancelOrderRequest) -> dict:
        order_id = order_id.lower()
        try:
            record = agent.get_order(order_id)
        except KeyError:
            raise HTTPException(404, "order not found")
        if req.deadline <= now_fn():
            raise HTTPException(400, "cancel request deadline already passed")
        trader = record.order.trader_id

        if verify_signatures:
            message = {"orderId": order_id, "cancelNonce": req.cancel_nonce, "deadline": req.deadline}
            try:
                signer = _recover(domain, CANCEL_TYPES, message, req.signature)
            except ValueError:
                raise HTTPException(401, "invalid signature")
            if signer != trader:
                raise HTTPException(401, "signature does not match the order's trader")
        if (trader, req.cancel_nonce) in used_cancel_nonces:
            raise HTTPException(409, "cancel_nonce already used")
        if record.status not in ACTIVE_STATUSES:
            raise HTTPException(409, f"order is already {record.status.value}")

        used_cancel_nonces.add((trader, req.cancel_nonce))
        agent.cancel_order(order_id)
        await _push_book(record.order.token_id)
        return {
            "orderId": order_id,
            "status": OrderStatus.CANCELLED.value,
            # Hủy ngoài chuỗi chỉ rút lệnh khỏi engine; chữ ký gốc vẫn dùng được on-chain đến hạn này.
            "onchain_valid_until": record.order.deadline,
        }

    @app.get("/api/v1/orders/{order_id}")
    async def get_order(order_id: str) -> dict:
        try:
            return _order_view(order_id.lower())
        except KeyError:
            raise HTTPException(404, "order not found")

    @app.get("/api/v1/orderbook/{token_id}")
    async def get_orderbook(token_id: int) -> dict:
        return agent.snapshot(token_id)

    @app.post("/api/v1/sessions/run")
    async def run_session(req: RunSessionRequest, x_api_key: Optional[str] = Header(default=None)) -> dict:
        if admin_key is not None and x_api_key != admin_key:
            raise HTTPException(401, "missing or wrong X-API-Key")
        matches = agent.run_periodic_double_auction(req.tokenId)
        payload = [
            {
                "bidOrderId": m.bid_order_id,
                "askOrderId": m.ask_order_id,
                "tokenId": m.token_id,
                "amount": m.amount,
                "clearingPrice": m.clearing_price,
            }
            for m in matches
        ]
        # `match.executed` mang trạng thái pending: engine chưa có bằng chứng settlement on-chain
        for item in payload:
            await manager.broadcast(
                req.tokenId,
                {"event": "match.executed", "sessionId": agent.session_id, "status": "pending", "data": item},
            )
        await _push_book(req.tokenId)
        return {"session_id": agent.session_id, "matches": payload}

    @app.get("/api/v1/sessions/current")
    async def current_session() -> dict:
        return {"next_session_id": agent.session_id + 1, "last_session_id": agent.session_id}

    @app.get("/api/v1/sessions/{session_id}/matches")
    async def session_matches(session_id: int) -> dict:
        if session_id not in agent.matches:
            raise HTTPException(404, "session not found")
        return {
            "session_id": session_id,
            "matches": [
                {
                    "bidOrderId": m.bid_order_id,
                    "askOrderId": m.ask_order_id,
                    "tokenId": m.token_id,
                    "amount": m.amount,
                    "clearingPrice": m.clearing_price,
                }
                for m in agent.matches[session_id]
            ],
        }

    @app.websocket("/ws/orderbook/{token_id}")
    async def ws_orderbook(ws: WebSocket, token_id: int) -> None:
        await manager.connect(token_id, ws)
        try:
            await ws.send_json(
                {"event": "orderbook.snapshot", "tokenId": token_id, "data": agent.snapshot(token_id)}
            )
            while True:
                await ws.receive_text()  # giữ kết nối; client không cần gửi gì
        except WebSocketDisconnect:
            manager.disconnect(token_id, ws)

    return app


app = create_app()
