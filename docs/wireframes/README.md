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

**Link Figma có quyền xem cho Huy:** chờ nhập bộ thiết kế vào workspace của nhóm.

1. Mở một file **Figma Design** có quyền chỉnh sửa và nhập bốn tệp SVG vào canvas. Tạo bốn frame 1440 × 1000 px, mỗi frame chứa một mockup theo thứ tự của bảng trên. [Hướng dẫn nhập vector trong Figma](https://help.figma.com/hc/en-us/articles/360040027794-Guide-to-imports-in-Figma-Design)
2. Kiểm tra chữ tiếng Việt, biểu đồ và QR sau khi nhập. Dùng các ảnh PNG trong bảng để đối chiếu bố cục và chèn vào báo cáo.
3. Ghi link của file vào mục trên, xác minh Huy có thể xem và cập nhật checklist T.4 sau khi bàn giao.
