# Phân Tích Mô Hình Đe Dọa (Threat Modeling)
## Hệ Thống Khớp Lệnh Đấu Giá Kép Ngoài Chuỗi & Thanh Quyết Toán Trên Chuỗi

- **Dự án:** Sàn giao dịch Tín chỉ Carbon Phi tập trung (EPU Carbon Double Auction).
- **Mã tài liệu:** `docs/THREAT_MODELING.md`.
- **Phiên bản:** 1.0 (Bản nháp kỹ thuật Giai đoạn 2).
- **Kiến trúc mục tiêu:** Khớp lệnh định kỳ ngoài chuỗi (Matching Engine Python/FastAPI) kết hợp thanh quyết toán nguyên tử trên chuỗi (Smart Contract `CarbonDoubleAuction.sol`).

---

### 1. Tổng Quan Kiến Trúc & Bề Mặt Tấn Công (Attack Surface)

Hệ thống giao dịch tín chỉ carbon vận hành theo mô hình lai (Hybrid Architecture - Off-chain Matching, On-chain Settlement) nhằm kết hợp ưu thế về thông lượng khớp lệnh cao và tính bảo chứng tài sản của công nghệ chuỗi khối:

```text
+-----------------------+        POST /orders (EIP-712)        +-----------------------------------+
|  Trader (Web3 Client) | -----------------------------------> |  Matching Engine API (FastAPI)    |
+-----------------------+                                      +-----------------------------------+
           |                                                                     |
           | Allowance Approve                                                   | Sổ lệnh RAM & k-DA
           v                                                                     v
+-----------------------+        batchSettleTrades()           +-----------------------------------+
| CarbonDoubleAuction   | <----------------------------------- | Settlement Submitter (Operator)   |
| (Amoy Smart Contract) |                                      +-----------------------------------+
+-----------------------+
   |             |
   | SafeTransfer| SafeTransferFrom
   v             v
[MockUSDC]   [CarbonCredit1155]
```

1. **Phân hệ Ngoài Chuỗi (Off-chain Matching Engine):**
   - **Giao diện API REST & WebSocket:** Cung cấp các endpoint nhận lệnh ký gasless EIP-712 (`api_service.py`, hàm `place_order`), hủy mềm ngoài chuỗi (hàm `cancel_order`), và truyền phát luồng dữ liệu sổ lệnh thời gian thực (hàm `ws_orderbook`).
   - **Cấu trúc dữ liệu lệnh EIP-712 (`contracts/CarbonDoubleAuction.sol:38-40`):**
     `Order(bytes32 orderId, address trader, uint8 orderType, uint256 tokenId, uint128 amount, uint128 pricePerUnit, uint256 nonce, uint256 deadline)`.
   - **Sổ lệnh Bộ nhớ (In-memory OrderBook):** Quản lý tập hợp lệnh Bid và Ask khả dụng (`auction_agent.py:92`), gán số thứ tự đơn điệu `seq` (`auction_agent.py:117`) để chống thao túng thứ tự nộp.
   - **Tác tử Khớp lệnh Định kỳ (Periodic Double Auction Agent):** Vận hành chu kỳ Call Phase theo quyết định kiến trúc tại `docs/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md:31-95` (5 phút trên Testnet Polygon Amoy và 15 phút trên Mainnet). Thuật toán áp dụng quy tắc giá cân bằng đồng nhất toàn phiên $k$-DA (`auction_agent.py:39`, `docs/SRS_DOCUMENT.md:269-279`) kết hợp cơ chế phá hòa đa tiêu chí `age_prorata` và chia phần dư lớn nhất Hamilton (`auction_agent.py:35`, `docs/SRS_DOCUMENT.md:280-291`). Lệnh chưa khớp GTC được chuyển tiếp tối đa 3 phiên (`auction_agent.py:42`).
2. **Phân hệ Trên Chuỗi (On-chain Settlement Contract):**
   - **Hợp đồng `CarbonDoubleAuction.sol`:** Tiếp nhận các lô thanh quyết toán từ ví tác tử nắm giữ quyền độc quyền `SETTLEMENT_OPERATOR_ROLE` (`contracts/CarbonDoubleAuction.sol:36, 163, 182`).
   - **Cơ chế 7 Chốt chặn Bảo mật (7 Security Guards):** Kiểm tra toàn diện chữ ký số EIP-712, hạn chót hiệu lực, tính hợp thức của cặp lệnh, dải giá thanh toán, hạn mức khối lượng lũy kế, trạng thái hủy lệnh và chống nộp trùng giao dịch (`contracts/CarbonDoubleAuction.sol:221-301`).
   - **Hoán đổi Nguyên tử T+0 (Atomic Swap):** Thực hiện chuyển nhượng đồng thời token thanh toán MockUSDC (ERC-20, 6 decimals) từ Buyer sang Seller và tín chỉ carbon CarbonCredit (ERC-1155) từ Seller sang Buyer trong cùng một transaction EVM (`contracts/CarbonDoubleAuction.sol:318-325`).

Bề mặt tấn công (Attack Surface) trải rộng trên cả hai môi trường: giao diện API mở, mempool công khai của mạng Polygon Amoy, tính toàn vẹn của tiến trình Python và khóa riêng tư của ví Submitter.

---

### 2. Phân Tích Bốn Nguy Cơ Đe Dọa Bắt Buộc

#### 2.1. Operator Front-running: Người vận hành chèn lệnh riêng hoặc đổi thứ tự khớp ngoài chuỗi
- **Tài sản bị đe dọa:** Thặng dư kinh tế (economic surplus) của người mua/người bán hợp lệ; quyền ưu tiên khớp lệnh; tài sản MockUSDC và token ERC-1155.
- **Kẻ tấn công và năng lực:** Người vận hành máy chủ Matching Engine (Operator) hoặc kẻ tấn công chiếm quyền điều khiển tiến trình `api_service.py` / `auction_agent.py`. Năng lực: Quan sát toàn bộ sổ lệnh trong Call Phase trước khi đóng sổ (Freeze Phase), tự tạo và ký lệnh riêng, tùy ý thay đổi thứ tự hàng đợi `BookOrder` hoặc loại bỏ lệnh hợp lệ trước khi gọi hàm khớp lệnh.
- **Các bước tấn công cụ thể:**
  1. Operator theo dõi luồng lệnh nộp vào qua endpoint `POST /api/v1/orders` (`system_agents/matching_engine/api_service.py`, hàm `place_order`).
  2. Tại thời điểm sát mốc Freeze Phase, Operator phát hiện cơ hội chênh lệch giá lớn giữa tập Bid và Ask (ví dụ: Bid cao nhất là 15 USDC, Ask thấp nhất là 10 USDC).
  3. Operator sử dụng ví cá nhân tự tạo và ký lệnh Ask với giá 10 USDC để khớp vét toàn bộ thanh khoản của Bid 15 USDC; hoặc chèn một lệnh Bid 14.9 USDC để cướp quyền khớp của trader khác.
  4. Operator can thiệp vào danh sách `BookOrder` nạp vào `match_session` (`system_agents/matching_engine/auction_agent.py:182-195`), tráo đổi thứ tự ưu tiên hoặc gán trường `seq` có lợi cho mình.
  5. Operator kích hoạt `run_periodic_double_auction` (`system_agents/matching_engine/auction_agent.py:175`) và nộp kết quả trục lợi lên blockchain.
- **Hệ quả của việc lệnh là chữ ký EIP-712 gasless non-custodial:**
  + Vì lệnh EIP-712 không yêu cầu khóa tài sản (non-custodial) tại thời điểm nộp lệnh qua API (`api_service.py`, hàm `place_order`), Operator có thể tự do tạo và chèn các lệnh riêng của mình mà không tốn bất kỳ chi phí vốn nào trước phiên khớp.
  + Mặt khác, cấu trúc EIP-712 yêu cầu chữ ký mật mã của cả hai bên đối ứng (`contracts/CarbonDoubleAuction.sol:224-225, 343-367`), do đó Operator **tuyệt đối không thể giả mạo** hay sửa đổi giá (`pricePerUnit`), khối lượng (`amount`), hạn chót (`deadline`) trong lệnh của người dùng hợp lệ. Operator chỉ có thể gian lận ở khâu lựa chọn đưa lệnh nào vào phiên và sắp xếp thứ tự ngoài chuỗi.
- **Điều kiện tiên quyết:** Sổ lệnh được lưu trữ hoàn toàn trong bộ nhớ RAM (`system_agents/matching_engine/auction_agent.py:92`), không có cơ chế công bố băm (hash commitment) hoặc mật mã chứng minh tính toàn vẹn trước khi khớp.
- **Tác động:** Phá vỡ tính công bằng thị trường; nhà giao dịch trung thực bị mất thặng dư hoặc không được khớp lệnh; Operator trục lợi phi rủi ro.
- **Mức độ:** **Cao** (Do Operator nắm toàn quyền kiểm soát quy trình khớp lệnh ngoài chuỗi trong khi smart contract không thể kiểm tra thứ tự nộp lệnh gốc).
- **Biện pháp đã có trong mã:**
  + Xác thực chữ ký EIP-712 của cả Buyer và Seller tại `contracts/CarbonDoubleAuction.sol:224-225` và `343-367`: Operator không thể tự ý sửa đổi tham số lệnh của người dùng.
  + Kiểm tra dải giá hợp lệ tại `contracts/CarbonDoubleAuction.sol:260-262` (`trade.clearingPrice < ask.pricePerUnit || trade.clearingPrice > bid.pricePerUnit`), ngăn Operator ép giá clearing price $P^*$ ra ngoài khoảng giá hai bên đã ký.
  + Chống tự khớp lệnh tại `contracts/CarbonDoubleAuction.sol:249-251` và `system_agents/matching_engine/auction_agent.py:198-201` (`bid.trader != ask.trader`), ngăn Operator dùng 1 ví tự giao dịch tạo volume ảo.
- **Biện pháp đề xuất (chưa có):**
  + Triển khai cơ chế Commit-Reveal sổ lệnh: Trước khi Freeze Phase kết thúc, Engine phải tính mã băm trạng thái sổ lệnh `keccak256(allOrderHashes)` và phát sóng công khai (lên on-chain hoặc P2P network) trước khi công bố kết quả khớp.
  + Cơ chế kiểm toán độc lập (Verifiable Matching): Công bố công khai snapshot sổ lệnh tại thời điểm cutoff để bất kỳ bên thứ ba nào cũng có thể kiểm chứng việc chạy thuật toán $k$-DA và Hamilton.
- **Rủi ro còn lại:** Do lệnh là EIP-712 non-custodial, Operator vẫn có thể âm thầm bỏ qua một lệnh hợp lệ (censorship) mà smart contract không thể phát hiện.
- **Cách kiểm chứng biện pháp:** Viết kịch bản kiểm thử cố tình tráo đổi thứ tự hai lệnh có cùng mức giá hoặc chèn lệnh sai giá, đối soát kết quả khớp lệnh off-chain với quy tắc chuẩn trong `docs/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md`.

---

#### 2.2. MEV Searcher: Chèn giao dịch trước/sau `batchSettleTrades`
- **Tài sản bị đe dọa:** Tính toàn vẹn của lô thanh quyết toán; phí gas của Settlement Submitter; cơ hội thanh toán của trader.
- **Kẻ tấn công và năng lực:** MEV searcher, bot giao dịch trên mạng Polygon Amoy, hoặc node validator mempool. Năng lực: Lắng nghe public mempool, phát hiện giao dịch `batchSettleTrades` đang chờ đóng khối, gửi giao dịch với gas price (priority fee) cao hơn để chen ngang (front-run), kẹp giữa (sandwich) hoặc đi sau (back-run).
- **Các bước tấn công cụ thể:**
  1. Searcher giám sát mempool, phát hiện giao dịch `batchSettleTrades(MatchedTrade[])` từ ví Settlement Submitter (`contracts/CarbonDoubleAuction.sol:180`).
  2. Kịch bản phá hoại (Griefing/Front-run): Một trader thông đồng với searcher thấy giá thị trường biến động bất lợi, lập tức gửi transaction gas cao gọi `cancelOrder` (`contracts/CarbonDoubleAuction.sol:377`) hoặc rút hết tiền MockUSDC/tín chỉ ERC-1155 để đi trước `batchSettleTrades`.
  3. Khi `batchSettleTrades` được thực thi, lệnh của trader đó bị revert.
  4. Nhờ khối `try/catch` tại `contracts/CarbonDoubleAuction.sol:193-198`, hàm `executeSettlementExternal` gặp lỗi sẽ bị bắt lại và bỏ qua im lặng: trade đó thất bại, nhưng các trade khác trong batch vẫn tiếp tục.
  5. Searcher có thể tiếp tục thực hiện giao dịch arbitrage ở các pool DEX bên ngoài (back-run) dựa trên sự thay đổi số dư tín chỉ sau batch settlement.
- **Điều kiện tiên quyết:** Giao dịch `batchSettleTrades` được gửi qua public mempool; tài sản trader không bị khóa ký quỹ trong hợp đồng trước khi thanh toán.
- **Tác động:** Làm lãng phí gas của Submitter; làm hỏng giao dịch của đối tác thiện chí; gây trễ thanh toán cho các cặp lệnh bị ảnh hưởng.
- **Mức độ:** **Trung bình** (Do hợp đồng đã có chốt chặn `SETTLEMENT_OPERATOR_ROLE` ngăn searcher trực tiếp giả mạo batch và `try/catch` ngăn DoS toàn batch).
- **Biện pháp đã có trong mã:**
  + Phân quyền nộp batch độc quyền tại `contracts/CarbonDoubleAuction.sol:182` (`onlyRole(SETTLEMENT_OPERATOR_ROLE)`): Searcher không thể tự nộp giao dịch settlement hoặc thay thế nội dung batch.
  + Cơ chế cách ly lỗi độc lập tại `contracts/CarbonDoubleAuction.sol:193-198`: Sử dụng khối `try this.executeSettlementExternal(trades[i]) catch {}`. Nếu một trade bị cố tình làm lỗi, nó bị bỏ qua im lặng và không làm revert toàn bộ 10-20 trade khác trong batch.
  + Chống nộp trùng giao dịch tại `contracts/CarbonDoubleAuction.sol:298-301`: `executedTrades[tradeHash] = true` ngăn chặn searcher phát lại (replay) giao dịch đã khớp.
- **Biện pháp đề xuất (chưa có):**
  + Định tuyến giao dịch qua kênh Private RPC / Flashbots Protect trên Polygon để ẩn transaction khỏi public mempool.
  + Cơ chế phạt hoặc đưa vào danh sách đen (blacklist) đối với các tài khoản thường xuyên hủy lệnh hoặc rút tiền sau khi đã có kết quả khớp off-chain.
- **Rủi ro còn lại:** Việc `batchSettleTrades` bỏ qua trade lỗi im lặng (`contracts/CarbonDoubleAuction.sol:195-198`) khiến đối tác thiện chí bị treo lệnh mà không có bất kỳ event báo lỗi chi tiết nào trên chuỗi, chỉ phát hiện qua `successCount < trades.length` tại event `BatchSettlementCompleted` (`contracts/CarbonDoubleAuction.sol:201`).
- **Cách kiểm chứng biện pháp:** Giả lập gửi một batch gồm 3 trade trong đó trade thứ 2 có số dư không đủ, kiểm tra xem trade 1 và 3 có thanh toán thành công và trade 2 có bị bỏ qua an toàn hay không.

---

#### 2.3. Rò Rỉ Private Key Ví Settlement Submitter (`SETTLEMENT_OPERATOR_ROLE`)
- **Tài sản bị đe dọa:** Toàn bộ quyền thanh quyết toán trên hợp đồng `CarbonDoubleAuction.sol`; tài sản MockUSDC và CarbonCredit của các trader đã cấp quyền `approve` cho hợp đồng; quỹ gas của ví Submitter.
- **Kẻ tấn công và năng lực:** Hacker tấn công hạ tầng máy chủ backend, trích xuất biến môi trường/file `.env` chứa private key của ví Submitter; hoặc insider biến chất. Năng lực: Nắm giữ private key được cấp quyền `SETTLEMENT_OPERATOR_ROLE` (`contracts/CarbonDoubleAuction.sol:148`).
- **Các bước tấn công cụ thể:**
  1. Kẻ tấn công chiếm đoạt private key của ví Settlement Submitter.
  2. Kẻ tấn công thu thập các chữ ký EIP-712 còn hiệu lực (`deadline` chưa quá hạn) từ cơ sở dữ liệu hoặc nhật ký mạng.
  3. Kẻ tấn công tự cấu tạo các payload `MatchedTrade` độc hại, cố tình ghép các lệnh có lợi cho ví của mình hoặc kích hoạt thanh toán các lệnh mà người dùng đã hủy mềm ngoài chuỗi nhưng chưa hủy trên chuỗi.
  4. Kẻ tấn công trực tiếp gọi `settleMatchedTrade` (`contracts/CarbonDoubleAuction.sol:161`) hoặc `batchSettleTrades` (`contracts/CarbonDoubleAuction.sol:180`) để rút MockUSDC hoặc token của nạn nhân về ví bán chỉ định.
- **Điều kiện tiên quyết:** Private key bị lộ; các trader đã ký lệnh EIP-712 và cấp hạn mức `approve` (hoặc `setApprovalForAll`) cho hợp đồng mà chưa thu hồi.
- **Tác động:** Thất thoát tài sản nghiêm trọng của người dùng; mất uy tín toàn bộ sàn giao dịch; đình trệ hoạt động hệ thống.
- **Mức độ:** **Cao** (Do ví Submitter là điểm tập trung quyền lực on-chain duy nhất được ủy nhiệm thực thi thanh toán).
- **Biện pháp đã có trong mã:**
  + Thực thi nghiêm ngặt 7 chốt chặn bảo mật tại `contracts/CarbonDoubleAuction.sol:221-301`: Kẻ tấn công DÙ CÓ KEY SUBMITTER vẫn không thể tự bịa ra giao dịch nếu không có chữ ký EIP-712 hợp lệ của cả Buyer và Seller (`contracts/CarbonDoubleAuction.sol:224-225`), không thể khớp ngoài dải giá (`contracts/CarbonDoubleAuction.sol:260-262`), và không thể chuyển tiền về ví lạ nếu ví đó không phải là `ask.trader` trong chữ ký gốc (`contracts/CarbonDoubleAuction.sol:321`).
  + Ví Operator không có hàm rút hay chuyển tài sản: hợp đồng không giữ tài sản người dùng (non-custodial) và chỉ chuyển token theo chữ ký đã ký, trong `settleMatchedTrade`/`batchSettleTrades` (`contracts/CarbonDoubleAuction.sol:321, 324`).
  + Cơ chế dừng khẩn cấp tại `contracts/CarbonDoubleAuction.sol:399-405`: Quản trị viên (`DEFAULT_ADMIN_ROLE`) có thể gọi `pause()` để ngắt toàn bộ hàm settlement (`whenNotPaused` tại dòng 164, 183).
- **Biện pháp đề xuất (chưa có):**
  + **Tách quyền (separation of duties):** constructor cấp cả `DEFAULT_ADMIN_ROLE` lẫn `SETTLEMENT_OPERATOR_ROLE` cho ví triển khai (`contracts/CarbonDoubleAuction.sol:147-148`). Ví bot nên là một địa chỉ riêng chỉ giữ `SETTLEMENT_OPERATOR_ROLE`; nếu bot dùng ví deployer thì lộ khóa đồng nghĩa mất cả quyền `pause`, `unpause` và `grantRole`.
  + Lưu trữ private key trong thiết bị phần cứng chuyên dụng (Cloud HSM / AWS KMS) kết hợp IP Whitelisting và giới hạn tốc độ gọi hàm (rate limit).
  + Chuyển quyền `SETTLEMENT_OPERATOR_ROLE` sang mô hình Multi-Party Computation (MPC) hoặc Multi-sig (Gnosis Safe).
  + Thiết lập hạn mức thanh toán tối đa theo ngày (Daily Settlement Volume Cap) trên smart contract.
- **Rủi ro còn lại:** Trong khoảng thời gian từ khi lộ key đến khi Admin phát hiện và kích hoạt `pause()`, kẻ tấn công vẫn có thể khớp các lệnh hợp lệ có sẵn để cưỡng chế chuyển giao tài sản ngoài ý muốn của người dùng.
- **Cách kiểm chứng biện pháp:** Kiểm tra quyền `hasRole(SETTLEMENT_OPERATOR_ROLE, caller)` và thử nghiệm gọi `pause()` từ Admin, sau đó kiểm tra xem hàm `batchSettleTrades` có revert `ContractIsPaused()` hay không.

---

#### 2.4. Spam Lệnh GTC Rác Không Khóa Tài Sản: Tích tuổi lệnh (`age_prorata`) hoặc vét phần dư Hamilton
- **Tài sản bị đe dọa:** Tính công bằng phân bổ thanh khoản; tài nguyên tính toán/bộ nhớ của Matching Engine; tính sẵn sàng của sổ lệnh; cơ hội giao dịch của trader chân chính.
- **Kẻ tấn công và năng lực:** Trader đầu cơ hoặc mạng lưới bot Sybil. Năng lực: Tạo hàng loạt ví Web3 không tốn phí, ký số EIP-712 gasless không giới hạn, nộp lệnh tự do qua API `POST /api/v1/orders`.
- **Các bước tấn công cụ thể:**
  1. Kẻ tấn công tạo hàng chục ví con rác không có số dư MockUSDC hoặc CarbonCredit.
  2. Kẻ tấn công ký và nộp hàng trăm lệnh GTC với khối lượng nhỏ (1 tCO2e) ở các mức giá khác nhau vào `POST /api/v1/orders` (`system_agents/matching_engine/api_service.py`, hàm `place_order`). Do API không kiểm tra số dư on-chain (`system_agents/matching_engine/api_service.py`, mục "Giới hạn của bản mock" ở docstring đầu file), các lệnh này đều được ghi nhận ở trạng thái `NEW`.
  3. Lệnh không khớp trong phiên hiện tại được chuyển tiếp (Rollover) qua các phiên sau, tăng biến đếm thâm niên `rollover_count += 1` (`system_agents/matching_engine/auction_agent.py:188, 215`).
  4. Khi có thanh khoản thật, lệnh ảo gây hại theo hai đường (đã chỉnh sau review Argon, kiểm lại bằng `session_engine._allocate_side`):
     - *Ưu tiên giá (tác động lớn hơn):* lệnh ảo đặt giá tốt hơn giá biên (mua cao, bán thấp) được khớp trọn trước mọi lệnh ở mức biên; khi settlement thất bại thì lệnh thật đối ứng đã khớp với chúng mất cơ hội trong phiên đó. Đường này không cần tích tuổi.
     - *Ưu tiên tuổi (chỉ ở mức giá biên):* `age_prorata` chỉ chạy tại mức giá biên khi khối lượng khả dụng ở mức đó thiếu (`session_engine.py`, nhánh `age_prorata` của `_allocate_side`); nhóm tuổi cao được khớp trọn trước, Hamilton chỉ chia trong nhóm cuối. Lệnh ảo muốn hưởng ưu tiên này phải sống 1-3 phiên mà không bị khớp, rồi đúng tick của nó trở thành giá biên; kẻ tấn công không biết trước tick đó nhưng có thể rải lệnh nhiều tick với chi phí bằng 0.
  5. Đồng thời, việc chẻ nhỏ thành nhiều lệnh 1 tCO2e giúp kẻ tấn công khai thác hai khiếm khuyết toán học của phương pháp Hamilton Largest Remainder (được tài liệu hóa tại `docs/MATCHING_ENGINE_SPEC.md:162-164`):
     - *Hành vi tách lệnh có lợi (Order Splitting):* Nhóm lệnh {A=2, B=1, C=1} với 2 đơn vị khả dụng, A chỉ nhận 1 đơn vị; nếu A tách thành hai lệnh khối lượng 1 có số thứ tự nhỏ hơn B và C thì tổng A nhận trọn 2 đơn vị.
     - *Nghịch lý Alabama (Alabama Paradox):* Nhóm khối lượng (1, 3, 3) được chia (1, 1, 1) khi tổng khả dụng là 3, nhưng bị chia (0, 2, 2) khi tổng khả dụng tăng lên 4 (lệnh nhỏ mất phần khi đối ứng tăng khối lượng).
  6. Nếu giá thị trường biến động bất lợi, kẻ tấn công đơn giản là không nạp tiền/token; khi submit lên chuỗi, trade sẽ bị `catch` im lặng (`contracts/CarbonDoubleAuction.sol:195-198`) mà không tốn bất kỳ chi phí nào.
- **Hệ quả của việc lệnh là chữ ký EIP-712 gasless non-custodial:**
  + Mô hình non-custodial không đòi hỏi trader phải ký quỹ hay chuyển token vào smart contract trước phiên đấu giá. Tài sản chỉ chuyển khi lệnh được thanh toán trên chuỗi (`contracts/CarbonDoubleAuction.sol:321, 324`).
  + Điều này dẫn đến sự mất cân xứng kinh tế: chi phí tạo và spam lệnh rác bằng 0, nhưng chi phí thanh toán on-chain và rủi ro DoS lại dồn lên vai hệ thống sàn và người dùng trung thực.
- **Điều kiện tiên quyết:** Lệnh ký EIP-712 là gasless và non-custodial; API không kiểm tra số dư trước; không có phí đặt/hủy lệnh và không có ngưỡng khối lượng tối thiểu (Min Order Size).
- **Tác động:** Chiếm đoạt thâm niên và khối lượng phân bổ của người dùng thật; làm rác sổ lệnh (OrderBook bloat); tỷ lệ settle thất bại on-chain tăng cao gây lãng phí gas của sàn.
- **Mức độ:** **Cao** (Do chi phí tấn công bằng 0 nhưng trực tiếp thao túng được thuật toán phân bổ cốt lõi của đề tài).
- **Biện pháp đã có trong mã:**
  + Giới hạn số phiên chuyển tiếp tối đa `MAX_ROLLOVER_SESSIONS = 3` tại `system_agents/matching_engine/auction_agent.py:42, 202`: Lệnh GTC chỉ sống tối đa 3 phiên, sau đó bị cưỡng chế sang trạng thái `EXPIRED` (`system_agents/matching_engine/auction_agent.py:49`), hạn chế tích lũy tuổi vô hạn.
  + Kiểm tra hạn chót `deadline` khi tiếp nhận tại `system_agents/matching_engine/api_service.py` (hàm `place_order`) và `system_agents/matching_engine/auction_agent.py:111-112`, kết hợp kiểm tra on-chain tại `contracts/CarbonDoubleAuction.sol:230-235`, ngăn dùng lệnh quá hạn.
  + Sử dụng số thứ tự `seq` do engine gán nội bộ tại `system_agents/matching_engine/auction_agent.py:61, 117` làm tiêu chí phụ phá hòa FIFO thay vì dùng `orderId`, chống việc đào `orderId` nhỏ để hưởng lợi.
- **Biện pháp đề xuất (chưa có):**
  + Áp dụng khối lượng đặt lệnh tối thiểu (Min Order Size, ví dụ $\ge 10$ tCO2e) trên cả API và Smart Contract để tăng chi phí chẻ nhỏ lệnh.
  + Cơ chế Pre-flight Balance Check: API truy vấn số dư và allowance on-chain của ví trước khi chấp nhận nạp lệnh vào OrderBook.
  + Yêu cầu ký quỹ chống spam hoặc áp dụng Rate Limit nghiêm ngặt theo IP và địa chỉ ví trên API Gateway.
- **Rủi ro còn lại:** Kẻ tấn công vẫn có thể dùng bot tự động nộp lại lệnh mới sau mỗi 3 phiên để duy trì độ tuổi tương đối nếu thị trường có thanh khoản mỏng.
- **Cách kiểm chứng biện pháp:** Chạy test suite mô phỏng trong `test_session_engine.py` với hàng loạt lệnh rác 1 đơn vị, kiểm tra xem sau 3 phiên các lệnh này có bị đánh dấu `EXPIRED` đúng quy định hay không.

---

### 3. Phân Tích Hai Đặc Điểm Kỹ Thuật Trọng Yếu Của Kiến Trúc

#### 3.1. Hệ quả của cơ chế `batchSettleTrades` sử dụng try/catch bỏ qua lỗi im lặng
Hàm `batchSettleTrades` trong `contracts/CarbonDoubleAuction.sol:180-202` thực hiện lặp qua mảng các cặp lệnh khớp và gọi hàm `executeSettlementExternal` thông qua khối:
```solidity
// contracts/CarbonDoubleAuction.sol:193-198
try this.executeSettlementExternal(trades[i]) {
    successCount++;
} catch {
    // Giao dịch lỗi bị bỏ qua, tiếp tục xử lý trade tiếp theo
    // (DoS Protection - Chống 1 lệnh lỗi làm tắc toàn batch)
}
```
- **Mặt tích cực (Fault Tolerance / DoS Protection):** Đảm bảo tính sẵn sàng của hệ thống. Nếu một cặp giao dịch trong lô bị lỗi (ví dụ một trader thiếu số dư hoặc đã hủy lệnh), toàn bộ lô 10-20 giao dịch không bị revert, bảo vệ gas và quyền lợi của các trader hợp lệ khác.
- **Mặt tiêu cực & Nguy cơ bảo mật:**
  + **Bỏ qua lỗi im lặng (Silent Failure):** Smart contract hoàn toàn không emit bất kỳ event lỗi chi tiết nào (như lý do revert, tradeIndex bị lỗi, hay địa chỉ ví vi phạm). Event duy nhất được phát là `BatchSettlementCompleted(trades.length, successCount)` (`contracts/CarbonDoubleAuction.sol:201`).
  + **Tạo quyền chọn miễn phí (Free Option Abuse):** Trader có thể nộp lệnh, chờ xem giá khớp off-chain. Nếu thấy bất lợi, trader cố tình rút số dư MockUSDC để giao dịch on-chain thất bại mà không phải chịu bất kỳ chế tài hay phạt gas nào, đẩy toàn bộ rủi ro và chi phí lỡ cơ hội (opportunity cost) cho đối tác.
  + **Gây lệch trạng thái giữa Engine và Contract:** Matching Engine đã đánh dấu lệnh là `FILLED` ngoài chuỗi (`auction_agent.py:213`), nhưng on-chain lại không thanh toán thành công, đòi hỏi cơ chế đồng bộ `confirm_settlement` (`auction_agent.py:134`) phức tạp để tránh ghi nhận sai khối lượng.

#### 3.2. Hệ quả của công thức `tradeHash` không chứa `sessionId`
Công thức băm giao dịch trong `contracts/CarbonDoubleAuction.sol:291-296` được định nghĩa như sau:
```solidity
// contracts/CarbonDoubleAuction.sol:291-296
bytes32 tradeHash = keccak256(abi.encodePacked(
    bid.orderId,
    ask.orderId,
    trade.matchAmount,
    trade.clearingPrice
));
```
- **Thiếu `sessionId` và `fillIndex`:** Mã băm chỉ dựa trên 4 tham số tĩnh của cặp lệnh mà không có mã định danh phiên (`sessionId`) hay số thứ tự lần khớp.
- **Hệ quả gây bế tắc khớp từng phần (Partial Fill Deadlock):**
  + Giả sử một lệnh Bid GTC lớn khớp với một lệnh Ask lớn. Ở phiên 1, hai lệnh khớp 50 tCO2e tại giá 10 USDC. `tradeHash` được tính và ghi nhận `executedTrades[tradeHash] = true` (`contracts/CarbonDoubleAuction.sol:306`).
  + Ở phiên 2, phần dư của hai lệnh này tiếp tục khớp thêm 50 tCO2e nữa tại cùng mức giá 10 USDC.
  + Khi Submitter nộp giao dịch phiên 2, `tradeHash` sinh ra **HOÀN TOÀN TRÙNG KHỚP** với phiên 1.
  + Chốt chặn #7 (`contracts/CarbonDoubleAuction.sol:298-300`) sẽ kiểm tra:
    `if (executedTrades[tradeHash]) revert TradeAlreadyExecuted(tradeHash);`
  + Hậu quả: Giao dịch hợp lệ ở phiên 2 lập tức bị revert! Do nằm trong `batchSettleTrades`, giao dịch này bị catch im lặng và vĩnh viễn không thể thanh toán on-chain dù cả hai bên đều còn đủ hạn mức `filledAmount`.
- **Rủi ro băm packed (`abi.encodePacked`):** Mặc dù các trường hiện tại có kiểu dữ liệu cố định (`bytes32`, `uint128`), việc không dùng `abi.encode` chuẩn EIP-712 domain separator làm giảm khả năng tương thích và an toàn mật mã.

---

### 4. Đối Soát Ba Biện Pháp Kiểm Soát Trọng Yếu

Đối soát sự hiện diện thực tế của ba biện pháp kiểm soát được gợi ý trong hồ sơ nhiệm vụ:

| Biện pháp | Trạng thái trong mã nguồn | Chi tiết vị trí / Căn cứ mã nguồn | Đánh giá & Hướng triển khai |
| :--- | :---: | :--- | :--- |
| **(a) Commit-Reveal / Công bố băm batch** | **KHÔNG CÓ trong mã** | Cả `CarbonDoubleAuction.sol`, `auction_agent.py`, và `api_service.py` đều không có hàm hay biến nào phục vụ commit-reveal mã băm batch. | **Đề xuất triển khai:** Thêm mapping `mapping(uint256 => bytes32) public batchCommits;` trên hợp đồng. Cuối Call Phase, Submitter gọi `commitBatch(sessionId, hash)`. Khi gọi `batchSettleTrades`, contract đối chiếu hash của payload với hash đã commit. |
| **(b) Phân quyền `SETTLEMENT_OPERATOR_ROLE`** | **CÓ** | `contracts/CarbonDoubleAuction.sol:36, 148, 163, 182` | **Đã triển khai:** Khai báo hằng tại dòng 36, gán quyền cho deployer tại dòng 148, áp dụng modifier `onlyRole(SETTLEMENT_OPERATOR_ROLE)` bảo vệ hàm `settleMatchedTrade` (dòng 163) và `batchSettleTrades` (dòng 182). Ngăn chặn bên ngoài nộp batch tùy tiện. |
| **(c) Khối lượng tối thiểu & Biên độ giá Oracle** | **KHÔNG CÓ trong mã** | • `CarbonDoubleAuction.sol:253` chỉ kiểm `matchAmount == 0`<br/>• `auction_agent.py:105` chỉ kiểm `amount > 0`<br/>• `api_service.py` (docstring đầu file) ghi chú: `"Chưa kiểm dải giá Oracle (mã 422)"` | **Đề xuất triển khai:**<br/>1. Thêm constant `MIN_ORDER_AMOUNT = 10` trên contract và API validator.<br/>2. Tích hợp interface Oracle lấy giá $P_{ref}$, kiểm tra điều kiện $0.8 \times P_{ref} \le P^* \le 1.2 \times P_{ref}$ trước khi khớp và khi settle. |

---

### 5. Các Nguy Cơ Khác Tìm Thấy Khi Đọc Mã Nguồn

Qua quá trình rà soát trực tiếp mã nguồn hợp đồng và mã nguồn Python, phát hiện thêm các nguy cơ kỹ thuật cụ thể (5.1-5.4 từ bản nháp, 5.5-5.7 sau review Argon ngày 13/11 và kiểm chứng lại):

#### 5.1. Nguy cơ DoS qua hàm `cancelOrder` không kiểm tra quyền sở hữu (`contracts/CarbonDoubleAuction.sol:377-380`)
- **Vị trí mã nguồn:** `contracts/CarbonDoubleAuction.sol:377-380`:
```solidity
function cancelOrder(bytes32 orderId) external {
    cancelledOrders[orderId] = true;
    emit OrderCancelled(msg.sender, orderId);
}
```
- **Phân tích rủi ro:** Hàm `cancelOrder` nhận tham số `orderId` và đánh dấu `cancelledOrders[orderId] = true` mà **HOÀN TOÀN KHÔNG KIỂM TRA** `msg.sender == order.trader` hay chữ ký của chủ sở hữu lệnh! Bất kỳ ai biết được `orderId` (vốn công khai trên API `GET /api/v1/orders/{orderId}` hoặc WebSocket) đều có thể gọi hàm này để hủy lệnh của nạn nhân trên chuỗi, gây từ chối dịch vụ (Griefing DoS) phá hoại toàn bộ phiên đấu giá.
- **Mức độ:** **Cao về tính sẵn sàng** (không mất tài sản, nhưng chi phí tấn công chỉ là gas và `orderId` công khai qua API). Argon xác nhận phát hiện này (13/11).
- **Biện pháp khắc phục (đã đổi sau review Argon):** hai hướng ở bản nháp đầu đều kém. `mapping(orderId => trader)` không khả thi vì hợp đồng không thấy lệnh trước khi settlement; `cancelOrder(Order, sig)` đổi ABI, tốn calldata và `ecrecover`, và không hủy trước được lệnh chưa ký. Hướng được chọn: gắn người gọi vào khóa hủy, giữ nguyên chữ ký hàm:
```solidity
function cancelOrder(bytes32 orderId) external {
    cancelledOrders[keccak256(abi.encode(msg.sender, orderId))] = true;
    emit OrderCancelled(msg.sender, orderId);
}
// _executeSettlement kiểm: cancelledOrders[keccak256(abi.encode(bid.trader, bid.orderId))] (và ask tương tự)
```
Kẻ tấn công chỉ ghi vào khóa của chính họ nên không ảnh hưởng lệnh của nạn nhân; trader vẫn hủy trước được `orderId` chưa tồn tại. Hệ quả cho bot: hàm `Web3Chain.cancelled` trong `settlement_submitter.py` hiện đọc `cancelledOrders(orderId)` trực tiếp, phải đổi sang đọc theo khóa `keccak256(abi.encode(trader, orderId))` khi hợp đồng được sửa.

#### 5.2. Bế tắc thanh toán do va chạm `tradeHash` khi khớp từng phần (`contracts/CarbonDoubleAuction.sol:291-300`)
- **Vị trí mã nguồn:** `contracts/CarbonDoubleAuction.sol:291-300`.
- **Phân tích rủi ro:** Như đã phân tích tại mục 3.2, do `tradeHash` không chứa `sessionId` hay `fillIndex`, một cặp lệnh GTC khớp từng phần nhiều lần với cùng khối lượng và cùng mức giá sẽ sinh ra mã băm trùng nhau, khiến các lần thanh toán sau bị revert bởi `TradeAlreadyExecuted(tradeHash)`.
- **Biện pháp khắc phục (đã đổi sau review Argon):** bản nháp đầu đề xuất đưa `filledAmount[...]` đọc từ storage vào hàm băm. Phương án đó **sai**: sau khi một trade thành công, `filledAmount` tăng nên bản gửi trùng đúng calldata (retry của Operator) có `tradeHash` khác và còn nằm trong hạn mức, nên khớp lần hai thay vì bị chặn. Mô hình kiểm chứng (`scripts/verify_argon_findings.py`, kết quả dưới):

| Cách | Gửi trùng đúng calldata | Hai phiên hợp lệ cùng amount/giá |
| --- | --- | --- |
| Hiện tại (4 trường) | bị chặn | **lần 2 bị chặn sai** |
| Đọc `filledAmount` từ storage vào hash | **khớp đôi** (30 rồi 60) | khớp được |
| `expectedBidFilled`, `expectedAskFilled` nằm trong calldata, hợp đồng bắt buộc bằng storage, và cùng vào hash | bị chặn | khớp được |

  Hướng được chọn là dòng cuối: thêm hai trường `expectedBidFilled`, `expectedAskFilled` vào `MatchedTrade`, `require` chúng bằng `filledAmount` hiện tại, và đưa chúng vào `tradeHash`. Thay đổi này đổi ABI của struct nên cần Đức đồng ý. Bot phải đổi `compute_trade_hash` và tính trước giá trị `expected*` tuần tự trong batch (cộng dồn các trade đã xếp trước, chỉ tính trade dự kiến thành công).
  Hệ quả còn lại: `tradeHash` phụ thuộc thứ tự trade trong batch và vào việc trade trước có thành công hay không; indexer không nên dùng `tradeHash` làm khóa duy nhất ngoài cặp `(bid, ask, expected*)`.

#### 5.3. Endpoint kích hoạt phiên `POST /api/v1/sessions/run` không có xác thực mặc định (`system_agents/matching_engine/api_service.py` (docstring đầu file, hàm `run_session`, dòng `app = create_app()` ở cuối file))
- **Vị trí mã nguồn:** `system_agents/matching_engine/api_service.py` (docstring đầu file, hàm `run_session`, dòng `app = create_app()` ở cuối file):
```python
# api_service.py, hàm run_session
@app.post("/api/v1/sessions/run")
async def run_session(req: RunSessionRequest, x_api_key: Optional[str] = Header(default=None)) -> dict:
    if admin_key is not None and x_api_key != admin_key:
        raise HTTPException(401, "missing or wrong X-API-Key")
```
- **Phân tích rủi ro:** Khi biến môi trường `MATCHING_API_KEY` không được đặt, `app = create_app(...)` ở cuối `api_service.py` có `admin_key is None` nên khối kiểm tra `x_api_key` bị bỏ qua hoàn toàn. Bất kỳ ai truy cập được service đều gửi được HTTP POST tới `/api/v1/sessions/run` để kích hoạt khớp lệnh tùy tiện, phá vỡ chu kỳ Call Phase 5 phút / 15 phút và làm xáo trộn vòng đời lệnh. (Bản đầu của mục này, viết trước khi có biến `MATCHING_API_KEY`, nêu rằng service luôn mở.)
- **Biện pháp khắc phục:** Service đọc `MATCHING_API_KEY` và bảo vệ ba endpoint quản trị (`/sessions/run`, `/sessions/{id}/trades`, `/settlements/confirm`) bằng header `X-API-Key`; kiểm thử end-to-end (`system_agents/matching_engine/e2e_hardhat/run_e2e.py`) kiểm cả trường hợp thiếu khóa bị từ chối. Còn thiếu: từ chối khởi động ở môi trường production khi biến không được đặt.

#### 5.4. Bất đối xứng trạng thái hủy lệnh: Hủy mềm ngoài chuỗi không vô hiệu hóa chữ ký on-chain (`system_agents/matching_engine/api_service.py` (hàm `cancel_order`))
- **Vị trí mã nguồn:** `system_agents/matching_engine/api_service.py` (hàm `cancel_order`):
```python
# api_service.py, hàm cancel_order
return {
    "orderId": order_id,
    "status": OrderStatus.CANCELLED.value,
    # Hủy ngoài chuỗi chỉ rút lệnh khỏi engine; chữ ký gốc vẫn dùng được on-chain đến hạn này.
    "onchain_valid_until": record.order.deadline,
}
```
- **Phân tích rủi ro:** Khi người dùng gọi API `DELETE /api/v1/orders/{orderId}`, Matching Engine đánh dấu lệnh là `CANCELLED` ngoài chuỗi và trả về `onchain_valid_until: record.order.deadline`. Chữ ký EIP-712 gốc của người dùng vẫn có hiệu lực pháp lý đầy đủ trên smart contract cho đến khi hết `deadline`. Nếu Matching Engine bị xâm nhập hoặc có lỗi đồng bộ, chữ ký này vẫn có thể bị nộp on-chain để thanh toán mà người dùng không thể can thiệp nếu chưa tốn gas gọi `cancelOrder` hoặc `incrementNonce`.
- **Biện pháp khắc phục:** Khuyến cáo người dùng đặt `deadline` ngắn sát với chu kỳ phiên (ví dụ 10-15 phút), hoặc tích hợp cơ chế ủy quyền hủy lệnh tự động lên chuỗi từ phía client.

#### 5.5. Đốt gas qua hook `onERC1155Received` của bên mua (đã kiểm bằng mô phỏng Hardhat)
- **Vị trí mã nguồn:** `contracts/CarbonDoubleAuction.sol:193` (`try this.executeSettlementExternal(trades[i])` không giới hạn gas) và dòng 324 (`carbonToken.safeTransferFrom(..., bid.trader, ...)`, ERC-1155 gọi `onERC1155Received` nếu `bid.trader` có mã).
- **Điều kiện (Argon bỏ sót):** hợp đồng chỉ nhận chữ ký `ECDSA.recover` (dòng 357), không có EIP-1271, nên một hợp đồng thông thường **không thể** là `bid.trader` vì không có khóa riêng. Tấn công chỉ khả thi với EOA được ủy quyền mã theo EIP-7702 (mã ủy quyền có độ dài > 0 nên ERC-1155 vẫn gọi hook), hoặc nếu sau này hợp đồng bổ sung EIP-1271. Mạng Amoy có hỗ trợ 7702 hay không là **UNKNOWN**, mô phỏng dưới dùng Hardhat 2.29.1.
- **Kết quả mô phỏng** (batch 3 trade, mỗi trade 10 tCO2e, một bên mua là EOA ủy quyền mã có hook `while(true){}`):

| Vị trí trade độc hại | Gas limit 0,7M / 1,5M / 3M | Gas limit 10M |
| --- | --- | --- |
| đầu batch | **cả giao dịch hết gas, revert** | thành công nhưng chỉ 2/3 trade, `gasUsed` ≈ 9,89M |
| giữa batch | **cả giao dịch hết gas, revert** (3 mức) | không đo (Hardhat sập vì thiếu RAM trong lần chạy này) |

  Đối chứng: batch 3 trade hợp lệ dùng ≈ 0,50M gas và `estimateGas` ≈ 0,50M. Vậy một trade độc hại biến chi phí 0,5M thành ≈ 9,9M (gấp ≈ 20 lần) hoặc làm cả batch revert, và kẻ tấn công không mất gì (giao dịch do Operator trả).
- **Mức độ:** **Trung bình** (cần 7702; chỉ gây tốn phí và trễ cho Operator và các trade khác trong batch, không mất tài sản). Argon xếp **Cao** và cho rằng không cần giả định thêm; mình không đồng ý ở cả hai điểm.
- **Biện pháp:** (a) *đề xuất, cần sửa hợp đồng:* giới hạn gas cho từng trade: `try this.executeSettlementExternal{gas: MAX_TRADE_GAS}(...)`; (b) *đã làm trong bot (13/11):* kiểm `eth_getCode(bid.trader)` trước khi gửi và đặt `SKIPPED` nếu có mã, trừ khi chạy `--allow-contract-traders`; kiểm thử trên Hardhat bằng `hardhat_setCode` (mục Phiên 3 của `run_e2e.py`); (c) *chưa làm:* khi cho phép bên mua có mã, bot vẫn dùng `estimateGas` x 1,3 nên có thể đặt gas limit rất lớn.

#### 5.6. Rút allowance hoặc đổi trạng thái giữa batch để chọn lọc trade (biến thể của Free Option)
- **Vị trí mã nguồn:** `contracts/CarbonDoubleAuction.sol:321, 324` (không khóa số dư/allowance).
- **Phân tích:** ngoài việc rút allowance để hủy cả lệnh (đã nêu ở mục 3.1), trader có nhiều trade trong cùng batch chỉ để lại số dư vừa đủ cho các trade giá tốt đứng trước, hoặc (với 7702) rút allowance ngay trong hook của trade đầu để các trade sau revert. Hệ quả là các trade bị `catch` nuốt, đối tác thật mất cơ hội, không mất tài sản. Cùng điều kiện 7702 của mục 5.5 cho phần hook; phần rút allowance bằng giao dịch thường thì không cần.
- **Mức độ:** **Trung bình.** Argon xếp Cao; không có thất thoát tài sản nên mình hạ mức.
- **Biện pháp:** *đã làm trong bot (13/11):* kiểm số dư, allowance, tín chỉ và `setApprovalForAll` trước khi gửi, cộng dồn theo từng bên trong batch (`SettlementSubmitter._funds_reject_reason`), nên trader thiếu tiền từ đầu bị `SKIPPED` thay vì làm hỏng trade của đối tác. Đây chỉ là ảnh chụp: trader vẫn rút được giữa lúc kiểm và lúc đào block. *Đề xuất:* ký quỹ/escrow nếu muốn loại hẳn.

#### 5.7. Các điểm đã kiểm và không phải lỗi
- **Làm tròn tại dòng 318:** `totalPayment = matchAmount * clearingPrice` là phép nhân `uint256`, không có phép chia nên không có sai số làm tròn; hai thừa số `uint128` nên tích không tràn `uint256`. Làm tròn giá nếu có chỉ xảy ra ở engine (`ROUNDING = "floor"`). Cả Argon và mình cùng kết luận **không tìm thấy**.
- **Fee-on-transfer và blacklist của token thanh toán** (Argon nêu): không áp dụng cho `MockUSDC` trên testnet; với USDC thật, blacklist chỉ làm trade đó revert (bị `catch`), không mất tài sản. Ghi là giả định khi chuyển lên mainnet.
- **Khẳng định K1-K4** (dải giá, chuyển token chỉ giữa hai `trader` đã ký, `pause()` chặn mọi đường settlement, lỗi một trade không làm revert các trade khác): đã đối chiếu với mã. `_verifyOrderSignature` (dòng 343-367) băm đủ 8 trường của `Order` gồm `trader` và `pricePerUnit`, nên K1 và K2 đúng; câu trả lời "CHƯA CHẮC" của Argon chỉ do đoạn trích bị rút gọn.

---

### 6. Bảng Giả Định Tin Cậy & Ngoài Phạm Vi

#### 6.1. Bảng Giả Định Tin Cậy (Trust Assumptions)

| Thành phần / Thực thể | Vai trò kiến trúc | Mức độ tin cậy giả định | Hệ quả khi giả định bị vi phạm |
| :--- | :--- | :---: | :--- |
| **Trader (Người dùng Web3)** | Ký lệnh EIP-712 mua/bán | **Không tin cậy (Untrusted)** | Được kiểm soát an toàn bởi 7 chốt chặn bảo mật on-chain (`contracts/CarbonDoubleAuction.sol:221-301`). |
| **Matching Engine (Python)** | Gom lệnh, tính $k$-DA & Hamilton | **Bán tin cậy (Semi-trusted)** | Có thể chèn lệnh, đổi thứ tự hoặc DoS; bị kiềm tỏa bởi chữ ký số của trader và dải giá thanh toán. |
| **Settlement Submitter** | Nắm giữ `SETTLEMENT_OPERATOR_ROLE` | **Tin cậy cao (Trusted)** | Nếu bị lộ key, có thể kích hoạt các lệnh cũ còn hạn; được kiềm tỏa bởi hàm `pause()` của Admin. |
| **Smart Contract (EVM)** | Thực thi thanh quyết toán nguyên tử | **Tin cậy tuyệt đối (Root of Trust)** | Mã nguồn bất biến chạy trên Polygon Amoy, đảm bảo tính đúng đắn toán học và an toàn tài sản. |
| **Oracle Agent** | Cung cấp giá tham chiếu $P_{ref}$ | **Bán tin cậy (Semi-trusted)** | Hiện tại chưa được tích hợp trong mã nguồn (`CHƯA XÁC MINH` trong runtime). |

#### 6.2. Bảng Ngoài Phạm Vi Phân Tích (Out of Scope)

| Phân vùng rủi ro ngoài phạm vi | Lý do không thuộc phạm vi tài liệu này | Cơ chế bảo vệ / Đơn vị chịu trách nhiệm |
| :--- | :--- | :--- |
| **Bảo mật thiết bị & Private Key của Trader** | Thuộc trách nhiệm cá nhân của người dùng cuối khi tương tác Web3. | Nhà cung cấp ví (MetaMask, Ledger) và ý thức bảo mật cá nhân. |
| **Lỗi đồng thuận / Reorg / 51% mạng Polygon Amoy** | Thuộc về tầng bảo mật hạ tầng mạng blockchain Layer 1 / Layer 2. | Đội ngũ phát triển Polygon và mạng lưới Validator PoS Amoy. |
| **Gian lận hồ sơ MRV ngoài đời thực** | Gian lận đo đạc phát thải trước khi đúc token ERC-1155. | Đơn vị thẩm tra độc lập (VVB) và quy chuẩn ISO 14064-2 / Verra VCS. |
| **Tấn công từ chối dịch vụ tầng mạng (DDoS Layer 3/4)** | Tấn công làm tràn băng thông mạng Internet vào server FastAPI. | Hạ tầng Cloud, tường lửa WAF, Cloudflare DDoS Protection. |

---
*Tài liệu này là bản nháp kỹ thuật đối soát an ninh phục vụ nghiệm thu Giai đoạn 2 của Đề tài NCKH Sinh viên EPU.*
