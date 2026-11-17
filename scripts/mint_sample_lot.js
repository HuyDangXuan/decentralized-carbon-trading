const { ethers } = require("hardhat");

/**
 * SCRIPT MINT LÔ TÍN CHỈ MẪU #101 TRÊN POLYGON AMOY
 * Dành cho: Nguyễn Hoàng Đức (Smart Contract Architect)
 * Phục vụ: Cung cấp lô tín chỉ thực tế on-chain cho Thắng (Frontend DApp) & Phi (Auction Engine)
 *
 * Cách chạy:
 * npx hardhat run scripts/mint_sample_lot.js --network amoy
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("===============================================================================");
  console.log("🌲 TIẾN HÀNH ĐÚC LÔ TÍN CHỈ CARBON MẪU #101 (POLYGON AMOY TESTNET)");
  console.log("===============================================================================");
  console.log("Deployer / Verifier Address:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("POL Balance:                ", ethers.formatEther(balance), "POL");

  const CARBON_CREDIT_ADDR = "0x851978601b47a61B8aF3bcC1707B689Fbc977697";
  const carbonCredit = await ethers.getContractAt("CarbonCredit1155", CARBON_CREDIT_ADDR, deployer);

  // 1. Kiểm tra quyền VERIFIER_ROLE của Deployer
  const VERIFIER_ROLE = await carbonCredit.VERIFIER_ROLE();
  const hasVerifierRole = await carbonCredit.hasRole(VERIFIER_ROLE, deployer.address);
  console.log("\n1. Kiểm tra quyền Verifier:");
  console.log("   - VERIFIER_ROLE:", VERIFIER_ROLE);
  console.log("   - Deployer có quyền Verifier:", hasVerifierRole ? "✅ CÓ" : "❌ KHÔNG");

  if (!hasVerifierRole) {
    throw new Error("Ví deployer không có quyền VERIFIER_ROLE!");
  }

  // 2. Thiết lập thông số Lô #101 theo chuẩn Dự án NCKH
  const tokenId = 101n;
  const totalAmount = 10_000n; // 10,000 tCO2e
  const vintageYear = 2026;
  const standardType = 3; // 3: Vietnam VCM (hoặc 0: Verra VCS)
  const bufferBps = 1500; // 15% trích lập Buffer Pool Vault
  // Metadata CID chuẩn IPFS Pinata lưu PDD & MRV Report
  const ipfsCID = "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi";
  const metadataHash = ethers.keccak256(ethers.toUtf8Bytes("EVCC-LOT-101-NORTHWEST-VIETNAM-2026"));

  // Kiểm tra xem lô 101 đã tồn tại chưa
  const existingLot = await carbonCredit.getLotDetails(tokenId);
  if (existingLot.totalIssued > 0n) {
    console.log(`\n⚠️ Lô #${tokenId} đã tồn tại trên Amoy!`);
    console.log(`   - Tổng phát hành: ${existingLot.totalIssued.toString()} tCO2e`);
    console.log(`   - Lưu hành:       ${existingLot.circulatingSupply.toString()} tCO2e`);
    console.log(`   - Buffer Pool:    ${existingLot.bufferPoolAmount.toString()} tCO2e`);
    return;
  }

  // 3. Phí Gas tối ưu trên Polygon Amoy (EIP-1559)
  const feeData = await ethers.provider.getFeeData();
  const maxPriority = ethers.parseUnits("35", "gwei");
  const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
  const gasOverrides = {
    maxPriorityFeePerGas: maxPriority,
    maxFeePerGas: maxFee,
  };

  // 4. Gửi giao dịch đúc lô mẫu #101
  console.log(`\n2. Đang gửi giao dịch mint lô #${tokenId} (10,000 tCO2e, Vintage 2026, 15% Buffer)...`);
  const mintTx = await carbonCredit.mintProjectLot(
    deployer.address, // Nhận tín chỉ lưu hành vào ví Deployer
    tokenId,
    totalAmount,
    vintageYear,
    standardType,
    bufferBps,
    ipfsCID,
    metadataHash,
    gasOverrides
  );

  console.log("   - Transaction Hash:", mintTx.hash);
  console.log("   - Đang chờ xác thực trên Polygon Amoy...");
  const receipt = await mintTx.wait();
  console.log("   ✅ Giao dịch thành công tại Block:", receipt.blockNumber);
  console.log("   - Gas tiêu thụ:", receipt.gasUsed.toString(), "units");

  // 5. Kiểm tra lại thông tin lô sau khi đúc
  const newLot = await carbonCredit.getLotDetails(tokenId);
  const myBalance = await carbonCredit.balanceOf(deployer.address, tokenId);
  const vaultAddress = await carbonCredit.bufferPoolVault();
  const vaultBalance = await carbonCredit.balanceOf(vaultAddress, tokenId);

  console.log("\n===============================================================================");
  console.log("🎉 ĐÚC THÀNH CÔNG LÔ TÍN CHỈ CARBON #101 TRÊN POLYGON AMOY!");
  console.log("===============================================================================");
  console.log("Thông tin xác nhận on-chain:");
  console.log(`- Token ID:             #${tokenId}`);
  console.log(`- Tên lô:               EVCC Rừng Tây Bắc (Vintage 2026)`);
  console.log(`- Tổng khối lượng:      ${newLot.totalIssued.toString()} tCO2e`);
  console.log(`- Tín chỉ lưu hành:     ${newLot.circulatingSupply.toString()} tCO2e (Số dư ví Deployer: ${myBalance.toString()})`);
  console.log(`- Trích Buffer Vault:   ${newLot.bufferPoolAmount.toString()} tCO2e (15%) (Số dư Vault: ${vaultBalance.toString()})`);
  console.log(`- IPFS CID:             ipfs://${ipfsCID}`);
  console.log(`- PolygonScan Tra cứu:  https://amoy.polygonscan.com/tx/${mintTx.hash}`);
  console.log("===============================================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Lỗi khi mint lô mẫu:", error);
    process.exit(1);
  });
