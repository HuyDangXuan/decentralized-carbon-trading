/**
 * hooks/useCarbonCredit.ts
 * Custom hooks tương tác với CarbonCredit1155.sol thông qua Wagmi/Viem.
 *
 * Cung cấp:
 *   - Đọc: balanceOf, uri (metadata IPFS), totalSupply, totalRetired
 *   - Ghi: mintCarbonCredit, retireCarbonCredit, safeTransferFrom, setApprovalForAll
 *   - Event: lắng nghe TransferSingle, CarbonRetired
 */

"use client";

import {
  useReadContract,
  useWriteContract,
  useWaitForTransactionReceipt,
  useWatchContractEvent,
} from "wagmi";
import { CARBON_CREDIT_1155_ABI, CONTRACT_ADDRESSES } from "../contracts";

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

/** Lấy địa chỉ contract theo chainId hiện tại */
function getContractAddress(chainId?: number): `0x${string}` {
  if (chainId === 80002) return CONTRACT_ADDRESSES.polygonAmoy.carbonCredit1155;
  if (chainId === 11155111) return CONTRACT_ADDRESSES.sepolia.carbonCredit1155;
  // Fallback: Polygon Amoy
  return CONTRACT_ADDRESSES.polygonAmoy.carbonCredit1155;
}

// ─────────────────────────────────────────────
// READ HOOKS
// ─────────────────────────────────────────────

/** Đọc số dư tín chỉ carbon của một tài khoản cho một token ID */
export function useCreditBalance(account?: `0x${string}`, tokenId?: bigint, chainId?: number) {
  return useReadContract({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "balanceOf",
    args: account && tokenId !== undefined ? [account, tokenId] : undefined,
    query: {
      enabled: !!account && tokenId !== undefined,
    },
  });
}

/** Đọc metadata URI (IPFS) cho một token ID – kết quả dùng để fetch JSON theo METADATA_SCHEMA */
export function useCreditURI(tokenId?: bigint, chainId?: number) {
  return useReadContract({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "uri",
    args: tokenId !== undefined ? [tokenId] : undefined,
    query: {
      enabled: tokenId !== undefined,
    },
  });
}

/** Đọc tổng cung tín chỉ đã phát hành cho token ID */
export function useCreditTotalSupply(tokenId?: bigint, chainId?: number) {
  return useReadContract({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "totalSupply",
    args: tokenId !== undefined ? [tokenId] : undefined,
    query: {
      enabled: tokenId !== undefined,
    },
  });
}

/** Đọc tổng tín chỉ đã tiêu hủy (retired) cho token ID */
export function useCreditTotalRetired(tokenId?: bigint, chainId?: number) {
  return useReadContract({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "totalRetired",
    args: tokenId !== undefined ? [tokenId] : undefined,
    query: {
      enabled: tokenId !== undefined,
    },
  });
}

/** Kiểm tra operator approval */
export function useIsApprovedForAll(
  account?: `0x${string}`,
  operator?: `0x${string}`,
  chainId?: number
) {
  return useReadContract({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "isApprovedForAll",
    args: account && operator ? [account, operator] : undefined,
    query: {
      enabled: !!account && !!operator,
    },
  });
}

// ─────────────────────────────────────────────
// WRITE HOOKS
// ─────────────────────────────────────────────

/** Hook ghi: Đúc tín chỉ mới (chỉ admin) */
export function useMintCarbonCredit(chainId?: number) {
  const { writeContract, data: txHash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const mint = (to: `0x${string}`, tokenId: bigint, amount: bigint, ipfsURI: string) => {
    writeContract({
      address: getContractAddress(chainId),
      abi: CARBON_CREDIT_1155_ABI,
      functionName: "mintCarbonCredit",
      args: [to, tokenId, amount, ipfsURI],
    });
  };

  return { mint, txHash, isPending, isConfirming, isSuccess, error };
}

/** Hook ghi: Tiêu hủy tín chỉ để bù đắp phát thải */
export function useRetireCarbonCredit(chainId?: number) {
  const { writeContract, data: txHash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const retire = (tokenId: bigint, amount: bigint, reason: string) => {
    writeContract({
      address: getContractAddress(chainId),
      abi: CARBON_CREDIT_1155_ABI,
      functionName: "retireCarbonCredit",
      args: [tokenId, amount, reason],
    });
  };

  return { retire, txHash, isPending, isConfirming, isSuccess, error };
}

/** Hook ghi: Chuyển tín chỉ giữa các ví */
export function useTransferCredit(chainId?: number) {
  const { writeContract, data: txHash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const transfer = (
    from: `0x${string}`,
    to: `0x${string}`,
    tokenId: bigint,
    amount: bigint
  ) => {
    writeContract({
      address: getContractAddress(chainId),
      abi: CARBON_CREDIT_1155_ABI,
      functionName: "safeTransferFrom",
      args: [from, to, tokenId, amount, "0x"],
    });
  };

  return { transfer, txHash, isPending, isConfirming, isSuccess, error };
}

/** Hook ghi: Cấp quyền cho sàn đấu giá (CarbonDoubleAuction) thay mặt chuyển token */
export function useSetApprovalForAll(chainId?: number) {
  const { writeContract, data: txHash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const approve = (operator: `0x${string}`, approved: boolean) => {
    writeContract({
      address: getContractAddress(chainId),
      abi: CARBON_CREDIT_1155_ABI,
      functionName: "setApprovalForAll",
      args: [operator, approved],
    });
  };

  return { approve, txHash, isPending, isConfirming, isSuccess, error };
}

// ─────────────────────────────────────────────
// EVENT HOOKS
// ─────────────────────────────────────────────

/** Lắng nghe event CarbonRetired real-time (dùng cho dashboard ESG) */
export function useWatchCarbonRetiredEvents(
  onRetired: (log: {
    burner: `0x${string}`;
    id: bigint;
    amount: bigint;
    reason: string;
  }) => void,
  chainId?: number
) {
  useWatchContractEvent({
    address: getContractAddress(chainId),
    abi: CARBON_CREDIT_1155_ABI,
    eventName: "CarbonRetired",
    onLogs: (logs) => {
      for (const log of logs) {
        if (log.args.burner && log.args.id !== undefined && log.args.amount !== undefined) {
          onRetired({
            burner: log.args.burner,
            id: log.args.id,
            amount: log.args.amount,
            reason: log.args.reason ?? "",
          });
        }
      }
    },
  });
}
