const { ethers } = require("hardhat");

/**
 * SCRIPT CẤP QUYỀN VÀ TÀI TRỢ GAS CHO BOT CỦA PHI
 * Dành cho: Nguyễn Hoàng Đức (Smart Contract Architect)
 * Phục vụ: Bàn giao Task Đ.3 cho Nguyễn Bảo Phi (Auction Matching & Submitter Bot)
 *
 * Cách chạy:
 * npx hardhat run scripts/setup_operator_bot.js --network amoy
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("===============================================================================");
  console.log("🤖 CẤP QUYỀN SETTLEMENT OPERATOR & CHUYỂN GAS CHO BOT CỦA PHI (POLYGON AMOY)");
  console.log("===============================================================================");
  console.log("Deployer Address:", deployer.address);

  const PHI_BOT_WALLET = "0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE";
  console.log("Phi Bot Wallet:  ", PHI_BOT_WALLET);

  const initialPOL = await ethers.provider.getBalance(PHI_BOT_WALLET);
  console.log("Số dư POL hiện tại của Bot:", ethers.formatEther(initialPOL), "POL");

  const AUCTION_ADDR = "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f";
  const carbonAuction = await ethers.getContractAt("CarbonDoubleAuction", AUCTION_ADDR, deployer);

  // Gas settings cho Amoy
  const feeData = await ethers.provider.getFeeData();
  const maxPriority = ethers.parseUnits("35", "gwei");
  const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
  const gasOverrides = {
    maxPriorityFeePerGas: maxPriority,
    maxFeePerGas: maxFee,
  };

  // 1. Kiểm tra và Cấp quyền SETTLEMENT_OPERATOR_ROLE
  console.log("\n1. Cấp quyền SETTLEMENT_OPERATOR_ROLE trên CarbonDoubleAuction...");
  const SETTLEMENT_ROLE = await carbonAuction.SETTLEMENT_OPERATOR_ROLE();
  console.log("   - SETTLEMENT_OPERATOR_ROLE Hash:", SETTLEMENT_ROLE);

  const hasRoleAlready = await carbonAuction.hasRole(SETTLEMENT_ROLE, PHI_BOT_WALLET);
  let grantTxHash = "N/A (Đã có từ trước)";

  if (!hasRoleAlready) {
    const txGrant = await carbonAuction.grantRole(SETTLEMENT_ROLE, PHI_BOT_WALLET, gasOverrides);
    grantTxHash = txGrant.hash;
    console.log("   - TxHash grantRole:", txGrant.hash);
    console.log("   - Đang chờ xác thực trên Amoy...");
    await txGrant.wait();
    console.log("   ✅ Đã cấp quyền SETTLEMENT_OPERATOR_ROLE thành công!");
  } else {
    console.log("   ℹ️ Ví bot của Phi đã có quyền SETTLEMENT_OPERATOR_ROLE từ trước.");
  }

  // 2. Chuyển 0.1 POL cho bot để trả phí gas nộp batch settlement
  console.log("\n2. Chuyển 0.1 POL phí gas cho ví bot...");
  const txSendPOL = await deployer.sendTransaction({
    to: PHI_BOT_WALLET,
    value: ethers.parseEther("0.1"),
    ...gasOverrides,
  });
  console.log("   - TxHash send POL:", txSendPOL.hash);
  console.log("   - Đang chờ xác thực trên Amoy...");
  await txSendPOL.wait();
  console.log("   ✅ Đã chuyển 0.1 POL cho ví bot thành công!");

  // 3. Kiểm tra lại trạng thái cuối cùng
  const finalHasRole = await carbonAuction.hasRole(SETTLEMENT_ROLE, PHI_BOT_WALLET);
  const finalPOL = await ethers.provider.getBalance(PHI_BOT_WALLET);

  console.log("\n===============================================================================");
  console.log("🎉 BÀN GIAO THÀNH CÔNG CHO BOT CỦA PHI!");
  console.log("===============================================================================");
  console.log("Thông tin bàn giao:");
  console.log(`- Địa chỉ ví bot:                ${PHI_BOT_WALLET}`);
  console.log(`- Quyền SETTLEMENT_OPERATOR_ROLE: ${finalHasRole ? "✅ HỢP LỆ" : "❌ THẤT BẠI"}`);
  console.log(`- TxHash grantRole:              https://amoy.polygonscan.com/tx/${grantTxHash}`);
  console.log(`- Số dư POL ví bot:              ${ethers.formatEther(finalPOL)} POL`);
  console.log(`- TxHash chuyển POL:             https://amoy.polygonscan.com/tx/${txSendPOL.hash}`);
  console.log("===============================================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Lỗi khi setup bot cho Phi:", error);
    process.exit(1);
  });
