/**
 * contracts/index.ts
 * Barrel export: địa chỉ contract đã deploy + ABIs.
 *
 * ⚠️  Sau khi deploy lên testnet (Polygon Amoy / Ethereum Sepolia),
 *     thay các giá trị CONTRACT_ADDRESSES bằng địa chỉ thực.
 */

export { CARBON_CREDIT_1155_ABI } from "./CarbonCredit1155ABI";
export { CARBON_DOUBLE_AUCTION_ABI } from "./CarbonDoubleAuctionABI";

/**
 * Địa chỉ contract đã deploy.
 * Mặc định là placeholder – thay bằng giá trị thực sau khi deploy.
 */
export const CONTRACT_ADDRESSES = {
  /** Polygon Amoy Testnet (chainId 80002) */
  polygonAmoy: {
    carbonCredit1155: "0x0000000000000000000000000000000000000000" as `0x${string}`,
    carbonDoubleAuction: "0x0000000000000000000000000000000000000000" as `0x${string}`,
  },
  /** Ethereum Sepolia Testnet (chainId 11155111) */
  sepolia: {
    carbonCredit1155: "0x0000000000000000000000000000000000000000" as `0x${string}`,
    carbonDoubleAuction: "0x0000000000000000000000000000000000000000" as `0x${string}`,
  },
} as const;
