/**
 * hooks/useWalletConnection.ts
 * Custom hook quản lý toàn bộ vòng đời kết nối ví MetaMask:
 *   - Connect / Disconnect
 *   - Theo dõi trạng thái (connected, connecting, error)
 *   - Chuyển mạng (Switch Chain)
 *   - Lấy thông tin địa chỉ, balance, chainId
 *
 * Sử dụng Wagmi v2 hooks (wrapper trên Viem).
 */

"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import {
  ProviderNotFoundError,
  useAccount,
  useBalance,
  useConfig,
  useConnect,
  useDisconnect,
  useSwitchChain,
} from "wagmi";
import { ResourceUnavailableRpcError, UserRejectedRequestError } from "viem";
import { DEFAULT_CHAIN, CHAIN_DISPLAY_NAMES } from "../web3/config";

/** Trạng thái kết nối ví trả về cho UI */
export interface WalletState {
  /** Đã kết nối thành công? */
  isConnected: boolean;
  /** Đang trong quá trình kết nối? */
  isConnecting: boolean;
  /** Đang ngắt kết nối? */
  isDisconnecting: boolean;
  /** Địa chỉ ví hiện tại (checksummed) */
  address: `0x${string}` | undefined;
  /** Địa chỉ rút gọn hiển thị: 0x71C7...976F */
  shortAddress: string;
  /** Chain ID hiện tại */
  chainId: number | undefined;
  /** Tên chain hiển thị tiếng Việt */
  chainName: string;
  /** Có đang ở đúng mạng hỗ trợ? */
  isCorrectChain: boolean;
  /** Số dư native token (MATIC/ETH) */
  nativeBalance: string;
  /** Symbol native token */
  nativeSymbol: string;
  /** Lỗi kết nối (nếu có) */
  error: Error | null;
}

/** Các action điều khiển ví */
export interface WalletActions {
  /** Kết nối MetaMask */
  connect: () => void;
  /** Ngắt kết nối */
  disconnect: () => void;
  /** Chuyển sang chain được chỉ định */
  switchChain: (chainId: number) => void;
  /** Chuyển về chain mặc định (Polygon Amoy) */
  switchToDefaultChain: () => void;
}

export function useWalletConnection(): WalletState & WalletActions {
  // --- Wagmi hooks ---
  const { address, isConnected, isConnecting, chain } = useAccount();
  const config = useConfig();
  const { data: balanceData } = useBalance({ address });
  const { connectAsync } = useConnect();
  const { disconnect: wagmiDisconnect, isPending: isDisconnecting } = useDisconnect();
  const { switchChain: wagmiSwitchChain } = useSwitchChain();
  const [isConnectingWallet, setIsConnectingWallet] = useState(false);
  const [connectError, setConnectError] = useState<Error | null>(null);
  const connectionInProgress = useRef(false);

  // --- Derived state ---
  const shortAddress = useMemo(() => {
    if (!address) return "";
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }, [address]);

  const chainName = useMemo(() => {
    if (!chain) return "Chưa kết nối";
    return CHAIN_DISPLAY_NAMES[chain.id] ?? chain.name ?? `Chain #${chain.id}`;
  }, [chain]);

  const isCorrectChain = useMemo(() => {
    if (!chain) return false;
    // Polygon Amoy (80002) hoặc Sepolia (11155111)
    return chain.id === 80002 || chain.id === 11155111;
  }, [chain]);

  const nativeBalance = useMemo(() => {
    if (!balanceData) return "0";
    // Hiển thị tối đa 4 chữ số thập phân
    const formatted = Number(balanceData.formatted).toFixed(4);
    return formatted;
  }, [balanceData]);

  const nativeSymbol = balanceData?.symbol ?? "ETH";

  // --- Actions ---
  const connect = useCallback(async () => {
    if (connectionInProgress.current) return;
    connectionInProgress.current = true;
    setIsConnectingWallet(true);
    setConnectError(null);
    try {
      // Prefer EIP-6963 discovery when another wallet owns window.ethereum.
      for (const id of ["io.metamask", "metaMask"]) {
        const connector = config.connectors.find((candidate) => candidate.id === id);
        if (!connector || !(await connector.getProvider())) continue;
        await connectAsync({ connector });
        return;
      }
      throw new ProviderNotFoundError();
    } catch (error) {
      const code = typeof error === "object" && error !== null && "code" in error ? error.code : undefined;
      if (error instanceof ProviderNotFoundError) {
        setConnectError(error);
      } else if (code === UserRejectedRequestError.code) {
        setConnectError(new Error("Bạn đã hủy yêu cầu kết nối. Bấm nút kết nối để thử lại."));
      } else if (code === ResourceUnavailableRpcError.code) {
        setConnectError(new Error("Mở tiện ích MetaMask để xử lý yêu cầu kết nối đang chờ."));
      } else {
        setConnectError(new Error("Kết nối thất bại. Mở khóa MetaMask rồi thử lại."));
      }
    } finally {
      connectionInProgress.current = false;
      setIsConnectingWallet(false);
    }
  }, [config, connectAsync]);

  const disconnect = useCallback(() => {
    wagmiDisconnect();
  }, [wagmiDisconnect]);

  const switchChain = useCallback(
    (targetChainId: number) => {
      wagmiSwitchChain({ chainId: targetChainId });
    },
    [wagmiSwitchChain]
  );

  const switchToDefaultChain = useCallback(() => {
    wagmiSwitchChain({ chainId: DEFAULT_CHAIN.id });
  }, [wagmiSwitchChain]);

  return {
    // State
    isConnected,
    isConnecting: isConnecting || isConnectingWallet,
    isDisconnecting,
    address,
    shortAddress,
    chainId: chain?.id,
    chainName,
    isCorrectChain,
    nativeBalance,
    nativeSymbol,
    error: connectError,

    // Actions
    connect,
    disconnect,
    switchChain,
    switchToDefaultChain,
  };
}
