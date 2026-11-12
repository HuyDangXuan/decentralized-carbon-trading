"use client";

import { erc20Abi, formatUnits } from "viem";
import { useAccount, useReadContract } from "wagmi";
import { getContractAddresses } from "../contracts";

export function MockUsdcBalanceCard() {
  const { address, chainId } = useAccount();
  const contractAddress = getContractAddresses(chainId)?.mockUsdc;
  const balance = useReadContract({
    address: contractAddress,
    abi: erc20Abi,
    chainId,
    functionName: "balanceOf",
    args: address ? [address] : undefined,
    query: { enabled: Boolean(address && contractAddress) },
  });

  return (
    <section aria-labelledby="mock-usdc-title" className="bg-gray-800 border border-gray-700 rounded-2xl p-5 min-w-0">
      <h3 id="mock-usdc-title" className="text-sm font-semibold text-gray-300 mb-4">MockUSDC</h3>
      {!contractAddress ? (
        <p role="status" className="text-sm text-gray-400">Chưa cấu hình MockUSDC trên mạng này.</p>
      ) : balance.isError ? (
        <p role="status" className="text-sm text-red-300">Không đọc được số dư MockUSDC.</p>
      ) : balance.isPending ? (
        <p role="status" className="text-sm text-gray-400">Đang đọc số dư MockUSDC…</p>
      ) : (
        <div className="text-3xl font-bold text-white break-all">
          <output aria-label="Số dư MockUSDC">{balance.data === undefined ? "—" : formatUnits(balance.data, 6)}</output>
          <span className="block mt-1 text-xs font-normal text-gray-400">MockUSDC sở hữu</span>
        </div>
      )}
    </section>
  );
}
