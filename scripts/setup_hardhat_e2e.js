// SPDX-License-Identifier: MIT
// Dựng môi trường Hardhat cục bộ cho script test E2E liên thông 3 phân hệ.
// Triển khai MockUSDC, CarbonCredit1155, CarbonDoubleAuction, EvccFaucet và cấu hình quyền RBAC.
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();

  // 1. MockUSDC
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();

  // 2. CarbonCredit1155
  const CarbonCredit1155 = await ethers.getContractFactory("CarbonCredit1155");
  const carbon = await CarbonCredit1155.deploy("https://ipfs.io/ipfs/", deployer.address);
  await carbon.waitForDeployment();
  const carbonAddress = await carbon.getAddress();

  // 3. CarbonDoubleAuction
  const CarbonDoubleAuction = await ethers.getContractFactory("CarbonDoubleAuction");
  const auction = await CarbonDoubleAuction.deploy(carbonAddress, usdcAddress);
  await auction.waitForDeployment();
  const auctionAddress = await auction.getAddress();

  // 4. Cấp AUCTION_CONTRACT_ROLE cho CarbonDoubleAuction trên CarbonCredit1155
  const auctionRole = await carbon.AUCTION_CONTRACT_ROLE();
  await (await carbon.grantRole(auctionRole, auctionAddress)).wait();

  // 5. Triển khai EvccFaucet (phục vụ test faucet tín chỉ)
  const EvccFaucet = await ethers.getContractFactory("EvccFaucet");
  const faucet = await EvccFaucet.deploy(carbonAddress);
  await faucet.waitForDeployment();
  const faucetAddress = await faucet.getAddress();

  // 6. Đúc trước Lô tín chỉ #101 (1,000 tCO2e, 10% buffer pool = 100 vào vault, 900 về deployer)
  await (
    await carbon.mintProjectLot(
      deployer.address,
      101n,
      1000n,
      2026,
      0, // Verra VCS
      1000, // 10% buffer
      "bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku",
      ethers.ZeroHash
    )
  ).wait();

  // 7. Nạp 200 tCO2e Lô #101 vào EvccFaucet
  await (await carbon.safeTransferFrom(deployer.address, faucetAddress, 101n, 200n, "0x")).wait();

  // In ra kết quả cấu hình dưới dạng JSON chuẩn cho script E2E
  console.log(
    JSON.stringify({
      usdc: usdcAddress,
      carbon: carbonAddress,
      auction: auctionAddress,
      faucet: faucetAddress,
      deployer: deployer.address,
      operator: deployer.address,
      chainId: 80002,
    })
  );
}

main().catch((err) => {
  console.error("Lỗi khởi tạo Hardhat E2E:", err);
  process.exit(1);
});
