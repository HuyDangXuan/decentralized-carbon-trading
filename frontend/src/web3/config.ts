/**
 * web3/config.ts
 * Cấu hình Wagmi v2 + Viem cho CarbonChain DApp.
 *
 * - Hỗ trợ 2 testnet: Polygon Amoy & Ethereum Sepolia.
 * - Connector chính: MetaMask (injected).
 * - Transport: HTTP public RPC (đổi sang Alchemy/Infura khi production).
 */

import { http, createConfig, injected } from "wagmi";
import { polygonAmoy, sepolia } from "wagmi/chains";

/**
 * Cấu hình Wagmi chính.
 * `injected()` tự phát hiện MetaMask, Rabby, Coinbase Wallet… trong trình duyệt.
 */
export const wagmiConfig = createConfig({
  ssr: true,
  chains: [polygonAmoy, sepolia],
  connectors: [
    injected({
      target: "metaMask",
    }),
  ],
  transports: {
    /**
     * ⚠️  Public RPC có rate-limit.
     * Khi benchmark / demo thực tế, thay bằng:
     *   http("https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY")
     *   http("https://sepolia.infura.io/v3/YOUR_KEY")
     */
    [polygonAmoy.id]: http(),
    [sepolia.id]: http(),
  },
});

/** Chain mặc định khi người dùng kết nối lần đầu */
export const DEFAULT_CHAIN = polygonAmoy;

/** Mapping chainId → tên hiển thị tiếng Việt */
export const CHAIN_DISPLAY_NAMES: Record<number, string> = {
  [polygonAmoy.id]: "Polygon Amoy Testnet",
  [sepolia.id]: "Ethereum Sepolia Testnet",
};
