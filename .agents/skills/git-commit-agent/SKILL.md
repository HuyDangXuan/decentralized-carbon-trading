---
name: git-commit-agent
description: Chuyên gia DevOps & Quản trị mã nguồn. Tự động rà soát file thay đổi, soạn commit message chuẩn quốc tế Conventional Commits (feat:, fix:, docs:) và đồng bộ lên GitHub an toàn. Hỗ trợ cả nhóm.
---

# Git Commit Agent (Hỗ trợ Cả Nhóm)

Kỹ năng này trao quyền cho trợ lý AI Antigravity tự động hóa quy trình rà soát thay đổi mã nguồn, tạo commit chuẩn mực và đồng bộ an toàn lên repository GitHub cho các thành viên trong nhóm.

## Khi nào kích hoạt kỹ năng này?
- Khi hoàn thành một tính năng hoặc sửa lỗi cần commit và push lên nhánh cá nhân.
- Khi cần kiểm tra nhanh trạng thái các tệp thay đổi (`git status`, `git diff`).
- Khi chuẩn bị tạo Pull Request vào nhánh `main` và gán Reviewer theo đúng quy trình.
- Khi cần đồng bộ cập nhật mới nhất từ `main` về nhánh làm việc (`git pull origin main`).

## Quy Chuẩn Conventional Commits
- `feat(scope): ...`: Tính năng mới (ví dụ: `feat(thang): add EIP-712 signing hook`)
- `fix(scope): ...`: Sửa lỗi kỹ thuật (ví dụ: `fix(matching): resolve integer tick round error`)
- `docs(scope): ...`: Cập nhật tài liệu (ví dụ: `docs(srs): add UML sequence diagram`)
- `test(scope): ...`: Thêm hoặc sửa kịch bản kiểm thử
- `refactor(scope): ...`: Tối ưu cấu trúc mã nguồn không làm đổi logic nghiệp vụ

## Quy Trình Tạo Pull Request Chuẩn
1. Merge cập nhật mới từ `main`: `git checkout <branch> && git merge origin/main`
2. Push lên GitHub: `git push origin <branch>`
3. Mở Pull Request vào `main`, đặt tiêu đề rõ ràng kèm mô tả các tệp thay đổi.
4. Gán Reviewer là Chủ nhiệm đề tài: **Đặng Xuân Huy** (`@HuyDangXuan`).
