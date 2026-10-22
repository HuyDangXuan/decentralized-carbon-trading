// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./CarbonCredit1155.sol";

/**
 * @title CarbonDoubleAuction
 * @dev Hợp đồng tiếp nhận kết quả khớp lệnh từ Auction Matching Agent
 * và thực hiện thanh toán, chuyển nhượng tín chỉ Carbon on-chain an toàn.
 */
contract CarbonDoubleAuction {
    CarbonCredit1155 public carbonToken;
    address public matchingAgentAddress;

    struct TradeSettlement {
        bytes32 tradeHash;
        address buyer;
        address seller;
        uint256 tokenId;
        uint256 amount;
        uint256 pricePerUnitWei; // Giá thanh toán theo Wei hoặc Stablecoin
        uint256 settledAt;
    }

    mapping(bytes32 => bool) public executedTrades;
    TradeSettlement[] public settlementHistory;

    event TradeExecuted(
        bytes32 indexed tradeHash,
        address indexed buyer,
        address indexed seller,
        uint256 tokenId,
        uint256 amount,
        uint256 clearingPrice
    );

    modifier onlyMatchingAgent() {
        require(msg.sender == matchingAgentAddress, "Chi Matching Agent moi duoc phep thanh quyet toan");
        _;
    }

    constructor(address _carbonTokenAddress, address _matchingAgent) {
        carbonToken = CarbonCredit1155(_carbonTokenAddress);
        matchingAgentAddress = _matchingAgent;
    }

    function setMatchingAgent(address _newAgent) external {
        require(msg.sender == matchingAgentAddress, "Khong co quyen");
        matchingAgentAddress = _newAgent;
    }

    /**
     * @dev Thanh quyết toán một cặp lệnh đã được Matching Agent khớp ngoài chuỗi.
     * Cần người bán đã gọi `setApprovalForAll` cho hợp đồng này trước đó.
     */
    function settleMatchedTrade(
        bytes32 tradeHash,
        address buyer,
        address seller,
        uint256 tokenId,
        uint256 amount,
        uint256 pricePerUnit
    ) external onlyMatchingAgent {
        require(!executedTrades[tradeHash], "Giao dich da duoc thanh quyet toan truoc do");
        require(buyer != address(0) && seller != address(0), "Dia chi khong hop le");
        require(amount > 0, "So luong phai > 0");

        executedTrades[tradeHash] = true;

        // Chuyển giao tín chỉ carbon từ người bán sang người mua
        carbonToken.safeTransferFrom(seller, buyer, tokenId, amount, "");

        settlementHistory.push(TradeSettlement({
            tradeHash: tradeHash,
            buyer: buyer,
            seller: seller,
            tokenId: tokenId,
            amount: amount,
            pricePerUnitWei: pricePerUnit,
            settledAt: block.timestamp
        }));

        emit TradeExecuted(tradeHash, buyer, seller, tokenId, amount, pricePerUnit);
    }

    function getSettlementCount() external view returns (uint256) {
        return settlementHistory.length;
    }
}
