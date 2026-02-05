const { HardhatUserConfig } = require("hardhat/config");
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
    solidity: "0.8.20",
    networks: {
        neox_testnet: {
            url: "https://neoxt4seed1.ngd.network",
            accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
            gasPrice: 50000000000, // 50 Gwei
            timeout: 120000
        },
        banelabs: {
            url: "https://testnet.rpc.banelabs.org",
            accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
            gasPrice: 50000000000,
            timeout: 120000
        }
    },
};
