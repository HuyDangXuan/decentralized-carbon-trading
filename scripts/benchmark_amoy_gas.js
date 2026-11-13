const { ethers } = require("hardhat");
const fs = require("fs");

/**
 * Script đo lường Benchmark Gas thực tế trên mạng Polygon Amoy Testnet (ChainID 80002)
 * Phục vụ Task Đ.4 và cung cấp số liệu thực nghiệm khoa học cho bài báo IEEE.
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("===============================================================================");
  console.log("⚡ BẮT ĐẦU CHẠY BENCHMARK GAS THỰC TẾ TRÊN MẠNG POLYGON AMOY TESTNET");
  console.log("===============================================================================");
  console.log("Deployer / Admin Address:", deployer.address);
  const initialBalance = await ethers.provider.getBalance(deployer.address);
  console.log("Initial POL Balance:     ", ethers.formatEther(initialBalance), "POL\n");

  const MOCK_USDC_ADDR = "0xe35681b0882d533458d22B344268642136ebD813";
  const CARBON_CREDIT_ADDR = "0x851978601b47a61B8aF3bcC1707B689Fbc977697";
  const AUCTION_ADDR = "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f";

  const mockUSDC = await ethers.getContractAt("MockUSDC", MOCK_USDC_ADDR, deployer);
  const carbonCredit = await ethers.getContractAt("CarbonCredit1155", CARBON_CREDIT_ADDR, deployer);
  const carbonAuction = await ethers.getContractAt("CarbonDoubleAuction", AUCTION_ADDR, deployer);

  // Helper lấy gas options để transaction trên Polygon Amoy được đào tức thì (< 3s)
  async function getGasOverrides() {
    const feeData = await ethers.provider.getFeeData();
    const maxPriority = ethers.parseUnits("35", "gwei");
    const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
    return {
      maxPriorityFeePerGas: maxPriority,
      maxFeePerGas: maxFee,
    };
  }

  // 1. Tạo 2 tài khoản tạm (Buyer & Seller) cục bộ để ký EIP-712
  console.log("1. Khởi tạo 2 tài khoản Trader (Buyer & Seller) và cấp vốn...");
  const buyerWallet = ethers.Wallet.createRandom().connect(ethers.provider);
  const sellerWallet = ethers.Wallet.createRandom().connect(ethers.provider);
  console.log("   - Buyer Address: ", buyerWallet.address);
  console.log("   - Seller Address:", sellerWallet.address);

  // Chuyển 0.05 POL cho Buyer và Seller để gửi approve tx
  let txFund1 = await deployer.sendTransaction({
    to: buyerWallet.address,
    value: ethers.parseEther("0.04"),
    ...(await getGasOverrides()),
  });
  await txFund1.wait();

  let txFund2 = await deployer.sendTransaction({
    to: sellerWallet.address,
    value: ethers.parseEther("0.04"),
    ...(await getGasOverrides()),
  });
  await txFund2.wait();
  console.log("   ✅ Đã cấp vốn POL cho Buyer và Seller thành công.");

  // Cấp 5,000,000 USDC cho Buyer
  let txMintUSDC = await mockUSDC.mint(buyerWallet.address, 5_000_000n * 10n ** 6n, await getGasOverrides());
  await txMintUSDC.wait();

  // Buyer approve MockUSDC cho Auction
  let txApproveUSDC = await mockUSDC.connect(buyerWallet).approve(AUCTION_ADDR, ethers.MaxUint256, await getGasOverrides());
  await txApproveUSDC.wait();

  // Seller approve CarbonCredit cho Auction
  let txApprove1155 = await carbonCredit.connect(sellerWallet).setApprovalForAll(AUCTION_ADDR, true, await getGasOverrides());
  await txApprove1155.wait();
  console.log("   ✅ Buyer đã approve USDC, Seller đã approve CarbonCredit cho sàn đấu giá.");

  const benchmarkResults = [];

  // =========================================================================
  // BENCHMARK 1: MINT 1 LÔ TÍN CHỈ CARBON (CarbonCredit1155.sol)
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 1: Đúc Lô Tín Chỉ Carbon (mintProjectLot)");
  console.log("===============================================================================");
  const tokenId = Math.floor(Date.now() / 1000); // Unique tokenId
  const totalAmount = 100_000n; // 100,000 tCO2e
  const vintageYear = 2026;
  const standardType = 0; // Verra VCS
  const bufferBps = 1500; // 15%
  const ipfsCID = "QmCarbonBenchmarkAmoy2026RealTxProof123456789";
  const metadataHash = ethers.keccak256(ethers.toUtf8Bytes("benchmark_proof_amoy"));

  console.log(`   Đang gửi transaction mint lô ${tokenId} (100,000 tCO2e, 15% Buffer Pool)...`);
  const mintTx = await carbonCredit.mintProjectLot(
    sellerWallet.address,
    tokenId,
    totalAmount,
    vintageYear,
    standardType,
    bufferBps,
    ipfsCID,
    metadataHash,
    await getGasOverrides()
  );
  console.log("   Đang đợi xác nhận trên Amoy...");
  const mintReceipt = await mintTx.wait();
  const mintGas = Number(mintReceipt.gasUsed);
  const mintCostPOL = ethers.formatEther(mintReceipt.gasUsed * mintReceipt.gasPrice);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${mintReceipt.hash}`);
  console.log(`   - Gas tiêu thụ:     ${mintGas.toLocaleString()} gas`);
  console.log(`   - Phí thực tế:      ${mintCostPOL} POL`);

  benchmarkResults.push({
    action: "Khởi tạo Lô Tín chỉ (mintProjectLot)",
    txHash: mintReceipt.hash,
    gasUsed: mintGas,
    costPOL: mintCostPOL,
    avgGasPerTrade: mintGas,
    savingsPercent: "0% (Baseline)",
  });

  // =========================================================================
  // SETUP EIP-712 TYPED DATA SIGNING
  // =========================================================================
  const domain = {
    name: "EPU Carbon Double Auction",
    version: "2.0",
    chainId: 80002,
    verifyingContract: AUCTION_ADDR,
  };

  const types = {
    Order: [
      { name: "orderId", type: "bytes32" },
      { name: "trader", type: "address" },
      { name: "orderType", type: "uint8" },
      { name: "tokenId", type: "uint256" },
      { name: "amount", type: "uint128" },
      { name: "pricePerUnit", type: "uint128" },
      { name: "nonce", type: "uint256" },
      { name: "deadline", type: "uint256" },
    ],
  };

  async function createSignedMatchedTrade(saltIndex, matchQty = 10n, clearingPrice = 11_000_000n) {
    const block = await ethers.provider.getBlock("latest");
    const deadline = block.timestamp + 3600 * 24;

    const bidOrderId = ethers.keccak256(ethers.toUtf8Bytes(`BID_${Date.now()}_${saltIndex}`));
    const askOrderId = ethers.keccak256(ethers.toUtf8Bytes(`ASK_${Date.now()}_${saltIndex}`));

    const bidOrder = {
      orderId: bidOrderId,
      trader: buyerWallet.address,
      orderType: 0, // BID
      tokenId: tokenId,
      amount: matchQty,
      pricePerUnit: 12_000_000n, // $12.00
      nonce: 0,
      deadline: deadline,
    };

    const askOrder = {
      orderId: askOrderId,
      trader: sellerWallet.address,
      orderType: 1, // ASK
      tokenId: tokenId,
      amount: matchQty,
      pricePerUnit: 10_000_000n, // $10.00
      nonce: 0,
      deadline: deadline,
    };

    const bidSignature = await buyerWallet.signTypedData(domain, types, bidOrder);
    const askSignature = await sellerWallet.signTypedData(domain, types, askOrder);

    return {
      bidOrder,
      askOrder,
      bidSignature,
      askSignature,
      matchAmount: matchQty,
      clearingPrice: clearingPrice, // $11.00
    };
  }

  // =========================================================================
  // BENCHMARK 2: THANH TOÁN 1 CẶP LỆNH ĐƠN LẺ (settleMatchedTrade)
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 2: Thanh Toán 1 Cặp Lệnh Đơn Lẻ (settleMatchedTrade)");
  console.log("===============================================================================");
  const singleTrade = await createSignedMatchedTrade(101);
  console.log("   Đang gửi transaction settleMatchedTrade on-chain...");
  const singleTx = await carbonAuction.settleMatchedTrade(singleTrade, await getGasOverrides());
  console.log("   Đang đợi xác nhận trên Amoy...");
  const singleReceipt = await singleTx.wait();
  const singleGas = Number(singleReceipt.gasUsed);
  const singleCostPOL = ethers.formatEther(singleReceipt.gasUsed * singleReceipt.gasPrice);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${singleReceipt.hash}`);
  console.log(`   - Gas tiêu thụ:     ${singleGas.toLocaleString()} gas`);
  console.log(`   - Phí thực tế:      ${singleCostPOL} POL`);

  benchmarkResults.push({
    action: "Khớp lệnh Đơn lẻ (settleMatchedTrade)",
    txHash: singleReceipt.hash,
    gasUsed: singleGas,
    costPOL: singleCostPOL,
    avgGasPerTrade: singleGas,
    savingsPercent: "0% (Baseline)",
  });

  // =========================================================================
  // BENCHMARK 3: BATCH SETTLEMENT 5 CẶP LỆNH
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 3: Batch Settlement - 5 Cặp Lệnh (batchSettleTrades)");
  console.log("===============================================================================");
  const batch5 = [];
  for (let i = 0; i < 5; i++) {
    batch5.push(await createSignedMatchedTrade(500 + i));
  }
  console.log("   Đang gửi transaction batch 5 cặp lệnh on-chain...");
  const batch5Tx = await carbonAuction.batchSettleTrades(batch5, await getGasOverrides());
  console.log("   Đang đợi xác nhận trên Amoy...");
  const batch5Receipt = await batch5Tx.wait();
  const batch5Gas = Number(batch5Receipt.gasUsed);
  const batch5CostPOL = ethers.formatEther(batch5Receipt.gasUsed * batch5Receipt.gasPrice);
  const avgBatch5 = Math.round(batch5Gas / 5);
  const savings5 = (((singleGas - avgBatch5) / singleGas) * 100).toFixed(1);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${batch5Receipt.hash}`);
  console.log(`   - Tổng gas tiêu thụ: ${batch5Gas.toLocaleString()} gas`);
  console.log(`   - Gas TB / cặp lệnh: ${avgBatch5.toLocaleString()} gas (Tiết kiệm ${savings5}%)`);
  console.log(`   - Phí thực tế:      ${batch5CostPOL} POL`);

  benchmarkResults.push({
    action: "Khớp lô 5 cặp lệnh (Batch 5)",
    txHash: batch5Receipt.hash,
    gasUsed: batch5Gas,
    costPOL: batch5CostPOL,
    avgGasPerTrade: avgBatch5,
    savingsPercent: `-${savings5}%`,
  });

  // =========================================================================
  // BENCHMARK 4: BATCH SETTLEMENT 10 CẶP LỆNH
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 4: Batch Settlement - 10 Cặp Lệnh (batchSettleTrades)");
  console.log("===============================================================================");
  const batch10 = [];
  for (let i = 0; i < 10; i++) {
    batch10.push(await createSignedMatchedTrade(1000 + i));
  }
  console.log("   Đang gửi transaction batch 10 cặp lệnh on-chain...");
  const batch10Tx = await carbonAuction.batchSettleTrades(batch10, await getGasOverrides());
  console.log("   Đang đợi xác nhận trên Amoy...");
  const batch10Receipt = await batch10Tx.wait();
  const batch10Gas = Number(batch10Receipt.gasUsed);
  const batch10CostPOL = ethers.formatEther(batch10Receipt.gasUsed * batch10Receipt.gasPrice);
  const avgBatch10 = Math.round(batch10Gas / 10);
  const savings10 = (((singleGas - avgBatch10) / singleGas) * 100).toFixed(1);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${batch10Receipt.hash}`);
  console.log(`   - Tổng gas tiêu thụ: ${batch10Gas.toLocaleString()} gas`);
  console.log(`   - Gas TB / cặp lệnh: ${avgBatch10.toLocaleString()} gas (Tiết kiệm ${savings10}%)`);
  console.log(`   - Phí thực tế:      ${batch10CostPOL} POL`);

  benchmarkResults.push({
    action: "Khớp lô 10 cặp lệnh (Batch 10)",
    txHash: batch10Receipt.hash,
    gasUsed: batch10Gas,
    costPOL: batch10CostPOL,
    avgGasPerTrade: avgBatch10,
    savingsPercent: `-${savings10}%`,
  });

  // =========================================================================
  // BENCHMARK 5: BATCH SETTLEMENT 20 CẶP LỆNH
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 5: Batch Settlement - 20 Cặp Lệnh (batchSettleTrades)");
  console.log("===============================================================================");
  const batch20 = [];
  for (let i = 0; i < 20; i++) {
    batch20.push(await createSignedMatchedTrade(2000 + i));
  }
  console.log("   Đang gửi transaction batch 20 cặp lệnh on-chain...");
  const batch20Tx = await carbonAuction.batchSettleTrades(batch20, await getGasOverrides());
  console.log("   Đang đợi xác nhận trên Amoy...");
  const batch20Receipt = await batch20Tx.wait();
  const batch20Gas = Number(batch20Receipt.gasUsed);
  const batch20CostPOL = ethers.formatEther(batch20Receipt.gasUsed * batch20Receipt.gasPrice);
  const avgBatch20 = Math.round(batch20Gas / 20);
  const savings20 = (((singleGas - avgBatch20) / singleGas) * 100).toFixed(1);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${batch20Receipt.hash}`);
  console.log(`   - Tổng gas tiêu thụ: ${batch20Gas.toLocaleString()} gas`);
  console.log(`   - Gas TB / cặp lệnh: ${avgBatch20.toLocaleString()} gas (Tiết kiệm ${savings20}%)`);
  console.log(`   - Phí thực tế:      ${batch20CostPOL} POL`);

  benchmarkResults.push({
    action: "Khớp lô 20 cặp lệnh (Batch 20)",
    txHash: batch20Receipt.hash,
    gasUsed: batch20Gas,
    costPOL: batch20CostPOL,
    avgGasPerTrade: avgBatch20,
    savingsPercent: `-${savings20}%`,
  });

  // =========================================================================
  // BENCHMARK 6: TIÊU HỦY TÍN CHỈ (retireCarbonCredit - FR-14)
  // =========================================================================
  console.log("\n===============================================================================");
  console.log("📊 BENCHMARK 6: Tiêu Hủy Tín Chỉ Bù Trừ Phát Thải (retireCarbonCredit)");
  console.log("===============================================================================");
  console.log("   Đang gửi transaction retire 50 tCO2e từ ví Seller...");
  const retireTx = await carbonCredit.connect(sellerWallet).retireCarbonCredit(
    tokenId,
    50n,
    "Bù đắp phát thải Scope 1 - Thử nghiệm Benchmark Amoy 2026",
    await getGasOverrides()
  );
  console.log("   Đang đợi xác nhận trên Amoy...");
  const retireReceipt = await retireTx.wait();
  const retireGas = Number(retireReceipt.gasUsed);
  const retireCostPOL = ethers.formatEther(retireReceipt.gasUsed * retireReceipt.gasPrice);
  console.log(`   ✅ Thành công!`);
  console.log(`   - Transaction Hash: ${retireReceipt.hash}`);
  console.log(`   - Gas tiêu thụ:     ${retireGas.toLocaleString()} gas`);
  console.log(`   - Phí thực tế:      ${retireCostPOL} POL`);

  benchmarkResults.push({
    action: "Tiêu hủy Bù đắp (retireCarbonCredit)",
    txHash: retireReceipt.hash,
    gasUsed: retireGas,
    costPOL: retireCostPOL,
    avgGasPerTrade: retireGas,
    savingsPercent: "N/A",
  });

  // Lưu file kết quả JSON
  fs.writeFileSync("docs/BENCHMARK_RESULTS_AMOY.json", JSON.stringify(benchmarkResults, null, 2));

  console.log("\n===============================================================================");
  console.log("🎉 TẤT CẢ 6 BÀI BENCHMARK THỰC TẾ TRÊN POLYGON AMOY ĐÃ HOÀN TẤT!");
  console.log("===============================================================================");
  console.table(benchmarkResults);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ LỖI TRONG QUÁ TRÌNH CHẠY BENCHMARK:", error);
    process.exit(1);
  });

