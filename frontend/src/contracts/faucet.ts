import { parseAbi, parseUnits } from "viem";

export const MOCK_USDC_FAUCET_AMOUNT = parseUnits("10000", 6);

export const mockUsdcMintAbi = parseAbi([
  "function mint(address to, uint256 amount)",
]);

export const evccFaucetAbi = parseAbi([
  "function credit() view returns (address)",
  "function claimStatus(address recipient) view returns (bool claimed, bool funded)",
  "function claim()",
  "error AlreadyClaimed()",
  "error InsufficientInventory()",
]);
