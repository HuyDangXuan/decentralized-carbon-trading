const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EPU Decentralized Carbon Trading - Phase 2 Test Suite", function () {
  let admin, verifier, developer, buyer, seller, vault, malicious;
  let mockUSDC, carbonCredit, carbonAuction;

  const BASE_URI = "https://gateway.pinata.cloud/ipfs/";
  const SAMPLE_CID = "QmCarbonVNForest2026NorthWestProtectedArea12345";
  const SAMPLE_HASH = ethers.keccak256(ethers.toUtf8Bytes("sample_metadata_hash"));

  const TOKEN_ID_FOREST = 101;
  const TOTAL_MINT_AMOUNT = 1000n; // 1,000 tCO2e
  const VINTAGE_YEAR = 2026;
  const STANDARD_VERRA = 0;
  const BUFFER_BPS_15 = 1500; // 15%

  // Đơn vị tiền tệ: Micro-USDC (6 decimals)
  // 10 USD = 10,000,000 micro-USDC
  const PRICE_10_USD = 10_000_000n;
  const PRICE_11_USD = 11_000_000n;
  const PRICE_12_USD = 12_000_000n;

  beforeEach(async function () {
    [admin, verifier, developer, buyer, seller, vault, malicious] = await ethers.getSigners();

    // 1. Deploy MockUSDC (6 decimals)
    const MockUSDC = await ethers.getContractFactory("MockUSDC");
    mockUSDC = await MockUSDC.deploy();
    await mockUSDC.waitForDeployment();

    // 2. Deploy CarbonCredit1155
    const CarbonCredit1155 = await ethers.getContractFactory("CarbonCredit1155");
    carbonCredit = await CarbonCredit1155.deploy(BASE_URI, vault.address);
    await carbonCredit.waitForDeployment();

    // Gán quyền VERIFIER_ROLE cho verifier
    const VERIFIER_ROLE = await carbonCredit.VERIFIER_ROLE();
    await carbonCredit.grantRole(VERIFIER_ROLE, verifier.address);

    // 3. Deploy CarbonDoubleAuction
    const CarbonDoubleAuction = await ethers.getContractFactory("CarbonDoubleAuction");
    carbonAuction = await CarbonDoubleAuction.deploy(
      await carbonCredit.getAddress(),
      await mockUSDC.getAddress()
    );
    await carbonAuction.waitForDeployment();

    // Gán quyền AUCTION_CONTRACT_ROLE cho sàn đấu giá trên hợp đồng CarbonCredit
    const AUCTION_ROLE = await carbonCredit.AUCTION_CONTRACT_ROLE();
    await carbonCredit.grantRole(AUCTION_ROLE, await carbonAuction.getAddress());

    // Cấp tiền MockUSDC cho Buyer: 100,000 USDC = 100,000,000,000 micro-USDC
    await mockUSDC.mint(buyer.address, 100_000_000_000n);

    // Buyer approve cho sàn đấu giá rút MockUSDC
    await mockUSDC.connect(buyer).approve(await carbonAuction.getAddress(), ethers.MaxUint256);
  });

  // =========================================================================
  //                     TEST PHÂN HỆ 1: MOCK USDC (6 DECIMALS)
  // =========================================================================
  describe("1. MockUSDC Specification", function () {
    it("phải có đúng 6 decimals (Micro-USDC)", async function () {
      expect(await mockUSDC.decimals()).to.equal(6);
    });

    it("phải cấp số dư chính xác cho tài khoản thử nghiệm", async function () {
      const balance = await mockUSDC.balanceOf(buyer.address);
      expect(balance).to.equal(100_000_000_000n);
    });
  });

  // =========================================================================
  //           TEST PHÂN HỆ 2: CARBONCREDIT1155 (STORAGE, RBAC, BUFFER)
  // =========================================================================
  describe("2. CarbonCredit1155 Specification (V2)", function () {
    it("chỉ có VERIFIER_ROLE mới được phép gọi mintProjectLot", async function () {
      await expect(
        carbonCredit.connect(malicious).mintProjectLot(
          developer.address,
          TOKEN_ID_FOREST,
          TOTAL_MINT_AMOUNT,
          VINTAGE_YEAR,
          STANDARD_VERRA,
          BUFFER_BPS_15,
          SAMPLE_CID,
          SAMPLE_HASH
        )
      ).to.be.revertedWithCustomError(carbonCredit, "AccessControlUnauthorizedAccount");
    });

    it("tự động trích lập đúng 15% vào Buffer Pool Vault và 85% cho Developer", async function () {
      await carbonCredit.connect(verifier).mintProjectLot(
        developer.address,
        TOKEN_ID_FOREST,
        TOTAL_MINT_AMOUNT,
        VINTAGE_YEAR,
        STANDARD_VERRA,
        BUFFER_BPS_15,
        SAMPLE_CID,
        SAMPLE_HASH
      );

      // 15% của 1000 = 150 token chuyển vào Vault
      const vaultBalance = await carbonCredit.balanceOf(vault.address, TOKEN_ID_FOREST);
      expect(vaultBalance).to.equal(150n);

      // 85% còn lại = 850 token cấp cho Developer
      const devBalance = await carbonCredit.balanceOf(developer.address, TOKEN_ID_FOREST);
      expect(devBalance).to.equal(850n);

      // Kiểm tra Packed Struct trong storage
      const lot = await carbonCredit.getLotDetails(TOKEN_ID_FOREST);
      expect(lot.projectDeveloper).to.equal(developer.address);
      expect(lot.totalIssued).to.equal(1000n);
      expect(lot.circulatingSupply).to.equal(850n);
      expect(lot.bufferPoolAmount).to.equal(150n);
      expect(lot.vintageYear).to.equal(2026);
      expect(lot.bufferPoolBps).to.equal(1500);
      expect(lot.isActive).to.equal(true);
    });

    it("trả về đúng đường dẫn IPFS CID qua hàm uri()", async function () {
      await carbonCredit.connect(verifier).mintProjectLot(
        developer.address,
        TOKEN_ID_FOREST,
        TOTAL_MINT_AMOUNT,
        VINTAGE_YEAR,
        STANDARD_VERRA,
        BUFFER_BPS_15,
        SAMPLE_CID,
        SAMPLE_HASH
      );

      const tokenURI = await carbonCredit.uri(TOKEN_ID_FOREST);
      expect(tokenURI).to.equal(BASE_URI + SAMPLE_CID);
    });

    it("cho phép tiêu hủy tín chỉ (Retire/Burn - FR-14) và ghi nhận lý do", async function () {
      // Mint tín chỉ
      await carbonCredit.connect(verifier).mintProjectLot(
        developer.address,
        TOKEN_ID_FOREST,
        TOTAL_MINT_AMOUNT,
        VINTAGE_YEAR,
        STANDARD_VERRA,
        BUFFER_BPS_15,
        SAMPLE_CID,
        SAMPLE_HASH
      );

      // Developer tiêu hủy 100 tín chỉ
      await expect(
        carbonCredit.connect(developer).retireCarbonCredit(
          TOKEN_ID_FOREST,
          100n,
          "Bù đắp phát thải Scope 1 - Quý 4/2026"
        )
      )
        .to.emit(carbonCredit, "CarbonCreditsRetired")
        .withArgs(
          TOKEN_ID_FOREST,
          developer.address,
          developer.address,
          100n,
          "Bù đắp phát thải Scope 1 - Quý 4/2026"
        );

      // Số dư giảm còn 750
      expect(await carbonCredit.balanceOf(developer.address, TOKEN_ID_FOREST)).to.equal(750n);

      const lot = await carbonCredit.getLotDetails(TOKEN_ID_FOREST);
      expect(lot.totalRetired).to.equal(100n);
      expect(lot.circulatingSupply).to.equal(750n);
    });

    it("cho phép giải tỏa Buffer Pool khi có sự cố đảo ngược phát thải (Reversal)", async function () {
      await carbonCredit.connect(verifier).mintProjectLot(
        developer.address,
        TOKEN_ID_FOREST,
        TOTAL_MINT_AMOUNT,
        VINTAGE_YEAR,
        STANDARD_VERRA,
        BUFFER_BPS_15,
        SAMPLE_CID,
        SAMPLE_HASH
      );

      const proofHash = ethers.keccak256(ethers.toUtf8Bytes("forest_fire_report_2026"));
      await expect(
        carbonCredit.connect(verifier).compensateReversal(TOKEN_ID_FOREST, 50n, proofHash)
      )
        .to.emit(carbonCredit, "BufferCompensated")
        .withArgs(TOKEN_ID_FOREST, 50n, proofHash);

      // Vault bị đốt 50 token, còn 100 token
      expect(await carbonCredit.balanceOf(vault.address, TOKEN_ID_FOREST)).to.equal(100n);
    });
  });

  // =========================================================================
  //       TEST PHÂN HỆ 3: CARBONDOUBLEAUCTION (EIP-712 & 7 CHỐT CHẶN)
  // =========================================================================
  describe("3. CarbonDoubleAuction Specification (EIP-712 & 7 Checkpoints)", function () {
    let domain, types;

    beforeEach(async function () {
      // Đúc 1,000 tín chỉ cho Seller
      await carbonCredit.connect(verifier).mintProjectLot(
        seller.address,
        TOKEN_ID_FOREST,
        TOTAL_MINT_AMOUNT,
        VINTAGE_YEAR,
        STANDARD_VERRA,
        BUFFER_BPS_15,
        SAMPLE_CID,
        SAMPLE_HASH
      );

      // Seller ủy quyền ERC-1155 cho Sàn đấu giá
      await carbonCredit.connect(seller).setApprovalForAll(await carbonAuction.getAddress(), true);

      // Thiết lập Domain EIP-712
      const auctionAddress = await carbonAuction.getAddress();
      domain = {
        name: "EPU Carbon Double Auction",
        version: "2.0",
        chainId: 80002,
        verifyingContract: auctionAddress,
      };

      types = {
        Order: [
          { name: "orderId", type: "bytes32" },
          { name: "trader", type: "address" },
          { name: "orderType", type: "uint8" },
          { name: "tokenId", type: "uint256" },
          { name: "amount", type: "uint128" },
          { name: "pricePerUnit", type: "uint128" },
          { name: "nonce", type: "uint256" },
          { name: "deadline", type: "uint256" },
        ],
      };
    });

    async function createAndSignOrder(signer, orderType, amount, price, deadlineOffset = 3600) {
      const block = await ethers.provider.getBlock("latest");
      const deadline = block.timestamp + deadlineOffset;
      const nonce = await carbonAuction.userNonces(signer.address);

      const orderId = ethers.keccak256(
        ethers.AbiCoder.defaultAbiCoder().encode(
          ["address", "uint8", "uint256", "uint128", "uint256"],
          [signer.address, orderType, TOKEN_ID_FOREST, amount, block.timestamp]
        )
      );

      const order = {
        orderId: orderId,
        trader: signer.address,
        orderType: orderType, // 0: BID, 1: ASK
        tokenId: TOKEN_ID_FOREST,
        amount: amount,
        pricePerUnit: price,
        nonce: nonce,
        deadline: deadline,
      };

      const signature = await signer.signTypedData(domain, types, order);
      return { order, signature };
    }

    it("CHỐT #1: Revert nếu chữ ký EIP-712 không hợp lệ (mạo danh)", async function () {
      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_12_USD);
      const ask = await createAndSignOrder(seller, 1, 100n, PRICE_10_USD);

      // Đánh tráo chữ ký của bên mua bằng chữ ký của kẻ tấn công (malicious)
      const fakeSig = await malicious.signTypedData(domain, types, bid.order);

      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: fakeSig,
        askSignature: ask.signature,
        matchAmount: 100n,
        clearingPrice: PRICE_11_USD,
      };

      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "InvalidSignature"
      );
    });

    it("CHỐT #2: Revert nếu lệnh đã quá hạn (Deadline Expired)", async function () {
      // Tạo lệnh có hạn deadline -10 giây
      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_12_USD, -10);
      const ask = await createAndSignOrder(seller, 1, 100n, PRICE_10_USD, 3600);

      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: bid.signature,
        askSignature: ask.signature,
        matchAmount: 100n,
        clearingPrice: PRICE_11_USD,
      };

      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "SignatureExpired"
      );
    });

    it("CHỐT #3: Revert nếu cùng địa chỉ ví (Chống Wash Trading / Tự giao dịch)", async function () {
      // Buyer tự mua tự bán
      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_12_USD);
      const ask = await createAndSignOrder(buyer, 1, 100n, PRICE_10_USD);

      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: bid.signature,
        askSignature: ask.signature,
        matchAmount: 100n,
        clearingPrice: PRICE_11_USD,
      };

      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "SelfTradingNotAllowed"
      );
    });

    it("CHỐT #4: Revert nếu giá khớp P* nằm ngoài dải [ask, bid]", async function () {
      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_11_USD);
      const ask = await createAndSignOrder(seller, 1, 100n, PRICE_10_USD);

      // Đặt giá khớp $13 > Bid $11
      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: bid.signature,
        askSignature: ask.signature,
        matchAmount: 100n,
        clearingPrice: 13_000_000n,
      };

      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "PriceMismatch"
      );
    });

    it("CHỐT #5 & #7: Khớp lệnh thành công Atomic Swap T+0 và chống nộp trùng", async function () {
      const matchQty = 50n; // 50 tCO2e
      const clearingP = PRICE_11_USD; // 11 USDC / tCO2e -> Tổng: 550 USDC = 550,000,000 micro-USDC

      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_12_USD);
      const ask = await createAndSignOrder(seller, 1, 100n, PRICE_10_USD);

      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: bid.signature,
        askSignature: ask.signature,
        matchAmount: matchQty,
        clearingPrice: clearingP,
      };

      const buyerInitialUSDC = await mockUSDC.balanceOf(buyer.address);
      const sellerInitialUSDC = await mockUSDC.balanceOf(seller.address);
      const sellerInitialCarbon = await carbonCredit.balanceOf(seller.address, TOKEN_ID_FOREST);

      // Thực thi thanh toán Atomic
      const tx = await carbonAuction.settleMatchedTrade(trade);
      const receipt = await tx.wait();

      console.log(`\n  ⚡ Gas tiêu thụ cho 1 cặp lệnh Atomic Swap: ${receipt.gasUsed.toString()} gas`);

      // Kiểm tra chuyển tiền: Buyer mất 550 USDC, Seller nhận 550 USDC
      const totalCost = matchQty * clearingP;
      expect(await mockUSDC.balanceOf(buyer.address)).to.equal(buyerInitialUSDC - totalCost);
      expect(await mockUSDC.balanceOf(seller.address)).to.equal(sellerInitialUSDC + totalCost);

      // Kiểm tra chuyển tín chỉ: Seller mất 50 token, Buyer nhận 50 token
      expect(await carbonCredit.balanceOf(seller.address, TOKEN_ID_FOREST)).to.equal(sellerInitialCarbon - matchQty);
      expect(await carbonCredit.balanceOf(buyer.address, TOKEN_ID_FOREST)).to.equal(matchQty);

      // CHỐT #7: Thử nộp lại đúng giao dịch này trong cùng block -> Phải Revert
      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "TradeAlreadyExecuted"
      );
    });

    it("CHỐT #6: Revert nếu lệnh đã bị người dùng hủy qua cancelOrder()", async function () {
      const bid = await createAndSignOrder(buyer, 0, 100n, PRICE_12_USD);
      const ask = await createAndSignOrder(seller, 1, 100n, PRICE_10_USD);

      // Buyer chủ động hủy lệnh
      await carbonAuction.connect(buyer).cancelOrder(bid.order.orderId);

      const trade = {
        bidOrder: bid.order,
        askOrder: ask.order,
        bidSignature: bid.signature,
        askSignature: ask.signature,
        matchAmount: 100n,
        clearingPrice: PRICE_11_USD,
      };

      await expect(carbonAuction.settleMatchedTrade(trade)).to.be.revertedWithCustomError(
        carbonAuction,
        "OrderAlreadyCancelledOrFilled"
      );
    });

    it("Thanh toán hàng loạt theo lô (Batch Settlement - FR-11) đạt chuẩn Gas < 85,000 gas/lệnh", async function () {
      const batchTrades = [];
      const BATCH_SIZE = 5;

      for (let i = 0; i < BATCH_SIZE; i++) {
        const bid = await createAndSignOrder(buyer, 0, 10n, PRICE_12_USD);
        const ask = await createAndSignOrder(seller, 1, 10n, PRICE_10_USD);
        batchTrades.push({
          bidOrder: bid.order,
          askOrder: ask.order,
          bidSignature: bid.signature,
          askSignature: ask.signature,
          matchAmount: 10n,
          clearingPrice: PRICE_11_USD,
        });
      }

      const tx = await carbonAuction.batchSettleTrades(batchTrades);
      const receipt = await tx.wait();

      const avgGasPerTrade = Number(receipt.gasUsed) / BATCH_SIZE;
      console.log(`\n  🚀 BATCH SETTLEMENT (${BATCH_SIZE} cặp lệnh):`);
      console.log(`     - Tổng gas tiêu thụ: ${receipt.gasUsed.toString()} gas`);
      console.log(`     - Gas trung bình / 1 cặp lệnh: ${Math.round(avgGasPerTrade)} gas`);

      // Kiểm chứng yêu cầu phi chức năng NFR-02 (< 85,000 gas/lệnh)
      expect(avgGasPerTrade).to.be.lessThan(85000);
    });
  });
});

