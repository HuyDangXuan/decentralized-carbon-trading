# Mockup CarbonChain · T.4

Bộ thiết kế desktop cho bốn phân hệ CarbonChain, theo [SRS §3.1](../SRS_DOCUMENT.md#31-giao-diện-người-dùng-user-interfaces---web3-dapp) và [luồng người dùng](../USER_FLOWS.md). Các màn hình dùng dữ liệu minh họa. Mỗi ảnh PNG có kích thước 2880 × 2000 px. Các tệp SVG là nguồn vector cùng bố cục ở kích thước 1440 × 1000 px để nhập vào Figma Design.

| Phân hệ | Nội dung | Bản bàn giao |
| --- | --- | --- |
| **Chủ dự án** | Soạn PDD, tải báo cáo MRV lên IPFS, nộp hồ sơ, theo dõi thẩm tra và số tín chỉ sau khi trích quỹ dự phòng. | [PNG](01-project-developer.png) · [SVG](01-project-developer.svg) |
| **Kiểm toán viên VVB** | Hàng đợi hồ sơ, đối chiếu SHA-256 của tệp trên IPFS, kiểm tra vai trò, yêu cầu bổ sung hoặc ký duyệt phát hành. | [PNG](02-verifier-vvb.png) · [SVG](02-verifier-vvb.svg) |
| **Sàn giao dịch** | Đồng hồ phiên, biểu đồ giá khớp k-DA, biểu đồ độ sâu, sổ lệnh mua/bán, đặt lệnh GTC/IOC và lịch sử thanh toán. | [PNG](03-trading-floor.png) · [SVG](03-trading-floor.svg) |
| **Tiêu hủy ESG** | Chọn lô và số lượng, nhập người thụ hưởng và lý do, xác nhận tiêu hủy vĩnh viễn, tải chứng nhận kèm QR. | [PNG](04-esg-retirement.png) · [SVG](04-esg-retirement.svg) |

## Luồng cần đối chiếu khi review

- **Chủ dự án** đi từ bản nháp đến nộp hồ sơ sau khi tệp MRV đã có CID. Số EVCC khả dụng tăng sau khi giao dịch đúc được xác nhận.
- **VVB** chỉ ký duyệt khi quyền hợp lệ và hash tài liệu khớp. Nếu hồ sơ thiếu hoặc sai, dùng hành động yêu cầu bổ sung để trả hồ sơ.
- **Sàn giao dịch** cho thấy bước ký EIP-712 và phân biệt lệnh đang chờ khớp, chờ thanh toán và đã thanh toán. Nút ký cần tạm khóa khi phiên đóng hoặc khi chưa có dữ liệu phiên.
- **ESG** hiển thị lại số lượng, người thụ hưởng và lý do trước khi ký. Chứng nhận xuất hiện sau khi giao dịch tiêu hủy được xác nhận. QR trong mockup dẫn tới [giao dịch benchmark tiêu hủy trên Amoy](https://amoy.polygonscan.com/tx/0x007c649d04977c061b132081743af2a23b0ec55a1af116b8a1064f217b4e128e).

## Bàn giao Figma

**Link Figma có quyền xem cho Huy (Anyone with the link → Can view):** [CarbonChain DApp Mockups - T.4 (Figma Design)](https://www.figma.com/design/L85Og4PIRjZGjrdBQ6zhYb/CarbonChain-DApp-Mockups---T.4?node-id=0-1&p=f&t=6YjgjYTBTElvnSnX-0)

1. ✅ Đã tạo file **Figma Design** (`CarbonChain DApp Mockups - T.4`) và nhập đủ bốn tệp SVG vào canvas thành bốn frame `1440 × 1000 px` (`01-project-developer`, `02-verifier-vvb`, `03-trading-floor`, `04-esg-retirement`), sắp xếp ngang không chồng lấn theo đúng thứ tự bảng trên.
2. ✅ Đã đối chiếu hiển thị chữ tiếng Việt, biểu đồ và mã QR trên canvas Figma khớp với bốn ảnh PNG 2880 × 2000 px.
3. ✅ Đã bật quyền chia sẻ công khai **Anyone with the link → Can view** và đính kèm link vào tài liệu này để Huy kiểm tra mở xem trực tiếp.
