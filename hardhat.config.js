require("@nomicfoundation/hardhat-toolbox");

const amoyRpcUrl = process.env.AMOY_RPC_URL;
const amoyDeployerKey = process.env.PRIVATE_KEY;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    compilers: [
      {
        version: "0.8.24",
        settings: {
          evmVersion: "cancun",
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    ],
  },
  networks: {
    hardhat: {
      chainId: 80002, // Polygon Amoy chainId
    },
    ...(amoyRpcUrl && amoyDeployerKey ? {
      amoy: { chainId: 80002, url: amoyRpcUrl, accounts: [amoyDeployerKey] },
    } : {}),
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};
