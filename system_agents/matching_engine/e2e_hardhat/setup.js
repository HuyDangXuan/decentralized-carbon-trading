// Triển khai bộ 3 hợp đồng lên node Hardhat cục bộ và dựng dữ liệu cho bài kiểm thử end-to-end.
// Chạy bởi run_e2e.py:  npx hardhat run <file này> --network localhost
// In đúng một dòng JSON (địa chỉ hợp đồng và ví) ở cuối đầu ra.
const { ethers } = require("hardhat");

async function main() {
  const [deployer, seller, buyer1, buyer2, noAllowance] = await ethers.getSigners();
  const usdc = await (await ethers.getContractFactory("MockUSDC")).deploy();
  await usdc.waitForDeployment();
  const carbon = await (await ethers.getContractFactory("CarbonCredit1155")).deploy("https://example.invalid/", deployer.address);
  await carbon.waitForDeployment();
  const auction = await (await ethers.getContractFactory("CarbonDoubleAuction")).deploy(await carbon.getAddress(), await usdc.getAddress());
  await auction.waitForDeployment();
  await (await carbon.grantRole(await carbon.AUCTION_CONTRACT_ROLE(), await auction.getAddress())).wait();
  // Lô tín chỉ 1: 1000 tCO2e, 10% vào buffer pool -> seller nhận 900.
  await (await carbon.mintProjectLot(seller.address, 1, 1000, 2025, 0, 1000, "cid", ethers.ZeroHash)).wait();
  for (const b of [buyer1, buyer2, noAllowance]) await (await usdc.mint(b.address, 10n ** 12n)).wait();
  // noAllowance cố ý KHÔNG cấp allowance để kiểm tra trade bị hợp đồng bỏ qua.
  for (const b of [buyer1, buyer2]) await (await usdc.connect(b).approve(await auction.getAddress(), ethers.MaxUint256)).wait();
  await (await carbon.connect(seller).setApprovalForAll(await auction.getAddress(), true)).wait();
  console.log(JSON.stringify({
    usdc: await usdc.getAddress(), carbon: await carbon.getAddress(), auction: await auction.getAddress(),
    operator: deployer.address, seller: seller.address, buyer1: buyer1.address, buyer2: buyer2.address,
    noAllowance: noAllowance.address,
  }));
}

main().catch((e) => { console.error(e); process.exit(1); });
