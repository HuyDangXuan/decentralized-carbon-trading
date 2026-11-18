import { parseAbi, parseGwei, parseUnits } from "viem";

export const MOCK_USDC_FAUCET_AMOUNT = parseUnits("10000", 6);
export const AMOY_PROJECT_EVCC_FAUCET = "0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED";
export const EVCC_FAUCET_LOT = 101n;
export const EVCC_FAUCET_AMOUNT = 100n;
const AMOY_MIN_PRIORITY_FEE = parseGwei("25");

export function amoyFaucetFees({ maxFeePerGas, maxPriorityFeePerGas }: {
  maxFeePerGas: bigint;
  maxPriorityFeePerGas: bigint;
}) {
  // Amoy rejected MetaMask's 1.5 Gwei tip with a 25 Gwei minimum.
  if (maxPriorityFeePerGas >= AMOY_MIN_PRIORITY_FEE) {
    return { maxFeePerGas, maxPriorityFeePerGas };
  }
  return {
    maxFeePerGas: maxFeePerGas + AMOY_MIN_PRIORITY_FEE - maxPriorityFeePerGas,
    maxPriorityFeePerGas: AMOY_MIN_PRIORITY_FEE,
  };
}

export const mockUsdcMintAbi = parseAbi([
  "function mint(address to, uint256 amount)",
]);

export const evccFaucetAbi = parseAbi([
  "function credit() view returns (address)",
  "function carbonCredit() view returns (address)",
  "function claimStatus(address recipient) view returns (bool claimed, bool funded)",
  "function claim()",
  "error AlreadyClaimed()",
  "error InsufficientInventory()",
]);
