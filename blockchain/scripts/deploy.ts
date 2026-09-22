import { network } from "hardhat";

const { ethers } = await network.connect();

const CertificateRegistry = await ethers.getContractFactory("CertificateRegistry");

const certificateRegistry = await CertificateRegistry.deploy();

await certificateRegistry.waitForDeployment();

console.log(
  "CertificateRegistry deployed to:",
  await certificateRegistry.getAddress()
);