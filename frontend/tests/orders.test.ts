import test from "node:test";
import assert from "node:assert/strict";
import { concatHex, keccak256, toHex, verifyTypedData, zeroAddress } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { buildOrderMessage, getEIP712Domain, MAX_UINT128, microUsdcToUsd, ORDER_TYPES, OrderType, parseCreditAmount, parseTokenId, TimeInForce, usdToMicroUsdc } from "../src/lib/orders";

// Public deterministic test key. Never used for a network transaction.
const account = privateKeyToAccount(`0x${"01".repeat(32)}`);
const auction = `0x${"22".repeat(20)}` as const;
const params = { orderType: OrderType.BID, tokenId: 101n, amount: 3n, pricePerUnit: 14500000n, timeInForce: TimeInForce.GTC, deadline: 2000n };

test("price conversion preserves six decimals and large amounts exactly", () => {
  assert.equal(usdToMicroUsdc("14.500001"), 14500001n);
  assert.equal(usdToMicroUsdc("0.000001"), 1n);
  assert.equal(microUsdcToUsd(900719925474099312345n), "900719925474099.312345");
  for (const bad of ["0", "-1", "1e3", "1.0000001", "NaN", "1,5", ""]) assert.throws(() => usdToMicroUsdc(bad));
});
test("amount and token parsers reject fractional, negative and overflowing inputs", () => {
  assert.equal(parseCreditAmount(MAX_UINT128.toString()), MAX_UINT128);
  for (const bad of ["0", "-1", "0.5", "1e2", (MAX_UINT128 + 1n).toString()]) assert.throws(() => parseCreditAmount(bad));
  assert.equal(parseTokenId("0"), 0n);
  assert.throws(() => parseTokenId((1n << 256n).toString()));
});
test("FR-04 identifier matches seven independently padded ABI words", () => {
  const order = buildOrderMessage(account.address, params, 7n, 1000n);
  const reference = keccak256(concatHex([
    `0x${account.address.slice(2).padStart(64, "0")}`, toHex(0n, { size: 32 }), toHex(101n, { size: 32 }),
    toHex(3n, { size: 32 }), toHex(14500000n, { size: 32 }), toHex(7n, { size: 32 }), toHex(2000n, { size: 32 }),
  ]));
  assert.equal(order.orderId, reference);
  assert.notEqual(order.orderId, buildOrderMessage(account.address, { ...params, amount: 4n }, 7n, 1000n).orderId);
});
test("invalid network, empty contract and expired orders are blocked", () => {
  assert.throws(() => getEIP712Domain(1, auction));
  assert.throws(() => getEIP712Domain(80002, zeroAddress));
  assert.throws(() => buildOrderMessage(account.address, { ...params, deadline: 1000n }, 0n, 1000n));
});
test("signature binds GTC/IOC, nonce, chain and verifying contract", async () => {
  const domain = getEIP712Domain(80002, auction);
  const message = buildOrderMessage(account.address, params, 7n, 1000n);
  const data = { domain, types: ORDER_TYPES, primaryType: "Order" as const, message };
  const signature = await account.signTypedData(data);
  assert.equal(await verifyTypedData({ ...data, address: account.address, signature }), true);
  for (const changed of [{ ...message, timeInForce: TimeInForce.IOC }, { ...message, nonce: 8n }]) {
    assert.equal(await verifyTypedData({ ...data, message: changed, address: account.address, signature }), false);
  }
  for (const changed of [{ ...domain, chainId: 11155111 }, { ...domain, verifyingContract: `0x${"33".repeat(20)}` as const }]) {
    assert.equal(await verifyTypedData({ ...data, domain: changed, address: account.address, signature }), false);
  }
});
