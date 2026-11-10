import test from "node:test";
import assert from "node:assert/strict";
import { MatchingApiClient } from "../src/services/matchingApi";
import { OrderType, TimeInForce, type SignedOrder } from "../src/lib/orders";

const id = `0x${"11".repeat(32)}` as const;
const address = `0x${"22".repeat(20)}` as const;
const signed: SignedOrder = { orderId: id, trader: address, verifyingContract: address, orderType: OrderType.BID, timeInForce: TimeInForce.IOC, tokenId: "101", amount: "9007199254740993", pricePerUnit: "14500001", nonce: "7", deadline: "2000000000", signature: `0x${"33".repeat(65)}`, chainId: 80002 };
const rawOrder = { order_id: id, trader: address, order_type: 0, token_id: "101", amount: "9007199254740993", remaining_amount: "3", price_per_unit: "14500001", status: "ROLLED_OVER", rollover_count: 1 };
function fetchJson(payload: unknown, code = 200): typeof fetch { return async () => new Response(JSON.stringify(payload), { status: code }); }

test("submission sends signed fields as exact strings including time_in_force", async () => {
  let sent: Record<string, unknown> = {};
  const fetcher: typeof fetch = async (url, init) => {
    assert.equal(url, "http://engine/api/v1/orders");
    assert.equal(init?.method, "POST");
    sent = JSON.parse(String(init?.body));
    return new Response(JSON.stringify({ order_id: id, status: "ACTIVE" }), { status: 201 });
  };
  const result = await new MatchingApiClient("http://engine/", fetcher).submitOrder(signed);
  assert.equal(result.success, true);
  assert.equal(sent.amount, signed.amount);
  assert.equal(sent.time_in_force, 1);
  assert.equal(sent.nonce, "7");
  assert.equal(sent.verifying_contract, address);
});
test("snake_case and success envelopes normalize orderbook without losing integers", async () => {
  const payload = { success: true, data: { token_id: "101", bids: [rawOrder], asks: [] } };
  const result = await new MatchingApiClient("http://engine", fetchJson(payload)).getOrderBook("101");
  assert.equal(result.data?.bids[0].amount, "9007199254740993");
  assert.equal(result.data?.bids[0].rolloverCount, 1);
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
  assert.equal(result.data?.cutoffAt, 2000000000);
  assert.equal(result.data?.durationSeconds, 300);
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
