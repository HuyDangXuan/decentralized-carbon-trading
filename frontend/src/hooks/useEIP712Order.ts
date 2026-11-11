/**
 * hooks/useEIP712Order.ts
 * Hook ký lệnh EIP-712 Typed Data trên MetaMask (Gasless Order).
 *
 * Giải quyết vấn đề T2 & Đ11:
 *   - Người dùng ký lệnh off-chain (không tốn gas)
 *   - Cấu trúc ký tuân thủ EIP-712 Typed Data
 *   - Tương thích với CarbonDoubleAuction.sol v2 (spec mới Đức)
 *   - Gửi qua API Service của Matching Engine (Phi)
 *
 * Luồng: User ký EIP-712 → Frontend gửi POST /api/v1/orders → Engine nhận & khớp
 */

"use client";

import { useCallback, useState } from "react";
import { useAccount, useChainId, useSignTypedData } from "wagmi";
import { keccak256, encodePacked, toHex } from "viem";
import { CONTRACT_ADDRESSES } from "../contracts";

// ─────────────────────────────────────────────
// EIP-712 Type Definitions
// ─────────────────────────────────────────────

/** Domain separator cho CarbonDoubleAuction v2 */
function getEIP712Domain(chainId: number) {
  const contractAddress =
    chainId === 80002
      ? CONTRACT_ADDRESSES.polygonAmoy.carbonDoubleAuction
      : CONTRACT_ADDRESSES.sepolia.carbonDoubleAuction;

  return {
    name: "EPU Carbon Double Auction",
    version: "2.0",
    chainId: BigInt(chainId),
    verifyingContract: contractAddress,
  } as const;
}

/** EIP-712 Order struct (khớp với Spec Đức §3.2) */
const ORDER_TYPES = {
  Order: [
    { name: "orderId", type: "bytes32" },
    { name: "trader", type: "address" },
    { name: "orderType", type: "uint8" },      // 0 = BID, 1 = ASK
    { name: "tokenId", type: "uint256" },
    { name: "amount", type: "uint128" },        // Đơn vị: tCO2e (số nguyên)
    { name: "pricePerUnit", type: "uint128" },  // Đơn vị: micro-USDC (10^6 = 1 USD)
    { name: "nonce", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
} as const;

// ─────────────────────────────────────────────
// Order Types & Interfaces
// ─────────────────────────────────────────────

export enum OrderType {
  BID = 0,   // Lệnh Mua
  ASK = 1,   // Lệnh Bán
}

export interface OrderParams {
  orderType: OrderType;
  tokenId: bigint;
  amount: bigint;         // tCO2e (số nguyên)
  pricePerUnit: bigint;   // micro-USDC (1 USD = 1_000_000)
  /** Thời hạn hiệu lực lệnh (Unix timestamp, giây). Mặc định: +24h */
  deadline?: bigint;
}

export interface SignedOrder {
  orderId: `0x${string}`;
  trader: `0x${string}`;
  orderType: number;
  tokenId: string;
  amount: string;
  pricePerUnit: string;
  nonce: string;
  deadline: string;
  signature: `0x${string}`;
  chainId: number;
}

export interface UseEIP712OrderReturn {
  /** Ký lệnh EIP-712 và trả về SignedOrder */
  signOrder: (params: OrderParams) => Promise<SignedOrder | null>;
  /** Đang chờ user ký trên MetaMask? */
  isSigning: boolean;
  /** Lỗi khi ký */
  error: Error | null;
  /** Lệnh đã ký gần nhất */
  lastSignedOrder: SignedOrder | null;
}

// ─────────────────────────────────────────────
// Hook Implementation
// ─────────────────────────────────────────────

export function useEIP712Order(): UseEIP712OrderReturn {
  const { address } = useAccount();
  const chainId = useChainId();
  const { signTypedDataAsync } = useSignTypedData();

  const [isSigning, setIsSigning] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastSignedOrder, setLastSignedOrder] = useState<SignedOrder | null>(null);

  // Nonce counter local (trong production sẽ lấy từ contract)
  const [nonceCounter, setNonceCounter] = useState(0);

  const signOrder = useCallback(
    async (params: OrderParams): Promise<SignedOrder | null> => {
      if (!address) {
        setError(new Error("Chưa kết nối ví MetaMask"));
        return null;
      }

      setIsSigning(true);
      setError(null);

      try {
        const nonce = BigInt(nonceCounter);
        const deadline =
          params.deadline ?? BigInt(Math.floor(Date.now() / 1000) + 86400); // +24h
        const timestamp = BigInt(Math.floor(Date.now() / 1000));

        // Sinh orderId tất định: keccak256(trader, nonce, timestamp)
        const orderId = keccak256(
          encodePacked(
            ["address", "uint256", "uint256"],
            [address, nonce, timestamp]
          )
        );

        // Chuẩn bị message EIP-712
        const orderMessage = {
          orderId,
          trader: address,
          orderType: params.orderType,
          tokenId: params.tokenId,
          amount: params.amount,
          pricePerUnit: params.pricePerUnit,
          nonce,
          deadline,
        };

        // Gọi MetaMask ký EIP-712 Typed Data (Gasless - không tốn gas!)
        const signature = await signTypedDataAsync({
          domain: getEIP712Domain(chainId),
          types: ORDER_TYPES,
          primaryType: "Order",
          message: orderMessage,
        });

        // Tăng nonce cho lệnh tiếp theo
        setNonceCounter((prev) => prev + 1);

        const signedOrder: SignedOrder = {
          orderId,
          trader: address,
          orderType: params.orderType,
          tokenId: params.tokenId.toString(),
          amount: params.amount.toString(),
          pricePerUnit: params.pricePerUnit.toString(),
          nonce: nonce.toString(),
          deadline: deadline.toString(),
          signature,
          chainId,
        };

        setLastSignedOrder(signedOrder);
        return signedOrder;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        return null;
      } finally {
        setIsSigning(false);
      }
    },
    [address, chainId, nonceCounter, signTypedDataAsync]
  );

  return {
    signOrder,
    isSigning,
    error,
    lastSignedOrder,
  };
}

// ─────────────────────────────────────────────
// Utility: Chuyển đổi giá hiển thị ↔ on-chain
// ─────────────────────────────────────────────

/** Chuyển giá USD hiển thị (VD: 14.50) sang micro-USDC on-chain (VD: 14500000n) */
export function usdToMicroUsdc(usdPrice: number): bigint {
  return BigInt(Math.round(usdPrice * 1_000_000));
}

/** Chuyển micro-USDC on-chain (VD: 14500000n) sang giá USD hiển thị (VD: 14.50) */
export function microUsdcToUsd(microUsdc: bigint): number {
  return Number(microUsdc) / 1_000_000;
}
