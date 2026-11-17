const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * SCRIPT TRIỂN KHAI VÀ NẠP TOKEN VÀO EVCC FAUCET (POLYGON AMOY)
 * Phục vụ: Cung cấp Smart Contract Faucet cho Thắng (Task T.2 Frontend DApp)
 *
 * Cách chạy:
 * npx hardhat run scripts/deploy_evcc_faucet.js --network amoy
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("===============================================================================");
  console.log("🚰 TRIỂN KHAI HỢP ĐỒNG EVCC FAUCET TRÊN MẠNG POLYGON AMOY TESTNET");
  console.log("===============================================================================");
  console.log("Deployer Address:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("POL Balance:     ", ethers.formatEther(balance), "POL");

  const CARBON_CREDIT_ADDR = "0x851978601b47a61B8aF3bcC1707B689Fbc977697";
  const carbonCredit = await ethers.getContractAt("CarbonCredit1155", CARBON_CREDIT_ADDR, deployer);

  // Gas settings cho Amoy
  const feeData = await ethers.provider.getFeeData();
  const maxPriority = ethers.parseUnits("35", "gwei");
  const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
  const gasOverrides = {
    maxPriorityFeePerGas: maxPriority,
    maxFeePerGas: maxFee,
  };

  // 1. Triển khai hợp đồng EvccFaucet
  console.log("\n1. Đang triển khai EvccFaucet.sol...");
  const EvccFaucetFactory = await ethers.getContractFactory("EvccFaucet");
  const evccFaucet = await EvccFaucetFactory.deploy(CARBON_CREDIT_ADDR, gasOverrides);
  console.log("   - Đang chờ triển khai trên Amoy...");
  await evccFaucet.waitForDeployment();
  const faucetAddress = await evccFaucet.getAddress();
  console.log("   ✅ EvccFaucet đã triển khai tại:", faucetAddress);

  // 2. Nạp 1,000 tCO2e Lô #101 vào EvccFaucet
  const TOKEN_ID = 101n;
  const DEPOSIT_AMOUNT = 1_000n;
  console.log(`\n2. Nạp ${DEPOSIT_AMOUNT} tCO2e Lô #${TOKEN_ID} vào EvccFaucet...`);
  const txDeposit = await carbonCredit.safeTransferFrom(
    deployer.address,
    faucetAddress,
    TOKEN_ID,
    DEPOSIT_AMOUNT,
    "0x",
    gasOverrides
  );
  console.log("   - Mã giao dịch nạp (TxHash):", txDeposit.hash);
  console.log("   - Đang chờ xác thực trên Amoy...");
  await txDeposit.wait();
  console.log("   ✅ Đã nạp thành công!");

  // 3. Kiểm tra số dư của Faucet
  const faucetBalance = await carbonCredit.balanceOf(faucetAddress, TOKEN_ID);
  console.log(`\n3. Số dư tín chỉ trong EvccFaucet: ${faucetBalance.toString()} tCO2e (Lô #${TOKEN_ID})`);

  // 4. Xuất ABI cho Thắng
  const artifact = await artifacts.readArtifact("EvccFaucet");
  const abiPath = path.join(__dirname, "../contracts/abis/EvccFaucet.json");
  fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
  console.log("   ✅ Đã xuất ABI tại:", abiPath);

  console.log("\n===============================================================================");
  console.log("🎉 BÀN GIAO THÔNG TIN EVCC FAUCET CHO BẠN THẮNG (TASK T.2)!");
  console.log("===============================================================================");
  console.log(`- Địa chỉ hợp đồng EvccFaucet: ${faucetAddress}`);
  console.log(`- PolygonScan tra cứu:         https://amoy.polygonscan.com/address/${faucetAddress}`);
  console.log(`- Mã giao dịch nạp Lô #101:   ${txDeposit.hash}`);
  console.log(`- PolygonScan TxHash nạp:      https://amoy.polygonscan.com/tx/${txDeposit.hash}`);
  console.log(`- Khối lượng nạp sẵn:         ${faucetBalance.toString()} tCO2e`);
  console.log(`- Mỗi lượt nhận (claim):       100 tCO2e`);
  console.log("===============================================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Lỗi triển khai EvccFaucet:", error);
    process.exit(1);
  });
