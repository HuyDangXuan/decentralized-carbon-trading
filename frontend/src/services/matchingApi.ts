import type { SignedOrder } from "../lib/orders";

const API_BASE_URL = process.env.NEXT_PUBLIC_MATCHING_API_URL ?? "http://localhost:8000";
const WS_BASE_URL = process.env.NEXT_PUBLIC_MATCHING_WS_URL ?? "ws://localhost:8000";
export interface ApiResponse<T> { success: boolean; data?: T; error?: string; timestamp: number }
export const ORDER_STATUSES = ["NEW", "ACTIVE", "PARTIALLY_FILLED", "FILLED", "ROLLED_OVER", "EXPIRED", "CANCELLED", "REJECTED", "ONCHAIN_PENDING", "SETTLED_FINAL"] as const;
export type OrderStatus = typeof ORDER_STATUSES[number];
export interface OrderBookEntry {
  orderId: string; trader: string; orderType: "BID" | "ASK"; tokenId: string;
  amount: string; remainingAmount: string; pricePerUnit: string; status: OrderStatus;
  createdAt?: number; rolloverCount?: number;
}
export interface OrderBookSnapshot { tokenId: string; bids: OrderBookEntry[]; asks: OrderBookEntry[]; lastClearingPrice?: string }
export interface CurrentSession {
  sessionId: string; tokenId: string; phase: "CALL" | "MATCH" | "SETTLE";
  cutoffAt: number; phaseEndsAt: number; durationSeconds: 300 | 900;
}
export interface MatchedPair { bidOrderId: string; askOrderId: string; matchAmount: string; clearingPrice: string; tradeHash: string }
export interface SessionResult { sessionId: string; tokenId: string; clearingPrice: string; totalMatchedAmount: string; matchCount: number; matches: MatchedPair[]; executedAt: number }
export interface SubmitOrderResponse { orderId: string; status: OrderStatus; message?: string }
type JsonObject = Record<string, unknown>;
function object(value: unknown): JsonObject {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Phản hồi API không đúng cấu trúc.");
  return value as JsonObject;
}
function field(data: JsonObject, camel: string, snake: string): unknown { return data[camel] ?? data[snake]; }
function string(value: unknown, label: string): string {
  if (typeof value !== "string" || !value) throw new Error(`API thiếu ${label}.`);
  return value;
}
function uint(value: unknown, label: string): string {
  if (typeof value === "number" && Number.isSafeInteger(value) && value >= 0) return String(value);
  if (typeof value === "string" && /^\d+$/.test(value)) return value;
  throw new Error(`API trả ${label} không phải chuỗi số nguyên an toàn.`);
}
function safeInteger(value: unknown, label: string): number {
  const parsed = uint(value, label);
  if (BigInt(parsed) > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error(`API trả ${label} vượt giới hạn số nguyên an toàn.`);
  return Number(parsed);
}
function status(value: unknown): OrderStatus {
  if (!ORDER_STATUSES.includes(value as OrderStatus)) throw new Error("API trả trạng thái lệnh chưa được hỗ trợ.");
  return value as OrderStatus;
}
export function normalizeOrder(value: unknown): OrderBookEntry {
  const data = object(value);
  const type = field(data, "orderType", "order_type");
  if (![0, 1, "BID", "ASK"].includes(type as string | number)) throw new Error("API trả loại lệnh không hợp lệ.");
  const amount = uint(data.amount, "amount");
  const remaining = uint(field(data, "remainingAmount", "remaining_amount"), "remaining_amount");
  if (BigInt(remaining) > BigInt(amount)) throw new Error("Khối lượng còn lại vượt tổng khối lượng lệnh.");
  return {
    orderId: string(field(data, "orderId", "order_id"), "order_id"),
    trader: string(data.trader ?? data.trader_address, "trader"),
    orderType: type === 0 || type === "BID" ? "BID" : "ASK",
    tokenId: uint(field(data, "tokenId", "token_id"), "token_id"),
    amount,
    remainingAmount: remaining,
    pricePerUnit: uint(field(data, "pricePerUnit", "price_per_unit"), "price_per_unit"),
    status: status(data.status),
    ...(field(data, "rolloverCount", "rollover_count") !== undefined ? { rolloverCount: safeInteger(field(data, "rolloverCount", "rollover_count"), "rollover_count") } : {}),
  };
}
function describeError(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(item => typeof item === "object" && item ? String((item as JsonObject).msg ?? "Dữ liệu không hợp lệ") : String(item)).join("; ");
  return "Matching Engine từ chối yêu cầu.";
}

export class MatchingApiClient {
  constructor(private baseUrl = API_BASE_URL, private fetcher: typeof fetch = (input, init) => fetch(input, init), private timeoutMs = 10000) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }
  private async request<T>(method: string, path: string, body: unknown, parse: (value: unknown) => T): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const response = await this.fetcher(`${this.baseUrl}/api/v1${path}`, {
        method, headers: { "Content-Type": "application/json" }, signal: controller.signal,
        ...(body !== undefined ? { body: JSON.stringify(body) } : {}), cache: "no-store",
      });
      const payload: unknown = await response.json();
      const data = object(payload);
      if (!response.ok || data.success === false) throw new Error(describeError(data.detail ?? data.error ?? `HTTP ${response.status}`));
      return { success: true, data: parse(data.success === true ? data.data : payload), timestamp: Date.now() };
    } catch (cause) {
      const detail = cause instanceof Error ? cause.message : "Lỗi không xác định";
      return { success: false, error: controller.signal.aborted ? "Matching Engine phản hồi quá lâu. Kiểm tra trạng thái lệnh trước khi gửi lại." : detail, timestamp: Date.now() };
    } finally { clearTimeout(timer); }
  }
  submitOrder(order: SignedOrder): Promise<ApiResponse<SubmitOrderResponse>> {
    return this.request("POST", "/orders", {
      order_id: order.orderId, trader: order.trader, order_type: order.orderType,
      token_id: order.tokenId, amount: order.amount, price_per_unit: order.pricePerUnit,
      time_in_force: order.timeInForce, nonce: order.nonce, deadline: order.deadline,
      signature: order.signature, chain_id: order.chainId, verifying_contract: order.verifyingContract,
    }, value => {
      const data = object(value);
      const orderId = string(field(data, "orderId", "order_id"), "order_id");
      if (orderId.toLowerCase() !== order.orderId.toLowerCase()) throw new Error("API xác nhận sai mã lệnh.");
      return { orderId, status: status(data.status), ...(typeof data.message === "string" ? { message: data.message } : {}) };
    });
  }
  getOrder(orderId: string): Promise<ApiResponse<OrderBookEntry>> {
    return this.request("GET", `/orders/${encodeURIComponent(orderId)}`, undefined, value => {
      const order = normalizeOrder(value);
      if (order.orderId.toLowerCase() !== orderId.toLowerCase()) throw new Error("API trả sai mã lệnh.");
      return order;
    });
  }
  cancelOrder(orderId: string, trader: string, signature: string): Promise<ApiResponse<SubmitOrderResponse>> {
    return this.request("DELETE", `/orders/${encodeURIComponent(orderId)}`, { trader, signature }, value => {
      const data = object(value);
      return { orderId: string(field(data, "orderId", "order_id"), "order_id"), status: status(data.status) };
    });
  }
  getOrderBook(tokenId: string): Promise<ApiResponse<OrderBookSnapshot>> {
    return this.request("GET", `/orderbook/${encodeURIComponent(tokenId)}`, undefined, value => {
      const data = object(value);
      const returnedId = field(data, "tokenId", "token_id");
      if (returnedId !== undefined && uint(returnedId, "token_id") !== tokenId) throw new Error("API trả sổ lệnh của token khác.");
      if (!Array.isArray(data.bids) || !Array.isArray(data.asks)) throw new Error("API thiếu bids/asks.");
      const bids = data.bids.map(normalizeOrder), asks = data.asks.map(normalizeOrder);
      if (bids.some(order => order.orderType !== "BID") || asks.some(order => order.orderType !== "ASK")) throw new Error("API đặt lệnh sai phía mua/bán.");
      if ([...bids, ...asks].some(order => order.tokenId !== tokenId)) throw new Error("Sổ lệnh chứa tokenId khác; khớp chéo token chưa được bật.");
      const lastPrice = field(data, "lastClearingPrice", "last_clearing_price");
      return { tokenId, bids, asks, ...(lastPrice !== undefined ? { lastClearingPrice: uint(lastPrice, "last_clearing_price") } : {}) };
    });
  }
  getCurrentSession(tokenId: string): Promise<ApiResponse<CurrentSession>> {
    return this.request("GET", `/sessions/current?token_id=${encodeURIComponent(tokenId)}`, undefined, value => {
      const data = object(value);
      const phase = data.phase;
      if (!["CALL", "MATCH", "SETTLE"].includes(phase as string)) throw new Error("API trả giai đoạn phiên không hợp lệ.");
      const duration = safeInteger(field(data, "durationSeconds", "duration_seconds"), "duration_seconds");
      if (duration !== 300 && duration !== 900) throw new Error("Chu kỳ phiên phải là 300 hoặc 900 giây theo ADR-001.");
      return {
        sessionId: string(field(data, "sessionId", "session_id"), "session_id"), tokenId,
        phase: phase as CurrentSession["phase"], durationSeconds: duration,
        cutoffAt: safeInteger(field(data, "cutoffAt", "cutoff_at"), "cutoff_at"),
        phaseEndsAt: safeInteger(field(data, "phaseEndsAt", "phase_ends_at"), "phase_ends_at"),
      };
    });
  }
}

export const WS_EVENTS = ["orderbook.update", "match.executed", "settlement.confirmed", "settlement.failed", "session.completed", "price.update"] as const;
export type WSEventType = typeof WS_EVENTS[number];
export interface WSMessage { event: WSEventType; data: unknown; timestamp?: number }
const aliases: Record<string, WSEventType> = { orderbook_update: "orderbook.update", trade_executed: "match.executed", session_completed: "session.completed", price_update: "price.update" };
export class OrderBookWebSocket {
  private ws: WebSocket | null = null;
  private handlers = new Map<WSEventType, Set<(message: WSMessage) => void>>();
  private reconnectTimer: ReturnType<typeof setTimeout> | undefined;
  private attempts = 0;
  private stopped = true;
  constructor(private tokenId: string, private baseUrl = WS_BASE_URL, private createSocket = (url: string) => new WebSocket(url), private reconnectDelay = 2000) {}
  connect(): void {
    if (this.ws && (this.ws.readyState === 0 || this.ws.readyState === 1)) return;
    this.stopped = false;
    try {
      const socket = this.createSocket(`${this.baseUrl.replace(/\/$/, "")}/ws/orderbook/${encodeURIComponent(this.tokenId)}`);
      this.ws = socket;
      socket.onopen = () => { this.attempts = 0; };
      socket.onmessage = event => {
        if (this.stopped || this.ws !== socket) return;
        try {
          const raw = object(JSON.parse(event.data));
          const name = typeof raw.event === "string" ? aliases[raw.event] ?? raw.event : "";
          if (!WS_EVENTS.includes(name as WSEventType)) return;
          const message: WSMessage = { event: name as WSEventType, data: raw.data };
          this.handlers.get(message.event)?.forEach(handler => handler(message));
        } catch { /* Ignore malformed messages; REST polling remains authoritative. */ }
      };
      socket.onclose = () => { if (this.ws === socket) { this.ws = null; this.reconnect(); } };
      socket.onerror = () => { /* onclose schedules reconnect. */ };
    } catch { this.reconnect(); }
  }
  on(event: WSEventType, handler: (message: WSMessage) => void): void {
    const handlers = this.handlers.get(event) ?? new Set(); handlers.add(handler); this.handlers.set(event, handlers);
  }
  disconnect(): void {
    this.stopped = true;
    clearTimeout(this.reconnectTimer);
    const socket = this.ws;
    this.ws = null;
    if (socket) { socket.onclose = null; socket.onmessage = null; socket.onopen = null; socket.close(); }
    this.handlers.clear();
  }
  private reconnect(): void {
    if (this.stopped || this.attempts >= 5) return;
    clearTimeout(this.reconnectTimer);
    const delay = this.reconnectDelay * 2 ** this.attempts++;
    this.reconnectTimer = setTimeout(() => { if (!this.stopped) this.connect(); }, delay);
  }
  get isConnected(): boolean { return this.ws?.readyState === 1; }
}
export const matchingApi = new MatchingApiClient();
export function createOrderBookWS(tokenId: string): OrderBookWebSocket { return new OrderBookWebSocket(tokenId); }
