const { ethers } = require("hardhat");

async function main() {
  console.log("Đang kiểm tra 3 contracts trên Polygon Amoy...");
  const addrs = {
    MockUSDC: "0xe35681b0882d533458d22B344268642136ebD813",
    CarbonCredit1155: "0x851978601b47a61B8aF3bcC1707B689Fbc977697",
    CarbonDoubleAuction: "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f",
  };

  for (const [name, addr] of Object.entries(addrs)) {
    const code = await ethers.provider.getCode(addr);
    console.log(`✅ ${name} (${addr}) -> Bytecode size: ${code.length} chars (LIVE ON CHAIN)`);
  }
}

main().catch(console.error);

