const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  const SELLER_WALLET = "0x485ed29E56A57c59ca817554950C4C19EB00aF0c";
  const BUYER_WALLET = "0xA4405ECe027f9C0585764b97b3E96dA947b52E7d";

  const CARBON_CREDIT_ADDR = "0x851978601b47a61B8aF3bcC1707B689Fbc977697";
  const MOCK_USDC_ADDR = "0xe35681b0882d533458d22B344268642136ebD813";

  const carbonCredit = await ethers.getContractAt("CarbonCredit1155", CARBON_CREDIT_ADDR, deployer);
  const mockUSDC = await ethers.getContractAt("MockUSDC", MOCK_USDC_ADDR, deployer);

  const sellerCredits = await carbonCredit.balanceOf(SELLER_WALLET, 101n);
  const buyerUSDC = await mockUSDC.balanceOf(BUYER_WALLET);
  const sellerPOL = await ethers.provider.getBalance(SELLER_WALLET);
  const buyerPOL = await ethers.provider.getBalance(BUYER_WALLET);

  console.log("------------------------------------------");
  console.log("Bên Bán (Seller):", SELLER_WALLET);
  console.log("  - EVCC Lô #101:", sellerCredits.toString(), "tCO2e");
  console.log("  - POL Balance: ", ethers.formatEther(sellerPOL), "POL");
  console.log("Bên Mua (Buyer): ", BUYER_WALLET);
  console.log("  - MockUSDC:    ", ethers.formatUnits(buyerUSDC, 6), "USDC");
  console.log("  - POL Balance: ", ethers.formatEther(buyerPOL), "POL");
  console.log("------------------------------------------");

  const feeData = await ethers.provider.getFeeData();
  const maxPriority = ethers.parseUnits("35", "gwei");
  const maxFee = (feeData.maxFeePerGas || ethers.parseUnits("50", "gwei")) + maxPriority;
  const gasOverrides = {
    maxPriorityFeePerGas: maxPriority,
    maxFeePerGas: maxFee,
  };

  if (sellerPOL < ethers.parseEther("0.01")) {
    console.log("Chuyển 0.03 POL cho Seller...");
    const tx1 = await deployer.sendTransaction({  
      to: SELLER_WALLET,
      value: ethers.parseEther("0.03"),
      ...gasOverrides,
    });
    await tx1.wait();
    console.log("✅ Chuyển POL cho Seller thành công:", tx1.hash);
  }

  if (buyerPOL < ethers.parseEther("0.01")) {
    console.log("Chuyển 0.03 POL cho Buyer...");
    const tx2 = await deployer.sendTransaction({
      to: BUYER_WALLET,
      value: ethers.parseEther("0.03"),
      ...gasOverrides,
    });
    await tx2.wait();
    console.log("✅ Chuyển POL cho Buyer thành công:", tx2.hash);
  }

  console.log("🎉 TẤT CẢ VÍ ĐÃ SẴN SÀNG KHỚP LỆNH!");
}

main().catch(console.error);
