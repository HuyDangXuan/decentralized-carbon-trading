# 📜 ĐỊA CHỈ HỢP ĐỒNG THÔNG MINH TRÊN POLYGON AMOY TESTNET
## HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON PHI TẬP TRUNG (GIAI ĐOẠN 2 - V2.0)

- **Mạng Blockchain:** Polygon Amoy Testnet
- **Chain ID:** `80002` (Hex: `0x13882`)
- **Đồng tiền phí Gas (Native Token):** POL (Polygon Ecosystem Token)
- **RPC URL:** `https://poly-amoy-testnet.api.pocket.network` *(hoặc `https://polygon-amoy.drpc.org`)*
- **Block Explorer:** [PolygonScan Amoy](https://amoy.polygonscan.com)
- **Người triển khai (Deployer / Admin):** `0x6Ea660D087C90c8ff915E2646a5A282a53Cd8694`
- **Thời điểm triển khai:** 12/11/2026 (Hoàn thành vượt tiến độ Sprint)
- **Tác giả:** Nguyễn Hoàng Đức (*Smart Contract Architect*)

---

## 1. BẢNG ĐỊA CHỈ HỢP ĐỒNG CHÍNH THỨC (OFFICIAL CONTRACT ADDRESSES)

| Tên Hợp đồng | Chuẩn Kỹ thuật | Địa chỉ Contract (Amoy Testnet) | Link Tra cứu PolygonScan |
| :--- | :---: | :---: | :---: |
| **`MockUSDC`** | ERC-20 (6 decimals) | `0xe35681b0882d533458d22B344268642136ebD813` | [Xem trên PolygonScan](https://amoy.polygonscan.com/address/0xe35681b0882d533458d22B344268642136ebD813) |
| **`CarbonCredit1155`** | ERC-1155 (Packed 3-slots, 15% Buffer) | `0x851978601b47a61B8aF3bcC1707B689Fbc977697` | [Xem trên PolygonScan](https://amoy.polygonscan.com/address/0x851978601b47a61B8aF3bcC1707B689Fbc977697) |
| **`CarbonDoubleAuction`**| EIP-712 Atomic Swap T+0 | `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f` | [Xem trên PolygonScan](https://amoy.polygonscan.com/address/0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f) |

---

## 2. THÔNG TIN CẤU HÌNH LIÊN KẾT HỢP ĐỒNG (ON-CHAIN RBAC WIRING)

* **`AUCTION_CONTRACT_ROLE`:** Đã được cấp quyền tự động cho hợp đồng `CarbonDoubleAuction` (`0x6Ee8...c46f`) trên hợp đồng `CarbonCredit1155` (`0x8519...7697`).
* **Vault Quỹ dự phòng rủi ro (Buffer Pool Vault):** Đang trích lập tự động $15\%$ số lượng đúc chuyển vào địa chỉ Vault của Admin (`0x6Ea66...d8694`).
* **Tiền tệ thanh toán:** `MockUSDC` với tỷ giá $1\text{ USDC} = 1,000,000\text{ micro-USDC}$ (6 decimals).

---

## 3. HƯỚNG DẪN BÀN GIAO CHO CÁC THÀNH VIÊN TRONG NHÓM

### 3.1 Dành cho bạn Ngô Văn Thắng (Web3 Frontend Engineer)
1. **Import ABI:** Sử dụng các file ABI chuẩn đã xuất tại thư mục:
   * [`contracts/abis/CarbonCredit1155.json`](contracts/abis/CarbonCredit1155.json)
   * [`contracts/abis/CarbonDoubleAuction.json`](contracts/abis/CarbonDoubleAuction.json)
   * [`contracts/abis/MockUSDC.json`](contracts/abis/MockUSDC.json)
   * Hoặc import TypeScript: `import { CarbonDoubleAuctionABI, CarbonCredit1155ABI, MockUSDCABI } from '@/contracts/abis';`
2. **Cấu hình Địa chỉ Contract trong `.env.local` Frontend:**
   ```env
   NEXT_PUBLIC_CHAIN_ID=80002
   NEXT_PUBLIC_RPC_URL=https://poly-amoy-testnet.api.pocket.network
   NEXT_PUBLIC_MOCK_USDC_ADDRESS=0xe35681b0882d533458d22B344268642136ebD813
   NEXT_PUBLIC_CARBON_CREDIT_ADDRESS=0x851978601b47a61B8aF3bcC1707B689Fbc977697
   NEXT_PUBLIC_AUCTION_ADDRESS=0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f
   ```
3. **EIP-712 Domain Separator Frontend:**
   ```javascript
   const domain = {
     name: "EPU Carbon Double Auction",
     version: "2.0",
     chainId: 80002,
     verifyingContract: "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f"
   };
   ```

### 3.2 Dành cho bạn Nguyễn Bảo Phi (Auction Matching & Submitter Bot)
1. **Cấu hình bot thanh toán on-chain:** Bot nộp kết quả khớp lệnh gọi hàm `batchSettleTrades` vào hợp đồng `0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f`.
2. **Quyền hạn:** Để ví bot của Phi có thể gọi hàm settlement, Đức đã cấp sẵn quyền `SETTLEMENT_OPERATOR_ROLE` cho deployer và có thể cấp thêm cho địa chỉ ví bot của Phi khi Phi gửi địa chỉ ví.

---

*Tài liệu được sinh tự động và cam kết tính xác thực bởi Nguyễn Hoàng Đức – Smart Contract Architect.*

