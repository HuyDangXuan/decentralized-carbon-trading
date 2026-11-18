"use client";

import { useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { BaseError, UserRejectedRequestError, type Hash } from "viem";
import { useAccount, useConfig, usePublicClient, useReadContract, useWriteContract } from "wagmi";
import { getAccount } from "wagmi/actions";
import { polygonAmoy } from "wagmi/chains";
import { CARBON_CREDIT_1155_ABI, getContractAddresses } from "../contracts";
import {
  AMOY_PROJECT_EVCC_FAUCET, EVCC_FAUCET_AMOUNT, EVCC_FAUCET_LOT,
  amoyFaucetFees, evccFaucetAbi, mockUsdcMintAbi, MOCK_USDC_FAUCET_AMOUNT,
} from "../contracts/faucet";

type Asset = "mockUsdc" | "evcc";
type Operation = {
  scope: string;
  message: string;
  status: "wallet" | "pending" | "success" | "error" | "unconfirmed";
  hash?: Hash;
};

export function FaucetModal() {
  const dialog = useRef<HTMLDialogElement>(null);
  const inProgress = useRef(false);
  const [isOpen, setIsOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [operation, setOperation] = useState<Operation>();
  const { address, chainId, isConnected } = useAccount();
  const config = useConfig();
  const queryClient = useQueryClient();
  const publicClient = usePublicClient({ chainId: polygonAmoy.id });
  const { writeContractAsync } = useWriteContract();
  const onAmoy = isConnected && chainId === polygonAmoy.id;
  const contracts = getContractAddresses(chainId);
  const faucetAddress = contracts?.evccFaucet;
  const creditAddress = contracts?.carbonCredit1155;
  const isProjectFaucet = faucetAddress?.toLowerCase() === AMOY_PROJECT_EVCC_FAUCET.toLowerCase();
  const scope = `${address ?? ""}:${chainId ?? ""}`;
  const visibleOperation = operation?.scope === scope ? operation : undefined;
  const statusEnabled = Boolean(isOpen && onAmoy && address && faucetAddress && creditAddress);
  const faucetCredit = useReadContract({
    chainId: polygonAmoy.id,
    address: faucetAddress,
    abi: evccFaucetAbi,
    functionName: isProjectFaucet ? "carbonCredit" : "credit",
    query: { enabled: statusEnabled },
  });
  const claimStatus = useReadContract({
    chainId: polygonAmoy.id,
    address: faucetAddress,
    abi: evccFaucetAbi,
    functionName: "claimStatus",
    args: address ? [address] : undefined,
    query: { enabled: statusEnabled && !isProjectFaucet },
  });
  const inventory = useReadContract({
    chainId: polygonAmoy.id,
    address: creditAddress,
    abi: CARBON_CREDIT_1155_ABI,
    functionName: "balanceOf",
    args: faucetAddress ? [faucetAddress, EVCC_FAUCET_LOT] : undefined,
    query: { enabled: statusEnabled && isProjectFaucet },
  });
  const activeStatus = isProjectFaucet ? inventory : claimStatus;
  const claimed = !isProjectFaucet && claimStatus.data?.[0] === true;
  const funded = isProjectFaucet
    ? (inventory.data ?? 0n) >= EVCC_FAUCET_AMOUNT
    : claimStatus.data?.[1] === true;
  const creditMatches = Boolean(
    faucetCredit.data && faucetCredit.data.toLowerCase() === creditAddress?.toLowerCase(),
  );
  const statusError = activeStatus.isError || faucetCredit.isError;
  const evccReady = Boolean(statusEnabled && creditMatches && funded && !claimed && !statusError);

  function open() {
    dialog.current?.showModal();
    setIsOpen(true);
  }

  function refreshBalances(asset: Asset) {
    const targets = asset === "mockUsdc" ? [contracts?.mockUsdc] : [contracts?.carbonCredit1155, faucetAddress];
    void queryClient.invalidateQueries({
      queryKey: ["readContract"],
      predicate: ({ queryKey }) => {
        const request = queryKey[1] as { address?: string; chainId?: number } | undefined;
        return request?.chainId === polygonAmoy.id && targets.some(
          target => target && target.toLowerCase() === request.address?.toLowerCase(),
        );
      },
    });
  }

  async function claim(asset: Asset) {
    if (inProgress.current || !onAmoy || !address || !publicClient) return;
    const destination = asset === "mockUsdc" ? contracts?.mockUsdc : faucetAddress;
    if (!destination || (asset === "evcc" && !evccReady)) return;

    inProgress.current = true;
    setBusy(true);
    let hash: Hash | undefined;
    let knownFailure = false;
    let replacedByDifferentTransaction = false;
    try {
      setOperation({ scope, status: "wallet", message: "Đang kiểm tra giao dịch thử nghiệm…" });
      const code = await publicClient.getBytecode({ address: destination });
      if (!code || code === "0x") throw new Error("Không tìm thấy hợp đồng nhận token trên Amoy.");
      const params = { address: destination, account: address };
      const mint = { ...params, abi: mockUsdcMintAbi, functionName: "mint", args: [address, MOCK_USDC_FAUCET_AMOUNT] } as const;
      const distribute = { ...params, abi: evccFaucetAbi, functionName: "claim" } as const;
      if (asset === "mockUsdc") await publicClient.simulateContract(mint);
      else await publicClient.simulateContract(distribute);
      const fees = amoyFaucetFees(await publicClient.estimateFeesPerGas());

      const wallet = getAccount(config);
      if (wallet.address !== address || wallet.chainId !== polygonAmoy.id) {
        throw new Error("Ví hoặc mạng đã thay đổi. Hãy kiểm tra rồi thử lại.");
      }
      setOperation({ scope, status: "wallet", message: "Hãy xác nhận giao dịch trong MetaMask." });
      hash = asset === "mockUsdc"
        ? await writeContractAsync({ ...mint, ...fees, chainId: polygonAmoy.id })
        : await writeContractAsync({ ...distribute, ...fees, chainId: polygonAmoy.id });
      setOperation({ scope, status: "pending", message: "Đang chờ xác nhận trên Polygon Amoy…", hash });
      const receipt = await publicClient.waitForTransactionReceipt({
        hash,
        onReplaced: ({ reason, transaction }) => {
          replacedByDifferentTransaction = reason !== "repriced";
          if (!replacedByDifferentTransaction) {
            hash = transaction.hash;
            setOperation({ scope, status: "pending", message: "Đang chờ xác nhận trên Polygon Amoy…", hash });
          }
        },
      });
      if (replacedByDifferentTransaction || receipt.status !== "success") {
        knownFailure = true;
        throw new Error(replacedByDifferentTransaction ? "Giao dịch nhận token đã bị thay thế hoặc hủy." : "Blockchain đã từ chối giao dịch.");
      }
      refreshBalances(asset);
      const amount = asset === "mockUsdc" ? "10.000 MockUSDC" : "100 EVCC của lô #101";
      setOperation({ scope, status: "success", message: `Đã nhận ${amount}.`, hash: receipt.transactionHash });
    } catch (cause) {
      const rejected = cause instanceof BaseError && Boolean(cause.walk(error => error instanceof UserRejectedRequestError));
      const unconfirmed = Boolean(hash) && !knownFailure && !replacedByDifferentTransaction;
      const message = unconfirmed
        ? "Chưa xác nhận được kết quả. Hãy xem trạng thái giao dịch trên AmoyScan trước khi gửi lại."
        : rejected ? "Bạn đã từ chối giao dịch trong MetaMask."
        : cause instanceof BaseError ? cause.shortMessage
        : cause instanceof Error ? cause.message
        : "Không thể nhận token. Hãy kiểm tra mạng và số dư POL.";
      if (asset === "evcc" && statusEnabled) void activeStatus.refetch();
      setOperation({ scope, status: unconfirmed ? "unconfirmed" : "error", message, hash });
    } finally {
      inProgress.current = false;
      setBusy(false);
    }
  }

  let evccNote = isProjectFaucet ? "Faucet cấp 100 EVCC #101 mỗi lượt khi còn tồn kho." : "Mỗi ví thử nghiệm nhận một lần.";
  if (!faucetAddress) evccNote = "Faucet EVCC chưa được triển khai hoặc cấu hình.";
  else if (!contracts?.carbonCredit1155) evccNote = "Chưa cấu hình hợp đồng EVCC trên Amoy.";
  else if (statusError) evccNote = "Không đọc được trạng thái faucet EVCC.";
  else if (activeStatus.isPending || faucetCredit.isPending) evccNote = "Đang kiểm tra faucet EVCC…";
  else if (!creditMatches) evccNote = "Faucet chưa được nối với hợp đồng EVCC của dự án.";
  else if (claimed) evccNote = "Ví này đã nhận EVCC từ faucet.";
  else if (!funded) evccNote = "Faucet chưa có đủ EVCC #101 để cấp.";

  return (
    <>
      <button type="button" onClick={open} className="rounded-lg border border-carbon-500/50 px-3 py-2 text-sm font-semibold text-carbon-300 hover:bg-carbon-500/10">
        Faucet thử nghiệm
      </button>
      <dialog ref={dialog} onClose={() => setIsOpen(false)} aria-labelledby="faucet-title"
        className="m-auto max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-md rounded-2xl border border-gray-700 bg-gray-900 p-5 text-gray-100 shadow-xl backdrop:bg-black/70">
        <div className="flex items-center justify-between gap-4">
          <h2 id="faucet-title" className="text-lg font-semibold">Nhận token thử nghiệm</h2>
          <form method="dialog">
            <button type="submit" className="rounded px-2 py-1 text-sm text-gray-300 hover:bg-gray-800">Đóng</button>
          </form>
        </div>
        <p className="mb-5 mt-2 text-sm text-gray-300">Polygon Amoy. Ví cần một ít POL thử nghiệm để trả phí mạng.</p>
        {!onAmoy && <p role="status" className="mb-4 text-sm text-amber-300">{isConnected ? "Chuyển sang Polygon Amoy để nhận token." : "Kết nối MetaMask để nhận token."}</p>}
        <div className="space-y-4">
          <div>
            <button type="button" disabled={!onAmoy || !contracts?.mockUsdc || !publicClient || busy}
              onClick={() => void claim("mockUsdc")} className="w-full rounded-lg bg-carbon-600 px-3 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
              Nhận 10.000 MockUSDC
            </button>
            {onAmoy && !contracts?.mockUsdc && <p className="mt-1.5 text-sm text-amber-300">Chưa cấu hình MockUSDC trên Amoy.</p>}
          </div>
          <div>
            <button type="button" disabled={!evccReady || !publicClient || busy}
              onClick={() => void claim("evcc")} className="w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2.5 text-sm font-semibold disabled:opacity-50">
              Nhận 100 EVCC (#101)
            </button>
            {onAmoy && <p className="mt-1.5 text-sm text-gray-300">{evccNote}</p>}
          </div>
        </div>
        {visibleOperation && (
          <div className="mt-4 space-y-1 text-sm">
            <p role={visibleOperation.status === "error" ? "alert" : "status"} className={
              visibleOperation.status === "success" ? "text-green-300" :
              visibleOperation.status === "error" ? "text-red-300" : "text-amber-300"
            }>{visibleOperation.message}</p>
            {visibleOperation.hash && <a className="text-carbon-300 underline" target="_blank" rel="noreferrer"
              href={`${polygonAmoy.blockExplorers.default.url}/tx/${visibleOperation.hash}`}>Xem trên AmoyScan</a>}
          </div>
        )}
      </dialog>
    </>
  );
}
