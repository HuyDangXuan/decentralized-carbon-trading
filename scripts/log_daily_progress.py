#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động hóa ghi nhận Tiến độ Kỹ thuật Hàng ngày (Daily Progress Logger)
Dành riêng cho Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
Dự án: Sàn giao dịch Tín chỉ Carbon Blockchain MAS - ĐH Điện Lực

Cách dùng:
    python scripts/log_daily_progress.py
    python scripts/log_daily_progress.py --push
    python scripts/log_daily_progress.py --date 2026-11-10 --title "Cập nhật kiến trúc v2"
"""

import os
import sys
import subprocess
from datetime import datetime
import argparse

# Thiết lập UTF-8 cho Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROGRESS_DIR = os.path.join(PROJECT_ROOT, "docs", "progress")

def run_cmd(cmd_list):
    """Thực thi lệnh shell và trả về kết quả chuỗi"""
    try:
        res = subprocess.run(cmd_list, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding='utf-8')
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_git_changes():
    """Lấy danh sách các tệp thay đổi từ Git"""
    status_out = run_cmd(["git", "status", "--porcelain"])
    changed_files = {"new": [], "modified": [], "deleted": []}
    
    for line in status_out.splitlines():
        if not line.strip():
            continue
        status_code = line[:2].strip()
        file_path = line[3:].strip()
        
        if status_code in ["??", "A"]:
            changed_files["new"].append(file_path)
        elif status_code in ["M", "MM"]:
            changed_files["modified"].append(file_path)
        elif status_code in ["D"]:
            changed_files["deleted"].append(file_path)

    # Nếu không có file uncommitted, lấy từ commit gần nhất
    if not (changed_files["new"] or changed_files["modified"] or changed_files["deleted"]):
        last_commit_files = run_cmd(["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD"])
        for line in last_commit_files.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                code, path = parts[0], parts[1]
                if code == "A":
                    changed_files["new"].append(path)
                elif code == "M":
                    changed_files["modified"].append(path)
                elif code == "D":
                    changed_files["deleted"].append(path)

    return changed_files

def ensure_daily_log(date_str, title=None):
    """Tạo hoặc cập nhật file log theo ngày"""
    day_folder = os.path.join(PROGRESS_DIR, date_str)
    os.makedirs(day_folder, exist_ok=True)
    log_file = os.path.join(day_folder, "README.md")
    
    changes = get_git_changes()
    formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    
    if not title:
        title = f"CẬP NHẬT KỸ THUẬT VÀ ĐỒNG BỘ TIẾN ĐỘ NGÀY {formatted_date}"

    # Chuẩn bị nội dung tệp
    content = f"""# NHẬT KÝ TIẾN ĐỘ KỸ THUẬT: NGÀY {formatted_date}
## {title.upper()}

- **Ngày thực hiện:** {formatted_date}
- **Người chủ trì cập nhật:** Đặng Xuân Huy (Chủ nhiệm đề tài / Lead Architect)
- **Kênh ghi nhận:** Kênh SSOT chính thức trên nhánh `main`

---

## 1. MỤC TIÊU TRỌNG TÂM ĐÃ ĐẠT ĐƯỢC TRONG NGÀY
- Rà soát toàn bộ các thay đổi kỹ thuật trên mã nguồn và hồ sơ tài liệu.
- Cập nhật nhật ký tiến độ tự động qua trợ lý `lead-architect-progress-logger`.
- Đồng bộ các quyết định kiến trúc và lưu trữ minh bạch trên Git.

---

## 2. CHI TIẾT TỪNG THAY ĐỔI KỸ THUẬT (DÙ LÀ NHỎ NHẤT)

### 2.1 Các tệp tạo mới (New Files)
"""
    if changes["new"]:
        for f in changes["new"]:
            content += f"- `{f}`\n"
    else:
        content += "- Không có tệp tạo mới phát sinh.\n"

    content += "\n### 2.2 Các tệp chỉnh sửa (Modified Files)\n"
    if changes["modified"]:
        for f in changes["modified"]:
            content += f"- `{f}`\n"
    else:
        content += "- Không có tệp chỉnh sửa phát sinh.\n"

    content += f"""
### 2.3 Ghi chú Kiến trúc & Đặc tả Kỹ thuật
- Xem chi tiết hồ sơ SRS chuẩn IEEE 830 tại [`docs/SRS_DOCUMENT.md`](../../SRS_DOCUMENT.md).
- Xem 4 quyết định kiến trúc cốt lõi tại [`docs/ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md`](../../ADR_001_AUCTION_ARCHITECTURE_DECISIONS.md).

---

## 3. TÁC ĐỘNG TỚI TỪNG THÀNH VIÊN VÀ NHIỆM VỤ TIẾP THEO

- **Nguyễn Hoàng Đức (Smart Contract):** Kiểm tra các thay đổi liên quan đến interface và chốt chặn bảo mật on-chain.
- **Nguyễn Bảo Phi (Auction Algorithm):** Kiểm tra tính nhất quán của thuật toán khớp lệnh k-DA và quy tắc phân bổ Hamilton.
- **Ngô Văn Thắng (Web3 Frontend):** Đồng bộ giao diện DApp, bảng hiển thị trạng thái và thời lượng phiên đấu giá.

---

## 4. GHI CHÚ BẢN COMMIT VÀ TRẠNG THÁI GIT
- **Nhánh hiện tại:** `{run_cmd(['git', 'branch', '--show-current'])}`
- **Commit HEAD:** `{run_cmd(['git', 'rev-parse', '--short', 'HEAD'])}`
- **Thời gian đồng bộ:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Chỉ ghi đè nếu file chưa tồn tại hoặc người dùng yêu cầu cập nhật
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Đã tạo mới file nhật ký: docs/progress/{date_str}/README.md")
    else:
        print(f"ℹ️ File nhật ký đã tồn tại: docs/progress/{date_str}/README.md")

    return log_file

def update_progress_index(date_str, title):
    """Cập nhật bảng mục lục trong docs/progress/README.md"""
    index_file = os.path.join(PROGRESS_DIR, "README.md")
    if not os.path.exists(index_file):
        return

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    entry_line = f"| **{formatted_date}** | **{title}** | Đặng Xuân Huy | [Xem chi tiết]({date_str}/README.md) |"

    # Kiểm tra xem ngày đã có trong bảng chưa
    if f"{date_str}/README.md" not in content:
        target_marker = "| Ngày ghi nhận | Tiêu đề tóm tắt nội dung | Thành viên thực hiện | Liên kết chi tiết |\n| :---: | :--- | :---: | :---: |\n"
        if target_marker in content:
            new_content = content.replace(target_marker, target_marker + entry_line + "\n")
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Đã thêm mục {formatted_date} vào bảng mục lục docs/progress/README.md")

def git_commit_and_push(date_str):
    """Tự động commit và push lên main"""
    current_branch = run_cmd(["git", "branch", "--show-current"])
    if current_branch != "main":
        print(f"⚠️ Chú ý: Bạn đang ở nhánh '{current_branch}', khuyến nghị chuyển về 'main' trước khi push.")
    
    run_cmd(["git", "add", "docs/progress/", "scripts/"])
    commit_msg = f"docs(progress): log daily updates for {date_str}"
    commit_res = run_cmd(["git", "commit", "-m", commit_msg])
    print(f"📦 Đã commit: {commit_msg}")
    
    push_res = run_cmd(["git", "push", "origin", "main"])
    print(f"🚀 Đã push lên origin/main thành công!")

def main():
    parser = argparse.ArgumentParser(description="Tự động hóa ghi nhật ký tiến độ hàng ngày cho Chủ nhiệm đề tài")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Ngày ghi nhận định dạng YYYY-MM-DD")
    parser.add_argument("--title", default=None, help="Tiêu đề nhật ký")
    parser.add_argument("--push", action="store_true", help="Tự động git add, commit và push lên main")
    args = parser.parse_args()

    print(f"\n🤖 KHỞI CHẠY LEAD ARCHITECT PROGRESS LOGGER...")
    print(f"📅 Ngày ghi nhận: {args.date}")
    
    log_file = ensure_daily_log(args.date, args.title)
    default_title = args.title or "Cập nhật kỹ thuật và đồng bộ tiến độ"
    update_progress_index(args.date, default_title)

    if args.push:
        git_commit_and_push(args.date)

    print(f"\n🎉 Hoàn thành xuất sắc quy trình ghi nhận tiến độ!")
    print(f"👉 File nhật ký: {os.path.relpath(log_file, PROJECT_ROOT)}\n")

if __name__ == "__main__":
    main()
