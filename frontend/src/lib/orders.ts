import { encodeAbiParameters, formatUnits, isAddress, keccak256, parseUnits, zeroAddress, type Address, type Hex } from "viem";

export enum OrderType { BID = 0, ASK = 1 }
export enum TimeInForce { GTC = 0, IOC = 1 }
export const MAX_UINT128 = (1n << 128n) - 1n;
const MAX_UINT256 = (1n << 256n) - 1n;
// SRS §3.4. Field order is part of the signature.
export const ORDER_TYPES = {
  Order: [
    { name: "orderId", type: "bytes32" }, { name: "trader", type: "address" },
    { name: "orderType", type: "uint8" }, { name: "tokenId", type: "uint256" },
    { name: "amount", type: "uint128" }, { name: "pricePerUnit", type: "uint128" },
    { name: "timeInForce", type: "uint8" }, { name: "nonce", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
} as const;
export const ORDER_TYPE_STRING = "Order(bytes32 orderId,address trader,uint8 orderType,uint256 tokenId,uint128 amount,uint128 pricePerUnit,uint8 timeInForce,uint256 nonce,uint256 deadline)";
export interface OrderParams {
  orderType: OrderType;
  tokenId: bigint;
  amount: bigint;
  pricePerUnit: bigint;
  timeInForce: TimeInForce;
  deadline?: bigint;
}
export interface OrderMessage extends Omit<OrderParams, "deadline"> {
  orderId: Hex;
  trader: Address;
  nonce: bigint;
  deadline: bigint;
}
export interface SignedOrder {
  orderId: Hex;
  trader: Address;
  orderType: OrderType;
  timeInForce: TimeInForce;
  tokenId: string;
  amount: string;
  pricePerUnit: string;
  nonce: string;
  deadline: string;
  signature: Hex;
  chainId: number;
  verifyingContract: Address;
}
export function getEIP712Domain(chainId: number, verifyingContract: Address) {
  if (chainId !== 80002 && chainId !== 11155111) throw new Error("Mạng không được hỗ trợ.");
  if (!isAddress(verifyingContract) || verifyingContract.toLowerCase() === zeroAddress) throw new Error("Địa chỉ hợp đồng đấu giá chưa hợp lệ.");
  return { name: "EPU Carbon Double Auction", version: "2.0", chainId, verifyingContract } as const;
}
export function parseCreditAmount(value: string): bigint {
  if (!/^\d+$/.test(value)) throw new Error("Khối lượng phải là số nguyên tCO2e.");
  const amount = BigInt(value);
  if (amount < 1n || amount > MAX_UINT128) throw new Error("Khối lượng vượt giới hạn uint128 hoặc bằng 0.");
  return amount;
}
export function parseTokenId(value: string): bigint {
  if (!/^\d+$/.test(value) || BigInt(value) > MAX_UINT256) throw new Error("Token ID phải là số nguyên uint256.");
  return BigInt(value);
}
export function usdToMicroUsdc(value: string): bigint {
  if (!/^\d+(\.\d{1,6})?$/.test(value)) throw new Error("Giá USDC phải dương, tối đa 6 chữ số thập phân.");
  const price = parseUnits(value, 6);
  if (price < 1n || price > MAX_UINT128) throw new Error("Giá vượt giới hạn uint128 hoặc bằng 0.");
  return price;
}
export function microUsdcToUsd(value: bigint): string { return formatUnits(value, 6); }
export function buildOrderMessage(trader: Address, params: OrderParams, nonce: bigint, now = BigInt(Math.floor(Date.now() / 1000))): OrderMessage {
  if (!isAddress(trader) || trader.toLowerCase() === zeroAddress) throw new Error("Địa chỉ ví không hợp lệ.");
  if (![OrderType.BID, OrderType.ASK].includes(params.orderType)) throw new Error("Loại lệnh không hợp lệ.");
  if (![TimeInForce.GTC, TimeInForce.IOC].includes(params.timeInForce)) throw new Error("GTC/IOC không hợp lệ.");
  parseCreditAmount(params.amount.toString());
  parseTokenId(params.tokenId.toString());
  if (params.pricePerUnit < 1n || params.pricePerUnit > MAX_UINT128) throw new Error("Giá phải thuộc uint128 dương.");
  if (nonce < 0n || nonce > MAX_UINT256) throw new Error("Nonce không hợp lệ.");
  const deadline = params.deadline ?? now + 3600n;
  if (deadline <= now || deadline > MAX_UINT256) throw new Error("Thời hạn lệnh phải nằm trong tương lai.");
  // Exact FR-04 formula. timeInForce is bound by the typed signature.
  // Identical seven-field orders share an ID and must be deduplicated by the API.
  const orderId = keccak256(encodeAbiParameters(
    [{ type: "address" }, { type: "uint8" }, { type: "uint256" }, { type: "uint128" }, { type: "uint128" }, { type: "uint256" }, { type: "uint256" }],
    [trader, params.orderType, params.tokenId, params.amount, params.pricePerUnit, nonce, deadline],
  ));
  return { ...params, orderId, trader, nonce, deadline };
}
