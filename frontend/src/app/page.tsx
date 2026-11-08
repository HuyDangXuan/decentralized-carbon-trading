/**
 * app/page.tsx
 * Trang chủ CarbonChain DApp.
 * Tích hợp kết nối ví MetaMask, hiển thị thông tin tín chỉ carbon.
 */

"use client";

import React, { useState } from "react";
import { useAccount } from "wagmi";
import { ConnectWalletButton } from "@/components/ConnectWalletButton";
import { NetworkBadge } from "@/components/NetworkBadge";
import { CreditBalanceCard } from "@/components/CreditBalanceCard";

export default function HomePage() {
  const { isConnected } = useAccount();
  const [tokenIdInput, setTokenIdInput] = useState("101");

  return (
    <div className="min-h-screen">
      {/* ── HEADER / NAVBAR ── */}
      <header className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur-md border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <span className="text-2xl">🌱</span>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">
                CarbonChain
              </h1>
              <p className="text-[10px] text-gray-500">
                Giao dịch Tín chỉ Carbon · ĐH Điện Lực
              </p>
            </div>
          </div>

          {/* Network + Wallet */}
          <div className="flex items-center gap-4">
            <NetworkBadge />
            <ConnectWalletButton />
          </div>
        </div>
      </header>

      {/* ── MAIN CONTENT ── */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {!isConnected ? (
          /* ── Landing (chưa kết nối) ── */
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="text-6xl mb-6">🌍</div>
            <h2 className="text-3xl font-bold text-white mb-3">
              Chào mừng đến CarbonChain
            </h2>
            <p className="text-gray-400 max-w-lg mb-8 leading-relaxed">
              Hệ thống giao dịch tín chỉ carbon minh bạch trên Blockchain.
              Kết nối ví MetaMask để bắt đầu xem, mua bán và hủy tín chỉ carbon
              theo cơ chế đấu giá kép phi tập trung.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl">
              <FeatureCard
                icon="🔗"
                title="ERC-1155"
                desc="Token hóa tín chỉ carbon theo lô vintage, chống trùng lặp"
              />
              <FeatureCard
                icon="⚖️"
                title="Đấu giá kép"
                desc="Khớp lệnh tối ưu, giá thị trường cân bằng tự động"
              />
              <FeatureCard
                icon="🌿"
                title="ESG Compliance"
                desc="Tiêu hủy tín chỉ vĩnh viễn, chứng nhận bù đắp bất biến"
              />
            </div>
          </div>
        ) : (
          /* ── Dashboard (đã kết nối) ── */
          <div>
            <h2 className="text-xl font-bold text-white mb-6">
              📊 Bảng điều khiển Tín chỉ Carbon
            </h2>

            {/* Token ID Input */}
            <div className="flex items-center gap-3 mb-6">
              <label className="text-sm text-gray-400">Token ID:</label>
              <input
                type="number"
                value={tokenIdInput}
                onChange={(e) => setTokenIdInput(e.target.value)}
                className="
                  w-32 px-3 py-1.5 rounded-lg
                  bg-gray-800 border border-gray-600
                  text-white text-sm font-mono
                  focus:outline-none focus:border-carbon-500
                "
                placeholder="101"
              />
            </div>

            {/* Credit Balance Card */}
            {tokenIdInput && (
              <CreditBalanceCard tokenId={BigInt(tokenIdInput || "0")} />
            )}
          </div>
        )}
      </main>

      {/* ── FOOTER ── */}
      <footer className="border-t border-gray-800 mt-16">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-xs text-gray-600">
          <p>
            CarbonChain · Đề tài NCKH Sinh viên · Trường Đại học Điện Lực
            2026-2027
          </p>
          <p className="mt-1">
            GVHD: TS. Nguyễn Thị Hồng Khánh · Nhóm: Đặng Xuân Huy, Ngô Văn
            Thắng, Nguyễn Hoàng Đức, Nguyễn Bảo Phi
          </p>
        </div>
      </footer>
    </div>
  );
}

/* ── Sub-component: Feature Card ── */
function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: string;
  title: string;
  desc: string;
}) {
  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 text-left">
      <span className="text-2xl">{icon}</span>
      <h3 className="text-sm font-semibold text-white mt-2 mb-1">{title}</h3>
      <p className="text-xs text-gray-400 leading-relaxed">{desc}</p>
    </div>
  );
}
