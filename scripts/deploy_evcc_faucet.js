const { ethers, network } = require("hardhat");

async function main() {
  if (network.name !== "amoy" || (await ethers.provider.getNetwork()).chainId !== 80002n) {
    throw new Error("Run with --network amoy against Polygon Amoy.");
  }

  const creditAddress = process.env.AMOY_CARBON_CREDIT_ADDRESS;
  if (!creditAddress || !ethers.isAddress(creditAddress) || creditAddress === ethers.ZeroAddress) {
    throw new Error("Set AMOY_CARBON_CREDIT_ADDRESS to the CarbonCredit1155 deployment.");
  }
  const existingAddress = process.env.AMOY_EVCC_FAUCET_ADDRESS;
  if (existingAddress && (!ethers.isAddress(existingAddress) || existingAddress === ethers.ZeroAddress)) {
    throw new Error("AMOY_EVCC_FAUCET_ADDRESS must be a deployed faucet address.");
  }
  const target = process.env.AMOY_EVCC_FAUCET_TARGET_BALANCE;
  if (target !== undefined && (!/^\d+$/.test(target) || BigInt(target) < 100n)) {
    throw new Error("AMOY_EVCC_FAUCET_TARGET_BALANCE must be an integer of at least 100 EVCC.");
  }

  const [signer] = await ethers.getSigners();
  const credit = await ethers.getContractAt("CarbonCredit1155", creditAddress, signer);
  const tokenId = 101n;
  let faucet;
  if (existingAddress) {
    faucet = await ethers.getContractAt("EvccFaucet", existingAddress, signer);
    const [configuredCredit, configuredLot, claimAmount] = await Promise.all([
      faucet.credit(), faucet.TOKEN_ID(), faucet.CLAIM_AMOUNT(),
    ]);
    if (configuredCredit !== ethers.getAddress(creditAddress) || configuredLot !== tokenId || claimAmount !== 100n) {
      throw new Error("The existing faucet does not match the Amoy CarbonCredit1155, lot #101 and claim amount.");
    }
  }

  const currentBalance = faucet ? await credit.balanceOf(existingAddress, tokenId) : 0n;
  const topUp = target === undefined ? 0n : BigInt(target) - currentBalance;
  const owner = await signer.getAddress();
  if (topUp > 0n) {
    const [lot, vault, ownerBalance] = await Promise.all([
      credit.getLotDetails(tokenId), credit.bufferPoolVault(), credit.balanceOf(owner, tokenId),
    ]);
    if (!lot.isActive) throw new Error("Lot #101 is not active on the configured contract.");
    const reserve = owner === vault ? lot.bufferPoolAmount : 0n;
    if (ownerBalance < topUp + reserve) {
      throw new Error(`Wallet ${owner} cannot supply ${topUp} circulating EVCC #101 and keep the buffer intact.`);
    }
  }

  if (!faucet) {
    faucet = await ethers.deployContract("EvccFaucet", [creditAddress], signer);
    await faucet.waitForDeployment();
    console.log("Deployment transaction:", faucet.deploymentTransaction().hash);
  }
  const faucetAddress = await faucet.getAddress();
  console.log("NEXT_PUBLIC_AMOY_EVCC_FAUCET_ADDRESS=" + faucetAddress);

  if (topUp > 0n) {
    await credit.safeTransferFrom.staticCall(owner, faucetAddress, tokenId, topUp, "0x");
    const funding = await credit.safeTransferFrom(owner, faucetAddress, tokenId, topUp, "0x");
    const receipt = await funding.wait();
    console.log("Funding transaction:", receipt.hash);
  }
  console.log("Faucet EVCC #101 balance:", (await credit.balanceOf(faucetAddress, tokenId)).toString());
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
