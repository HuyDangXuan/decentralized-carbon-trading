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

1. Người có `VERIFIER_ROLE` tạo lô thử #101 (Rừng Tây Bắc, vintage 2026) trên hợp đồng EVCC đã bàn giao, với metadata của lô và đủ tín chỉ lưu hành để cấp thử. Nếu lô đã tồn tại, dùng số dư của chủ lô.
2. Người triển khai faucet cấu hình `AMOY_RPC_URL`, `PRIVATE_KEY` của ví triển khai testnet và `AMOY_CARBON_CREDIT_ADDRESS` trong môi trường Hardhat. Từ thư mục gốc, chạy `npx hardhat run scripts/deploy_evcc_faucet.js --network amoy`.
3. Chủ số dư chuyển tín chỉ #101 vào địa chỉ faucet bằng `safeTransferFrom`. Mỗi lượt nhận cần 100 tín chỉ lưu hành, sau phần trích quỹ dự phòng của lô.
4. Đặt địa chỉ được in ra vào `NEXT_PUBLIC_AMOY_EVCC_FAUCET_ADDRESS` trong `frontend/.env.local`, khởi động lại frontend, rồi xác nhận hai giao dịch từ một ví thử có POL. So sánh số dư trên UI với biên nhận và số dư blockchain sau mỗi lần nhận.

```powershell
npm test
npm run typecheck
npm run lint
npm run build
```

Theo [Task Workflow](../docs/tasks/README.md), gửi PR từ nhánh sprint vào `main` để Đặng Xuân Huy review.
