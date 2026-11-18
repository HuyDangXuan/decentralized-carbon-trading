# CarbonChain frontend

Phần việc Ngô Văn Thắng: metadata và nhóm tín chỉ, giao diện giao dịch, ký EIP-712, kết nối Matching API. Xem [bàn giao và các phụ thuộc tích hợp](../docs/FRONTEND_INTEGRATION.md), [từ điển dữ liệu](../docs/DATA_DICTIONARY.md), [luồng người dùng](../docs/USER_FLOWS.md).

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

`.env.example` chứa RPC và ba địa chỉ thuộc bản triển khai Polygon Amoy của nhóm. Sau khi kết nối MetaMask trên Amoy (chain ID 80002), bảng điều khiển hiển thị số dư EVCC của token ID được chọn và số dư MockUSDC của ví. Để đối chiếu, đọc `balanceOf(ví, tokenId)` trên EVCC và `balanceOf(ví)` trên MockUSDC. Đổi số dư MockUSDC từ micro-USDC bằng 6 chữ số thập phân.

Nếu đã có `.env.local`, cập nhật riêng `NEXT_PUBLIC_AMOY_RPC_URL` theo `.env.example`. Nếu chính tiện ích MetaMask báo không kết nối được Amoy, có thể chọn RPC đang hoạt động trong phần quản lý mạng của MetaMask. RPC của tiện ích và RPC dùng để đọc số dư trên DApp được cấu hình riêng.

### Đặt lệnh và biểu đồ độ sâu (T.3)

Chạy FastAPI từ thư mục gốc của repo bằng Python 3.12. Cài các dependency của Matching Engine và hỗ trợ WebSocket. Đặt `AUCTION_CONTRACT_ADDRESS` theo địa chỉ `CarbonDoubleAuction` trên Amoy trong [tài liệu bàn giao](../docs/DEPLOYED_ADDRESSES.md).

```powershell
python -m pip install -r system_agents/matching_engine/requirements.txt "uvicorn[standard]==0.54.0"
$env:AUCTION_CONTRACT_ADDRESS = '0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f'
python -m uvicorn --app-dir system_agents/matching_engine api_service:app --host 127.0.0.1 --port 8000
```

Khởi động frontend từ thư mục `frontend`. Next.js chuyển tiếp yêu cầu REST tới `MATCHING_API_URL` trên máy chủ. Trình duyệt dùng `NEXT_PUBLIC_MATCHING_WS_URL` để nhận sổ lệnh qua WebSocket. Cả hai biến có giá trị mẫu trong `.env.example`.

Kết nối MetaMask trên Amoy, nhập lệnh mua hoặc bán và ký EIP-712. FastAPI tiếp nhận lệnh và phát sổ lệnh mới theo mức giá. Kiểm tra thông báo thành công và biểu đồ độ sâu ở tab thứ hai. Bản API hiện tại khớp phiên thủ công. Hợp đồng Amoy xác minh hạn lệnh đã ký và Matching Engine xử lý GTC/IOC ngoài chuỗi. Sai khác với yêu cầu ký `timeInForce` được theo dõi trong [đặc tả Matching Engine](../docs/MATCHING_ENGINE_SPEC.md).

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
