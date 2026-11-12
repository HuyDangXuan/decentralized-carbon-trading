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

```powershell
npm test
npm run typecheck
npm run lint
npm run build
```

Theo [Task Workflow](../docs/tasks/README.md), gửi PR từ nhánh sprint vào `main` để Đặng Xuân Huy review.
