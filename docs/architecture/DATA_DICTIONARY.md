# Từ điển dữ liệu metadata CarbonChain

Áp dụng cho `METADATA_SCHEMA.json` v2. Các ràng buộc liên trường được kiểm tra bằng `scripts/validate_metadata.py`; kiểm tra JSON Schema đơn thuần chưa đủ để nghiệm thu metadata. Quy ước của giao thức là tCO2e nguyên, USDC 6 decimals và buffer 10–20%, không phải tuyên bố về mọi tiêu chuẩn carbon bên ngoài.

## Các trường dữ liệu

| Đường dẫn | Kiểu | Bắt buộc | Ràng buộc | Ý nghĩa |
|---|---|---|---|---|
| name | string | Có | Theo schema | Tên hiển thị của lô tín chỉ. Định dạng: 'Carbon Credit - {project_name} ({vintage_year})'. |
| description | string | Có | Theo schema | Mô tả ngắn gọn về tín chỉ, bao gồm tiêu chuẩn áp dụng. |
| image | string | Có | pattern="^ipfs://" | URI ảnh đại diện dự án trên IPFS (CID v1 hoặc v0). |
| decimals | integer | Có | const=0 | Cố định 0: một token là một tCO2e nguyên. |
| unit | string | Có | const="tCO2e" | Đơn vị tín chỉ thống nhất toàn dự án. |
| price_unit | string | Có | const="USDC" | Ký hiệu tiền định giá; token thanh toán testnet là MockUSDC. |
| price_decimals | integer | Có | const=6 | Một USDC bằng 1.000.000 micro-USDC. |
| properties.project_id | string | Có | pattern="^[A-Z]{2,3}-[A-Z]{2,5}-[0-9]{4}-[0-9]{3,6}$\|^VCS-[0-9]+$\|^GS-[0-9]+$" | Mã định danh duy nhất của dự án. Tuân thủ quy ước: {QUỐC GIA}-{LOẠI}-{NĂM}-{SỐ THỨ TỰ}. Ví dụ Verra: 'VCS-1234', Gold Standard: 'GS-5678'. |
| properties.standard | string | Có | enum=["Verra VCS", "Verra VCS + CCB", "Verra VCS + SD VISta", "Gold Standard VER", "Gold Standard CER", "CDM", "Vietnam VCM", "Article 6.4"] | Tiêu chuẩn chứng nhận tín chỉ carbon áp dụng. |
| properties.methodology | string | Có | Theo schema | Phương pháp luận tính toán giảm phát thải (Methodology). Verra: VM0007, VM0015, VM0042… Gold Standard: GS-METH-001… |
| properties.project_type | string | Tùy chọn | enum=["FORESTRY_AFOLU", "RENEWABLE_ENERGY", "ENERGY_EFFICIENCY", "COOKSTOVE", "WASTE_MANAGEMENT", "TRANSPORT", "INDUSTRIAL_GAS", "BLUE_CARBON", "AGRICULTURE", "OTHER"] | Phân loại lĩnh vực dự án theo Verra Sectoral Scope hoặc Gold Standard Project Type. |
| properties.asset_class | string | Có | enum=["forestry", "renewable_energy", "waste_treatment", "energy_efficiency", "cookstove", "blue_carbon", "agriculture", "transport", "industrial_gas", "other"] | Phân loại để lọc và đánh giá tương đương; không tự cấp quyền khớp chéo tokenId. |
| properties.standard_category | string | Có | enum=["Verra_VCS", "Gold_Standard", "CDM", "Vietnam_VCM", "Article_6_4"] | Danh mục tiêu chuẩn rút gọn dùng cho phân nhóm fungibility. Ánh xạ từ trường 'standard' sang nhóm đơn giản hơn để engine giao dịch ghép lệnh. |
| properties.vintage_window | object | Có | Theo schema | Cửa sổ năm vintage, bao gồm hai đầu. Bộ kiểm tra nghiệp vụ xác minh start_year <= vintage_year <= end_year. |
| properties.vintage_window.start_year | integer | Có | minimum=2000; maximum=2100 | Năm bắt đầu cửa sổ vintage (bao gồm). |
| properties.vintage_window.end_year | integer | Có | minimum=2000; maximum=2100 | Năm kết thúc cửa sổ vintage (bao gồm). Phải >= start_year. |
| properties.is_fungible_pool | boolean | Có | Theo schema | Cờ khai báo lô đủ điều kiện tham gia nhóm phân loại. Khớp chéo tokenId còn phụ thuộc phê duyệt và khả năng của Engine/contract; frontend hiện gửi đúng một tokenId. |
| properties.vintage_year | integer | Có | minimum=2000; maximum=2100 | Năm vintage – năm mà lượng giảm phát thải thực sự xảy ra (không phải năm phát hành). |
| properties.vintage_period | object | Tùy chọn | Theo schema | Khoảng thời gian giám sát cụ thể của đợt vintage (Monitoring Period). |
| properties.vintage_period.start_date | string | Có | Theo schema | Ngày bắt đầu chu kỳ giám sát (ISO 8601). |
| properties.vintage_period.end_date | string | Có | Theo schema | Ngày kết thúc chu kỳ giám sát (ISO 8601). |
| properties.total_issued_tCO2e | integer | Có | minimum=1; maximum=340282366920938463463374607431768211455 | Tổng số tín chỉ carbon được phê duyệt phát hành trong đợt này (đơn vị: tấn CO2 tương đương – tCO2e). |
| properties.serial_number_range | object | Tùy chọn | Theo schema | Dải số serial theo quy định Verra Registry hoặc Gold Standard Impact Registry. |
| properties.serial_number_range.start | string | Có | Theo schema | Số serial bắt đầu. |
| properties.serial_number_range.end | string | Có | Theo schema | Số serial kết thúc. |
| properties.country | string | Có | pattern="^[A-Z]{2}$" | Mã quốc gia nơi dự án triển khai (ISO 3166-1 alpha-2). |
| properties.region | string | Có | Theo schema | Khu vực / tỉnh thành cụ thể nơi dự án triển khai. |
| properties.coordinates | object | Tùy chọn | Theo schema | Tọa độ GPS trung tâm vùng dự án. |
| properties.coordinates.latitude | number | Có | minimum=-90; maximum=90 |  |
| properties.coordinates.longitude | number | Có | minimum=-180; maximum=180 |  |
| properties.developer | string | Có | Theo schema | Địa chỉ ví Ethereum (hoặc tên tổ chức) của chủ dự án / bên phát triển. |
| properties.developer_name | string | Tùy chọn | Theo schema | Tên đầy đủ tổ chức phát triển dự án. |
| properties.verifier | string | Có | Theo schema | Tên đơn vị thẩm tra/kiểm định (VVB – Validation/Verification Body) hoặc ID tác tử tự động. |
| properties.verification_body_id | string | Tùy chọn | Theo schema | Mã định danh VVB trên registry (nếu có). |
| properties.verified_at | integer | Có | minimum=0 | Unix timestamp (giây) thời điểm MRV Agent hoàn tất thẩm tra. Tương thích với trường verified_at trong MRVVerificationAgent. |
| properties.verification_report_uri | string | Tùy chọn | pattern="^ipfs://" | URI trỏ tới bản báo cáo thẩm tra đầy đủ lưu trên IPFS. |
| properties.status | string | Có | enum=["PENDING_VERIFICATION", "VERIFIED_ACTIVE", "LISTED_FOR_SALE", "PARTIALLY_RETIRED", "FULLY_RETIRED", "SUSPENDED", "CANCELLED"] | Trạng thái hiện tại của lô tín chỉ trên hệ thống CarbonChain. |
| properties.retirement_details | object | Khi đã retire một phần/toàn bộ | Theo schema | Thông tin tiêu hủy (chỉ có khi status là PARTIALLY_RETIRED hoặc FULLY_RETIRED). Tương thích với RetirementComplianceAgent. |
| properties.retirement_details.retired_amount_tCO2e | integer | Tùy chọn | minimum=0 | Số lượng tín chỉ đã tiêu hủy vĩnh viễn. |
| properties.retirement_details.beneficiary_company | string | Tùy chọn | Theo schema | Tên doanh nghiệp hưởng thụ quyền bù đắp. |
| properties.retirement_details.retirement_reason | string | Tùy chọn | Theo schema | Lý do / mục đích tiêu hủy tín chỉ. |
| properties.retirement_details.retirement_timestamp | integer | Tùy chọn | Theo schema | Unix timestamp thời điểm tiêu hủy. |
| properties.retirement_details.certificate_hash | string | Tùy chọn | pattern="^0x[a-fA-F0-9]{64}$" | Mã hash SHA-256 chứng nhận ESG bất biến trên blockchain. |
| properties.sdg_contributions | array | Gold Standard | Theo schema | Danh sách các Mục tiêu Phát triển Bền vững (SDGs) mà dự án đóng góp. Bắt buộc với Gold Standard, khuyến nghị với Verra VCS + SD VISta. |
| properties.sdg_contributions[].sdg_number | integer | Có | minimum=1; maximum=17 | Số thứ tự SDG (1-17). |
| properties.sdg_contributions[].sdg_name | string | Tùy chọn | Theo schema | Tên SDG. |
| properties.sdg_contributions[].contribution_description | string | Tùy chọn | Theo schema | Mô tả ngắn gọn đóng góp cụ thể. |
| properties.additionality | string | Có | enum=["PROVEN", "CONDITIONAL", "NOT_ASSESSED"] | Kết quả đánh giá tính bổ sung (Additionality Assessment) – dự án chỉ khả thi nhờ cơ chế tín chỉ carbon. |
| properties.permanence_risk_buffer | number | Có | minimum=10; maximum=20 | Tỷ lệ trích lập của giao thức CarbonChain, đơn vị phần trăm; 10–20%. Chuyển sang basis points bằng nhân 100, không làm tròn ngầm. |
| properties.corresponding_adjustment | boolean | Tùy chọn | Theo schema | Đánh dấu tín chỉ đã được điều chỉnh tương ứng (Corresponding Adjustment) theo Điều 6 Thỏa thuận Paris, tránh double counting giữa các quốc gia. |
| properties.fungibility_group_id | string | Khi is_fungible_pool=true | pattern="^[a-z_]+_[0-9]{4}-[0-9]{4}_[A-Za-z_]+$" | Mã nhóm duy nhất: {asset_class}_{start_year}-{end_year}_{standard_category}; mọi lô trong nhóm phải có cùng cửa sổ và tiêu chuẩn. |
| properties.content_hash | string | Tùy chọn | pattern="^0x[a-fA-F0-9]{64}$" | Mã hash SHA-256 của toàn bộ metadata JSON (trước khi thêm trường này). Dùng để xác minh tính toàn vẹn on-chain. Sinh bởi MRVVerificationAgent. |

## Quy tắc nghiệp vụ

- `start_year <= vintage_year <= end_year`; năm vintage là năm giảm phát thải, không phải năm mint.
- `standard_category` phải suy ra đúng từ `standard`; giữ tên đầy đủ tiêu chuẩn trong `standard`, tên chuẩn hóa trong `standard_category`.
- Nếu có `project_type`, nó phải khớp `asset_class` theo bảng ánh xạ trong validator; ví dụ FORESTRY_AFOLU tương ứng forestry.
- Mã nhóm: `{asset_class}_{start_year}-{end_year}_{standard_category}`. Chỉ phân loại eligibility; không tự bật khớp chéo tokenId.
- Buffer lưu theo phần trăm, tối đa hai số lẻ; nhân 100 sang số nguyên basis points. Ví dụ 15% = 1500 bps. Lượng buffer = floor(totalIssued × bps / 10000), phần khả dụng = totalIssued − buffer.
- Gold Standard cần ít nhất một SDG; không được lặp số SDG. Verra có thể không gửi danh sách này.
- Khối lượng đã retire không vượt tổng phát hành. FULLY_RETIRED yêu cầu bằng tổng phát hành; PARTIALLY_RETIRED yêu cầu lớn hơn 0 và nhỏ hơn tổng.
- `content_hash` tùy chọn là bằng chứng do producer sinh; bộ kiểm tra hiện xác minh định dạng, không thay thế bước xác thực hash/tài liệu của VVB.
- Timestamp là Unix giây; URI hồ sơ/ảnh là ipfs://. Trường chưa có dữ liệu không được điền hash/CID giả để coi là đã xác thực.

## Chuyển từ schema cũ

Không còn trường `fungibility_pool_id`. Producer dùng `fungibility_group_id` và object `vintage_window` duy nhất. Bỏ cách mã hóa cửa sổ bằng chuỗi và ID nhóm chỉ có một năm. Phải bổ sung các trường bắt buộc trước khi gửi metadata v2; output MRV baseline cũ chưa tự tương thích.

Ví dụ đã đối soát nằm trong `docs/examples/`. Backend hoặc công cụ upload cần chạy cả validator JSON Schema và các quy tắc nghiệp vụ trước khi pin IPFS.

Các mẫu là dữ liệu minh họa offline, không phải bằng chứng dự án đã được registry chứng nhận hoặc hồ sơ đã được pin. Bộ kiểm tra URI hiện chỉ kiểm tra định dạng URI/prefix, không xác nhận CID tồn tại hay nội dung tài liệu IPFS.
