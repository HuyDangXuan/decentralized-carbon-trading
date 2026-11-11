# Luồng người dùng CarbonChain

Tài liệu thiết kế phần giao diện của Ngô Văn Thắng. Trading Floor có mã triển khai; các cổng chủ dự án, VVB và ESG dưới đây là luồng thiết kế để đối soát trước khi dựng wireframe, chưa phải chức năng đã nghiệm thu.

## Chủ dự án và kiểm toán viên

```mermaid
flowchart LR
    A[Chủ dự án kết nối ví] --> B[Nhập thông tin dự án và hồ sơ MRV]
    B --> C[Kiểm tra schema và quy tắc nghiệp vụ]
    C --> D[Lưu hồ sơ IPFS qua dịch vụ MRV]
    D --> E[VVB xem hồ sơ và kiểm tra tính toàn vẹn]
    E --> F{Phê duyệt?}
    F -->|Không| G[Trả lý do và yêu cầu sửa]
    G --> B
    F -->|Có| H[Ký giao dịch mint sau khi kiểm tra quyền]
    H --> I[Trích buffer 10–20 phần trăm]
    I --> J[Hiển thị tín chỉ khả dụng và transaction hash]
```

Form dự án thu thập tên, vintage, vị trí, methodology, additionality, tiêu chuẩn và tỷ lệ buffer; SDGs bắt buộc cho Gold Standard. Dữ liệu không hợp lệ phải được sửa trước khi gửi. Xác nhận thành công chỉ sau khi dịch vụ lưu và giao dịch mint thực được xác nhận.

## Sàn giao dịch

```mermaid
flowchart TD
    A[Xem sổ lệnh theo tokenId] --> B[Kết nối ví và chọn mạng]
    B --> C[Chọn mua hoặc bán, số nguyên tCO2e, giá USDC, GTC hoặc IOC]
    C --> D[Kiểm tra cấu hình, số liệu phiên và dữ liệu nhập]
    D --> E[Đọc nonce và kiểm tra hợp đồng thực]
    E --> F[Ký EIP-712 trên ví]
    F --> G[Kiểm tra phiên vẫn còn nhận lệnh]
    G --> H[Gửi POST orders]
    H --> I[API xác nhận tiếp nhận]
    I --> J[Theo dõi ACTIVE và kết quả khớp]
    J --> K{Còn khối lượng?}
    K -->|IOC| L[CANCELLED phần dư]
    K -->|GTC dưới 3 phiên| M[ROLLED_OVER]
    M --> J
    K -->|GTC đạt 3 phiên| N[EXPIRED]
    J --> O[Phần khớp chờ settlement]
    O --> P{Blockchain xác nhận?}
    P -->|Có| Q[SETTLED_FINAL]
    P -->|Thất bại| R[Hiển thị lỗi và chờ dịch vụ xử lý]
```

Không tự gửi lại POST khi mất kết nối. Nếu chưa có ABI hoặc API, hiển thị lý do chưa sẵn sàng. Đơn vị giao diện là USDC/tCO2e, payload giá là micro-USDC. Cấp quyền ERC-20/ERC-1155 là điều kiện settlement riêng, có thể cần gas; việc ký lệnh không chuyển tài sản.

## Bù đắp phát thải ESG

```mermaid
flowchart LR
    A[Chọn token đang sở hữu] --> B[Nhập số nguyên cần hủy và người hưởng lợi]
    B --> C[Hiển thị lý do và tác động không thể chuyển lại tín chỉ]
    C --> D[Người dùng xác nhận giao dịch trên ví]
    D --> E[Chờ receipt và sự kiện retirement]
    E --> F[Hiển thị chứng nhận và QR tra cứu giao dịch]
```

Chứng nhận chỉ sinh từ bằng chứng retirement được xác nhận; lỗi hoặc giao dịch bị từ chối không được hiển thị là đã hủy thành công.
