const { ethers } = require("hardhat");

/**
 * Script triển khai bộ 3 hợp đồng lên mạng Polygon Amoy Testnet (ChainID 80002)
 * hoặc mạng Hardhat local.
 *
 * Cách chạy:
 * npx hardhat run scripts/deploy_contracts.js --network hardhat
 * npx hardhat run scripts/deploy_contracts.js --network amoy (khi có PRIVATE_KEY)
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("=================================================================");
  console.log("🚀 KHỞI CHẠY TRIỂN KHAI SMART CONTRACT GIAI ĐOẠN 2 (POLYGON AMOY)");
  console.log("=================================================================");
  console.log("Deployer Address:", deployer.address);
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("POL Balance:", ethers.formatEther(balance));

  // 1. Deploy MockUSDC (6 decimals)
  console.log("\n1. Triển khai MockUSDC (ERC-20, 6 decimals)...");
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const mockUSDC = await MockUSDC.deploy();
  await mockUSDC.waitForDeployment();
  const mockUSDCAddress = await mockUSDC.getAddress();
  console.log("✅ MockUSDC deployed at:", mockUSDCAddress);

  // 2. Deploy CarbonCredit1155 (Packed Storage + Buffer Pool)
  console.log("\n2. Triển khai CarbonCredit1155 (ERC-1155, 3-slot Packed Storage)...");
  const baseURI = "https://gateway.pinata.cloud/ipfs/";
  const bufferPoolVault = deployer.address; // Tạm dùng deployer làm Vault nếu chưa có multisig

  const CarbonCredit1155 = await ethers.getContractFactory("CarbonCredit1155");
  const carbonCredit = await CarbonCredit1155.deploy(baseURI, bufferPoolVault);
  await carbonCredit.waitForDeployment();
  const carbonCreditAddress = await carbonCredit.getAddress();
  console.log("✅ CarbonCredit1155 deployed at:", carbonCreditAddress);

  // 3. Deploy CarbonDoubleAuction (EIP-712 + 7 Checkpoints + Batch Settlement)
  console.log("\n3. Triển khai CarbonDoubleAuction (EIP-712, Batch Settlement T+0)...");
  const CarbonDoubleAuction = await ethers.getContractFactory("CarbonDoubleAuction");
  const carbonAuction = await CarbonDoubleAuction.deploy(carbonCreditAddress, mockUSDCAddress);
  await carbonAuction.waitForDeployment();
  const carbonAuctionAddress = await carbonAuction.getAddress();
  console.log("✅ CarbonDoubleAuction deployed at:", carbonAuctionAddress);

  // 4. Phân quyền liên hợp đồng
  console.log("\n4. Cấu hình phân quyền liên hợp đồng (RBAC)...");
  const AUCTION_ROLE = await carbonCredit.AUCTION_CONTRACT_ROLE();
  await carbonCredit.grantRole(AUCTION_ROLE, carbonAuctionAddress);
  console.log("✅ Đã cấp AUCTION_CONTRACT_ROLE cho CarbonDoubleAuction trên CarbonCredit1155");

  console.log("\n=================================================================");
  console.log("🎉 TẤT CẢ HỢP ĐỒNG ĐÃ ĐƯỢC TRIỂN KHAI VÀ LIÊN KẾT THÀNH CÔNG!");
  console.log("=================================================================");
  console.log("MockUSDC:            ", mockUSDCAddress);
  console.log("CarbonCredit1155:    ", carbonCreditAddress);
  console.log("CarbonDoubleAuction: ", carbonAuctionAddress);
  console.log("=================================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

