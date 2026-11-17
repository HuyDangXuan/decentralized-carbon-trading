import { parseAbi } from "viem";

// Read-only signing entries from Đức's deployed CarbonDoubleAuction ABI.
export const AUCTION_NONCE_FUNCTION = "userNonces";
export const CARBON_DOUBLE_AUCTION_ABI = parseAbi([
  "function ORDER_TYPEHASH() view returns (bytes32)",
  "function userNonces(address trader) view returns (uint256)",
]);
