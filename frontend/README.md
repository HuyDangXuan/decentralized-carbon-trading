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

Kết nối MetaMask trên Polygon Amoy và mở **Faucet thử nghiệm** ở đầu trang. Ví dùng POL thử nghiệm để trả phí mạng. Nút **Nhận 10.000 MockUSDC** gọi trực tiếp hợp đồng MockUSDC. Nút **Nhận 100 EVCC (#101)** gọi `claim()` trên faucet của nhóm khi tồn kho còn ít nhất 100 EVCC. Bảng số dư cập nhật sau khi blockchain xác nhận.

Sao chép cấu hình trong `.env.example` vào `frontend/.env.local` hoặc thêm `NEXT_PUBLIC_AMOY_EVCC_FAUCET_ADDRESS=0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED` vào tệp cấu hình hiện có. Frontend cũng đọc `NEXT_PUBLIC_EVCC_FAUCET_ADDRESS` từ hướng dẫn bàn giao khi biến trên để trống. Khởi động lại frontend sau khi cập nhật cấu hình. Đức đã nạp 1.000 EVCC #101 vào địa chỉ này. [Giao dịch nạp faucet](https://amoy.polygonscan.com/tx/0xafd2b6c47daa6132902a350f6a9ee3dd100486c2dbf70908cdccd4e086efe17d)

Khi nghiệm thu, ghi lại số dư trước khi bấm từng nút rồi xác nhận qua MetaMask. Đối chiếu mỗi biên nhận và số dư trên UI. Mức tăng cần đạt là 10.000 MockUSDC và 100 EVCC #101. Ghi địa chỉ ví, hai mã giao dịch và số dư trước/sau vào nhật ký T.2.

```powershell
npm test
npm run typecheck
npm run lint
npm run build
```

Theo [Task Workflow](../docs/tasks/README.md), gửi PR từ nhánh sprint vào `main` để Đặng Xuân Huy review.
