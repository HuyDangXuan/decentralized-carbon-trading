// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title CarbonDoubleAuction
 * @dev Hợp đồng Thanh quyết toán Nguyên tử (Atomic Settlement T+0) cho
 * Sàn đấu giá kép tín chỉ Carbon trên Polygon Amoy.
 *
 * Tính năng Phase 2 - V2:
 * - Xác thực chữ ký EIP-712 Gasless (MetaMask)
 * - 7 Chốt chặn bảo mật bắt buộc (FR-12)
 * - Thanh toán Atomic Swap: MockUSDC (ERC-20) <-> CarbonCredit (ERC-1155)
 * - Batch Settlement gom nhiều cặp lệnh trong 1 TX (FR-11)
 * - Anti-Replay: Nonce per-user + tradeHash dedup
 * - Anti-Wash Trading: bid.trader != ask.trader
 *
 * Đề tài NCKH Sinh viên - Trường Đại học Điện Lực (EPU).
 * Tác giả: Nguyễn Hoàng Đức (Smart Contract Architect)
 * AI Sub-Agent trợ lực: smart-contract-auditor
 * Chuẩn đối soát: FR-11, FR-12, FR-13 trong docs/SRS_DOCUMENT.md
 */
contract CarbonDoubleAuction is EIP712, AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // =====================================================================
    //                          CONSTANTS & ROLES
    // =====================================================================
    bytes32 public constant SETTLEMENT_OPERATOR_ROLE = keccak256("SETTLEMENT_OPERATOR_ROLE");

    bytes32 public constant ORDER_TYPEHASH = keccak256(
        "Order(bytes32 orderId,address trader,uint8 orderType,uint256 tokenId,uint128 amount,uint128 pricePerUnit,uint256 nonce,uint256 deadline)"
    );

    // =====================================================================
    //                          CUSTOM ERRORS
    // =====================================================================
    error SignatureExpired(bytes32 orderId, uint256 deadline, uint256 currentTime);
    error InvalidSignature(bytes32 orderId, address recovered, address expected);
    error PriceMismatch(uint128 bidPrice, uint128 askPrice, uint128 clearingPrice);
    error OrderAmountExceeded(bytes32 orderId, uint128 requested, uint128 remaining);
    error OrderAlreadyCancelledOrFilled(bytes32 orderId);
    error SelfTradingNotAllowed(address trader);
    error TokenIdMismatch(uint256 bidTokenId, uint256 askTokenId);
    error InvalidOrderType(uint8 bidType, uint8 askType);
    error InvalidMatchAmount();
    error TradeAlreadyExecuted(bytes32 tradeHash);
    error PaymentTransferFailed();
    error EmptyBatchArray();
    error ZeroAddressNotAllowed();
    error ContractIsPaused();

    // =====================================================================
    //                          STRUCTS
    // =====================================================================
    struct Order {
        bytes32 orderId;        // Mã hash duy nhất của lệnh
        address trader;         // Địa chỉ ví người ký
        uint8 orderType;        // 0: BID (Mua), 1: ASK (Bán)
        uint256 tokenId;        // Token ID lô tín chỉ ERC-1155
        uint128 amount;         // Số lượng tín chỉ (tCO2e)
        uint128 pricePerUnit;   // Giá tối đa (Bid) / tối thiểu (Ask) tính bằng micro-USDC
        uint256 nonce;          // Nonce chống phát lại
        uint256 deadline;       // Hạn chót hiệu lực (Unix timestamp)
    }

    struct MatchedTrade {
        Order bidOrder;
        Order askOrder;
        bytes bidSignature;     // Chữ ký ECDSA (v, r, s) của Buyer
        bytes askSignature;     // Chữ ký ECDSA (v, r, s) của Seller
        uint128 matchAmount;    // Khối lượng khớp (tCO2e)
        uint128 clearingPrice;  // Giá thanh toán P* (micro-USDC per tCO2e)
    }

    // =====================================================================
    //                          STATE VARIABLES
    // =====================================================================
    /// @dev Hợp đồng Carbon Credit ERC-1155
    IERC1155 public immutable carbonToken;

    /// @dev Hợp đồng token thanh toán MockUSDC (ERC-20, 6 decimals)
    IERC20 public immutable paymentToken;

    /// @dev Nonce chống phát lại cho từng người dùng
    mapping(address => uint256) public userNonces;

    /// @dev Khối lượng đã khớp lũy kế cho mỗi orderId
    mapping(bytes32 => uint128) public filledAmount;

    /// @dev Các lệnh đã bị hủy bởi người dùng
    mapping(bytes32 => bool) public cancelledOrders;

    /// @dev Các giao dịch đã thực hiện (chống nộp trùng - Chốt chặn #7)
    mapping(bytes32 => bool) public executedTrades;

    /// @dev Trạng thái tạm dừng khẩn cấp
    bool public paused;

    /// @dev Bộ đếm tổng số giao dịch đã thanh toán thành công
    uint256 public totalSettledTrades;

    // =====================================================================
    //                              EVENTS
    // =====================================================================
    event TradeSettled(
        bytes32 indexed tradeHash,
        bytes32 indexed bidOrderId,
        bytes32 indexed askOrderId,
        address buyer,
        address seller,
        uint256 tokenId,
        uint128 amount,
        uint128 clearingPrice,
        uint256 totalPayment
    );

    event OrderCancelled(address indexed trader, bytes32 indexed orderId);
    event UserNonceIncremented(address indexed trader, uint256 newNonce);
    event BatchSettlementCompleted(uint256 tradesCount, uint256 successCount);

    // =====================================================================
    //                           CONSTRUCTOR
    // =====================================================================
    /**
     * @param carbonToken_ Địa chỉ hợp đồng CarbonCredit1155
     * @param paymentToken_ Địa chỉ hợp đồng MockUSDC (ERC-20, 6 decimals)
     */
    constructor(
        address carbonToken_,
        address paymentToken_
    ) EIP712("EPU Carbon Double Auction", "2.0") {
        if (carbonToken_ == address(0) || paymentToken_ == address(0)) {
            revert ZeroAddressNotAllowed();
        }

        carbonToken = IERC1155(carbonToken_);
        paymentToken = IERC20(paymentToken_);

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SETTLEMENT_OPERATOR_ROLE, msg.sender);
    }

    // =====================================================================
    //     CORE FUNCTION: SETTLE SINGLE MATCHED TRADE (FR-12 - 7 CHỐT)
    // =====================================================================

    /**
     * @notice Thanh quyết toán nguyên tử một cặp lệnh đã khớp từ auction_agent.py.
     * Thực thi đầy đủ 7 chốt chặn bảo mật theo FR-12 trong SRS_DOCUMENT.md.
     *
     * @param trade Cấu trúc dữ liệu cặp lệnh Bid/Ask kèm chữ ký EIP-712
     */
    function settleMatchedTrade(MatchedTrade calldata trade)
        external
        onlyRole(SETTLEMENT_OPERATOR_ROLE)
        whenNotPaused
        nonReentrant
    {
        _executeSettlement(trade);
    }

    // =====================================================================
    //     CORE FUNCTION: BATCH SETTLE TRADES (FR-11)
    // =====================================================================

    /**
     * @notice Thanh quyết toán hàng loạt nhiều cặp lệnh trong 1 giao dịch (Batch Settlement).
     * Gom 10-20 cặp lệnh vào 1 TX để tiết kiệm gas overhead > 60%.
     *
     * @param trades Mảng các cặp lệnh đã khớp từ phiên đấu giá
     */
    function batchSettleTrades(MatchedTrade[] calldata trades)
        external
        onlyRole(SETTLEMENT_OPERATOR_ROLE)
        whenNotPaused
        nonReentrant
    {
        if (trades.length == 0) revert EmptyBatchArray();

        uint256 successCount = 0;

        for (uint256 i = 0; i < trades.length; i++) {
            // Mỗi trade trong batch được xử lý độc lập
            // Nếu 1 trade lỗi, nó bị bỏ qua, không ảnh hưởng toàn batch
            try this.executeSettlementExternal(trades[i]) {
                successCount++;
            } catch {
                // Giao dịch lỗi bị bỏ qua, tiếp tục xử lý trade tiếp theo
                // (DoS Protection - Chống 1 lệnh lỗi làm tắc toàn batch)
            }
        }

        emit BatchSettlementCompleted(trades.length, successCount);
    }

    /**
     * @dev Hàm internal được gọi qua try/catch trong batchSettleTrades.
     * Phải dùng external để try/catch hoạt động đúng trong Solidity.
     */
    function executeSettlementExternal(MatchedTrade calldata trade) external {
        require(msg.sender == address(this), "Internal only");
        _executeSettlement(trade);
    }

    // =====================================================================
    //     INTERNAL: SETTLEMENT LOGIC VỚI 7 CHỐT CHẶN BẢO MẬT
    // =====================================================================

    function _executeSettlement(MatchedTrade calldata trade) internal {
        Order calldata bid = trade.bidOrder;
        Order calldata ask = trade.askOrder;

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #1: Xác thực chữ ký EIP-712 của CẢ HAI BÊN
        // ═══════════════════════════════════════════════════════════════
        _verifyOrderSignature(bid, trade.bidSignature);
        _verifyOrderSignature(ask, trade.askSignature);

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #2: Kiểm tra thời hạn hiệu lực (Deadline)
        // ═══════════════════════════════════════════════════════════════
        if (block.timestamp > bid.deadline) {
            revert SignatureExpired(bid.orderId, bid.deadline, block.timestamp);
        }
        if (block.timestamp > ask.deadline) {
            revert SignatureExpired(ask.orderId, ask.deadline, block.timestamp);
        }

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #3: Kiểm tra tính hợp thức của cặp lệnh
        // ═══════════════════════════════════════════════════════════════
        // 3a. Cùng tokenId
        if (bid.tokenId != ask.tokenId) {
            revert TokenIdMismatch(bid.tokenId, ask.tokenId);
        }
        // 3b. Đúng loại lệnh: Bid=0, Ask=1
        if (bid.orderType != 0 || ask.orderType != 1) {
            revert InvalidOrderType(bid.orderType, ask.orderType);
        }
        // 3c. Khác địa chỉ ví (chống Wash Trading)
        if (bid.trader == ask.trader) {
            revert SelfTradingNotAllowed(bid.trader);
        }
        // 3d. Khối lượng khớp hợp lệ
        if (trade.matchAmount == 0) {
            revert InvalidMatchAmount();
        }

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #4: Kiểm tra dải giá (ask <= P* <= bid)
        // ═══════════════════════════════════════════════════════════════
        if (trade.clearingPrice < ask.pricePerUnit || trade.clearingPrice > bid.pricePerUnit) {
            revert PriceMismatch(bid.pricePerUnit, ask.pricePerUnit, trade.clearingPrice);
        }

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #5: Kiểm tra hạn mức lũy kế CẢ HAI BÊN
        // ═══════════════════════════════════════════════════════════════
        uint128 bidFilled = filledAmount[bid.orderId];
        uint128 askFilled = filledAmount[ask.orderId];

        if (bidFilled + trade.matchAmount > bid.amount) {
            revert OrderAmountExceeded(bid.orderId, trade.matchAmount, bid.amount - bidFilled);
        }
        if (askFilled + trade.matchAmount > ask.amount) {
            revert OrderAmountExceeded(ask.orderId, trade.matchAmount, ask.amount - askFilled);
        }

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #6: Kiểm tra trạng thái hủy lệnh
        // ═══════════════════════════════════════════════════════════════
        if (cancelledOrders[bid.orderId]) {
            revert OrderAlreadyCancelledOrFilled(bid.orderId);
        }
        if (cancelledOrders[ask.orderId]) {
            revert OrderAlreadyCancelledOrFilled(ask.orderId);
        }

        // ═══════════════════════════════════════════════════════════════
        // CHỐT CHẶN #7: Chống nộp trùng giao dịch (Anti-Replay)
        // Mã băm tất định dựa trên cặp lệnh, khối lượng và giá khớp
        // ═══════════════════════════════════════════════════════════════
        bytes32 tradeHash = keccak256(abi.encodePacked(
            bid.orderId,
            ask.orderId,
            trade.matchAmount,
            trade.clearingPrice
        ));

        if (executedTrades[tradeHash]) {
            revert TradeAlreadyExecuted(tradeHash);
        }

        // ═══════════════════════════════════════════════════════════════
        //           EFFECTS: Cập nhật state TRƯỚC khi chuyển tài sản
        //           (Checks-Effects-Interactions Pattern)
        // ═══════════════════════════════════════════════════════════════
        executedTrades[tradeHash] = true;
        filledAmount[bid.orderId] = bidFilled + trade.matchAmount;
        filledAmount[ask.orderId] = askFilled + trade.matchAmount;
        totalSettledTrades++;

        // ═══════════════════════════════════════════════════════════════
        //           INTERACTIONS: Atomic Swap T+0 (FR-13)
        //           Tiền (MockUSDC) Buyer -> Seller
        //           Tín chỉ (ERC-1155) Seller -> Buyer
        // ═══════════════════════════════════════════════════════════════

        // Tính tổng tiền thanh toán: matchAmount * clearingPrice (micro-USDC)
        uint256 totalPayment = uint256(trade.matchAmount) * uint256(trade.clearingPrice);

        // Chuyển tiền MockUSDC từ Buyer sang Seller
        paymentToken.safeTransferFrom(bid.trader, ask.trader, totalPayment);

        // Chuyển tín chỉ ERC-1155 từ Seller sang Buyer
        carbonToken.safeTransferFrom(ask.trader, bid.trader, bid.tokenId, trade.matchAmount, "");

        emit TradeSettled(
            tradeHash,
            bid.orderId,
            ask.orderId,
            bid.trader,
            ask.trader,
            bid.tokenId,
            trade.matchAmount,
            trade.clearingPrice,
            totalPayment
        );
    }

    // =====================================================================
    //                    EIP-712 SIGNATURE VERIFICATION
    // =====================================================================

    function _verifyOrderSignature(Order calldata order, bytes calldata signature) internal view {
        bytes32 structHash = keccak256(abi.encode(
            ORDER_TYPEHASH,
            order.orderId,
            order.trader,
            order.orderType,
            order.tokenId,
            order.amount,
            order.pricePerUnit,
            order.nonce,
            order.deadline
        ));

        bytes32 digest = _hashTypedDataV4(structHash);
        address recovered = ECDSA.recover(digest, signature);

        if (recovered != order.trader) {
            revert InvalidSignature(order.orderId, recovered, order.trader);
        }

        // Kiểm tra nonce: chỉ chấp nhận nonce >= userNonce hiện tại
        if (order.nonce < userNonces[order.trader]) {
            revert OrderAlreadyCancelledOrFilled(order.orderId);
        }
    }

    // =====================================================================
    //                  ORDER CANCELLATION & NONCE MANAGEMENT
    // =====================================================================

    /**
     * @notice Hủy một lệnh cụ thể (Soft Cancel)
     * @param orderId Mã lệnh cần hủy
     */
    function cancelOrder(bytes32 orderId) external {
        cancelledOrders[orderId] = true;
        emit OrderCancelled(msg.sender, orderId);
    }

    /**
     * @notice Tăng nonce cá nhân để vô hiệu hóa TOÀN BỘ lệnh cũ (Hard Cancel / Emergency Mass Cancel)
     */
    function incrementNonce() external {
        userNonces[msg.sender]++;
        emit UserNonceIncremented(msg.sender, userNonces[msg.sender]);
    }

    // =====================================================================
    //                     ADMIN FUNCTIONS
    // =====================================================================

    modifier whenNotPaused() {
        if (paused) revert ContractIsPaused();
        _;
    }

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        paused = true;
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        paused = false;
    }

    // =====================================================================
    //                         VIEW FUNCTIONS
    // =====================================================================

    /// @notice Kiểm tra khối lượng còn lại chưa khớp của một lệnh
    function getRemainingAmount(bytes32 orderId, uint128 originalAmount)
        external view returns (uint128)
    {
        return originalAmount - filledAmount[orderId];
    }

    /// @notice Trả về EIP-712 Domain Separator (tiện cho Frontend xác minh)
    function getDomainSeparator() external view returns (bytes32) {
        return _domainSeparatorV4();
    }
}
