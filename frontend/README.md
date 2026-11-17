# CarbonChain frontend

Phần việc Ngô Văn Thắng: metadata và nhóm tín chỉ, giao diện giao dịch, ký EIP-712, kết nối Matching API. Xem [bàn giao và các phụ thuộc tích hợp](../docs/FRONTEND_INTEGRATION.md), [từ điển dữ liệu](../docs/DATA_DICTIONARY.md), [luồng người dùng](../docs/USER_FLOWS.md).

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

`.env.example` chứa RPC và ba địa chỉ thuộc bản triển khai Polygon Amoy của nhóm. Sau khi kết nối MetaMask trên Amoy (chain ID 80002), bảng điều khiển hiển thị số dư EVCC của token ID được chọn và số dư MockUSDC của ví. Để đối chiếu, đọc `balanceOf(ví, tokenId)` trên EVCC và `balanceOf(ví)` trên MockUSDC. Đổi số dư MockUSDC từ micro-USDC bằng 6 chữ số thập phân.

Nếu đã có `.env.local`, cập nhật riêng `NEXT_PUBLIC_AMOY_RPC_URL` theo `.env.example`. Nếu chính tiện ích MetaMask báo không kết nối được Amoy, có thể chọn RPC đang hoạt động trong phần quản lý mạng của MetaMask. RPC của tiện ích và RPC dùng để đọc số dư trên DApp được cấu hình riêng.

Module ABI đấu giá cần artifact tương thích trước khi bật chức năng ký lệnh. Xem hướng dẫn importer trong tài liệu bàn giao.

### Faucet thử nghiệm (T.2)

Kết nối MetaMask trên Polygon Amoy và mở **Faucet thử nghiệm** ở đầu trang. Ví dùng POL thử nghiệm để trả phí mạng. Nút **Nhận 10.000 MockUSDC** gọi trực tiếp hợp đồng MockUSDC. Nút **Nhận 100 EVCC (#101)** lấy tín chỉ đã được đúc từ faucet và mỗi ví nhận một lần. Bảng số dư cập nhật sau khi blockchain xác nhận.

Để bật nút EVCC trên bản triển khai của nhóm:

1. Lô #101 đã có trên CarbonCredit1155 Amoy `0x851978601b47a61B8aF3bcC1707B689Fbc977697`. Ví giữ lô của Đức `0x6Ea660D087C90c8ff915E2646a5A282a53Cd8694` nhận 8.500 EVCC lưu hành và 1.500 EVCC dự phòng. [Giao dịch tạo lô](https://amoy.polygonscan.com/tx/0xc4eeb089df2de6643690c658c3c41cc4d524189b86d38cd13524b77064fd159b)
2. Từ thư mục gốc, người giữ lô cấu hình `AMOY_RPC_URL` và `PRIVATE_KEY` của ví Amoy trong môi trường Hardhat cục bộ. Chạy lệnh dưới đây để triển khai và nạp 300 EVCC lưu hành, đủ cho ba lượt thử. Nếu faucet đã triển khai, đặt thêm `AMOY_EVCC_FAUCET_ADDRESS` bằng địa chỉ đã in ra và chạy lại để bổ sung phần còn thiếu tới 300. Script kiểm tra hợp đồng, lô và số dư dự phòng trước khi nạp.

   ```powershell
   $env:AMOY_CARBON_CREDIT_ADDRESS = '0x851978601b47a61B8aF3bcC1707B689Fbc977697'
   $env:AMOY_EVCC_FAUCET_TARGET_BALANCE = '300'
   npx hardhat run scripts/deploy_evcc_faucet.js --network amoy
   ```

3. Đặt địa chỉ được in ra vào `NEXT_PUBLIC_AMOY_EVCC_FAUCET_ADDRESS` trong `frontend/.env.local`, rồi khởi động lại frontend. Ghi số dư trước khi nhận. Kết nối MetaMask bằng ví thử có POL, mở faucet và xác nhận từng giao dịch. UI và blockchain phải cùng tăng 10.000 MockUSDC và 100 EVCC #101. Mở lại modal để xác nhận nút EVCC báo ví đã nhận. Ghi lại địa chỉ thử, hai mã giao dịch và số dư trước/sau vào nhật ký T.2.

```powershell
npm test
npm run typecheck
npm run lint
npm run build
```

Theo [Task Workflow](../docs/tasks/README.md), gửi PR từ nhánh sprint vào `main` để Đặng Xuân Huy review.
