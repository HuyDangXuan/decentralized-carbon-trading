---
name: fullstack-web3-engineer
description: Chuyên sâu về Web3 DApp & Giao diện người dùng. Hỗ trợ xây dựng giao diện Next.js, kết nối ví MetaMask qua Ethers.js/Viem, chuẩn hóa Metadata JSON Schema cho IPFS Pinata. Ghép cặp với Ngô Văn Thắng.
---

# Fullstack Web3 Engineer (Hỗ trợ Ngô Văn Thắng)

Kỹ năng này trao quyền cho trợ lý AI Antigravity hỗ trợ bạn **Ngô Văn Thắng** (Fullstack Web3 Engineer) trong việc phát triển ứng dụng phi tập trung DApp, tích hợp ví Web3 và kết nối với hệ thống Matching Engine.

## Khi nào kích hoạt kỹ năng này?
- Khi xây dựng giao diện DApp sàn giao dịch tín chỉ carbon bằng Next.js 14, TailwindCSS.
- Khi cấu hình kết nối ví MetaMask thông qua Wagmi v2 và Viem (`useWalletConnection`).
- Khi lập trình hook ký lệnh EIP-712 Typed Data Gasless (`useEIP712Order`).
- Khi kết nối REST API và WebSocket Client với Matching Engine (`matchingApi.ts`).
- Khi chuẩn hóa lược đồ dữ liệu `docs/METADATA_SCHEMA.json` theo chuẩn Verra VCS và Gold Standard.

## Các Hạng Mục Kỹ Thuật Đã Triển Khai
1. **Metadata JSON Schema:** Bổ sung các trường gom nhóm thanh khoản (*Credit Fungibility*): `asset_class`, `standard_category`, `vintage_window`, `is_fungible_pool`, `fungibility_pool_id`.
2. **Ký lệnh EIP-712 Gasless:** Người dùng ký thông điệp ngoài chuỗi qua MetaMask, không tốn gas khi đặt lệnh hoặc hủy lệnh.
3. **Module API Service:** Gửi lệnh qua `POST /api/v1/orders`, nhận Depth Chart real-time qua `WS /ws/orderbook/{tokenId}`.
4. **Hiển thị Số Dư & Thông Tin Lô:** Đọc dữ liệu từ `CarbonCredit1155.sol` và metadata IPFS hiển thị trên card trực quan.
