// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import {ERC1155Holder} from "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";

/// @notice Distributes existing demo credits without granting permission to mint project lots.
contract EvccFaucet is ERC1155Holder {
    uint256 public constant TOKEN_ID = 101;
    uint256 public constant CLAIM_AMOUNT = 100;

    IERC1155 public immutable credit;
    mapping(address => bool) public hasClaimed;

    error InvalidCreditContract();
    error UnsupportedDeposit();
    error AlreadyClaimed();
    error InsufficientInventory();

    event CreditsClaimed(address indexed recipient, uint256 amount);

    constructor(IERC1155 credit_) {
        if (
            address(credit_).code.length == 0 ||
            !credit_.supportsInterface(type(IERC1155).interfaceId)
        ) revert InvalidCreditContract();
        credit = credit_;
    }

    function claimStatus(address recipient) external view returns (bool claimed, bool funded) {
        return (hasClaimed[recipient], credit.balanceOf(address(this), TOKEN_ID) >= CLAIM_AMOUNT);
    }

    function claim() external {
        if (hasClaimed[msg.sender]) revert AlreadyClaimed();
        if (credit.balanceOf(address(this), TOKEN_ID) < CLAIM_AMOUNT) revert InsufficientInventory();

        hasClaimed[msg.sender] = true;
        credit.safeTransferFrom(address(this), msg.sender, TOKEN_ID, CLAIM_AMOUNT, "");
        emit CreditsClaimed(msg.sender, CLAIM_AMOUNT);
    }

    function onERC1155Received(
        address,
        address,
        uint256 id,
        uint256,
        bytes memory
    ) public view override returns (bytes4) {
        if (msg.sender != address(credit) || id != TOKEN_ID) revert UnsupportedDeposit();
        return this.onERC1155Received.selector;
    }

    function onERC1155BatchReceived(
        address,
        address,
        uint256[] memory,
        uint256[] memory,
        bytes memory
    ) public pure override returns (bytes4) {
        revert UnsupportedDeposit();
    }
}
