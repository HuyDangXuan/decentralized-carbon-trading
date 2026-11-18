const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  if (!deployer) {
    console.log("❌ CHƯA TÌM THẤY TÀI KHOẢN. Kiểm tra lại PRIVATE_KEY trong .env");
    return;
  }
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("==========================================");
  console.log("✅ KẾT NỐI VÍ POLYGON AMOY THÀNH CÔNG!");
  console.log("Địa chỉ ví:   ", deployer.address);
  console.log("Số dư POL:    ", ethers.formatEther(balance), "POL");
  console.log("==========================================");
}

main().catch(console.error);

