# CarbonChain frontend

Phần việc Ngô Văn Thắng: metadata và nhóm tín chỉ, giao diện giao dịch, ký EIP-712, kết nối Matching API. Xem [bàn giao và các phụ thuộc tích hợp](../docs/FRONTEND_INTEGRATION.md), [từ điển dữ liệu](../docs/DATA_DICTIONARY.md), [luồng người dùng](../docs/USER_FLOWS.md).

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Các địa chỉ testnet phải lấy từ lần deploy thực. Module ABI đấu giá đang chờ artifact v2 từ Đức; xem hướng dẫn importer trong tài liệu bàn giao. Thiếu ABI hoặc cấu hình thì nút ký bị khóa. API chưa chạy thì giao diện hiển thị trạng thái chưa kết nối, không tự tạo dữ liệu hoặc xác nhận giả.

```powershell
npm test
npm run typecheck
npm run lint
npm run build
```

Không tự merge nhánh vào main sau khi sửa. Những PR trước đã được revert trên main; lần tích hợp tiếp theo cần xử lý việc khôi phục các file đã revert và đối soát contract/API mới trước khi mở PR.
