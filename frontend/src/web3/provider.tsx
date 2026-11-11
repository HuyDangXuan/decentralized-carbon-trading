/**
 * web3/provider.tsx
 * Web3Provider bọc toàn bộ ứng dụng Next.js,
 * cung cấp Wagmi context + React Query cho tất cả hooks bên trong.
 */

"use client";

import React from "react";
import { WagmiProvider } from "wagmi";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { wagmiConfig } from "./config";

/** React Query client – cache dehydrate/hydrate cho SSR nếu cần */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      /** Không tự refetch khi user quay lại tab – giảm RPC call */
      refetchOnWindowFocus: false,
      /** Retry 2 lần nếu gặp lỗi mạng */
      retry: 2,
    },
  },
});

interface Web3ProviderProps {
  children: React.ReactNode;
}

/**
 * Wrap component gốc trong `layout.tsx`:
 * ```tsx
 * <Web3Provider>{children}</Web3Provider>
 * ```
 */
export function Web3Provider({ children }: Web3ProviderProps) {
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </WagmiProvider>
  );
}
