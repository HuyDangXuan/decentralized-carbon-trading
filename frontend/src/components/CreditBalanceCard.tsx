/**
 * components/CreditBalanceCard.tsx
 * Card hiển thị số dư tín chỉ carbon (ERC-1155) của ví đang kết nối.
 * Fetch metadata URI từ hàm uri(tokenId) và hiển thị thông tin dự án.
 */

"use client";

import React from "react";
import { useAccount } from "wagmi";
import { getContractAddresses } from "../contracts";
import {
  useCreditBalance,
  useCreditURI,
  useCreditTotalSupply,
  useCreditTotalRetired,
} from "../hooks/useCarbonCredit";

interface CreditBalanceCardProps {
  tokenId: bigint;
}

export function CreditBalanceCard({ tokenId }: CreditBalanceCardProps) {
  const { address, chain } = useAccount();

  const { data: balance, isLoading: loadingBalance, error: balanceError } = useCreditBalance(address, tokenId, chain?.id);
  const { data: metadataURI } = useCreditURI(tokenId, chain?.id);
  const { data: totalSupply } = useCreditTotalSupply(tokenId, chain?.id);
  const { data: totalRetired } = useCreditTotalRetired(tokenId, chain?.id);

  const activeSupply =
    totalSupply !== undefined && totalRetired !== undefined
      ? totalSupply - totalRetired
      : undefined;

  if (!getContractAddresses(chain?.id)?.carbonCredit1155) {
    return <p role="status" className="text-sm text-gray-400">Chưa cấu hình hợp đồng tín chỉ trên mạng này.</p>;
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-2xl p-5 max-w-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Tín chỉ Carbon</h3>
        <span className="text-[10px] bg-carbon-600/20 text-carbon-400 px-2 py-0.5 rounded-full border border-carbon-600/30">
          Token #{tokenId.toString()}
        </span>
      </div>

      {/* Số dư */}
      <div className="mb-4">
        <p className="text-3xl font-bold text-white">
          {balanceError ? <span className="text-sm text-red-300">Không đọc được số dư</span> : loadingBalance ? (
            <span className="animate-pulse text-gray-500">---</span>
          ) : (
            balance !== undefined ? balance.toString() : "—"
          )}
        </p>
        <p className="text-xs text-gray-500 mt-1">tCO2e sở hữu</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-700/50 rounded-lg p-3">
          <p className="text-[10px] text-gray-400 uppercase mb-0.5">Tổng phát hành</p>
          <p className="text-sm font-semibold text-white">
            {totalSupply !== undefined ? totalSupply.toString() : "—"}
          </p>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-3">
          <p className="text-[10px] text-gray-400 uppercase mb-0.5">Đã tiêu hủy</p>
          <p className="text-sm font-semibold text-red-400">
            {totalRetired !== undefined ? totalRetired.toString() : "—"}
          </p>
        </div>
      </div>

      {/* Active supply bar */}
      {totalSupply !== undefined && totalRetired !== undefined && totalSupply > 0n && (
        <div className="mb-3">
          <div className="flex justify-between text-[10px] text-gray-400 mb-1">
            <span>Còn lưu hành</span>
            <span>{activeSupply?.toString()} tCO2e</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-carbon-500 h-2 rounded-full transition-all duration-500"
              style={{
                width: `${Number((activeSupply! * 100n) / totalSupply)}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Metadata URI */}
      {metadataURI && (
        <div className="bg-gray-900/50 rounded-lg p-2.5 mt-2">
          <p className="text-[10px] text-gray-400 mb-1">📦 IPFS Metadata URI</p>
          <p className="text-[11px] font-mono text-carbon-400 break-all">
            {metadataURI}
          </p>
        </div>
      )}
    </div>
  );
}
