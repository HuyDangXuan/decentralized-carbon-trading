/**
 * ABI rút gọn của CarbonDoubleAuction.sol
 * Chỉ giữ các hàm cần thiết cho DApp frontend.
 */
export const CARBON_DOUBLE_AUCTION_ABI = [
  // === READ FUNCTIONS ===
  {
    name: "carbonToken",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ name: "", type: "address" }],
  },
  {
    name: "matchingAgentAddress",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ name: "", type: "address" }],
  },
  {
    name: "executedTrades",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "", type: "bytes32" }],
    outputs: [{ name: "", type: "bool" }],
  },
  {
    name: "getSettlementCount",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ name: "", type: "uint256" }],
  },
  {
    name: "settlementHistory",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "", type: "uint256" }],
    outputs: [
      { name: "tradeHash", type: "bytes32" },
      { name: "buyer", type: "address" },
      { name: "seller", type: "address" },
      { name: "tokenId", type: "uint256" },
      { name: "amount", type: "uint256" },
      { name: "pricePerUnitWei", type: "uint256" },
      { name: "settledAt", type: "uint256" },
    ],
  },

  // === WRITE FUNCTIONS ===
  {
    name: "settleMatchedTrade",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "tradeHash", type: "bytes32" },
      { name: "buyer", type: "address" },
      { name: "seller", type: "address" },
      { name: "tokenId", type: "uint256" },
      { name: "amount", type: "uint256" },
      { name: "pricePerUnit", type: "uint256" },
    ],
    outputs: [],
  },
  {
    name: "setMatchingAgent",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "_newAgent", type: "address" }],
    outputs: [],
  },

  // === EVENTS ===
  {
    name: "TradeExecuted",
    type: "event",
    inputs: [
      { name: "tradeHash", type: "bytes32", indexed: true },
      { name: "buyer", type: "address", indexed: true },
      { name: "seller", type: "address", indexed: true },
      { name: "tokenId", type: "uint256", indexed: false },
      { name: "amount", type: "uint256", indexed: false },
      { name: "clearingPrice", type: "uint256", indexed: false },
    ],
  },
] as const;
