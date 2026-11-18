import test from "node:test";
import assert from "node:assert/strict";
import { MatchingApiClient, sessionAcceptsOrders } from "../src/services/matchingApi";
import { OrderType, TimeInForce, type SignedOrder } from "../src/lib/orders";

const id = `0x${"11".repeat(32)}` as const;
const address = `0x${"22".repeat(20)}` as const;
const signed: SignedOrder = { orderId: id, trader: address, verifyingContract: address, orderType: OrderType.BID, timeInForce: TimeInForce.IOC, tokenId: "101", amount: "9007199254740993", pricePerUnit: "14500001", nonce: "7", deadline: "2000000000", signature: `0x${"33".repeat(65)}`, chainId: 80002 };
const rawOrder = { order_id: id, trader: address, order_type: 0, token_id: "101", amount: "9007199254740993", remaining_amount: "3", price_per_unit: "14500001", status: "ROLLED_OVER", rollover_count: 1 };
function fetchJson(payload: unknown, code = 200): typeof fetch { return async () => new Response(JSON.stringify(payload), { status: code }); }

test("submission wraps signed fields in FastAPI's order object without losing integer precision", async () => {
  let sent: unknown;
  const fetcher: typeof fetch = async (url, init) => {
    assert.equal(url, "http://engine/api/v1/orders");
    assert.equal(init?.method, "POST");
    sent = JSON.parse(String(init?.body));
    return new Response(JSON.stringify({ order_id: id, status: "ACTIVE" }), { status: 201 });
  };
  const result = await new MatchingApiClient("http://engine/", fetcher).submitOrder(signed);
  assert.equal(result.success, true);
  assert.deepEqual(sent, {
    order: {
      orderId: id, trader: address, orderType: 0, tokenId: "101", amount: signed.amount,
      pricePerUnit: "14500001", nonce: "7", deadline: "2000000000",
    },
    signature: signed.signature,
    time_in_force: "IOC",
  });
});
test("the FastAPI aggregate book preserves amounts and sorts levels in market order", async () => {
  const payload = { success: true, data: { token_id: "101", bids: [
    { price: 14000000, amount: 2, orders: 1 },
    { price: "14500001", amount: "9007199254740993", orders: 2 },
  ], asks: [] } };
  const result = await new MatchingApiClient("http://engine", fetchJson(payload)).getOrderBook("101");
  assert.deepEqual(result.data?.bids, [
    { pricePerUnit: "14500001", remainingAmount: "9007199254740993", orderCount: 2 },
    { pricePerUnit: "14000000", remainingAmount: "2", orderCount: 1 },
  ]);
});
test("individual orders aggregate at each price while order detail remains per-order", async () => {
  const book = await new MatchingApiClient("http://engine", fetchJson({ bids: [rawOrder, { ...rawOrder, remaining_amount: "4" }], asks: [] })).getOrderBook("101");
  assert.deepEqual(book.data?.bids, [{ pricePerUnit: "14500001", remainingAmount: "7", orderCount: 2 }]);
  const detail = await new MatchingApiClient("http://engine", fetchJson(rawOrder)).getOrder(id);
  assert.equal(detail.data?.amount, "9007199254740993");
  assert.equal(detail.data?.rolloverCount, 1);
});
test("wrong tokens, unsafe numbers, floating prices and unknown statuses fail closed", async () => {
  for (const change of [{ token_id: "102" }, { amount: 9007199254740993 }, { price_per_unit: "14.5" }, { status: "SUCCESS" }, { remaining_amount: "9999999999999999999999" }, { order_type: 1 }]) {
    const result = await new MatchingApiClient("http://engine", fetchJson({ bids: [{ ...rawOrder, ...change }], asks: [] })).getOrderBook("101");
    assert.equal(result.success, false);
  }
});
test("FastAPI validation errors become readable text", async () => {
  const api = new MatchingApiClient("http://engine", fetchJson({ detail: [{ loc: ["body", "amount"], msg: "amount must be positive" }] }, 422));
  const result = await api.submitOrder(signed);
  assert.equal(result.success, false);
  assert.match(result.error!, /amount must be positive/);
});
test("session timer uses explicit server phase and timestamps", async () => {
  const result = await new MatchingApiClient("http://engine", fetchJson({ session_id: "s1", phase: "CALL", duration_seconds: 300, cutoff_at: 2000000000, phase_ends_at: 2000000000 })).getCurrentSession("101");
  assert.equal(result.data?.mode, "scheduled");
  assert.equal(result.data?.mode === "scheduled" && result.data.durationSeconds, 300);
  assert.equal(sessionAcceptsOrders(result.data ?? null, 1999999999), true);
  assert.equal(sessionAcceptsOrders(result.data ?? null, 2000000000), false);
});
test("a pair of session IDs enables manual mode without fabricating a timer", async () => {
  const api = new MatchingApiClient("http://engine", fetchJson({ next_session_id: 2, last_session_id: 1 }));
  const result = await api.getCurrentSession("101");
  assert.deepEqual(result.data, { mode: "manual", sessionId: "2", tokenId: "101" });
  assert.equal(sessionAcceptsOrders(result.data ?? null), true);
  const malformed = await new MatchingApiClient("http://engine", fetchJson({ next_session_id: 8, last_session_id: 1 })).getCurrentSession("101");
  assert.equal(malformed.success, false);
});
test("a timeout aborts the request and never retries a POST", async () => {
  let calls = 0;
  const fetcher: typeof fetch = async (_url, init) => new Promise((_resolve, reject) => {
    calls++;
    init?.signal?.addEventListener("abort", () => reject(new Error("aborted")));
  });
  const result = await new MatchingApiClient("http://engine", fetcher, 5).submitOrder(signed);
  assert.equal(result.success, false);
  assert.match(result.error!, /Kiểm tra trạng thái/);
  assert.equal(calls, 1);
});
test("a mismatched acknowledgement is not shown as an accepted order", async () => {
  const result = await new MatchingApiClient("http://engine", fetchJson({ order_id: "other", status: "ACTIVE" })).submitOrder(signed);
  assert.equal(result.success, false);
});
