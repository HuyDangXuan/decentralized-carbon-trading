# -*- coding: utf-8 -*-
"""
Script tạo file Word báo cáo phân tích toàn bộ lịch sử Git, các nhánh, suy luận
chuyên sâu các vấn đề trong docs/VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md và đưa ra
bộ giải pháp kỹ thuật cụ thể cho từng thành viên (Đức, Huy, Thắng, Phi).
"""

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


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def create_report_docx(output_path):
    doc = docx.Document()

    # Thiết lập căn lề chuẩn học thuật (Trái 3cm ~ 1.18 in, Phải 2cm ~ 0.79 in, Trên/Dưới 2cm ~ 0.79 in)
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.79)

    # Bảng màu nhận diện thương hiệu học thuật
    NAVY = RGBColor(16, 44, 87)       # #102C57
    STEEL = RGBColor(53, 89, 142)     # #35598E
    DARK_GRAY = RGBColor(50, 50, 50)
    BLACK = RGBColor(0, 0, 0)
    RED = RGBColor(185, 28, 28)       # #B91C1C
    AMBER = RGBColor(180, 83, 9)      # #B45309
    GREEN = RGBColor(21, 128, 61)     # #15803D

    # 1. Header cơ quan / trường học
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

    # 2. Tiêu đề chính
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("BÁO CÁO PHÂN TÍCH TOÀN BỘ LỊCH SỬ GIT, ĐỐI SOÁT CÁC NHÁNH,\nĐÁNH GIÁ VẤN ĐỀ TRÊN REPO VÀ BỘ GIẢI PHÁP THEO TỪNG THÀNH VIÊN\n")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(14)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY

    run_sub = p_title.add_run("Đối soát tài liệu 'VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md' bên branch algorithm\nvà thiết kế giải pháp kỹ thuật chi tiết cho Đức, Huy, Thắng, Phi")
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = STEEL

    # 3. Thông tin đề tài
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
        ("Thời điểm phân tích: ", True),
        ("Tháng 11/2026 (Tuần 2, Giai đoạn 2 - Phân tích Yêu cầu và Thiết kế Hệ thống)\n", False),
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

    # Helper tạo các kiểu đoạn văn
    def add_sec_heading(title_text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        run = h.add_run(title_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return h

    def add_sub_heading(title_text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        run = h.add_run(title_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = STEEL
        return h

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(11)
            r_bold.font.bold = True
            r_bold.font.color.rgb = NAVY
        r_text = p.add_run(text)
        r_text.font.name = "Times New Roman"
        r_text.font.size = Pt(11)
        r_text.font.italic = italic
        return p

    def add_bullet(title, desc):
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.line_spacing = 1.15
        r1 = bp.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r2 = bp.add_run(desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        return bp

    def add_code_block(code_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        run = p.add_run(code_text)
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 41, 59)
        # Background light gray
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        for side in ['top', 'left', 'bottom', 'right']:
            node = OxmlElement(f'w:{side}')
            node.set(qn('w:val'), 'single')
            node.set(qn('w:sz'), '4')
            node.set(qn('w:space'), '4')
            node.set(qn('w:color'), 'CBD5E1')
            pBdr.append(node)
        pPr.append(pBdr)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'F8FAFC')
        pPr.append(shd)
        return p

    # =========================================================================
    # PHẦN I: TỔNG QUAN LỊCH SỬ GIT VÀ CÁC NHÁNH
    # =========================================================================
    add_sec_heading("I. TỔNG QUAN LỊCH SỬ GIT VÀ HIỆN TRẠNG CÁC NHÁNH TRÊN REPOSITORY")

    add_p("Qua kiểm tra chi tiết toàn bộ lịch sử Git (`git log --all --graph`), hiện tại repository đang có 4 nhánh phát triển chính tương ứng với các phân hệ chuyên trách của đề tài:",
          bold_prefix="1. Bức tranh phân nhánh trên Git: ")

    headers_branches = ["Nhánh (Branch)", "Commit HEAD", "Phụ trách", "Nội dung trọng tâm", "Tình trạng tích hợp"]
    data_branches = [
        [
            "main",
            "18c6460 (local)\n7285ba3 (origin)",
            "Đặng Xuân Huy\n(Chủ nhiệm)",
            "Chứa kiến trúc tổng thể, tài liệu GĐ1, kế hoạch GĐ2 và các tác tử mẫu sơ khai (auction_agent, order_book, mrv_agent, contract thô sơ).",
            "Đang làm mốc cơ sở. Commit 7285ba3 trên remote là bản thảo đầu của spec Matching Engine do Phi push nhầm."
        ],
        [
            "origin/docs/smart-contract-spec",
            "3194bad",
            "Nguyễn Hoàng Đức\n(Smart Contract)",
            "Đặc tả kỹ thuật Smart Contract v2: Packed Storage, Buffer Pool Vault, EIP-712 gasless orders, Atomic Swap T+0 với ERC-20 payment.",
            "Mới dừng ở tài liệu Markdown (SMART_CONTRACT_SPEC.md), chưa có code Solidity thực thi tương ứng; chưa merge vào main."
        ],
        [
            "origin/feature/thang-web3-frontend-integration",
            "f47f381",
            "Ngô Văn Thắng\n(Fullstack Web3)",
            "Khởi tạo dự án Next.js (frontend/), tích hợp ví Web3 (MetaMask/Wagmi), xây dựng giao diện Trading Floor và file docs/METADATA_SCHEMA.json.",
            "Code UI đang import ABI của hợp đồng cũ từ main; chưa tích hợp ABI mới hay API của Matching Engine; chưa merge vào main."
        ],
        [
            "origin/auction-algorithm-engineer\n(branch 'algorithm')",
            "127af75",
            "Nguyễn Bảo Phi\n(Auction Algorithm)",
            "Nghiên cứu toán học, Game Theory, mô phỏng cân bằng Nash (k-Double Auction), xây dựng session_engine số nguyên, viết MATCHING_ENGINE_SPEC chi tiết.",
            "Phát triển độc lập, khối lượng thực nghiệm lớn nhất (+8.700 dòng code). Đã đối soát chéo và phát hiện hàng loạt lỗ hổng của các nhánh khác."
        ]
    ]

    t_branches = doc.add_table(rows=len(data_branches) + 1, cols=len(headers_branches))
    t_branches.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_branches.autofit = False
    col_w_branches = [Inches(1.5), Inches(1.0), Inches(1.1), Inches(2.2), Inches(1.4)]

    for i, title in enumerate(headers_branches):
        c = t_branches.rows[0].cells[i]
        c.text = title
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c, "102C57")
        set_cell_margins(c, top=100, bottom=100, left=80, right=80)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data_branches):
        row_cells = t_branches.rows[r_idx + 1].cells
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 1, 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = NAVY

    for row in t_branches.rows:
        for idx, w in enumerate(col_w_branches):
            row.cells[idx].width = w

    # =========================================================================
    # PHẦN II: PHÂN TÍCH SUY LUẬN FILE VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.MD
    # =========================================================================
    add_sec_heading("II. PHÂN TÍCH VÀ SUY LUẬN CHUYÊN SÂU CÁC VẤN ĐỀ TRONG 'VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.MD'")

    add_p("Tệp tài liệu docs/VAN_DE_CAN_TRAO_DOI_MATCHING_ENGINE.md trên branch auction-algorithm-engineer (Nguyễn Bảo Phi) là văn bản phản biện kỹ thuật cực kỳ chất lượng. Tác giả đã đối soát từng dòng tài liệu đặc tả Smart Contract của Đức (commit 3194bad), chạy kiểm thử thực tế trên mã nguồn mô phỏng, và review chéo độc lập bằng nhiều mô hình AI (Argon suy nghĩ cao, Claude Opus 4.6 và 5.5). Tài liệu chia thành 4 nhóm vấn đề trọng yếu:")

    # II.1 Với Đức
    add_sub_heading("1. Các vấn đề kỹ thuật với Smart Contract & Settlement EIP-712 (Nguyễn Hoàng Đức)")
    add_p("Phi liệt kê 15 điểm trao đổi (Đ1 đến Đ15). Dưới đây là bảng tổng hợp đối soát:")

    headers_duc = ["Mã", "Vấn đề tồn tại", "Bằng chứng đối soát", "Hệ quả kỹ thuật & Đề xuất giải pháp", "Mức độ"]
    data_duc = [
        [
            "Đ1",
            "Mâu thuẫn đơn vị khối lượng: kg CO2e hay tCO2e (chênh lệch 1.000 lần)",
            "Spec Đức §3.2 ghi: 'uint128 amount; // Số lượng tín chỉ tối đa (kg CO2e)'.\nBáo cáo GĐ1 ghi: 1 token = 1 tCO2e.\nThắng (Metadata): decimals = 0 (tấn).",
            "Cực kỳ nguy hiểm: Người mua trả tiền cho 1 tấn nhưng trên hợp đồng chỉ được ghi nhận 1 kg (hoặc ngược lại), gây thất thoát tài chính 1.000 lần. Cần chốt thống nhất toàn dự án đơn vị chuẩn là tCO2e (hoặc kg CO2e) trên mọi tầng.",
            "CAO"
        ],
        [
            "Đ2",
            "Hợp đồng chỉ kiểm tra filledAmount phía Bid, bỏ quên phía Ask",
            "Spec Đức §3.3 bước 3 chỉ ghi:\nfilledAmount[bidId] + matchAmount <= bidOrder.amount.",
            "Lỗ hổng bảo mật: Bên bán (Ask) có thể bị khớp vượt quá số lượng sở hữu, hoặc một lệnh bán có thể được tái sử dụng để khớp nhiều lần qua các phiên khác nhau. Bắt buộc hợp đồng phải kiểm tra cả filledAmount[askId].",
            "CAO"
        ],
        [
            "Đ3",
            "Khái niệm 'wei USDC' mơ hồ về số chữ số thập phân",
            "Spec Đức §3.2 comment: 'tính theo wei USDC'.",
            "USDC chuẩn trên Polygon/Ethereum có 6 chữ số thập phân (10^6), trong khi wei của ETH có 18 chữ số (10^18). Nếu hiểu nhầm 1 USDC = 10^18 đơn vị nhỏ nhất, phép tính giá trị thanh toán sẽ bị sai lệch hàng tỷ lần. Cần chốt số nguyên tick giá.",
            "CAO"
        ],
        [
            "Đ4",
            "Làm tròn số thực clearingPrice gây REVERT giao dịch on-chain",
            "Spec Đức §3.3: Hợp đồng revert PriceMismatch nếu giá nằm ngoài [ask, bid]. Baseline agent dùng round(price, 2).",
            "Nếu Ask=10.001, Bid=10.004, k=0 => giá khớp thô 10.001, bị round(..., 2) thành 10.00 < Ask (10.001). Khi đưa lên on-chain, transaction lập tức revert. Đề xuất: dùng số nguyên tick và quy tắc làm tròn half_even không thiên lệch.",
            "CAO"
        ],
        [
            "Đ5",
            "time_in_force (GTC/IOC) không có trong struct EIP-712 được ký",
            "Spec Đức §3.2 ORDER_TYPEHASH thiếu trường timeInForce.",
            "Người dùng ký ủy quyền ngoài chuỗi nhưng không ràng buộc lệnh là GTC hay IOC. Engine ngoài chuỗi có thể tùy tiện hủy hoặc gia hạn lệnh mà người dùng không thể kiểm chứng. Cần đưa vào struct hoặc nêu rõ trong tài liệu.",
            "TRUNG BÌNH"
        ],
        [
            "Đ6",
            "Ngữ nghĩa incrementNonce() gây hủy đồng loạt mọi lệnh GTC",
            "Spec Đức §3.4 chỉ có hàm incrementNonce(). orderId = keccak256(trader, nonce, timestamp).",
            "Nếu nonce là biến đếm duy nhất cho ví on-chain, khi người dùng muốn hủy 1 lệnh GTC bằng cách tăng nonce, toàn bộ các lệnh GTC khác đang mở của ví đó sẽ bị vô hiệu hóa cùng lúc. Cần cơ chế cancelOrder theo orderId cụ thể.",
            "TRUNG BÌNH"
        ],
        [
            "Đ7",
            "Chưa ràng buộc quyền gọi cancelOrder",
            "Spec Đức §3.4 chỉ liệt kê giao diện cancelOrder(bytes32 orderId).",
            "Cần quy định chặt chẽ: chỉ có chính địa chỉ trader tạo ra lệnh mới có quyền gửi giao dịch hủy lệnh on-chain để tránh việc kẻ xấu hủy lệnh của người khác.",
            "TRUNG BÌNH"
        ],
        [
            "Đ8",
            "Chưa xử lý trường hợp matchAmount = 0",
            "Quy tắc pro-rata có thể sinh ra phần chia bằng 0 cho các lệnh rất nhỏ.",
            "Hợp đồng cần revert nếu matchAmount == 0 để tránh tốn gas vô ích; Engine phải tự lọc bỏ các phân bổ bằng 0 trước khi nộp lên blockchain.",
            "THẤP"
        ],
        [
            "Đ9",
            "Quyền gọi settleMatchedTrade: onlyMatchingAgent hay công khai?",
            "Code main dùng modifier onlyMatchingAgent. Spec mới không nêu rõ.",
            "Nếu chỉ agent được gọi: tập quyền, rủi ro tắc nghẽn khi agent sập. Nếu công khai: bot/searcher có thể chèn giao dịch trục lợi (MEV). Cần có quyết định thiết kế có chủ đích (ví dụ: cấp quyền cho cụm submitter có chữ ký).",
            "TRUNG BÌNH"
        ],
        [
            "Đ10",
            "Nguồn gốc timestamp trong orderId",
            "orderId = keccak256(trader, nonce, timestamp).",
            "Do client phía người dùng tạo ra khi ký lệnh. Engine cần kiểm tra tính duy nhất của orderId và từ chối các orderId đã tồn tại trước đó.",
            "THẤP"
        ],
        [
            "Đ11",
            "Code thực tế trên main hoàn toàn chưa theo Spec mới",
            "CarbonDoubleAuction.sol trên main chỉ chuyển token carbon, không có ERC-20 payment, không có EIP-712.",
            "Sự phân kỳ lớn giữa mã nguồn thật và tài liệu giấy. Nhóm chưa thể thực hiện kiểm thử tích hợp (integration test) nếu Đức chưa code hợp đồng mới.",
            "TRUNG BÌNH"
        ],
        [
            "Đ12",
            "Số liệu tiêu hao gas chưa được benchmark thực tế",
            "Spec Đức §5 ước tính gas: 112k, 145k, 920k (nhãn NOT VERIFIED).",
            "Các con số này chỉ là phỏng đoán lý thuyết, chưa chạy qua Hardhat/Foundry trên Amoy testnet. Engine không thể dựa vào đây để tối ưu hóa kích thước batch.",
            "THẤP"
        ],
        [
            "Đ13",
            "Rủi ro thao túng từ mô hình Non-custodial không khóa tài sản",
            "Spec Đức §3.1: Không giam tiền/tín chỉ trước khi khớp.",
            "Người dùng có thể tạo hàng trăm ví miễn phí để spam lệnh GTC tích tuổi lệnh, hoặc chẻ nhỏ lệnh để chiếm phần dư trong phân bổ pro-rata (nghịch lý Alabama) mà không tốn chi phí. Cần biện pháp: hạn mức tối thiểu, biên độ giá.",
            "TRUNG BÌNH"
        ],
        [
            "Đ14",
            "Quy trình xác minh on-chain thiếu 6 chốt chặn an toàn cốt tử",
            "Spec Đức §3.3 chỉ liệt kê 4 bước sơ sài: chữ ký, dải giá, filledAmount bid, cập nhật.",
            "Hợp đồng đang thiếu kiểm tra: (1) filledAmount Ask; (2) deadline hợp lệ; (3) nonce/hủy lệnh; (4) hai lệnh phải cùng tokenId; (5) đúng vai trò BID/ASK; (6) trader mua khác trader bán (chống Wash Trading).",
            "CAO"
        ],
        [
            "Đ15",
            "Thiếu công thức tradeHash tất định và cơ chế chống nộp trùng",
            "Spec Đức §3.3 và §3.4 có event TradeSettled mang tradeHash nhưng không đưa công thức.",
            "Khi một lệnh lớn được khớp từng phần thành nhiều lệnh nhỏ cùng số lượng trong 1 phiên, nếu không có định danh tradeHash tất định, hợp đồng có thể từ chối nhầm hoặc bị gửi lặp lại giao dịch.",
            "TRUNG BÌNH"
        ]
    ]

    t_duc = doc.add_table(rows=len(data_duc) + 1, cols=len(headers_duc))
    t_duc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_duc.autofit = False
    col_w_duc = [Inches(0.5), Inches(1.8), Inches(1.6), Inches(2.6), Inches(0.7)]

    for i, title in enumerate(headers_duc):
        c = t_duc.rows[0].cells[i]
        c.text = title
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c, "102C57")
        set_cell_margins(c, top=100, bottom=100, left=60, right=60)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data_duc):
        row_cells = t_duc.rows[r_idx + 1].cells
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=70, bottom=70, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9)
                if c_idx == 0:
                    r.font.bold = True
                if c_idx == 4:
                    r.font.bold = True
                    if val == "CAO":
                        r.font.color.rgb = RED
                    elif val == "TRUNG BÌNH":
                        r.font.color.rgb = AMBER
                    else:
                        r.font.color.rgb = STEEL

    for row in t_duc.rows:
        for idx, w in enumerate(col_w_duc):
            row.cells[idx].width = w

    # II.2 Với Huy
    add_sub_heading("2. Các vấn đề lý thuyết, phạm vi & SRS/UML với Chủ nhiệm đề tài (Đặng Xuân Huy)")
    add_p("Phi nêu ra 6 vấn đề mang tính nền tảng học thuật và định hướng triển khai hệ thống:")

    headers_huy = ["Mã", "Vấn đề tồn tại", "Bằng chứng & Phân tích chuyên sâu", "Giải pháp & Đề xuất", "Mức độ"]
    data_huy = [
        [
            "H1",
            "Sai lầm bản chất lý thuyết trong Nhiệm vụ 3 trên Google Doc",
            "Đề cương ghi: 'So sánh social welfare giữa k=0, 0.5, 1 để tìm tham số tối ưu'.\nBằng chứng toán học: Khi các bên khai giá trung thực, Welfare hoàn toàn BẰNG NHAU với mọi k. k chỉ quyết định tỷ lệ chia thặng dư (buyer_share = 1 - k).",
            "Không thể dùng Welfare để chọn k trong giả định trung thực. Cần sửa đề cương thành: (A) Đo lường phân bổ thặng dư; (B) Đo lường tổn thất hiệu quả khi người chơi khai giá chiến lược (Strategic Bidding).",
            "CAO"
        ],
        [
            "H2",
            "Các quyết định thiết kế cốt lõi chưa được họp chốt",
            "Spec Matching §11: Độ dài chu kỳ phiên đấu giá; thuật toán phá hòa (age_prorata vs FIFO); quy tắc giá theo cặp hay giá chung của phiên (kda); giới hạn số vòng rollover của lệnh GTC; chính sách chống thao túng.",
            "Cần tổ chức họp nhóm chốt ngay trước tuần 3 Giai đoạn 2 để chốt kiến trúc API Service và hoàn thiện thiết kế.",
            "CAO"
        ],
        [
            "H3",
            "Tài liệu SRS và sơ đồ UML chưa cập nhật vòng đời lệnh",
            "Spec Matching §4, §6, §8 định nghĩa trạng thái lệnh mới: NEW -> ACTIVE -> PARTIALLY_FILLED -> ROLLED_OVER -> EXPIRED / CANCELLED.",
            "Huy cần cập nhật biểu đồ Trạng thái (State Machine), Hoạt động (Activity) và Tuần tự (Sequence Diagram) trong SRS chuẩn IEEE 830 để phản ánh đúng cơ chế Rollover giữa các phiên.",
            "TRUNG BÌNH"
        ],
        [
            "H4",
            "Độ tin cậy của tài liệu tham khảo học thuật (Evidence levels)",
            "Nhiều công thức giải tích (Chatterjee-Samuelson 1983, Rustichini et al. 1994) mới đọc qua bài tóm tắt; một nguồn thứ cấp trích con số '1/6' không khớp với tính toán của nhóm (9/32).",
            "Không đưa các kết luận chưa kiểm chứng trực tiếp vào Báo cáo NCKH chính thức. Phi cần tìm đọc bài gốc toàn văn trước khi trích dẫn công thức.",
            "TRUNG BÌNH"
        ],
        [
            "H5",
            "Nguy cơ hiểu sai kết quả thực nghiệm B2",
            "Kết quả B2 cho thấy hiệu quả đạt 92% - 94% và không tăng theo n.",
            "Đây là hệ quả của hàm chiến lược tuyến tính cố định, KHÔNG PHẢI trạng thái cân bằng Nash. Cần lưu ý khi viết báo cáo, không được khẳng định đây là đặc tính của thị trường cân bằng.",
            "TRUNG BÌNH"
        ],
        [
            "H6",
            "Lựa chọn Quy tắc Định giá: kda (giá chung) vượt trội pair (giá cặp)",
            "Thực nghiệm C cho thấy: Quy tắc giá chung kda giảm tổn thất hiệu quả với tốc độ O(1/m^2) ở cả k=1 và k=0.5. Trong khi định giá theo cặp (pair) hội tụ rất chậm ở k=1 (chỉ đạt O(1/m)).",
            "Đề xuất nhóm chính thức từ bỏ định giá theo từng cặp và chuyển sang quy tắc giá chung kda cho toàn phiên đấu giá định kỳ.",
            "CAO"
        ]
    ]

    t_huy = doc.add_table(rows=len(data_huy) + 1, cols=len(headers_huy))
    t_huy.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_huy.autofit = False
    col_w_huy = [Inches(0.5), Inches(1.8), Inches(2.2), Inches(2.0), Inches(0.7)]

    for i, title in enumerate(headers_huy):
        c = t_huy.rows[0].cells[i]
        c.text = title
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c, "102C57")
        set_cell_margins(c, top=100, bottom=100, left=60, right=60)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data_huy):
        row_cells = t_huy.rows[r_idx + 1].cells
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=70, bottom=70, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9)
                if c_idx == 0:
                    r.font.bold = True
                if c_idx == 4:
                    r.font.bold = True
                    if val == "CAO":
                        r.font.color.rgb = RED
                    elif val == "TRUNG BÌNH":
                        r.font.color.rgb = AMBER
                    else:
                        r.font.color.rgb = STEEL

    for row in t_huy.rows:
        for idx, w in enumerate(col_w_huy):
            row.cells[idx].width = w

    # II.3 Với Thắng
    add_sub_heading("3. Các vấn đề nghiệp vụ dữ liệu & Giao diện DApp với Frontend Engineer (Ngô Văn Thắng)")
    add_p("Phi chỉ ra 3 điểm vênh giữa logic nghiệp vụ của sàn và thiết kế Frontend:")

    headers_thang = ["Mã", "Vấn đề tồn tại", "Bằng chứng đối soát", "Giải pháp đề xuất", "Mức độ"]
    data_thang = [
        [
            "T1",
            "Tính thay thế của Tín chỉ Carbon (Credit Fungibility)",
            "Engine hiện tại chỉ khớp các lệnh có cùng tokenId chính xác. Trong thực tế thị trường, các lô tín chỉ cùng Vintage, cùng tiêu chuẩn (Verra) có thể được coi là cùng một lớp tài sản.",
            "Thắng cần làm rõ tiêu chí gom nhóm lô tín chỉ (Eligibility criteria). Nếu nghiệp vụ cho phép mua chéo các tokenId cùng nhóm, Engine phải nâng cấp thuật toán khớp đa mã.",
            "TRUNG BÌNH"
        ],
        [
            "T2",
            "Đồng bộ Wireframe Trading Floor với API Matching Engine",
            "Thắng đang dựng giao diện dựa trên ABI hợp đồng cũ, chưa tích hợp luồng gọi API và WebSocket.",
            "Đối chiếu các màn hình giao dịch với danh mục endpoint REST và sự kiện WebSocket mà Phi đã đặc tả tại §8.2 và §8.3 của MATCHING_ENGINE_SPEC. Đồng bộ đơn vị hiển thị USD/tCO2e.",
            "TRUNG BÌNH"
        ],
        [
            "T3",
            "Cấu trúc Metadata Schema hỗ trợ lọc sổ lệnh",
            "Tệp METADATA_SCHEMA.json trên nhánh feature/thang chưa định nghĩa trường phân nhóm lớp tài sản.",
            "Bổ sung trường quy ước nhóm lô (Project Type, Vintage Window, Standard Category) vào Metadata Schema để sổ lệnh và UI có thể phân loại và gom nhóm thanh khoản.",
            "THẤP"
        ]
    ]

    t_thang = doc.add_table(rows=len(data_thang) + 1, cols=len(headers_thang))
    t_thang.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_thang.autofit = False
    col_w_thang = [Inches(0.5), Inches(1.8), Inches(2.2), Inches(2.0), Inches(0.7)]

    for i, title in enumerate(headers_thang):
        c = t_thang.rows[0].cells[i]
        c.text = title
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c, "102C57")
        set_cell_margins(c, top=100, bottom=100, left=60, right=60)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data_thang):
        row_cells = t_thang.rows[r_idx + 1].cells
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=70, bottom=70, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9)
                if c_idx == 0:
                    r.font.bold = True
                if c_idx == 4:
                    r.font.bold = True
                    if val == "CAO":
                        r.font.color.rgb = RED
                    elif val == "TRUNG BÌNH":
                        r.font.color.rgb = AMBER
                    else:
                        r.font.color.rgb = STEEL

    for row in t_thang.rows:
        for idx, w in enumerate(col_w_thang):
            row.cells[idx].width = w

    # II.4 Việc tồn đọng của Phi
    add_sub_heading("4. Các hạng mục nội bộ của bộ phận Thuật toán chưa hoàn thành (Nguyễn Bảo Phi)")
    add_bullet("Đọc bài báo gốc: ", "Cần tìm đọc toàn văn hai bài báo nền tảng Chatterjee–Samuelson (1983) và Rustichini–Satterthwaite–Williams (1994) để kiểm chứng chắc chắn các công thức giải tích.")
    add_bullet("Mở rộng thực nghiệm C: ", "Cần mở rộng quy mô mô phỏng cho thị trường nhiều đơn vị (multi-unit) và số lượng người tham gia lớn hơn (m > 16), đồng thời kiểm chéo bằng một thuật toán tìm cân bằng độc lập khác.")
    add_bullet("Tích hợp Engine số nguyên vào hệ thống: ", "Mã nguồn session_engine.py (thuần số nguyên, chống float round, có age_prorata) hiện vẫn nằm trong thư mục simulation/. Cần chuyển đổi để thay thế trực tiếp cho auction_agent.py trên hệ thống chính ở Giai đoạn 3.")
    add_bullet("Thiết kế bảo mật (Threat Modeling): ", "Cần hoàn thiện kịch bản kiểm thử bảo mật cho tầng API Service, phân tích nguy cơ Front-running ngoài chuỗi của chính người vận hành Engine và quản trị khóa của bot Settlement Submitter.")

    # =========================================================================
    # PHẦN III: TOÀN CẢNH 5 VẤN ĐỀ CỐT LÕI ĐANG TỒN TẠI TRÊN REPO
    # =========================================================================
    add_sec_heading("III. TOÀN CẢNH 5 NGUY CƠ VÀ LỖ HỔNG CỐT LÕI ĐANG TỒN TẠI TRÊN REPO")

    add_p("Tổng hợp từ việc rà soát toàn bộ lịch sử Git, cấu trúc các nhánh và mã nguồn thực tế, repository hiện đang tồn tại 5 bất cập lớn mang tính hệ thống cần được xử lý ngay:")

    add_bullet("1. Tình trạng phân rã và lệch pha nghiêm trọng giữa 4 nhánh phát triển: ",
               "Mỗi thành viên đang làm việc biệt lập trên nhánh của mình mà không có sự đồng bộ định kỳ. Nhánh main vẫn chứa mã nguồn thô sơ từ Giai đoạn 1; nhánh của Đức có spec hợp đồng mới nhưng chưa có code; nhánh của Thắng viết giao diện nhưng lại kết nối với hợp đồng cũ; nhánh của Phi đi trước rất xa về thuật toán nhưng chưa thể ráp nối vào hệ sinh thái.")

    add_bullet("2. Bất đồng bộ dữ liệu cốt tử (Đơn vị tính và số chữ số thập phân): ",
               "Xung đột giữa đơn vị khối lượng (kg CO2e trong spec hợp đồng của Đức vs tCO2e trong Báo cáo GĐ1 và Metadata schema của Thắng) gây nguy cơ lệch giá trị 1.000 lần. Khái niệm 'wei USDC' gây nhầm lẫn giữa 6 decimals của USDC và 18 decimals của ETH.")

    add_bullet("3. Lỗ hổng bảo mật và xác thực on-chain trong thiết kế Smart Contract v2: ",
               "Hàm settleMatchedTrade trên spec của Đức bỏ quên kiểm tra filledAmount của bên bán, thiếu kiểm tra deadline, thiếu kiểm tra trạng thái hủy lệnh/nonce, không kiểm tra cùng tokenId, và không chặn tự giao dịch (Wash Trading).")

    add_bullet("4. Mã nguồn baseline trên main tiềm ẩn lỗi vỡ giao dịch: ",
               "Tệp auction_agent.py trên main có 2 lỗi kỹ thuật lớn: trừ trực tiếp vào thuộc tính bộ nhớ (Order.amount) gây side-effect nguy hiểm khi chạy nhiều phiên; và hàm round(..., 2) trên số thực có thể đưa giá khớp ra ngoài dải [ask, bid], khiến hợp đồng blockchain lập tức REVERT giao dịch.")

    add_bullet("5. Thiếu hụt hoàn toàn hạ tầng kiểm thử tích hợp (Integration Tests) và CI/CD: ",
               "Dự án chưa có môi trường testnet tự động (Hardhat/Foundry kết nối Polygon Amoy). Chưa có bất kỳ bài test E2E nào kiểm tra chu trình hoàn chỉnh: Người dùng ký EIP-712 trên Frontend -> Gửi qua REST API -> Engine khớp lệnh trong phiên -> Bot nộp giao dịch -> Smart contract thanh quyết toán nguyên tử T+0.")

    # =========================================================================
    # PHẦN IV: BỘ GIẢI PHÁP KỸ THUẬT CHI TIẾT THEO TỪNG THÀNH VIÊN (MỚI)
    # =========================================================================
    add_sec_heading("IV. BỘ GIẢI PHÁP KỸ THUẬT VÀ LỘ TRÌNH THỰC THI CHI TIẾT THEO TỪNG THÀNH VIÊN")

    add_p("Dưới đây là phương án hành động kỹ thuật cụ thể, chi tiết mã nguồn và sản phẩm bàn giao (Deliverables) được thiết kế riêng cho từng người nhằm tháo gỡ dứt điểm toàn bộ các xung đột trên:")

    # ----------------------------------------------------
    # IV.1 Giải pháp cho Nguyễn Hoàng Đức
    # ----------------------------------------------------
    add_sub_heading("1. Giải pháp cho NGUYỄN HOÀNG ĐỨC (Smart Contract Engineer)")
    add_p("Mục tiêu trọng tâm: Chuyển đổi thiết kế giấy sang mã nguồn Solidity v2 chạy được, vá 15 điểm xác thực và đo gas thực tế.", italic=True)

    add_bullet("Giải pháp 1.1: Chuẩn hóa đơn vị khối lượng và tiền tệ (Giải quyết Đ1, Đ3, Đ4): ",
               "Quy định rõ trong struct Order: amount có đơn vị là số nguyên tCO2e (nếu decimals=0) hoặc kg CO2e (nếu decimals=3). Tiền tệ thanh toán là MockUSDC có 6 chữ số thập phân (10^6 đơn vị nhỏ nhất = 1 USD). Trường pricePerUnit biểu diễn theo micro-USDC (số nguyên). Xóa bỏ vĩnh viễn thuật ngữ 'wei USDC' để tránh nhầm lẫn với 18 decimals của ETH.")

    add_bullet("Giải pháp 1.2: Bổ sung 7 chốt chặn bảo mật cho hàm settleMatchedTrade (Giải quyết Đ2, Đ8, Đ14): ",
               "Hợp đồng bắt buộc phải revert giao dịch nếu vi phạm bất kỳ điều kiện nào sau đây:")
    add_code_block(
        "// Đoạn mã kiểm tra hợp lệ đề xuất cho CarbonDoubleAuction.sol:\n"
        "// 1. Xác thực chữ ký EIP-712 cả 2 bên:\n"
        "require(_verifyOrderSignature(bidOrder, bidSignature), \"InvalidBidSignature\");\n"
        "require(_verifyOrderSignature(askOrder, askSignature), \"InvalidAskSignature\");\n\n"
        "// 2. Kiểm tra Deadline:\n"
        "if (block.timestamp > bidOrder.deadline || block.timestamp > askOrder.deadline)\n"
        "    revert SignatureExpired();\n\n"
        "// 3. Kiểm tra tính hợp thức của cặp lệnh:\n"
        "if (bidOrder.tokenId != askOrder.tokenId) revert TokenIdMismatch();\n"
        "if (bidOrder.orderType != 0 || askOrder.orderType != 1) revert InvalidOrderType();\n"
        "if (bidOrder.trader == askOrder.trader) revert SelfTradingNotAllowed(); // Chống Wash Trading\n"
        "if (matchAmount == 0) revert InvalidMatchAmount();\n\n"
        "// 4. Kiểm tra dải giá khớp [ask, bid]:\n"
        "if (clearingPrice < askOrder.pricePerUnit || clearingPrice > bidOrder.pricePerUnit)\n"
        "    revert PriceMismatch(clearingPrice, askOrder.pricePerUnit, bidOrder.pricePerUnit);\n\n"
        "// 5. Kiểm tra hạn mức filledAmount của CẢ HAI BÊN (Khắc phục Đ2):\n"
        "if (filledAmount[bidOrder.orderId] + matchAmount > bidOrder.amount)\n"
        "    revert BidAmountExceeded();\n"
        "if (filledAmount[askOrder.orderId] + matchAmount > askOrder.amount)\n"
        "    revert AskAmountExceeded();\n\n"
        "// 6. Kiểm tra trạng thái hủy lệnh:\n"
        "if (cancelledOrders[bidOrder.orderId] || cancelledOrders[askOrder.orderId])\n"
        "    revert OrderAlreadyCancelled();"
    )

    add_bullet("Giải pháp 1.3: Hoàn thiện logic hủy lệnh và chống nộp trùng (Giải quyết Đ6, Đ7, Đ15): ",
               "Xây dựng hàm cancelOrder(bytes32 orderId) với ràng buộc msg.sender == orders[orderId].trader. Giải thích rõ hàm incrementNonce() là cơ chế 'Hủy khẩn cấp hàng loạt mọi lệnh cũ'. Xây dựng tradeHash tất định: keccak256(abi.encodePacked(bidOrder.orderId, askOrder.orderId, matchAmount, clearingPrice, block.number)) và lưu executedTrades[tradeHash] = true để chặn hoàn toàn việc gửi lặp giao dịch.")

    add_bullet("Sản phẩm bàn giao (Deliverables): ",
               "Mã nguồn contracts/CarbonDoubleAuction.sol và contracts/CarbonCredit1155.sol trên nhánh docs/smart-contract-spec; Bộ test Hardhat đo gas thật (Đ12); Deploy lên Polygon Amoy Testnet và xuất file ABI chuẩn cho nhóm.")

    # ----------------------------------------------------
    # IV.2 Giải pháp cho Đặng Xuân Huy
    # ----------------------------------------------------
    add_sub_heading("2. Giải pháp cho ĐẶNG XUÂN HUY (Chủ nhiệm đề tài / Lead Architect)")
    add_p("Mục tiêu trọng tâm: Điều phối kỹ thuật toàn nhóm, hiệu chỉnh đề cương học thuật, hoàn thiện hồ sơ SRS (IEEE 830) và thiết kế UML bám sát thuật toán thực tế.", italic=True)

    add_bullet("Giải pháp 2.1: Triệu tập cuộc họp kỹ thuật Sprint Alignment (Giải quyết H2): ",
               "Chủ trì phiên họp nhóm để biểu quyết và chốt dứt điểm 4 thông số kiến trúc: (1) Chu kỳ phiên đấu giá Periodic Double Auction (5 phút cho testnet demo, 15 phút cho thực tế); (2) Quy tắc phá hòa: chốt dùng age_prorata kết hợp phần dư Largest Remainder (Hamilton); (3) Quy tắc giá: chính thức chuyển sang quy tắc giá kda cho toàn phiên; (4) Giới hạn rollover của lệnh GTC (sau N phiên thì tự động EXPIRED).")

    add_bullet("Giải pháp 2.2: Sửa đổi câu chữ học thuật Nhiệm vụ 3 trên Google Docs (Giải quyết H1, H5): ",
               "Xóa bỏ nội dung 'so sánh welfare giữa các k để tìm k tối ưu khi trung thực'. Thay bằng nội dung đúng đắn về mặt khoa học:\n"
               "• Đánh giá sự phân bổ thặng dư kinh tế (Surplus Split) giữa bên mua và bên bán theo tham số k (buyer_share = 1 - k) trong điều kiện khai giá trung thực.\n"
               "• Mô phỏng và đo lường tổn thất hiệu quả kinh tế (Efficiency Loss / Deadweight Loss) khi các bên tham gia sử dụng chiến lược khai giá không trung thực (Bayesian-Nash Equilibrium) trên các quy mô thị trường m khác nhau.")

    add_bullet("Giải pháp 2.3: Cập nhật tài liệu SRS và sơ đồ UML (Giải quyết H3): ",
               "Bổ sung vòng đời lệnh đầy đủ vào biểu đồ Trạng thái (State Diagram): NEW -> ACTIVE -> PARTIALLY_FILLED -> ROLLED_OVER -> EXPIRED / CANCELLED. Cập nhật biểu đồ Sequence Diagram thể hiện rõ luồng 3 bên: Trader ký EIP-712 -> REST API Matching Agent -> OrderBook -> Session Engine -> Settlement Submitter -> Smart Contract.")

    add_bullet("Sản phẩm bàn giao (Deliverables): ",
               "Google Docs kế hoạch Giai đoạn 2 đã cập nhật; Tài liệu docs/SRS_DOCUMENT.md (IEEE 830) và sơ đồ UML cập nhật bám sát logic rollover và batch settlement.")

    # ----------------------------------------------------
    # IV.3 Giải pháp cho Ngô Văn Thắng
    # ----------------------------------------------------
    add_sub_heading("3. Giải pháp cho NGÔ VĂN THẮNG (Fullstack Web3 & Frontend Engineer)")
    add_p("Mục tiêu trọng tâm: Chuẩn hóa Metadata schema, sửa mã nguồn DApp kết nối đúng ABI v2, và chuyển hướng giao dịch qua API Matching Engine thay vì gọi trực tiếp on-chain.", italic=True)

    add_bullet("Giải pháp 3.1: Chuẩn hóa tệp docs/METADATA_SCHEMA.json (Giải quyết T1, T3): ",
               "Đồng bộ thuộc tính decimals khớp với hợp đồng của Đức. Bổ sung các trường dữ liệu gom nhóm phân khúc tín chỉ (Credit Fungibility): asset_class (forestry, renewable_energy, waste_treatment), vintage_year (số nguyên), standard (Verra_VCS, Gold_Standard), và is_fungible_pool (boolean) để UI có thể gom nhóm thanh khoản trên sổ lệnh.")

    add_bullet("Giải pháp 3.2: Thay thế ABI và cập nhật luồng ký EIP-712 (Giải quyết T2, Đ11): ",
               "Xóa file ABI cũ CarbonDoubleAuctionABI.ts trên frontend/. Thay bằng file ABI mới sinh ra từ hợp đồng của Đức. Cập nhật hook useWalletConnection.ts để người dùng thực hiện ký cấu trúc EIP-712 Typed Data Gasless trên MetaMask:")
    add_code_block(
        "// Cấu trúc ký EIP-712 Gasless trên Frontend:\n"
        "const domain = {\n"
        "  name: 'EPU Carbon Double Auction',\n"
        "  version: '2.0',\n"
        "  chainId: 80002, // Polygon Amoy\n"
        "  verifyingContract: AUCTION_CONTRACT_ADDRESS\n"
        "};\n"
        "const types = {\n"
        "  Order: [\n"
        "    { name: 'orderId', type: 'bytes32' },\n"
        "    { name: 'trader', type: 'address' },\n"
        "    { name: 'orderType', type: 'uint8' },\n"
        "    { name: 'tokenId', type: 'uint256' },\n"
        "    { name: 'amount', type: 'uint128' },\n"
        "    { name: 'pricePerUnit', type: 'uint128' },\n"
        "    { name: 'nonce', type: 'uint256' },\n"
        "    { name: 'deadline', type: 'uint256' }\n"
        "  ]\n"
        "};"
    )

    add_bullet("Giải pháp 3.3: Tích hợp API Service của Matching Engine (Thay vì gửi on-chain): ",
               "Người dùng đặt lệnh không tốn gas. Frontend đóng gói struct Order và Signature gửi qua HTTP POST tới Matching Engine: POST /api/v1/orders. Thiết lập kết nối WebSocket WS /ws/orderbook/{tokenId} để cập nhật biểu đồ độ sâu (Depth Chart) thời gian thực và thông báo kết quả khớp lệnh.")

    add_bullet("Sản phẩm bàn giao (Deliverables): ",
               "Tệp docs/METADATA_SCHEMA.json hoàn thiện; Giao diện Trading Floor hiển thị đúng đơn vị USDC/tCO2e; Module frontend/src/services/matchingApi.ts kết nối trơn tru với API Engine.")

    # ----------------------------------------------------
    # IV.4 Giải pháp cho Nguyễn Bảo Phi
    # ----------------------------------------------------
    add_sub_heading("4. Giải pháp cho NGUYỄN BẢO PHI (Auction Algorithm Engineer)")
    add_p("Mục tiêu trọng tâm: Đưa mã nguồn mô phỏng số nguyên vào hệ sinh thái chính, đóng gói API Service, và hoàn thiện cơ sở học thuật toán học.", italic=True)

    add_bullet("Giải pháp 4.1: Đưa session_engine.py thành lõi chính của Matching Engine: ",
               "Thay thế hoàn toàn mã nguồn cũ system_agents/matching_engine/auction_agent.py bằng logic của session_engine.py. Khắc phục triệt để lỗi trừ trực tiếp vào Order.amount (dùng remaining_amount nội bộ) và lỗi round(..., 2) (dùng số nguyên tick giá và half_even). Kích hoạt mặc định quy tắc giá phiên kda và thuật toán chia tỷ lệ age_prorata.")

    add_bullet("Giải pháp 4.2: Xây dựng Mock API Service bằng FastAPI/Flask (Giải quyết T2): ",
               "Triển khai các endpoint đã đặc tả tại §8 trong MATCHING_ENGINE_SPEC.md: POST /api/v1/orders (tiếp nhận và xác thực chữ ký EIP-712); DELETE /api/v1/orders/{orderId} (hủy lệnh ngoài chuỗi); GET /api/v1/orderbook/{tokenId} (lấy trạng thái sổ lệnh); và POST /api/v1/sessions/run (kích hoạt khớp lệnh định kỳ). Cung cấp Swagger UI (/docs) để Thắng kết nối frontend ngay.")

    add_bullet("Giải pháp 4.3: Hoàn thiện học thuật & Báo cáo thực nghiệm: ",
               "Tìm đọc toàn văn bài báo gốc Chatterjee & Samuelson (1983) và Rustichini, Satterthwaite, Williams (1994) để giải quyết dứt điểm nghi vấn con số 1/6 so với 9/32. Chạy mở rộng Thí nghiệm C cho kịch bản nhiều đơn vị (multi-unit) và m > 16. Viết tài liệu docs/THREAT_MODELING.md phân tích nguy cơ người vận hành Engine chạy trước lệnh (Front-running) và cơ chế phòng chống.")

    add_bullet("Sản phẩm bàn giao (Deliverables): ",
               "Mã nguồn system_agents/matching_engine/auction_agent.py nâng cấp; Dịch vụ API system_agents/matching_engine/api_service.py; Báo cáo kết quả Thí nghiệm C mở rộng và tài liệu THREAT_MODELING.md.")

    # ----------------------------------------------------
    # IV.5 Bảng tổng hợp phân công và hạn nộp
    # ----------------------------------------------------
    add_sub_heading("5. Bảng ma trận phân công trách nhiệm và mốc thời gian bàn giao (RACI Matrix)")

    headers_raci = ["Thành viên", "Nhiệm vụ trọng tâm cần giải quyết", "Tệp mã nguồn / Tài liệu bàn giao", "Hạn chót (Deadline)"]
    data_raci = [
        [
            "Đặng Xuân Huy\n(Chủ nhiệm)",
            "Chủ trì họp thống nhất 4 thông số kiến trúc; Sửa đề cương Google Docs; Cập nhật tài liệu SRS IEEE 830 và sơ đồ UML State/Sequence.",
            "docs/SRS_DOCUMENT.md\ndocs/SYSTEM_ARCHITECTURE.md\nGoogle Docs Kế hoạch GĐ2",
            "Tuần 2\n(15/11/2026)"
        ],
        [
            "Nguyễn Hoàng Đức\n(Smart Contract)",
            "Viết code Solidity v2 (EIP-712, Atomic swap); Vá 7 chốt chặn bảo mật; Viết test Hardhat đo gas thật; Deploy Polygon Amoy; Cung cấp ABI chuẩn.",
            "contracts/CarbonDoubleAuction.sol\ncontracts/CarbonCredit1155.sol\ntest/CarbonAuction.test.ts",
            "Tuần 3\n(20/11/2026)"
        ],
        [
            "Nguyễn Bảo Phi\n(Algorithm)",
            "Đưa session_engine số nguyên vào lõi agent; Dựng API Service FastAPI; Mở rộng Thí nghiệm C (m>16); Đọc bài gốc và viết Threat Modeling.",
            "system_agents/matching_engine/auction_agent.py\nsystem_agents/matching_engine/api_service.py\ndocs/THREAT_MODELING.md",
            "Tuần 3\n(25/11/2026)"
        ],
        [
            "Ngô Văn Thắng\n(Web3 Frontend)",
            "Sửa METADATA_SCHEMA.json bổ sung gom nhóm lô; Thay ABI mới từ Đức; Chuyển luồng đặt lệnh sang ký EIP-712 và gọi API Service của Phi.",
            "docs/METADATA_SCHEMA.json\nfrontend/src/contracts/CarbonDoubleAuctionABI.ts\nfrontend/src/services/matchingApi.ts",
            "Tuần 4\n(30/11/2026)"
        ]
    ]

    t_raci = doc.add_table(rows=len(data_raci) + 1, cols=len(headers_raci))
    t_raci.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_raci.autofit = False
    col_w_raci = [Inches(1.5), Inches(2.7), Inches(2.0), Inches(1.0)]

    for i, title in enumerate(headers_raci):
        c = t_raci.rows[0].cells[i]
        c.text = title
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c, "102C57")
        set_cell_margins(c, top=100, bottom=100, left=80, right=80)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(data_raci):
        row_cells = t_raci.rows[r_idx + 1].cells
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], bg)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if c_idx in [0, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9)
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = NAVY
                if c_idx == 3:
                    r.font.bold = True
                    r.font.color.rgb = GREEN

    for row in t_raci.rows:
        for idx, w in enumerate(col_w_raci):
            row.cells[idx].width = w

    # =========================================================================
    # PHẦN V: KẾ HOẠCH HÀNH ĐỘNG VÀ KHUYẾN NGHỊ KHẨN CẤP CHO NHÓM
    # =========================================================================
    add_sec_heading("V. KẾ HOẠCH HÀNH ĐỘNG VÀ KHUYẾN NGHỊ KHẨN CẤP CHO NHÓM")

    add_p("Để đảm bảo tiến độ nghiệm thu Giai đoạn 2 (tháng 01/2027) và tính đúng đắn khoa học của đề tài, nhóm nghiên cứu cần triển khai ngay 4 bước hành động đồng bộ:")

    add_bullet("Bước 1 (Họp nhóm kỹ thuật tức thời - Ngay trong tuần 2): ",
               "Chủ nhiệm Đặng Xuân Huy triệu tập cuộc họp kỹ thuật. Đem bảng 15 điểm của Phi ra rà soát từng mục và chính thức phê duyệt bộ giải pháp đã nêu ở Phần IV.")

    add_bullet("Bước 2 (Đồng bộ tài liệu và mã nguồn - Tuần 2 đến Tuần 3): ",
               "Đức hoàn thiện mã nguồn hợp đồng v2; Phi đưa session_engine vào lõi hệ thống; Thắng cập nhật Metadata schema và cấu trúc DApp; Huy cập nhật hồ sơ SRS và sơ đồ UML.")

    add_bullet("Bước 3 (Triển khai Testnet và Tích hợp API - Tuần 3 đến Tuần 4): ",
               "Đức deploy hợp đồng lên Polygon Amoy Testnet; Phi dựng API Service; Thắng kết nối Frontend với API và hợp đồng để thực hiện phiên đấu giá thử nghiệm.")

    add_bullet("Bước 4 (Kiểm thử tích hợp End-to-End và Đo lường Gas - Tuần 5 trở đi): ",
               "Thực hiện kịch bản kiểm thử toàn diện: Đặt lệnh off-chain -> Khớp lệnh phiên -> Nộp giao dịch on-chain -> Kiểm tra số dư và giấy chứng nhận hủy tín chỉ. Ghi nhận số liệu thực nghiệm phục vụ viết báo cáo khoa học.")

    # Lưu tệp Word
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"Báo cáo Word đã được cập nhật thành công tại: {output_path}")


if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "BAO_CAO_PHAN_TICH_LICH_SU_GIT_VA_VAN_DE_MATCHING_ENGINE.docx")
    create_report_docx(out_file)
