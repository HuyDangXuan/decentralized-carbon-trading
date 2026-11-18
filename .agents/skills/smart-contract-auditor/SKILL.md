---
name: smart-contract-auditor
description: Chuyên sâu về Solidity, ERC-1155, Polygon Amoy. Tối ưu hóa gas (packed storage, custom errors), thiết kế cơ chế Quỹ dự phòng (Buffer Pool Vault) và audit các lỗ hổng Reentrancy, Front-running, Access Control. Ghép cặp với Nguyễn Hoàng Đức.
---

# Smart Contract Auditor (Hỗ trợ Nguyễn Hoàng Đức)

Kỹ năng này trao quyền cho trợ lý AI Antigravity hỗ trợ bạn **Nguyễn Hoàng Đức** (Smart Contract Engineer) trong việc phát triển, tối ưu hóa gas và kiểm toán bảo mật các hợp đồng thông minh của hệ thống CarbonChain.

## Khi nào kích hoạt kỹ năng này?
- Khi viết mã nguồn Solidity cho `CarbonCredit1155.sol` hoặc `CarbonDoubleAuction.sol`.
- Khi thiết kế cơ chế Buffer Pool Vault và lưu trữ packed storage.
- Khi kiểm toán 7 chốt chặn bảo mật cho hàm `settleMatchedTrade` hoặc `batchSettleTrades`.
- Khi viết unit tests trên Hardhat/Foundry để đo lường lượng gas thực tế.

## 7 Chốt Chặn Bảo Mật Cốt Tử
1. **Xác thực chữ ký EIP-712:** Kiểm tra `_verifyOrderSignature` cho cả bên mua (Bid) và bên bán (Ask).
2. **Kiểm tra Deadline:** Revert nếu `block.timestamp > order.deadline`.
3. **Kiểm tra tính hợp thức của cặp lệnh:** `bidOrder.tokenId == askOrder.tokenId`, `orderType` hợp lệ.
4. **Chống Wash Trading:** Revert nếu `bidOrder.trader == askOrder.trader`.
5. **Kiểm tra dải giá khớp:** `askOrder.pricePerUnit <= clearingPrice <= bidOrder.pricePerUnit`.
6. **Kiểm tra hạn mức filledAmount CẢ HAI PHÍA:**
   - `filledAmount[bidId] + matchAmount <= bidOrder.amount`
   - `filledAmount[askId] + matchAmount <= askOrder.amount`
7. **Kiểm tra trạng thái hủy lệnh và nonces:** Revert nếu lệnh đã bị hủy hoặc nonce không hợp lệ.

## Quy chuẩn Toàn dự án
- Tín chỉ Carbon: $1 \text{ token} = 1 \text{ tCO}_2\text{e}$ (`decimals = 0`).
- Tiền tệ thanh toán: `MockUSDC` với 6 chữ số thập phân (`decimals = 6`), đơn vị trong struct là micro-USDC ($1 \text{ USD} = 10^6 \text{ micro-USDC}$).
- **Nghiêm cấm tuyệt đối sử dụng thuật ngữ `wei USDC`**.
