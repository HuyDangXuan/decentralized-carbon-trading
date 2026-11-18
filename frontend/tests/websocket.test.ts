import test from "node:test";
import assert from "node:assert/strict";
import { setTimeout as wait } from "node:timers/promises";
import { normalizeOrderBook, OrderBookWebSocket } from "../src/services/matchingApi";

class FakeSocket {
  readyState = 0;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  close() { this.readyState = 3; this.onclose?.(); }
}
test("disconnect cancels a scheduled reconnect and parallel connects are ignored", async () => {
  const sockets: FakeSocket[] = [];
  const client = new OrderBookWebSocket("101", "ws://engine", () => {
    const socket = new FakeSocket(); sockets.push(socket); return socket as unknown as WebSocket;
  }, 5);
  client.connect(); client.connect();
  assert.equal(sockets.length, 1);
  sockets[0].close(); client.disconnect();
  await wait(20);
  assert.equal(sockets.length, 1);
});
test("legacy event names map to canonical events; malformed messages are ignored", () => {
  const socket = new FakeSocket();
  const client = new OrderBookWebSocket("101", "ws://engine", () => socket as unknown as WebSocket);
  let received = 0;
  client.on("orderbook.update", message => { assert.equal(message.event, "orderbook.update"); received++; });
  client.connect();
  socket.onmessage?.({ data: "not json" });
  socket.onmessage?.({ data: JSON.stringify({ event: "orderbook_update", data: {} }) });
  socket.onmessage?.({ data: JSON.stringify({ event: "orderbook.update", data: {} }) });
  assert.equal(received, 2);
  client.disconnect();
});
test("snapshot and update messages deliver validated price levels for the requested lot", () => {
  const socket = new FakeSocket();
  const client = new OrderBookWebSocket("101", "ws://engine", () => socket as unknown as WebSocket);
  const apply = (message: { data: unknown; tokenId?: unknown }) => {
    const book = normalizeOrderBook(message.data, "101", message.tokenId);
    seen.push(book.bids.map(level => level.remainingAmount));
  };
  const seen: string[][] = [];
  client.on("orderbook.snapshot", apply);
  client.on("orderbook.update", apply);
  client.connect();
  const data = { bids: [{ price: 14500000, amount: 2, orders: 1 }], asks: [] };
  socket.onmessage?.({ data: JSON.stringify({ event: "orderbook.snapshot", tokenId: 101, data: { bids: [], asks: [] } }) });
  socket.onmessage?.({ data: JSON.stringify({ event: "orderbook.update", tokenId: 102, data }) });
  socket.onmessage?.({ data: JSON.stringify({ event: "orderbook.update", tokenId: 101, data }) });
  assert.deepEqual(seen, [[], ["2"]]);
  client.disconnect();
});
