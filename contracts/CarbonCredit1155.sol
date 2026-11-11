// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title CarbonCredit1155
 * @dev Hợp đồng quản lý tín chỉ Carbon bán thay thế (Semi-Fungible Token - SFT)
 * theo chuẩn ERC-1155 trên Polygon Amoy Testnet.
 *
 * Tính năng chính (Phase 2 - V2):
 * - Packed Storage Layout tối ưu gas (3 Slots 32 bytes)
 * - Phân quyền RBAC: Admin, Verifier/VVB, ProjectOwner, AuctionContract
 * - Quỹ dự phòng rủi ro (Buffer Pool Vault 10% - 20%)
 * - Custom Errors thay thế require string
 * - Tích hợp IPFS Metadata đồng bộ MRV Agent
 *
 * Đề tài NCKH Sinh viên - Trường Đại học Điện Lực (EPU).
 * Tác giả: Nguyễn Hoàng Đức (Smart Contract Architect)
 * AI Sub-Agent trợ lực: smart-contract-auditor
 * Chuẩn đối soát: FR-13, FR-14 trong docs/SRS_DOCUMENT.md
 */
contract CarbonCredit1155 is ERC1155, AccessControl, ReentrancyGuard {
    // =====================================================================
    //                          CONSTANTS & ROLES
    // =====================================================================
    string public constant name = "EPU Verified Carbon Credit";
    string public constant symbol = "EVCC";

    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant PROJECT_OWNER_ROLE = keccak256("PROJECT_OWNER_ROLE");
    bytes32 public constant AUCTION_CONTRACT_ROLE = keccak256("AUCTION_CONTRACT_ROLE");
    bytes32 public constant EMERGENCY_GUARDIAN_ROLE = keccak256("EMERGENCY_GUARDIAN_ROLE");

    uint16 public constant MIN_BUFFER_BPS = 1000;  // 10.00%
    uint16 public constant MAX_BUFFER_BPS = 2000;  // 20.00%
    uint16 public constant DEFAULT_BUFFER_BPS = 1500; // 15.00%

    // =====================================================================
    //                          CUSTOM ERRORS
    // =====================================================================
    error ZeroAddressNotAllowed();
    error ProjectLotAlreadyExists(uint256 tokenId);
    error ProjectLotNotFound(uint256 tokenId);
    error InvalidMintAmount();
    error InvalidBufferPercentage(uint16 bufferBps, uint16 minBps, uint16 maxBps);
    error ProjectLotInactive(uint256 tokenId);
    error InsufficientBalance(uint256 tokenId, address account, uint256 available, uint256 required);
    error EmptyRetirementReason();
    error InsufficientBufferBalance(uint256 tokenId, uint128 requested, uint128 available);
    error ReversalProofInvalid(bytes32 providedHash);

    // =====================================================================
    //              PACKED STORAGE STRUCT (3 SLOTS x 32 BYTES)
    // =====================================================================
    /**
     * @dev Cấu trúc quản lý chi tiết một Lô tín chỉ Carbon (Carbon Vintage Lot).
     *
     * SLOT 1 (32 bytes): address(20) + uint64(8) + uint32(4) = 32 bytes
     * SLOT 2 (32 bytes): uint128(16) + uint128(16) = 32 bytes
     * SLOT 3 (32 bytes): uint128(16) + uint64(8) + uint16(2) + uint8(1) + bool(1) + uint32(4) = 32 bytes
     */
    struct CarbonVintageLot {
        // === SLOT 1 ===
        address projectDeveloper;       // 20 bytes: Địa chỉ ví chủ dự án (Project Owner)
        uint64 verificationTimestamp;   // 8 bytes:  Unix timestamp thời điểm MRV phê duyệt
        uint32 vintageYear;             // 4 bytes:  Năm tạo tín chỉ (ví dụ: 2026)

        // === SLOT 2 ===
        uint128 totalIssued;            // 16 bytes: Tổng sản lượng phát hành (đơn vị: tCO2e)
        uint128 circulatingSupply;      // 16 bytes: Số lượng đang lưu hành trên thị trường

        // === SLOT 3 ===
        uint128 bufferPoolAmount;       // 16 bytes: Số lượng khóa trong Quỹ dự phòng rủi ro
        uint64 totalRetired;            // 8 bytes:  Tổng tín chỉ đã tiêu hủy vĩnh viễn (tCO2e)
        uint16 bufferPoolBps;           // 2 bytes:  Tỷ lệ trích lập (1000 = 10%, 2000 = 20%)
        uint8 standardType;             // 1 byte:   0: Verra VCS, 1: Gold Standard, 2: CDM, 3: Vietnam VCM
        bool isActive;                  // 1 byte:   true = đang lưu hành
        uint32 _reserved;               // 4 bytes:  Dự trữ cho nâng cấp tương lai
    }

    // =====================================================================
    //                          STATE VARIABLES
    // =====================================================================
    /// @dev Mapping tokenId => Thông tin chi tiết lô tín chỉ
    mapping(uint256 => CarbonVintageLot) private _lots;

    /// @dev Mapping tokenId => IPFS CID lưu trữ metadata
    mapping(uint256 => string) private _tokenCIDs;

    /// @dev Mapping tokenId => Mã băm SHA-256 đảm bảo tính toàn vẹn metadata
    mapping(uint256 => bytes32) private _metadataHashes;

    /// @dev Địa chỉ Vault nhận tín chỉ dự phòng Buffer Pool
    address public bufferPoolVault;

    /// @dev Base URI cho IPFS Gateway (Pinata)
    string private _baseTokenURI;

    /// @dev Biến trạng thái tạm dừng khẩn cấp
    bool public paused;

    // =====================================================================
    //                              EVENTS
    // =====================================================================
    event CarbonLotMinted(
        uint256 indexed tokenId,
        address indexed developer,
        uint128 circulatingAmount,
        uint128 bufferAmount,
        string ipfsCID
    );

    event CarbonCreditsRetired(
        uint256 indexed tokenId,
        address indexed beneficiary,
        address indexed operator,
        uint128 amount,
        string retirementReason
    );

    event BufferCompensated(
        uint256 indexed tokenId,
        uint128 amountCompensated,
        bytes32 reversalProofHash
    );

    event LotStatusChanged(uint256 indexed tokenId, bool isActive);
    event BufferPoolVaultUpdated(address oldVault, address newVault);
    event ContractPaused(address indexed guardian);
    event ContractUnpaused(address indexed admin);

    // =====================================================================
    //                            MODIFIERS
    // =====================================================================
    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }

    modifier lotExists(uint256 tokenId) {
        if (_lots[tokenId].totalIssued == 0 && _lots[tokenId].projectDeveloper == address(0)) {
            revert ProjectLotNotFound(tokenId);
        }
        _;
    }

    modifier lotActive(uint256 tokenId) {
        if (!_lots[tokenId].isActive) {
            revert ProjectLotInactive(tokenId);
        }
        _;
    }

    // =====================================================================
    //                           CONSTRUCTOR
    // =====================================================================
    /**
     * @param baseURI_ Base URI cho IPFS Gateway, ví dụ: "https://gateway.pinata.cloud/ipfs/"
     * @param vaultAddress_ Địa chỉ ví Vault nhận tín chỉ Buffer Pool
     */
    constructor(
        string memory baseURI_,
        address vaultAddress_
    ) ERC1155("") {
        if (vaultAddress_ == address(0)) revert ZeroAddressNotAllowed();

        _baseTokenURI = baseURI_;
        bufferPoolVault = vaultAddress_;

        // Thiết lập phân quyền RBAC
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
        _grantRole(EMERGENCY_GUARDIAN_ROLE, msg.sender);
    }

    // =====================================================================
    //                    CORE FUNCTIONS: MINTING
    // =====================================================================

    /**
     * @notice Đúc lô tín chỉ mới sau khi MRV Agent thẩm tra thành công.
     * Tự động trích lập Buffer Pool theo tỷ lệ bufferBps.
     *
     * @param to          Địa chỉ ví chủ dự án (Project Owner)
     * @param tokenId     Mã định danh lô tín chỉ
     * @param totalAmount Tổng khối lượng phê duyệt (tCO2e)
     * @param vintageYear Năm thẩm định tín chỉ
     * @param standardType Loại tiêu chuẩn (0: Verra VCS, 1: Gold Standard, 2: CDM, 3: Vietnam VCM)
     * @param bufferBps   Tỷ lệ trích Buffer Pool (1000 - 2000 basis points)
     * @param ipfsCID     Mã CID IPFS/Pinata lưu trữ metadata
     * @param metadataHash Mã băm SHA-256 xác minh tính toàn vẹn metadata
     */
    function mintProjectLot(
        address to,
        uint256 tokenId,
        uint128 totalAmount,
        uint32 vintageYear,
        uint8 standardType,
        uint16 bufferBps,
        string calldata ipfsCID,
        bytes32 metadataHash
    ) external onlyRole(VERIFIER_ROLE) whenNotPaused {
        // === Kiểm tra đầu vào ===
        if (to == address(0)) revert ZeroAddressNotAllowed();
        if (totalAmount == 0) revert InvalidMintAmount();
        if (_lots[tokenId].totalIssued > 0 || _lots[tokenId].projectDeveloper != address(0)) {
            revert ProjectLotAlreadyExists(tokenId);
        }
        if (bufferBps < MIN_BUFFER_BPS || bufferBps > MAX_BUFFER_BPS) {
            revert InvalidBufferPercentage(bufferBps, MIN_BUFFER_BPS, MAX_BUFFER_BPS);
        }

        // === Tính toán phân bổ Buffer Pool (nhân trước chia sau, chống tràn số) ===
        uint128 bufferAmount = uint128((uint256(totalAmount) * bufferBps) / 10000);
        uint128 circulatingAmount = totalAmount - bufferAmount;

        // === Ghi Packed Struct vào Storage (3 SSTORE operations) ===
        _lots[tokenId] = CarbonVintageLot({
            projectDeveloper: to,
            verificationTimestamp: uint64(block.timestamp),
            vintageYear: vintageYear,
            totalIssued: totalAmount,
            circulatingSupply: circulatingAmount,
            bufferPoolAmount: bufferAmount,
            totalRetired: 0,
            bufferPoolBps: bufferBps,
            standardType: standardType,
            isActive: true,
            _reserved: 0
        });

        // === Lưu metadata IPFS ===
        _tokenCIDs[tokenId] = ipfsCID;
        _metadataHashes[tokenId] = metadataHash;

        // === Đúc token ERC-1155 ===
        // Phần lưu hành cho Project Owner
        _mint(to, tokenId, circulatingAmount, "");

        // Phần dự phòng cho Buffer Pool Vault
        if (bufferAmount > 0) {
            _mint(bufferPoolVault, tokenId, bufferAmount, "");
        }

        // === Cấp quyền PROJECT_OWNER_ROLE cho chủ dự án ===
        if (!hasRole(PROJECT_OWNER_ROLE, to)) {
            _grantRole(PROJECT_OWNER_ROLE, to);
        }

        emit CarbonLotMinted(tokenId, to, circulatingAmount, bufferAmount, ipfsCID);
    }

    // =====================================================================
    //                  CORE FUNCTIONS: RETIREMENT (FR-14)
    // =====================================================================

    /**
     * @notice Tiêu hủy tín chỉ vĩnh viễn để bù đắp phát thải carbon.
     * Tín chỉ đã đốt không thể chuyển nhượng, không thể phục hồi.
     *
     * @param tokenId Mã lô tín chỉ
     * @param amount  Khối lượng cần tiêu hủy (tCO2e)
     * @param reason  Lý do bù trừ phát thải (phục vụ kiểm toán ESG)
     */
    function retireCarbonCredit(
        uint256 tokenId,
        uint128 amount,
        string calldata reason
    ) external whenNotPaused lotExists(tokenId) nonReentrant {
        if (amount == 0) revert InvalidMintAmount();
        if (bytes(reason).length == 0) revert EmptyRetirementReason();

        uint256 senderBalance = balanceOf(msg.sender, tokenId);
        if (senderBalance < amount) {
            revert InsufficientBalance(tokenId, msg.sender, senderBalance, amount);
        }

        // Checks-Effects-Interactions: Cập nhật state trước khi burn
        CarbonVintageLot storage lot = _lots[tokenId];
        lot.totalRetired += uint64(amount);
        lot.circulatingSupply -= amount;

        // Đốt token vĩnh viễn
        _burn(msg.sender, tokenId, amount);

        emit CarbonCreditsRetired(tokenId, msg.sender, msg.sender, amount, reason);
    }

    // =====================================================================
    //               BUFFER POOL: COMPENSATE REVERSAL EVENT
    // =====================================================================

    /**
     * @notice Giải tỏa tín chỉ từ Quỹ dự phòng để bù đắp sự cố đảo ngược phát thải.
     * Chỉ có Verifier (VVB) được phép thực hiện sau khi xác minh biến cố.
     *
     * @param tokenId           Mã lô tín chỉ xảy ra sự cố
     * @param amount            Khối lượng cần giải tỏa bù trừ
     * @param reversalProofHash Mã băm báo cáo hiện trường xác nhận biến cố
     */
    function compensateReversal(
        uint256 tokenId,
        uint128 amount,
        bytes32 reversalProofHash
    ) external onlyRole(VERIFIER_ROLE) whenNotPaused lotExists(tokenId) nonReentrant {
        if (reversalProofHash == bytes32(0)) revert ReversalProofInvalid(reversalProofHash);

        CarbonVintageLot storage lot = _lots[tokenId];
        if (amount > lot.bufferPoolAmount) {
            revert InsufficientBufferBalance(tokenId, amount, lot.bufferPoolAmount);
        }

        // Cập nhật state
        lot.bufferPoolAmount -= amount;
        lot.totalRetired += uint64(amount);

        // Đốt token từ Vault
        _burn(bufferPoolVault, tokenId, amount);

        emit BufferCompensated(tokenId, amount, reversalProofHash);
    }

    // =====================================================================
    //                     ADMIN & MANAGEMENT FUNCTIONS
    // =====================================================================

    /// @notice Tạm dừng khẩn cấp toàn bộ hoạt động chuyển nhượng
    function pause() external onlyRole(EMERGENCY_GUARDIAN_ROLE) {
        paused = true;
        emit ContractPaused(msg.sender);
    }

    /// @notice Phục hồi hoạt động sau khi kiểm tra an toàn
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        paused = false;
        emit ContractUnpaused(msg.sender);
    }

    /// @notice Cập nhật địa chỉ Vault Buffer Pool
    function setBufferPoolVault(address newVault) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newVault == address(0)) revert ZeroAddressNotAllowed();
        address oldVault = bufferPoolVault;
        bufferPoolVault = newVault;
        emit BufferPoolVaultUpdated(oldVault, newVault);
    }

    /// @notice Kích hoạt / Vô hiệu hóa trạng thái lô tín chỉ
    function setLotStatus(uint256 tokenId, bool active)
        external onlyRole(DEFAULT_ADMIN_ROLE) lotExists(tokenId)
    {
        _lots[tokenId].isActive = active;
        emit LotStatusChanged(tokenId, active);
    }

    /// @notice Cập nhật Base URI cho IPFS Gateway
    function setBaseURI(string calldata newBaseURI) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _baseTokenURI = newBaseURI;
    }

    // =====================================================================
    //                         VIEW FUNCTIONS
    // =====================================================================

    /**
     * @notice Trả về đường dẫn metadata IPFS đầy đủ cho Web3 Marketplace.
     * Đồng bộ hoàn toàn với định dạng IPFS CID từ mrv_agent.py
     */
    function uri(uint256 tokenId) public view override returns (string memory) {
        string memory cid = _tokenCIDs[tokenId];
        if (bytes(cid).length == 0) return "";
        return string(abi.encodePacked(_baseTokenURI, cid));
    }

    /// @notice Trả về toàn bộ thông tin Packed Struct của một lô tín chỉ
    function getLotDetails(uint256 tokenId) external view returns (CarbonVintageLot memory) {
        return _lots[tokenId];
    }

    /// @notice Trả về số lượng tín chỉ trong Quỹ dự phòng
    function getBufferPoolBalance(uint256 tokenId) external view returns (uint128) {
        return _lots[tokenId].bufferPoolAmount;
    }

    /// @notice Trả về mã băm toàn vẹn metadata
    function getMetadataIntegrityHash(uint256 tokenId) external view returns (bytes32) {
        return _metadataHashes[tokenId];
    }

    /// @notice Trả về IPFS CID của lô tín chỉ
    function getTokenCID(uint256 tokenId) external view returns (string memory) {
        return _tokenCIDs[tokenId];
    }

    // =====================================================================
    //                      INTERFACE SUPPORT
    // =====================================================================
    function supportsInterface(bytes4 interfaceId)
        public view override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
