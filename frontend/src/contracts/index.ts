import { isAddress, zeroAddress, type Address } from "viem";
export { CARBON_CREDIT_1155_ABI } from "./CarbonCredit1155ABI";
export { CARBON_DOUBLE_AUCTION_ABI, AUCTION_ABI_READY, AUCTION_NONCE_FUNCTION } from "./CarbonDoubleAuctionABI";

function configuredAddress(value?: string): Address | undefined {
  return value && isAddress(value) && value.toLowerCase() !== zeroAddress ? value as Address : undefined;
}
export const CONTRACT_ADDRESSES = {
  polygonAmoy: {
    carbonCredit1155: configuredAddress(process.env.NEXT_PUBLIC_AMOY_CARBON_CREDIT_ADDRESS),
    carbonDoubleAuction: configuredAddress(process.env.NEXT_PUBLIC_AMOY_AUCTION_ADDRESS),
  },
  sepolia: {
    carbonCredit1155: configuredAddress(process.env.NEXT_PUBLIC_SEPOLIA_CARBON_CREDIT_ADDRESS),
    carbonDoubleAuction: configuredAddress(process.env.NEXT_PUBLIC_SEPOLIA_AUCTION_ADDRESS),
  },
} as const;
export function getContractAddresses(chainId?: number) {
  if (chainId === 80002) return CONTRACT_ADDRESSES.polygonAmoy;
  if (chainId === 11155111) return CONTRACT_ADDRESSES.sepolia;
  return undefined;
}
export function requireContractAddress(chainId: number | undefined, key: "carbonCredit1155" | "carbonDoubleAuction"): Address {
  const address = getContractAddresses(chainId)?.[key];
  if (!address) throw new Error("Chưa cấu hình hợp đồng cho mạng đang kết nối.");
  return address;
}
