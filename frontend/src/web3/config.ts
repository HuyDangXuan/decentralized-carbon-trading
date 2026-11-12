/**
 * web3/config.ts
 * Cấu hình Wagmi v2 + Viem cho CarbonChain DApp.
 *
 * - Hỗ trợ 2 testnet: Polygon Amoy & Ethereum Sepolia.
 * - Connector chính: MetaMask (injected).
 * - Transport: HTTP public RPC (đổi sang Alchemy/Infura khi production).
 */

import { createConfig, fallback, http, injected } from "wagmi";
import { polygonAmoy, sepolia } from "wagmi/chains";

const amoyRpcUrl = "https://polygon-amoy.gateway.tenderly.co";
const amoyRpcUrls = [amoyRpcUrl, ...polygonAmoy.rpcUrls.default.http] as const;
const amoy = {
  ...polygonAmoy,
  rpcUrls: { default: { http: amoyRpcUrls } },
};
const configuredAmoyRpc = process.env.NEXT_PUBLIC_AMOY_RPC_URL?.trim();
const amoyTransport = configuredAmoyRpc && configuredAmoyRpc !== amoyRpcUrl
  ? http(configuredAmoyRpc)
  : fallback(amoyRpcUrls.map((url) => http(url, { timeout: 5_000 })));

/**
 * Cấu hình Wagmi chính.
 * `injected()` tự phát hiện MetaMask, Rabby, Coinbase Wallet… trong trình duyệt.
 */
export const wagmiConfig = createConfig({
  ssr: true,
  chains: [amoy, sepolia],
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
    [amoy.id]: amoyTransport,
    [sepolia.id]: http(),
  },
});

/** Chain mặc định khi người dùng kết nối lần đầu */
export const DEFAULT_CHAIN = amoy;

/** Mapping chainId → tên hiển thị tiếng Việt */
export const CHAIN_DISPLAY_NAMES: Record<number, string> = {
  [polygonAmoy.id]: "Polygon Amoy Testnet",
  [sepolia.id]: "Ethereum Sepolia Testnet",
};
