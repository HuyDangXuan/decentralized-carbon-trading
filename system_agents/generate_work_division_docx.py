import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import sys
import os

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_work_division_docx(output_path):
    doc = docx.Document()

    # Set page margins (Standard academic: Left 3cm, Right 2cm, Top 2cm, Bottom 2cm)
    for section in doc.sections:
        section.top_margin = Inches(0.79)     # ~2cm
        section.bottom_margin = Inches(0.79)  # ~2cm
        section.left_margin = Inches(1.18)    # ~3cm
        section.right_margin = Inches(0.79)   # ~2cm

    # Colors
    NAVY = RGBColor(16, 44, 87)       # #102C57
    STEEL = RGBColor(53, 89, 142)     # #35598E
    DARK_GRAY = RGBColor(50, 50, 50)
    BLACK = RGBColor(0, 0, 0)

    # 1. Header (School & Department)
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    run_inst1 = p_inst.add_run("TRƯỜNG ĐẠI HỌC ĐIỆN LỰC\n")
    run_inst1.font.name = "Times New Roman"
    run_inst1.font.size = Pt(12)
    run_inst1.font.bold = True
    run_inst1.font.color.rgb = NAVY

    run_inst2 = p_inst.add_run("KHOA ĐIỆN TOÁN VÀ CÔNG NGHỆ SỐ NĂNG LƯỢNG\n")
    run_inst2.font.name = "Times New Roman"
    run_inst2.font.size = Pt(12)
    run_inst2.font.bold = True
    run_inst2.font.color.rgb = STEEL

    run_div = p_inst.add_run("-------------------- *** --------------------\n")
    run_div.font.name = "Times New Roman"
    run_div.font.size = Pt(10)
    run_div.font.color.rgb = RGBColor(150, 150, 150)

    # 2. Main Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("BẢNG PHÂN CÔNG NHIỆM VỤ VÀ KẾ HOẠCH TRIỂN KHAI\n")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(15)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY

    run_sub = p_title.add_run("GIAI ĐOẠN 2: PHÂN TÍCH YÊU CẦU VÀ THIẾT KẾ CHI TIẾT HỆ THỐNG\n(Thời gian thực hiện: Từ tháng 11/2026 đến tháng 01/2027)")
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = STEEL

    # 3. Project Details Block
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_before = Pt(8)
    p_info.paragraph_format.space_after = Pt(12)
    p_info.paragraph_format.line_spacing = 1.2

    runs_info = [
        ("Tên đề tài: ", True),
        ("HỆ THỐNG GIAO DỊCH TÍN CHỈ CARBON MINH BẠCH VÀ HIỆU QUẢ TRÊN NỀN TẢNG BLOCKCHAIN\n", False),
        ("Giảng viên hướng dẫn: ", True),
        ("TS. Nguyễn Thị Hồng Khánh (Bộ môn Hệ thống thông tin - Khoa CNS)\n", False),
        ("Chủ nhiệm đề tài: ", True),
        ("Sinh viên Đặng Xuân Huy – Lớp D18CNPM1 (MSV: 23810310007)\n", False),
        ("Nhóm nghiên cứu tham gia: ", True),
        ("Ngô Văn Thắng (23810310401), Nguyễn Hoàng Đức (23810310060), Nguyễn Bảo Phi (23810310017)\n", False),
        ("Mã nguồn dự án (GitHub): ", True),
        ("https://github.com/HuyDangXuan/decentralized-carbon-trading.git", False)
    ]
    for text, bold in runs_info:
        r = p_info.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = bold
        if bold:
            r.font.color.rgb = NAVY

    # Heading 1 helper
    def add_sec_heading(title_text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        run = h.add_run(title_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return h

    # Section 1
    add_sec_heading("I. MỤC TIÊU VÀ SẢN PHẨM BÀN GIAO GIAI ĐOẠN 2")
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_after = Pt(6)
    p_sec1.paragraph_format.line_spacing = 1.2
    r_sec1 = p_sec1.add_run(
        "Kế thừa kết quả nghiên cứu tổng quan và lựa chọn nền tảng từ Giai đoạn 1 (mạng Polygon Amoy, chuẩn ERC-1155, "
        "lưu trữ IPFS Pinata và cơ chế Đấu giá kép Hybrid), mục tiêu cốt lõi của Giai đoạn 2 là chuyển hóa toàn bộ cơ sở lý thuyết "
        "thành BẢN THIẾT KẾ KỸ THUẬT CHI TIẾT (System Specifications & Blueprints) sẵn sàng cho khâu lập trình ở Giai đoạn 3."
    )
    r_sec1.font.name = "Times New Roman"
    r_sec1.font.size = Pt(11)

    bullets_sec1 = [
        ("Tài liệu Đặc tả Yêu cầu Phần mềm (SRS): ", "Đặc tả đầy đủ các yêu cầu chức năng (FR), yêu cầu phi chức năng (NFR)."),
        ("Bộ sơ đồ mô hình hóa UML: ", "Sơ đồ Use Case tổng thể, Activity Diagrams và Sequence Diagrams cho 5 giai đoạn vòng đời tín chỉ."),
        ("Thiết kế Hợp đồng Thông minh chi tiết: ", "Giao diện (Interfaces), cấu trúc lưu trữ (Storage layout), quản lý phân quyền (RBAC), logic trích lập Quỹ dự phòng (Buffer Pool Vault) và chuẩn ký EIP-712."),
        ("Đặc tả Bộ khớp lệnh Đấu giá kép: ", "Quy tắc phá hòa (Tie-breaking), xử lý lệnh chuyển tiếp (Rollover), xác định giá cân bằng (Clearing Price) và thiết kế API Service."),
        ("Bộ thiết kế giao diện (UI/UX Wireframes / Mockups): ", "Thiết kế giao diện DApp 4 phân hệ (Chủ dự án, VVB, Sàn giao dịch, Quản lý chứng chỉ ESG).")
    ]
    for b_title, b_desc in bullets_sec1:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.line_spacing = 1.15
        r1 = bp.add_run(b_title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r2 = bp.add_run(b_desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)

    # Section 2: RACI Table
    add_sec_heading("II. BẢNG TỔNG HỢP MA TRẬN PHÂN CÔNG TRÁCH NHIỆM (RACI MATRIX)")
    
    headers = ["STT", "Hạng mục Công việc", "Phụ trách chính", "Phối hợp", "Sản phẩm bàn giao", "Hạn nộp (Deadline)"]
    data = [
        ["1", "Chủ trì xây dựng Tài liệu SRS (IEEE 830) & Vẽ bộ sơ đồ UML (Use Case, Activity, Sequence)", "Đặng Xuân Huy", "Cả nhóm", "Tài liệu docs/SRS_DOCUMENT.md & Sơ đồ UML", "15/11/2026"],
        ["2", "Thiết kế Cấu trúc Metadata JSON Schema trên IPFS & Từ điển dữ liệu (Data Dictionary)", "Ngô Văn Thắng", "Nguyễn Hoàng Đức", "Tệp docs/METADATA_SCHEMA.json", "20/11/2026"],
        ["3", "Thiết kế Wireframe & UI/UX Mockup cho 4 phân hệ Web3 DApp (Figma / Mockup)", "Ngô Văn Thắng", "Đặng Xuân Huy", "Link bản vẽ Figma & Thư mục docs/wireframes/", "30/11/2026"],
        ["4", "Thiết kế kỹ thuật Smart Contract ERC-1155 (Storage, Buffer Pool, Custom Errors)", "Nguyễn Hoàng Đức", "Ngô Văn Thắng", "docs/SMART_CONTRACT_SPEC.md (Phần ERC-1155)", "25/11/2026"],
        ["5", "Thiết kế hợp đồng Đấu giá CarbonDoubleAuction & Cơ chế ký ngoài chuỗi EIP-712", "Nguyễn Hoàng Đức", "Nguyễn Bảo Phi", "docs/SMART_CONTRACT_SPEC.md (Phần Auction)", "05/12/2026"],
        ["6", "Thiết kế logic Matching Engine (Tie-breaking, Rollover) & Đặc tả API Service", "Nguyễn Bảo Phi", "Đặng Xuân Huy", "Tệp docs/MATCHING_ENGINE_SPEC.md", "25/11/2026"],
        ["7", "Viết script mô phỏng thực nghiệm toán học (100 - 500 lệnh) đo thặng dư xã hội", "Nguyễn Bảo Phi", "Nguyễn Hoàng Đức", "Script Python mô phỏng & Đồ thị thực nghiệm", "10/12/2026"],
        ["8", "Tổng hợp toàn bộ Hồ sơ Thiết kế Giai đoạn 2, rà soát mã nguồn & Báo cáo GVHD", "Đặng Xuân Huy", "Cả nhóm", "Báo cáo tiến độ GĐ 2 hoàn chỉnh & Slide báo cáo", "30/12/2026"]
    ]

    table = doc.add_table(rows=len(data)+1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Widths: STT(0.4 in), Cong viec (2.0 in), Chinh (1.0 in), Phoi hop (0.8 in), San pham (1.5 in), Han nop (0.8 in)
    col_widths = [Inches(0.4), Inches(2.1), Inches(1.1), Inches(0.8), Inches(1.4), Inches(0.8)]

    # Format header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(hdr_cells[i], "102C57")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Format data rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = cell_value
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 2, 3, 5]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(9.5)
                if c_idx == 2:
                    run.font.bold = True
                    run.font.color.rgb = NAVY

    # Apply column widths across all rows
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Section 3: Detailed Tasks for each member
    add_sec_heading("III. BẢN MÔ TẢ CÔNG VIỆC CHI TIẾT THEO TỪNG THÀNH VIÊN")

    members_detail = [
        ("1. ĐẶNG XUÂN HUY – CHỦ NHIỆM ĐỀ TÀI (SYSTEM ANALYST & LEAD)", [
            ("Vai trò:", " Điều phối dự án, Kiến trúc sư hệ thống, Phân tích yêu cầu nghiệp vụ và kỹ thuật."),
            ("Nhiệm vụ 1 (Chủ trì xây dựng tài liệu SRS):", " Xây dựng tài liệu Đặc tả Yêu cầu Phần mềm (Software Requirements Specification) theo chuẩn IEEE 830. Liệt kê rõ các Yêu cầu chức năng (FR-01 đến FR-15) cho các phân hệ Đăng ký, Thẩm tra, Đấu giá, Hủy tín chỉ; và các Yêu cầu phi chức năng (NFR: Gas limit, TPS, bảo mật, tính bất biến)."),
            ("Nhiệm vụ 2 (Mô hình hóa hệ thống bằng UML):", " Thiết kế bộ sơ đồ UML hoàn chỉnh: Sơ đồ Use Case tổng quan; Sơ đồ Hoạt động (Activity Diagrams) cho luồng Đấu giá kép và Hủy tín chỉ; Sơ đồ Tuần tự (Sequence Diagrams) thể hiện tương tác giữa Frontend DApp, Matching Agent, IPFS và Smart Contract."),
            ("Nhiệm vụ 3 (Quản trị dự án & Báo cáo):", " Duy trì kho mã nguồn GitHub, phê duyệt Pull Request, tổ chức họp nhóm hàng tuần và định kỳ báo cáo tiến độ với GVHD (TS. Nguyễn Thị Hồng Khánh)."),
            ("AI Sub-Agent trợ lực:", " `scientific-research-writer` (hỗ trợ chuẩn hóa cấu trúc tài liệu khoa học).")
        ]),
        ("2. NGÔ VĂN THẮNG – THÀNH VIÊN 1 (BUSINESS ANALYST & UI/UX DESIGNER)", [
            ("Vai trò:", " Phân tích nghiệp vụ dữ liệu, Chuẩn hóa Metadata IPFS và Thiết kế Trải nghiệm Người dùng (UI/UX)."),
            ("Nhiệm vụ 1 (Chuẩn hóa Metadata Schema cho IPFS):", " Xây dựng tệp `docs/METADATA_SCHEMA.json` và Từ điển dữ liệu (Data Dictionary). Định nghĩa chuẩn các trường dữ liệu bắt buộc (Project Name, Vintage Year, Location, Baseline methodology, Additionality, UN SDGs, Buffer Pool rate) bám sát theo tiêu chuẩn Verra VCS và Gold Standard."),
            ("Nhiệm vụ 2 (Thiết kế Wireframe & UI/UX DApp):", " Sử dụng Figma (hoặc công cụ thiết kế) phác thảo chi tiết giao diện 4 phân hệ Web3 DApp:\n"
             "  • Phân hệ 1: Project Developer Portal (Bảng điều khiển nộp hồ sơ PDD, tải báo cáo MRV lên IPFS).\n"
             "  • Phân hệ 2: Verifier / VVB Portal (Giao diện kiểm toán độc lập, xem xét số liệu và ký xác nhận on-chain).\n"
             "  • Phân hệ 3: Trading Floor (Sổ lệnh Orderbook trực quan, giao diện đặt lệnh Bid/Ask, biểu đồ giá khớp).\n"
             "  • Phân hệ 4: ESG Retirement Portal (Khu vực doanh nghiệp kích hoạt hủy tín chỉ, xuất giấy chứng nhận có mã QR)."),
            ("AI Sub-Agent trợ lực:", " `fullstack-web3-engineer` (hỗ trợ chuyển đổi wireframe thành component React/Next.js).")
        ]),
        ("3. NGUYỄN HOÀNG ĐỨC – THÀNH VIÊN 2 (SMART CONTRACT ARCHITECT)", [
            ("Vai trò:", " Kiến trúc sư Hợp đồng thông minh và Chuyên gia tích hợp Web3."),
            ("Nhiệm vụ 1 (Thiết kế kỹ thuật hợp đồng CarbonCredit1155.sol):", " Thiết kế chi tiết cấu trúc lưu trữ dữ liệu (Storage Layout) tối ưu gas (sử dụng packed storage `uint128`, `uint64`). Thiết kế cơ chế phân quyền RBAC (Admin, Verifier, ProjectOwner). Thiết kế thuật toán tự động trích lập Quỹ dự phòng rủi ro (Buffer Pool Vault: 10% - 20%). Thiết kế bảng mã lỗi tùy chỉnh (Custom Errors) thay vì chuỗi string."),
            ("Nhiệm vụ 2 (Thiết kế hợp đồng CarbonDoubleAuction.sol & EIP-712):", " Thiết kế cơ chế ký quỹ (Escrow) và thanh toán nguyên tử (Atomic Swap T+0). Đặc tả cấu trúc dữ liệu lệnh chào mua/chào bán có chữ ký số ngoài chuỗi theo chuẩn EIP-712 (Typed Structured Data), cho phép người dùng đặt lệnh ký trên ví MetaMask mà không tốn gas ngay lập tức."),
            ("Sản phẩm bàn giao:", " Tài liệu đặc tả kỹ thuật hợp đồng `docs/SMART_CONTRACT_SPEC.md`."),
            ("AI Sub-Agent trợ lực:", " `smart-contract-auditor` (kiểm toán logic bảo mật, tối ưu gas và phòng chống tấn công).")
        ]),
        ("4. NGUYỄN BẢO PHI – THÀNH VIÊN 3 (AUCTION ALGORITHM ENGINEER)", [
            ("Vai trò:", " Kỹ sư Thuật toán Đấu giá, Thiết kế Matching Engine và Thực nghiệm Kinh tế lượng."),
            ("Nhiệm vụ 1 (Thiết kế logic Matching Engine chi tiết):", " Xây dựng quy tắc phá hòa (Tie-breaking rules) khi có nhiều lệnh cùng mức giá (ưu tiên theo thời gian FIFO hoặc chia theo tỷ lệ Pro-rata). Thiết kế cơ chế chuyển tiếp lệnh chưa khớp (Order Rollover: GTC hoặc IOC) giữa các phiên đấu giá theo nghiên cứu Liu et al. (2026)."),
            ("Nhiệm vụ 2 (Thiết kế API Service cho Bộ khớp lệnh):", " Đặc tả giao diện kết nối API (RESTful/WebSocket) giữa Matching Agent (Python) với Frontend DApp và Smart Contract."),
            ("Nhiệm vụ 3 (Mô phỏng thực nghiệm toán học):", " Viết kịch bản Python sinh 100 - 500 lệnh giao dịch ngẫu nhiên, đối chiếu thặng dư xã hội (Social Welfare) và độ lệch giá (spread) giữa các trường hợp hệ số k khác nhau (alpha = 0, alpha = 0.5, alpha = 1) để tìm ra tham số tối ưu."),
            ("Sản phẩm bàn giao:", " Tài liệu `docs/MATCHING_ENGINE_SPEC.md` + Thư mục script mô phỏng thực nghiệm."),
            ("AI Sub-Agent trợ lực:", " `auction-algorithm-specialist` (hỗ trợ mô hình hóa kinh tế học vi mô và tối ưu thuật toán).")
        ])
    ]

    for m_title, m_tasks in members_detail:
        mp = doc.add_paragraph()
        mp.paragraph_format.space_before = Pt(8)
        mp.paragraph_format.space_after = Pt(2)
        r_m = mp.add_run(m_title)
        r_m.font.name = "Times New Roman"
        r_m.font.size = Pt(11.5)
        r_m.font.bold = True
        r_m.font.color.rgb = STEEL

        for t_label, t_content in m_tasks:
            tp = doc.add_paragraph(style='List Bullet')
            tp.paragraph_format.space_after = Pt(2)
            tp.paragraph_format.line_spacing = 1.15
            r_l = tp.add_run(t_label)
            r_l.font.name = "Times New Roman"
            r_l.font.size = Pt(10.5)
            r_l.font.bold = True
            r_c = tp.add_run(t_content)
            r_c.font.name = "Times New Roman"
            r_c.font.size = Pt(10.5)

    # Section 4: Weekly Timeline
    add_sec_heading("IV. LỘ TRÌNH VÀ CỘT MỐC THEO TUẦN TRONG GIAI ĐOẠN 2")

    weeks_data = [
        ("Tuần 1 (01/11 – 07/11/2026): Khởi động & Thống nhất Yêu cầu",
         "Cả nhóm nghiên cứu kỹ Báo cáo Tổng quan Giai đoạn 1; Huy lập khung tài liệu SRS; Thắng phác thảo User flow; Đức viết khung Interface Smart Contract; Phi viết khung Matching Spec."),
        ("Tuần 2 (08/11 – 14/11/2026): Thiết kế Dữ liệu & Cấu trúc Hợp đồng",
         "Thắng hoàn thành Metadata Schema JSON; Đức hoàn thành bản thiết kế Storage Layout và RBAC cho CarbonCredit1155; Phi hoàn thiện thuật toán phá hòa; Huy vẽ sơ đồ Use Case và Activity."),
        ("Tuần 3 (15/11 – 21/11/2026): Thiết kế Giao diện & Cơ chế EIP-712",
         "Thắng thiết kế Wireframe Figma cho 4 phân hệ; Đức thiết kế cấu trúc lệnh EIP-712 trên CarbonDoubleAuction; Phi thiết kế API Service cho Matching Agent; Huy vẽ Sequence Diagrams."),
        ("Tuần 4 (22/11 – 30/11/2026): Rà soát chéo & Kiểm thử Mô phỏng",
         "Phi chạy thực nghiệm mô phỏng thuật toán đấu giá với 500 lệnh; Đức và Thắng rà soát đối khớp giữa các trường dữ liệu Metadata và tham số hàm Smart Contract; Huy hoàn thiện bản thảo SRS."),
        ("Tuần 5 – 8 (Tháng 12/2026): Tối ưu hóa Bản thiết kế & Viết Test Cases",
         "Rà soát bảo mật thiết kế (threat modeling); viết kịch bản kiểm thử (Test cases); chuẩn bị môi trường phát triển (Foundry/Hardhat, Python venv, Next.js boilerplate)."),
        ("Tuần 9 – 12 (Tháng 01/2027): Nghiệm thu Giai đoạn 2 & Báo cáo GVHD",
         "Tổng hợp toàn bộ hồ sơ thiết kế kỹ thuật; tổ chức báo cáo nghiệm thu Giai đoạn 2 với GVHD (TS. Nguyễn Thị Hồng Khánh); sẵn sàng bước vào Giai đoạn 3 (Coding).")
    ]

    for w_title, w_desc in weeks_data:
        wp = doc.add_paragraph(style='List Bullet')
        wp.paragraph_format.space_after = Pt(3)
        wp.paragraph_format.line_spacing = 1.15
        r_wt = wp.add_run(w_title + ": ")
        r_wt.font.name = "Times New Roman"
        r_wt.font.size = Pt(10.5)
        r_wt.font.bold = True
        r_wt.font.color.rgb = NAVY
        r_wd = wp.add_run(w_desc)
        r_wd.font.name = "Times New Roman"
        r_wd.font.size = Pt(10.5)

    # Section 5: Signature Block
    add_sec_heading("V. CAM KẾT VÀ XÁC NHẬN CỦA NHÓM NGHIÊN CỨU")
    p_sign_intro = doc.add_paragraph()
    p_sign_intro.paragraph_format.space_after = Pt(12)
    r_si = p_sign_intro.add_run(
        "Tất cả các thành viên trong nhóm nghiên cứu đã đọc, hiểu rõ trách nhiệm được phân công, cam kết hoàn thành đúng tiến độ "
        "và đảm bảo chất lượng kỹ thuật, tính trung thực học thuật theo quy định NCKH của Trường Đại học Điện Lực."
    )
    r_si.font.name = "Times New Roman"
    r_si.font.size = Pt(10.5)
    r_si.font.italic = True

    # 2-column signature table
    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False
    sig_table.rows[0].cells[0].width = Inches(3.2)
    sig_table.rows[0].cells[1].width = Inches(3.2)
    sig_table.rows[1].cells[0].width = Inches(3.2)
    sig_table.rows[1].cells[1].width = Inches(3.2)

    # Left: Members
    c_left = sig_table.rows[0].cells[0]
    p_left = c_left.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cl1 = p_left.add_run("CÁC THÀNH VIÊN THAM GIA\n(Ký và ghi rõ họ tên)\n\n\n\n")
    r_cl1.font.name = "Times New Roman"
    r_cl1.font.size = Pt(11)
    r_cl1.font.bold = True
    r_cl2 = p_left.add_run("Ngô Văn Thắng      Nguyễn Hoàng Đức      Nguyễn Bảo Phi")
    r_cl2.font.name = "Times New Roman"
    r_cl2.font.size = Pt(10)
    r_cl2.font.bold = True

    # Right: Leader & Date
    c_right = sig_table.rows[0].cells[1]
    p_right = c_right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cr1 = p_right.add_run("Hà Nội, ngày 01 tháng 11 năm 2026\nCHỦ NHIỆM ĐỀ TÀI\n(Ký và ghi rõ họ tên)\n\n\n\n")
    r_cr1.font.name = "Times New Roman"
    r_cr1.font.size = Pt(11)
    r_cr1.font.bold = True
    r_cr2 = p_right.add_run("Đặng Xuân Huy")
    r_cr2.font.name = "Times New Roman"
    r_cr2.font.size = Pt(11)
    r_cr2.font.bold = True

    # Save document
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    out_dir = r"e:\CODE\NCKH\Blockchain\docs"
    os.makedirs(out_dir, exist_ok=True)
    target_file = os.path.join(out_dir, "KE_HOACH_PHAN_CHIA_CONG_VIEC_GIAI_DOAN_2.docx")
    create_work_division_docx(target_file)
