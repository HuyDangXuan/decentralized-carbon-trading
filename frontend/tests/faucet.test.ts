import assert from "node:assert/strict";
import { test } from "node:test";
import { parseGwei } from "viem";
import { amoyFaucetFees } from "../src/contracts/faucet";

test("raises a low Amoy faucet tip while preserving room for the base fee", () => {
  const fees = amoyFaucetFees({ maxFeePerGas: parseGwei("6.5"), maxPriorityFeePerGas: parseGwei("1.5") });
  assert.deepEqual(fees, { maxFeePerGas: parseGwei("30"), maxPriorityFeePerGas: parseGwei("25") });
});

test("uses the estimate as-is when the Amoy tip clears the floor", () => {
  const fees = { maxFeePerGas: parseGwei("40"), maxPriorityFeePerGas: parseGwei("30") };
  assert.deepEqual(amoyFaucetFees(fees), fees);
});
