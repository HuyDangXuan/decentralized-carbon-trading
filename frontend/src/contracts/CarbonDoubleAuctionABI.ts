import type { Abi } from "viem";

// Await the compiled v2 artifact; the old baseline ABI cannot verify signed orders.
// Populate with scripts/import-auction-artifact.mjs after Đức delivers the build.
export const CARBON_DOUBLE_AUCTION_ABI: Abi = [];
export const AUCTION_ABI_READY = false;
export const AUCTION_NONCE_FUNCTION = "nonces";
