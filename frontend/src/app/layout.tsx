/**
 * app/layout.tsx
 * Root layout bọc Web3Provider cho toàn bộ ứng dụng CarbonChain DApp.
 */

import type { Metadata } from "next";
import { Web3Provider } from "@/web3/provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "CarbonChain – Giao dịch Tín chỉ Carbon trên Blockchain",
  description:
    "Hệ thống giao dịch tín chỉ carbon minh bạch, sử dụng ERC-1155, Đấu giá kép và Hệ Đa Tác Tử. Đề tài NCKH ĐH Điện Lực 2026-2027.",
  keywords: [
    "carbon credit",
    "blockchain",
    "ERC-1155",
    "double auction",
    "DApp",
    "Web3",
    "Đại học Điện Lực",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>
        <Web3Provider>{children}</Web3Provider>
      </body>
    </html>
  );
}
