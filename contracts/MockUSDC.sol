// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title MockUSDC
 * @dev Token ERC-20 giả lập thanh toán Stablecoin trên Testnet Polygon Amoy.
 * Chuẩn 6 chữ số thập phân (decimals = 6) theo chuẩn USDC thực tế.
 * 1 USDC = 1,000,000 micro-USDC (đơn vị nhỏ nhất).
 *
 * Đề tài NCKH Sinh viên - Trường Đại học Điện Lực (EPU).
 * Tác giả: Nguyễn Hoàng Đức (Smart Contract Architect)
 */
contract MockUSDC is ERC20 {
    uint8 private constant _DECIMALS = 6;

    constructor() ERC20("Mock USD Coin", "USDC") {
        // Đúc 10,000,000 USDC (10 triệu) cho deployer để thử nghiệm
        _mint(msg.sender, 10_000_000 * 10 ** _DECIMALS);
    }

    function decimals() public pure override returns (uint8) {
        return _DECIMALS;
    }

    /**
     * @dev Cho phép bất kỳ ai cũng có thể đúc USDC trên Testnet (phục vụ thử nghiệm).
     * @param to Địa chỉ nhận token
     * @param amount Số lượng micro-USDC cần đúc
     */
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

