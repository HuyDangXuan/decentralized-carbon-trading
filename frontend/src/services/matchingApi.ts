/**
 * services/matchingApi.ts
 * Module kết nối REST API + WebSocket của Matching Engine (Phi).
 *
 * Giải quyết vấn đề T2:
 *   - Chuyển luồng đặt lệnh: Frontend → API Service (off-chain) thay vì gọi on-chain
 *   - Tương thích với đặc tả API §8 trong MATCHING_ENGINE_SPEC.md
 *   - Hỗ trợ WebSocket real-time cho Depth Chart & Trade notifications
 *
 * Endpoints (theo spec Phi §8.2):
 *   POST   /api/v1/orders              – Gửi lệnh đã ký EIP-712
 *   DELETE  /api/v1/orders/{orderId}    – Hủy lệnh off-chain
 *   GET     /api/v1/orderbook/{tokenId} – Lấy sổ lệnh hiện tại
 *   POST    /api/v1/sessions/run        – Kích hoạt khớp lệnh (admin)
 *   GET     /api/v1/sessions/latest     – Kết quả phiên gần nhất
 *
 * WebSocket (theo spec Phi §8.3):
 *   WS /ws/orderbook/{tokenId}          – Stream sổ lệnh real-time
 */

import type { SignedOrder } from "../hooks/useEIP712Order";

// ─────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────

/** URL base của Matching Engine API Service */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_MATCHING_API_URL ?? "http://localhost:8000";

/** URL WebSocket của Matching Engine */
const WS_BASE_URL =
  process.env.NEXT_PUBLIC_MATCHING_WS_URL ?? "ws://localhost:8000";

// ─────────────────────────────────────────────
// API Response Types
// ─────────────────────────────────────────────

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
}

/** Trạng thái lệnh trên Engine */
export type OrderStatus =
  | "NEW"
  | "ACTIVE"
  | "PARTIALLY_FILLED"
  | "FILLED"
  | "ROLLED_OVER"
  | "EXPIRED"
  | "CANCELLED";

export interface OrderBookEntry {
  orderId: string;
  trader: string;
  orderType: "BID" | "ASK";
  tokenId: string;
  amount: string;
  remainingAmount: string;
  pricePerUnit: string;
  status: OrderStatus;
  createdAt: number;
}

export interface OrderBookSnapshot {
  tokenId: string;
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  lastUpdated: number;
  /** Giá khớp phiên gần nhất (micro-USDC) */
  lastClearingPrice?: string;
}

export interface SessionResult {
  sessionId: string;
  tokenId: string;
  clearingPrice: string;
  totalMatchedAmount: string;
  matchCount: number;
  matches: MatchedPair[];
  executedAt: number;
}

export interface MatchedPair {
  bidOrderId: string;
  askOrderId: string;
  matchAmount: string;
  clearingPrice: string;
  tradeHash: string;
}

export interface SubmitOrderResponse {
  orderId: string;
  status: OrderStatus;
  message: string;
}

// ─────────────────────────────────────────────
// REST API Client
// ─────────────────────────────────────────────

class MatchingApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error:
            errorData.detail ??
            errorData.error ??
            `HTTP ${response.status}: ${response.statusText}`,
          timestamp: Date.now(),
        };
      }

      const data = await response.json();
      return {
        success: true,
        data: data as T,
        timestamp: Date.now(),
      };
    } catch (err) {
      return {
        success: false,
        error:
          err instanceof Error
            ? `Không thể kết nối Matching Engine: ${err.message}`
            : "Lỗi không xác định",
        timestamp: Date.now(),
      };
    }
  }

  // ── POST /api/v1/orders ──────────────────

  /**
   * Gửi lệnh đã ký EIP-712 lên Matching Engine.
   * Không tốn gas – lệnh được xử lý off-chain.
   */
  async submitOrder(
    signedOrder: SignedOrder
  ): Promise<ApiResponse<SubmitOrderResponse>> {
    return this.request<SubmitOrderResponse>("POST", "/api/v1/orders", {
      order_id: signedOrder.orderId,
      trader: signedOrder.trader,
      order_type: signedOrder.orderType, // 0=BID, 1=ASK
      token_id: signedOrder.tokenId,
      amount: signedOrder.amount,
      price_per_unit: signedOrder.pricePerUnit,
      nonce: signedOrder.nonce,
      deadline: signedOrder.deadline,
      signature: signedOrder.signature,
      chain_id: signedOrder.chainId,
    });
  }

  // ── DELETE /api/v1/orders/{orderId} ──────

  /**
   * Hủy lệnh off-chain (trước khi bị khớp).
   * Chỉ trader tạo lệnh mới có quyền hủy.
   */
  async cancelOrder(
    orderId: string,
    traderAddress: string,
    signature: string
  ): Promise<ApiResponse<{ orderId: string; status: string }>> {
    return this.request("DELETE", `/api/v1/orders/${orderId}`, {
      trader: traderAddress,
      signature,
    });
  }

  // ── GET /api/v1/orderbook/{tokenId} ──────

  /**
   * Lấy snapshot sổ lệnh hiện tại cho một tokenId.
   * Dùng để render Order Book UI và Depth Chart.
   */
  async getOrderBook(
    tokenId: string
  ): Promise<ApiResponse<OrderBookSnapshot>> {
    return this.request<OrderBookSnapshot>(
      "GET",
      `/api/v1/orderbook/${tokenId}`
    );
  }

  // ── POST /api/v1/sessions/run ────────────

  /**
   * Kích hoạt chạy phiên khớp lệnh (Periodic Double Auction).
   * Thường chỉ dùng cho admin/testing; production chạy tự động theo chu kỳ.
   */
  async triggerSession(
    tokenId: string
  ): Promise<ApiResponse<SessionResult>> {
    return this.request<SessionResult>("POST", "/api/v1/sessions/run", {
      token_id: tokenId,
    });
  }

  // ── GET /api/v1/sessions/latest ──────────

  /**
   * Lấy kết quả phiên khớp lệnh gần nhất.
   */
  async getLatestSession(
    tokenId: string
  ): Promise<ApiResponse<SessionResult>> {
    return this.request<SessionResult>(
      "GET",
      `/api/v1/sessions/latest?token_id=${tokenId}`
    );
  }
}

// ─────────────────────────────────────────────
// WebSocket Client
// ─────────────────────────────────────────────

export type WSEventType =
  | "orderbook_update"    // Sổ lệnh thay đổi (lệnh mới / hủy / khớp)
  | "trade_executed"      // Có cặp lệnh vừa được khớp
  | "session_completed"   // Phiên đấu giá kết thúc
  | "price_update";       // Giá clearing mới

export interface WSMessage {
  event: WSEventType;
  data: unknown;
  timestamp: number;
}

type WSEventHandler = (message: WSMessage) => void;

class OrderBookWebSocket {
  private ws: WebSocket | null = null;
  private handlers: Map<WSEventType, WSEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // ms
  private tokenId: string;

  constructor(tokenId: string) {
    this.tokenId = tokenId;
  }

  /** Mở kết nối WebSocket tới Matching Engine */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const url = `${WS_BASE_URL}/ws/orderbook/${this.tokenId}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log(`[WS] Đã kết nối sổ lệnh token #${this.tokenId}`);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          const eventHandlers = this.handlers.get(message.event) ?? [];
          for (const handler of eventHandlers) {
            handler(message);
          }
        } catch (err) {
          console.error("[WS] Lỗi parse message:", err);
        }
      };

      this.ws.onclose = () => {
        console.log(`[WS] Mất kết nối token #${this.tokenId}`);
        this.tryReconnect();
      };

      this.ws.onerror = (err) => {
        console.error("[WS] Lỗi:", err);
      };
    } catch (err) {
      console.error("[WS] Không thể tạo kết nối:", err);
    }
  }

  /** Đăng ký lắng nghe sự kiện */
  on(event: WSEventType, handler: WSEventHandler): void {
    const existing = this.handlers.get(event) ?? [];
    existing.push(handler);
    this.handlers.set(event, existing);
  }

  /** Hủy lắng nghe sự kiện */
  off(event: WSEventType, handler: WSEventHandler): void {
    const existing = this.handlers.get(event) ?? [];
    this.handlers.set(
      event,
      existing.filter((h) => h !== handler)
    );
  }

  /** Ngắt kết nối */
  disconnect(): void {
    this.reconnectAttempts = this.maxReconnectAttempts; // Ngăn reconnect
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
  }

  /** Tự động reconnect với exponential backoff */
  private tryReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[WS] Đã vượt quá số lần thử kết nối lại.");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`[WS] Thử kết nối lại sau ${delay}ms (lần ${this.reconnectAttempts})...`);

    setTimeout(() => this.connect(), delay);
  }

  /** Trạng thái kết nối hiện tại */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// ─────────────────────────────────────────────
// Singleton Exports
// ─────────────────────────────────────────────

/** REST API client instance */
export const matchingApi = new MatchingApiClient();

/** Tạo WebSocket client cho một tokenId */
export function createOrderBookWS(tokenId: string): OrderBookWebSocket {
  return new OrderBookWebSocket(tokenId);
}

export { MatchingApiClient, OrderBookWebSocket };
