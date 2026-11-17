// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title EvccFaucet
 * @dev Hợp đồng Faucet công khai phân phối tín chỉ Carbon EVCC (ERC-1155) phục vụ thử nghiệm DApp.
 * Hỗ trợ các bên thử nghiệm, GVHD và Hội đồng nghiệm thu nhận 100 tCO2e Lô #101 mà không cần quyền Verifier.
 *
 * Đề tài NCKH Sinh viên - Đại học Điện Lực (EPU).
 * Tác giả: Nguyễn Hoàng Đức (Smart Contract Architect)
 */
contract EvccFaucet is ERC1155Holder, Ownable {
    IERC1155 public immutable carbonCredit;
    uint256 public constant DEFAULT_TOKEN_ID = 101;
    uint256 public constant FAUCET_AMOUNT = 100; // 100 tCO2e

    event FaucetDispensed(address indexed recipient, uint256 tokenId, uint256 amount);

    constructor(address carbonCreditAddress_) Ownable(msg.sender) {
        require(carbonCreditAddress_ != address(0), "Invalid carbon credit address");
        carbonCredit = IERC1155(carbonCreditAddress_);
    }

    /**
     * @dev Hàm nội bộ phân phối tín chỉ từ kho Faucet
     */
    function _dispense(address to, uint256 tokenId, uint256 amount) internal {
        require(to != address(0), "Cannot send to zero address");
        uint256 balance = carbonCredit.balanceOf(address(this), tokenId);
        require(balance >= amount, "Faucet pool depleted");

        carbonCredit.safeTransferFrom(address(this), to, tokenId, amount, "");
        emit FaucetDispensed(to, tokenId, amount);
    }

    /**
     * @notice Nút bấm Faucet trên DApp: Nhận 100 tCO2e Lô #101
     */
    function claim() external {
        _dispense(msg.sender, DEFAULT_TOKEN_ID, FAUCET_AMOUNT);
    }

    /**
     * @notice Alias faucet(): Nhận 100 tCO2e Lô #101
     */
    function faucet() external {
        _dispense(msg.sender, DEFAULT_TOKEN_ID, FAUCET_AMOUNT);
    }

    /**
     * @notice Alias evccFaucet(): Nhận 100 tCO2e Lô #101
     */
    function evccFaucet() external {
        _dispense(msg.sender, DEFAULT_TOKEN_ID, FAUCET_AMOUNT);
    }

    /**
     * @notice Yêu cầu token cho một địa chỉ cụ thể
     */
    function requestTokens(address to) external {
        _dispense(to, DEFAULT_TOKEN_ID, FAUCET_AMOUNT);
    }

    /**
     * @notice Faucet linh hoạt theo tokenId và khối lượng
     */
    function faucetCustom(address to, uint256 tokenId, uint256 amount) external {
        _dispense(to, tokenId, amount);
    }

    /**
     * @notice Rút token về ví Admin nếu cần thu hồi
     */
    function withdraw(uint256 tokenId, uint256 amount) external onlyOwner {
        carbonCredit.safeTransferFrom(address(this), msg.sender, tokenId, amount, "");
    }
}
