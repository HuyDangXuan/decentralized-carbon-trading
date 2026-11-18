const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EvccFaucet", function () {
  let verifier, stockOwner, firstUser, secondUser, vault, credit, faucet, faucetAddress;

  beforeEach(async function () {
    [verifier, stockOwner, firstUser, secondUser, vault] = await ethers.getSigners();
    credit = await ethers.deployContract("CarbonCredit1155", ["ipfs://", vault.address]);
    await credit.waitForDeployment();
    faucet = await ethers.deployContract("EvccFaucet", [await credit.getAddress()]);
    faucetAddress = await faucet.getAddress();
  });

  function createLot(tokenId) {
    return credit.connect(verifier).mintProjectLot(
      stockOwner.address, tokenId, 300, 2026, 0, 1500, "local-demo-metadata",
      ethers.sha256(ethers.toUtf8Bytes("local demo metadata")),
    );
  }

  it("distributes exactly 100 units of lot #101 to an ordinary wallet once", async function () {
    await createLot(101);
    await credit.connect(stockOwner).safeTransferFrom(stockOwner.address, faucetAddress, 101, 200, "0x");
    expect(await credit.hasRole(await credit.VERIFIER_ROLE(), firstUser.address)).to.equal(false);
    expect(await faucet.claimStatus(firstUser.address)).to.deep.equal([false, true]);

    await expect(faucet.connect(firstUser).claim())
      .to.emit(faucet, "CreditsClaimed").withArgs(firstUser.address, 100);
    expect(await credit.balanceOf(firstUser.address, 101)).to.equal(100);
    await expect(faucet.connect(firstUser).claim()).to.be.revertedWithCustomError(faucet, "AlreadyClaimed");

    await faucet.connect(secondUser).claim();
    expect(await credit.balanceOf(secondUser.address, 101)).to.equal(100);
    expect(await credit.balanceOf(faucetAddress, 101)).to.equal(0);
    expect(await faucet.claimStatus(firstUser.address)).to.deep.equal([true, false]);
  });

  it("keeps the wallet eligible after a failed claim while inventory is empty", async function () {
    await expect(faucet.connect(firstUser).claim()).to.be.revertedWithCustomError(faucet, "InsufficientInventory");
    expect(await faucet.claimStatus(firstUser.address)).to.deep.equal([false, false]);
    await createLot(101);
    await credit.connect(stockOwner).safeTransferFrom(stockOwner.address, faucetAddress, 101, 100, "0x");
    await faucet.connect(firstUser).claim();
    expect(await credit.balanceOf(firstUser.address, 101)).to.equal(100);
  });

  it("rejects deposits of another lot and batch deposits instead of trapping tokens", async function () {
    await createLot(101);
    await createLot(102);
    await expect(credit.connect(stockOwner).safeTransferFrom(stockOwner.address, faucetAddress, 102, 100, "0x"))
      .to.be.revertedWithCustomError(faucet, "UnsupportedDeposit");
    await expect(credit.connect(stockOwner).safeBatchTransferFrom(stockOwner.address, faucetAddress, [101, 102], [1, 1], "0x"))
      .to.be.revertedWithCustomError(faucet, "UnsupportedDeposit");
    expect(await credit.balanceOf(faucetAddress, 102)).to.equal(0);
  });
});
