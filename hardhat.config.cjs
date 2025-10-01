require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.26",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: true
    }
  },
  networks: {
    plasmaTestnet: {
      url: process.env.PLASMA_RPC_ENDPOINT || "https://testnet-rpc.plasma.to",
      chainId: 9746,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  },
  etherscan: {
    apiKey: {
      plasmaTestnet: "no-api-key-needed"
    },
    customChains: [
      {
        network: "plasmaTestnet",
        chainId: 9746,
        urls: {
          apiURL: "https://testnet.plasmascan.to/api",
          browserURL: "https://testnet.plasmascan.to"
        }
      }
    ]
  }
};
