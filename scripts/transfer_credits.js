const { ethers } = require("hardhat");

/**
 * SCRIPT BÀN GIAO TOÀN DIỆN CHO THẮNG (FRONTEND WEB3 DEVELOPER)
 * 1. Chuyển 1,000 tCO2e Lô #101 sang ví Thắng
 * 2. Cấp quyền VERIFIER_ROLE cho ví Thắng (để test Faucet Modal Task T.2)
 * 3. Đúc 100,000 MockUSDC cho ví Thắng (để test luồng Đặt lệnh Mua BID)
 *
 * Cách chạy:
 * npx hardhat run scripts/transfer_credits.js --network amoy
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("===============================================================================");
  console.log("🚀 KHỞI CHẠY BÀN GIAO ON-CHAIN CHO BẠN THẮNG (POLYGON AMOY TESTNET)");
  console.log("===============================================================================");
  console.log("Deployer Address:", deployer.address);

  const THANG_WALLET = "0xF6dD392EE535fdeDC37C0f3517b3795806f0B5d5";
  console.log("Thắng Wallet:    ", THANG_WALLET);

  const thangBalance = await ethers.provider.getBalance(THANG_WALLET);
  console.log("Số dư POL của Thắng:", ethers.formatEther(thangBalance), "POL");

  const CARBON_CREDIT_ADDR = "0x851978601b47a61B8aF3bcC1707B689Fbc977697";
  const MOCK_USDC_ADDR = "0xe35681b0882d533458d22B344268642136ebD813";

  const carbonCredit = await ethers.getContractAt("CarbonCredit1155", CARBON_CREDIT_ADDR, deployer);
  const mockUSDC = await ethers.getContractAt("MockUSDC", MOCK_USDC_ADDR, deployer);

  // Gas override chuẩn Amoy
  const feeData = await ethers.provider.getFeeData();
  const maxPriority = ethers.parseUnits("35", "gwei");
  const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
  const gasOverrides = {
    maxPriorityFeePerGas: maxPriority,
    maxFeePerGas: maxFee,
  };

  // 1. Chuyển 1,000 tCO2e Lô #101
  const TOKEN_ID = 101n;
  const AMOUNT_TO_SEND = 1_000n;
  console.log(`\n1. Chuyển ${AMOUNT_TO_SEND} tCO2e (Lô #${TOKEN_ID}) cho Thắng...`);
  const txTransfer = await carbonCredit.safeTransferFrom(
    deployer.address,
    THANG_WALLET,
    TOKEN_ID,
    AMOUNT_TO_SEND,
    "0x",
    gasOverrides
  );
  console.log("   - TxHash:", txTransfer.hash);
  await txTransfer.wait();
  console.log("   ✅ Đã chuyển 1,000 tCO2e thành công!");

  // 2. Cấp quyền VERIFIER_ROLE cho ví Thắng
  console.log("\n2. Cấp quyền VERIFIER_ROLE trên CarbonCredit1155 cho Thắng...");
  const VERIFIER_ROLE = await carbonCredit.VERIFIER_ROLE();
  const hasRoleAlready = await carbonCredit.hasRole(VERIFIER_ROLE, THANG_WALLET);
  if (!hasRoleAlready) {
    const txGrant = await carbonCredit.grantRole(VERIFIER_ROLE, THANG_WALLET, gasOverrides);
    console.log("   - TxHash:", txGrant.hash);
    await txGrant.wait();
    console.log("   ✅ Đã cấp quyền VERIFIER_ROLE cho ví Thắng thành công!");
  } else {
    console.log("   ℹ️ Ví Thắng đã có quyền VERIFIER_ROLE từ trước.");
  }

  // 3. Đúc 100,000 MockUSDC cho Thắng
  console.log("\n3. Đúc 100,000 MockUSDC cho ví Thắng...");
  const txMintUSDC = await mockUSDC.mint(THANG_WALLET, 100_000n * 10n ** 6n, gasOverrides);
  console.log("   - TxHash:", txMintUSDC.hash);
  await txMintUSDC.wait();
  console.log("   ✅ Đã đúc 100,000 MockUSDC cho Thắng thành công!");

  // 4. Nếu Thắng có ít POL phí gas, chuyển thêm 0.05 POL
  if (thangBalance < ethers.parseEther("0.1")) {
    console.log("\n4. Chuyển 0.05 POL phí gas cho Thắng...");
    const txSendPOL = await deployer.sendTransaction({
      to: THANG_WALLET,
      value: ethers.parseEther("0.05"),
      ...gasOverrides,
    });
    await txSendPOL.wait();
    console.log("   ✅ Đã chuyển 0.05 POL cho Thắng!");
  }

  // Kiểm tra số dư cuối cùng của Thắng
  const finalEVCC = await carbonCredit.balanceOf(THANG_WALLET, TOKEN_ID);
  const finalUSDC = await mockUSDC.balanceOf(THANG_WALLET);
  const finalPOL = await ethers.provider.getBalance(THANG_WALLET);

  console.log("\n===============================================================================");
  console.log("🎉 BÀN GIAO TẤT CẢ DỮ LIỆU ON-CHAIN CHO THẮNG THÀNH CÔNG VƯỢT MONG ĐỢI!");
  console.log("===============================================================================");
  console.log("Trạng thái ví Thắng (0xF6dD...B5d5):");
  console.log(`- Số dư EVCC Lô #101:  ${finalEVCC.toString()} tCO2e`);
  console.log(`- Số dư MockUSDC:      ${ethers.formatUnits(finalUSDC, 6)} USDC`);
  console.log(`- Số dư Native POL:    ${ethers.formatEther(finalPOL)} POL`);
  console.log(`- Quyền VERIFIER_ROLE: ✅ ĐÃ CẤP (Thắng có thể tự do bấm nút Faucet trên Web)`);
  console.log("===============================================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Lỗi khi bàn giao:", error);
    process.exit(1);
  });
