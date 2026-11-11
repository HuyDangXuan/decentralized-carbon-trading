/**
 * components/ConnectWalletButton.tsx
 * Nút kết nối / ngắt kết nối ví MetaMask.
 * Hiển thị trạng thái: chưa kết nối → đang kết nối → đã kết nối (địa chỉ + chain + balance).
 */

"use client";

import React, { useState } from "react";
import { useWalletConnection } from "../hooks/useWalletConnection";

export function ConnectWalletButton() {
  const {
    isConnected,
    isConnecting,
    isDisconnecting,
    address,
    shortAddress,
    chainName,
    isCorrectChain,
    nativeBalance,
    nativeSymbol,
    error,
    connect,
    disconnect,
    switchToDefaultChain,
  } = useWalletConnection();

  const [showDetails, setShowDetails] = useState(false);

  // ── Chưa kết nối ──
  if (!isConnected) {
    return (
      <div className="flex flex-col items-end gap-2">
        <button
          onClick={connect}
          disabled={isConnecting}
          className="
            flex items-center gap-2 px-5 py-2.5 rounded-xl
            bg-carbon-600 hover:bg-carbon-700 active:bg-carbon-800
            text-white font-semibold text-sm
            transition-all duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            shadow-lg shadow-carbon-600/25
          "
        >
          {/* MetaMask Fox Icon (SVG inline) */}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21.3 2L13.1 8.2L14.6 4.5L21.3 2Z" fill="#E2761B" stroke="#E2761B" strokeWidth="0.2"/>
            <path d="M2.7 2L10.8 8.3L9.4 4.5L2.7 2Z" fill="#E4761B" stroke="#E4761B" strokeWidth="0.2"/>
            <path d="M18.5 16.8L16.3 20.2L20.8 21.5L22.2 16.9L18.5 16.8Z" fill="#E4761B" stroke="#E4761B" strokeWidth="0.2"/>
            <path d="M1.8 16.9L3.2 21.5L7.7 20.2L5.5 16.8L1.8 16.9Z" fill="#E4761B" stroke="#E4761B" strokeWidth="0.2"/>
          </svg>

          {isConnecting ? "Đang kết nối..." : "Kết nối MetaMask"}
        </button>

        {error && (
          <p className="text-xs text-red-500 max-w-[280px] text-right">
            ⚠️ {error.message.length > 100 ? error.message.slice(0, 100) + "..." : error.message}
          </p>
        )}
      </div>
    );
  }

  // ── Đã kết nối ──
  return (
    <div className="relative">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="
          flex items-center gap-3 px-4 py-2 rounded-xl
          bg-gray-800 hover:bg-gray-700
          border border-gray-600
          text-white text-sm
          transition-all duration-200
        "
      >
        {/* Status indicator */}
        <span className={`w-2.5 h-2.5 rounded-full ${isCorrectChain ? "bg-green-400 animate-pulse" : "bg-yellow-400"}`} />

        <div className="flex flex-col items-start">
          <span className="font-mono font-semibold">{shortAddress}</span>
          <span className="text-[10px] text-gray-400">
            {nativeBalance} {nativeSymbol} · {chainName}
          </span>
        </div>

        {/* Chevron */}
        <svg className={`w-4 h-4 text-gray-400 transition-transform ${showDetails ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* ── Dropdown chi tiết ── */}
      {showDetails && (
        <div className="
          absolute right-0 top-full mt-2 w-72
          bg-gray-800 border border-gray-600 rounded-xl
          shadow-xl z-50 p-4
          flex flex-col gap-3
        ">
          {/* Địa chỉ đầy đủ */}
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Địa chỉ ví</p>
            <p className="font-mono text-xs text-white break-all">{address}</p>
          </div>

          {/* Mạng */}
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Mạng blockchain</p>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isCorrectChain ? "bg-green-400" : "bg-yellow-400"}`} />
              <span className="text-sm text-white">{chainName}</span>
            </div>
          </div>

          {/* Cảnh báo sai mạng */}
          {!isCorrectChain && (
            <button
              onClick={switchToDefaultChain}
              className="
                w-full py-2 rounded-lg
                bg-yellow-600/20 border border-yellow-600
                text-yellow-400 text-xs font-semibold
                hover:bg-yellow-600/30 transition-colors
              "
            >
              ⚠️ Chuyển sang Polygon Amoy Testnet
            </button>
          )}

          {/* Số dư */}
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Số dư</p>
            <p className="text-lg font-bold text-white">
              {nativeBalance} <span className="text-sm text-gray-400">{nativeSymbol}</span>
            </p>
          </div>

          {/* Nút ngắt kết nối */}
          <button
            onClick={() => {
              disconnect();
              setShowDetails(false);
            }}
            disabled={isDisconnecting}
            className="
              w-full py-2 rounded-lg
              bg-red-600/20 border border-red-600/50
              text-red-400 text-xs font-semibold
              hover:bg-red-600/30 transition-colors
              disabled:opacity-50
            "
          >
            {isDisconnecting ? "Đang ngắt..." : "🔌 Ngắt kết nối"}
          </button>
        </div>
      )}
    </div>
  );
}
