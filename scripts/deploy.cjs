const hre = require("hardhat");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);

    const brandAdmin = deployer.address;

    const product = await hre.ethers.deployContract("VeriChainProduct", [brandAdmin]);
    await product.waitForDeployment();

    console.log("VeriChainProduct deployed to:", await product.getAddress());
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
