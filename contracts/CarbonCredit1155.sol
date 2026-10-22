// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CarbonCredit1155
 * @dev Hợp đồng thông minh quản lý tín chỉ Carbon theo tiêu chuẩn ERC-1155.
 * Mỗi token ID đại diện cho một đợt phát hành tín chỉ (Project ID + Vintage Year).
 * Đề tài NCKH Sinh viên - Trường Đại học Điện Lực.
 */

interface IERC1155Receiver {
    function onERC1155Received(address operator, address from, uint256 id, uint256 value, bytes calldata data) external returns (bytes4);
    function onERC1155BatchReceived(address operator, address from, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external returns (bytes4);
}

contract CarbonCredit1155 {
    string public name = "EPU Verified Carbon Credit";
    string public symbol = "EVCC";
    address public admin;

    // Mapping: tokenId => (userAddress => balance)
    mapping(uint256 => mapping(address => uint256)) private _balances;
    // Mapping: userAddress => (operatorAddress => isApproved)
    mapping(address => mapping(address => bool)) private _operatorApprovals;
    // Mapping: tokenId => IPFS metadata URI
    mapping(uint256 => string) private _tokenURIs;
    // Mapping: tokenId => total retired credits (đã tiêu hủy vĩnh viễn)
    mapping(uint256 => uint256) public totalRetired;
    // Mapping: tokenId => total minted
    mapping(uint256 => uint256) public totalSupply;

    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);
    event URI(string value, uint256 indexed id);
    event CarbonRetired(address indexed burner, uint256 indexed id, uint256 amount, string reason);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Chi danh cho quan tri vien");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function balanceOf(address account, uint256 id) public view returns (uint256) {
        require(account != address(0), "Dia chi khong hop le");
        return _balances[id][account];
    }

    function setApprovalForAll(address operator, bool approved) public {
        require(msg.sender != operator, "Khong the tu uy quyen cho chinh minh");
        _operatorApprovals[msg.sender][operator] = approved;
    }

    function isApprovedForAll(address account, address operator) public view returns (bool) {
        return _operatorApprovals[account][operator];
    }

    function uri(uint256 id) public view returns (string memory) {
        return _tokenURIs[id];
    }

    /**
     * @dev Đúc tín chỉ carbon mới sau khi đã được MRV Verification Agent thẩm định.
     */
    function mintCarbonCredit(
        address to,
        uint256 id,
        uint256 amount,
        string memory ipfsMetadataURI
    ) external onlyAdmin {
        require(to != address(0), "Dia chi nhan khong hop le");
        require(amount > 0, "So luong phai lon hon 0");

        _balances[id][to] += amount;
        totalSupply[id] += amount;
        _tokenURIs[id] = ipfsMetadataURI;

        emit TransferSingle(msg.sender, address(0), to, id, amount);
        emit URI(ipfsMetadataURI, id);
    }

    /**
     * @dev Chuyển giao tín chỉ carbon giữa các bên (hoặc do sàn đấu giá chuyển giao).
     */
    function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public {
        require(from == msg.sender || isApprovedForAll(from, msg.sender), "Chua duoc cap quyen chuyen nhuong");
        require(to != address(0), "Dia chi nhan khong hop le");
        require(_balances[id][from] >= amount, "So du tin chi khong du");

        _balances[id][from] -= amount;
        _balances[id][to] += amount;

        emit TransferSingle(msg.sender, from, to, id, amount);
    }

    /**
     * @dev Hủy vĩnh viễn tín chỉ để bù đắp phát thải (Retirement / Burning).
     * Ngăn chặn hoàn toàn rủi ro tiêu xài hai lần (Double Spending).
     */
    function retireCarbonCredit(
        uint256 id,
        uint256 amount,
        string memory reason
    ) external {
        require(_balances[id][msg.sender] >= amount, "So du khong du de huy");
        
        _balances[id][msg.sender] -= amount;
        totalRetired[id] += amount;

        emit TransferSingle(msg.sender, msg.sender, address(0), id, amount);
        emit CarbonRetired(msg.sender, id, amount, reason);
    }
}
