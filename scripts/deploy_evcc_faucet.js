const { ethers, network } = require("hardhat");

async function main() {
  if (network.name !== "amoy" || (await ethers.provider.getNetwork()).chainId !== 80002n) {
    throw new Error("Run with --network amoy against Polygon Amoy.");
  }

  const creditAddress = process.env.AMOY_CARBON_CREDIT_ADDRESS;
  if (!creditAddress || !ethers.isAddress(creditAddress) || creditAddress === ethers.ZeroAddress) {
    throw new Error("Set AMOY_CARBON_CREDIT_ADDRESS to the CarbonCredit1155 deployment.");
  }
  const faucet = await ethers.deployContract("EvccFaucet", [creditAddress]);
  await faucet.waitForDeployment();
  console.log("NEXT_PUBLIC_AMOY_EVCC_FAUCET_ADDRESS=" + await faucet.getAddress());
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
