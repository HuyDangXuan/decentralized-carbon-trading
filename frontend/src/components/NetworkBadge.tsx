/**
 * components/NetworkBadge.tsx
 * Badge hiển thị mạng blockchain hiện tại với nút chuyển mạng nhanh.
 */

"use client";

import React from "react";
import { useWalletConnection } from "../hooks/useWalletConnection";

const CHAIN_COLORS: Record<number, string> = {
  80002: "bg-purple-600/20 text-purple-300 border-purple-500/30",    // Polygon Amoy
  11155111: "bg-blue-600/20 text-blue-300 border-blue-500/30",       // Sepolia
};

const CHAIN_ICONS: Record<number, string> = {
  80002: "🟣",     // Polygon
  11155111: "🔵",   // Ethereum
};

export function NetworkBadge() {
  const { isConnected, chainId, chainName, isCorrectChain, switchChain } = useWalletConnection();

  if (!isConnected || !chainId) return null;

  const colorClass = CHAIN_COLORS[chainId] ?? "bg-gray-600/20 text-gray-300 border-gray-500/30";
  const icon = CHAIN_ICONS[chainId] ?? "⚪";

  return (
    <div className="flex items-center gap-2">
      <span className={`
        inline-flex items-center gap-1.5 px-3 py-1 rounded-full
        text-xs font-medium border ${colorClass}
      `}>
        <span>{icon}</span>
        {chainName}
        {!isCorrectChain && " ⚠️"}
      </span>

      {/* Nút chuyển mạng nhanh */}
      {isCorrectChain && (
        <button
          onClick={() => switchChain(chainId === 80002 ? 11155111 : 80002)}
          className="text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
          title="Chuyển mạng"
        >
          🔄
        </button>
      )}
    </div>
  );
}
