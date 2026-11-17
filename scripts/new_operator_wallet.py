"""
Tạo ví Operator mới cho bot settlement và lưu khóa riêng vào `.env` (đã nằm trong .gitignore).

Chỉ in ĐỊA CHỈ ví; khóa riêng không bao giờ được in ra màn hình hay ghi vào chỗ khác.
Địa chỉ này gửi cho Đức để cấp SETTLEMENT_OPERATOR_ROLE; ví cần có ít POL từ faucet Amoy để trả gas.

Chạy từ gốc repo:  python scripts/new_operator_wallet.py
"""

import sys
from pathlib import Path

from eth_account import Account

KEY_NAME = "SETTLEMENT_OPERATOR_PRIVATE_KEY"
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def main() -> int:
    existing = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    if any(line.strip().startswith(f"{KEY_NAME}=") for line in existing.splitlines()):
        address = Account.from_key(
            next(l.split("=", 1)[1].strip() for l in existing.splitlines() if l.strip().startswith(f"{KEY_NAME}="))
        ).address
        print(f"{KEY_NAME} đã có trong {ENV_FILE.name}; không ghi đè. Địa chỉ hiện tại: {address}")
        return 0
    account = Account.create()
    separator = "" if existing.endswith("\n") or not existing else "\n"
    with ENV_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{separator}{KEY_NAME}={account.key.hex()}\n")
    print(f"Đã tạo ví Operator và lưu khóa vào {ENV_FILE.name} (không commit file này).")
    print(f"Địa chỉ ví: {account.address}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
