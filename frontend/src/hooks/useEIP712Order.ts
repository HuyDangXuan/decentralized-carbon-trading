"use client";
import { useCallback, useRef, useState } from "react";
import { useAccount, usePublicClient, useSignTypedData, useWalletClient } from "wagmi";
import { keccak256, stringToHex } from "viem";
import { AUCTION_ABI_READY, AUCTION_NONCE_FUNCTION, CARBON_DOUBLE_AUCTION_ABI, requireContractAddress } from "../contracts";
import { buildOrderMessage, getEIP712Domain, ORDER_TYPES, ORDER_TYPE_STRING, type OrderParams, type SignedOrder } from "../lib/orders";
export { OrderType, TimeInForce, usdToMicroUsdc, microUsdcToUsd } from "../lib/orders";
export type { OrderParams, SignedOrder } from "../lib/orders";
export interface UseEIP712OrderReturn {
  signOrder: (params: OrderParams) => Promise<SignedOrder | null>;
  isSigning: boolean;
  error: Error | null;
  lastSignedOrder: SignedOrder | null;
}
export function useEIP712Order(): UseEIP712OrderReturn {
  const { address, chainId } = useAccount();
  const publicClient = usePublicClient({ chainId });
  const { data: walletClient } = useWalletClient({ chainId });
  const { signTypedDataAsync } = useSignTypedData();
  const [isSigning, setIsSigning] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastSignedOrder, setLastSignedOrder] = useState<SignedOrder | null>(null);
  const busy = useRef(false);
  const wallet = useRef({ address, chainId });
  wallet.current = { address, chainId };
  const signOrder = useCallback(async (params: OrderParams): Promise<SignedOrder | null> => {
    if (busy.current) return null;
    busy.current = true;
    setIsSigning(true);
    setError(null);
    setLastSignedOrder(null);
    try {
      if (!address || !chainId || !publicClient || !walletClient) throw new Error("Kết nối ví trên Polygon Amoy hoặc Sepolia trước khi ký.");
      const verifyingContract = requireContractAddress(chainId, "carbonDoubleAuction");
      if (!AUCTION_ABI_READY) throw new Error("Đang chờ ABI đấu giá v2 được xuất từ hợp đồng đã kiểm thử.");
      const domain = getEIP712Domain(chainId, verifyingContract);
      const code = await publicClient.getBytecode({ address: verifyingContract });
      if (!code || code === "0x") throw new Error("Địa chỉ cấu hình không chứa hợp đồng trên mạng này.");
      const typeHash = await publicClient.readContract({ address: verifyingContract, abi: CARBON_DOUBLE_AUCTION_ABI, functionName: "ORDER_TYPEHASH" });
      if (typeHash !== keccak256(stringToHex(ORDER_TYPE_STRING))) throw new Error("Cấu trúc EIP-712 của hợp đồng chưa khớp SRS hiện tại.");
      const nonce = await publicClient.readContract({ address: verifyingContract, abi: CARBON_DOUBLE_AUCTION_ABI, functionName: AUCTION_NONCE_FUNCTION, args: [address] });
      if (typeof nonce !== "bigint") throw new Error("Không đọc được nonce hiện tại từ hợp đồng.");
      const message = buildOrderMessage(address, params, nonce);
      const stillSameWallet = () => wallet.current.address === address && wallet.current.chainId === chainId;
      if (!stillSameWallet() || await walletClient.getChainId() !== chainId) throw new Error("Ví hoặc mạng đã đổi; hãy tạo lại lệnh.");
      const signature = await signTypedDataAsync({ account: address, domain, types: ORDER_TYPES, primaryType: "Order", message });
      if (!stillSameWallet()) throw new Error("Ví hoặc mạng đã đổi trong lúc ký; lệnh chưa được gửi.");
      if (message.deadline <= BigInt(Math.floor(Date.now() / 1000))) throw new Error("Lệnh đã hết hạn trong lúc chờ ký; hãy tạo lệnh mới.");
      const signed: SignedOrder = {
        orderId: message.orderId, trader: address, orderType: message.orderType, timeInForce: message.timeInForce,
        tokenId: message.tokenId.toString(), amount: message.amount.toString(), pricePerUnit: message.pricePerUnit.toString(),
        nonce: message.nonce.toString(), deadline: message.deadline.toString(), signature, chainId, verifyingContract,
      };
      setLastSignedOrder(signed);
      return signed;
    } catch (cause) {
      setError(cause instanceof Error ? cause : new Error(String(cause)));
      return null;
    } finally { busy.current = false; setIsSigning(false); }
  }, [address, chainId, publicClient, walletClient, signTypedDataAsync]);
  return { signOrder, isSigning, error, lastSignedOrder };
}
