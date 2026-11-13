"""
Kiểm thử end-to-end của bot settlement trên node Hardhat cục bộ (chainId 80002, giống Polygon Amoy).

Luồng: node Hardhat -> triển khai hợp đồng -> API (uvicorn) -> đặt lệnh ký EIP-712 thật -> chạy phiên
-> `settlement_submitter.py` nộp batch -> đối chiếu số dư on-chain, trạng thái lệnh và event.

Yêu cầu: Node.js, `npm ci` đã chạy ở gốc repo, Python có fastapi, uvicorn, httpx, eth-account, web3.
Chạy từ gốc repo:  python system_agents/matching_engine/e2e_hardhat/run_e2e.py
Khóa dùng ở đây là các khóa dẫn xuất từ mnemonic công khai của Hardhat, chỉ dành cho node cục bộ.
"""

import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

HERE = Path(__file__).resolve().parent
ENGINE_DIR = HERE.parent
REPO = ENGINE_DIR.parents[1]
RPC, API = "http://127.0.0.1:8545", "http://127.0.0.1:8000"
HARDHAT_MNEMONIC = "test test test test test test test test test test test junk"
Account.enable_unaudited_hdwallet_features()
KEYS = {
    name: Account.from_mnemonic(HARDHAT_MNEMONIC, account_path=f"m/44'/60'/0'/0/{i}").key.hex()
    for i, name in enumerate(["operator", "seller", "buyer1", "buyer2", "noAllowance"])
}
ORDER_TYPES = {"Order": [{"name": n, "type": t} for n, t in [
    ("orderId", "bytes32"), ("trader", "address"), ("orderType", "uint8"), ("tokenId", "uint256"),
    ("amount", "uint128"), ("pricePerUnit", "uint128"), ("nonce", "uint256"), ("deadline", "uint256")]]}
ERC20_ABI = [{"name": "balanceOf", "type": "function", "stateMutability": "view",
              "inputs": [{"name": "a", "type": "address"}], "outputs": [{"type": "uint256"}]}]
ERC1155_ABI = [{"name": "balanceOf", "type": "function", "stateMutability": "view",
                "inputs": [{"name": "a", "type": "address"}, {"name": "id", "type": "uint256"}],
                "outputs": [{"type": "uint256"}]}]


def n_lines(text, word):
    """Số dòng kết quả của một trade bắt đầu bằng `word` (SETTLED, SKIPPED, FAILED)."""
    return sum(1 for line in text.splitlines() if line.strip().startswith(word))


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", **kw)


def wait_for(url, payload=None, tries=100):
    for _ in range(tries):
        try:
            httpx.post(url, json=payload, timeout=2) if payload else httpx.get(url, timeout=2)
            return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError(f"không kết nối được {url}")


def main() -> int:
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx or not (REPO / "node_modules").exists():
        print("Cần Node.js và `npm ci` ở gốc repo trước.", file=sys.stderr)
        return 2
    node = subprocess.Popen([npx, "hardhat", "node", "--port", "8545"], cwd=REPO,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    server = None
    try:
        wait_for(RPC, {"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []})
        out = run([npx, "hardhat", "run", str(HERE / "setup.js"), "--network", "localhost"])
        cfg = json.loads(out.stdout.strip().splitlines()[-1])
        env = dict(os.environ, AUCTION_CONTRACT_ADDRESS=cfg["auction"], PYTHONIOENCODING="utf-8",
                   MATCHING_API_KEY="e2e-admin-key")  # kiểm tra luôn đường xác thực quản trị
        admin = {"X-API-Key": env["MATCHING_API_KEY"]}
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api_service:app", "--port", "8000", "--log-level", "warning"],
            cwd=ENGINE_DIR, env=env,
        )
        wait_for(f"{API}/api/v1/sessions/current")

        domain = {"name": "EPU Carbon Double Auction", "version": "2.0", "chainId": 80002,
                  "verifyingContract": cfg["auction"]}

        def place(who, side, amount, price, nonce=0):
            acct = Account.from_key(KEYS[who])
            msg = {"orderId": "0x" + secrets.token_hex(32), "trader": acct.address, "orderType": side, "tokenId": 1,
                   "amount": amount, "pricePerUnit": price, "nonce": nonce, "deadline": int(time.time()) + 3600}
            signed = acct.sign_message(encode_typed_data(domain_data=domain, message_types=ORDER_TYPES, message_data=msg))
            r = httpx.post(f"{API}/api/v1/orders",
                           json={"order": msg, "signature": "0x" + signed.signature.hex().removeprefix("0x")})
            assert r.status_code == 201, r.text
            return msg["orderId"]

        def settle(session_id, *extra):
            e = dict(env, SETTLEMENT_OPERATOR_PRIVATE_KEY=KEYS["operator"])
            return subprocess.run(
                [sys.executable, "settlement_submitter.py", "--api-url", API, "--rpc", RPC,
                 "--session-id", str(session_id), *extra],
                cwd=ENGINE_DIR, env=e, capture_output=True, text=True, encoding="utf-8",
            )

        def order(oid):
            return httpx.get(f"{API}/api/v1/orders/{oid}").json()

        w3 = Web3(Web3.HTTPProvider(RPC))
        usdc = w3.eth.contract(address=cfg["usdc"], abi=ERC20_ABI)
        carbon = w3.eth.contract(address=cfg["carbon"], abi=ERC1155_ABI)

        def bal(who):
            return usdc.functions.balanceOf(cfg[who]).call(), carbon.functions.balanceOf(cfg[who], 1).call()

        assert httpx.post(f"{API}/api/v1/sessions/run", json={"tokenId": 1}).status_code == 401, "thiếu khóa phải bị từ chối"
        print("== Phiên 1: ask 100 @ 10 USDC; bid 60 @ 12 và 40 @ 11 (giá khớp 10,5 USDC)")
        ask1 = place("seller", 1, 100, 10_000_000)
        bid1 = place("buyer1", 0, 60, 12_000_000)
        bid2 = place("buyer2", 0, 40, 11_000_000)
        assert len(httpx.post(f"{API}/api/v1/sessions/run", json={"tokenId": 1}, headers=admin).json()["matches"]) == 2
        before = {w: bal(w) for w in ("seller", "buyer1", "buyer2")}
        dry = settle(1, "--dry-run")
        assert dry.returncode == 0 and "2 trade sẽ được gửi" in dry.stdout, dry.stdout + dry.stderr
        assert bal("seller") == before["seller"], "dry-run không được đổi số dư"
        real = settle(1)
        assert real.returncode == 0 and n_lines(real.stdout, "SETTLED") == 2 and "TxHash" in real.stdout, real.stdout + real.stderr
        after = {w: bal(w) for w in ("seller", "buyer1", "buyer2")}
        assert after["seller"] == (before["seller"][0] + 1_050_000_000, before["seller"][1] - 100), after
        assert after["buyer1"] == (before["buyer1"][0] - 630_000_000, 60), after
        assert after["buyer2"] == (before["buyer2"][0] - 420_000_000, 40), after
        assert all(order(o)["settled_amount"] == order(o)["filled_amount"] for o in (ask1, bid1, bid2))
        print("   OK: 2 trade SETTLED, số dư và settled_amount đúng")

        print("== Nộp lại phiên 1: phải bị bỏ qua, không tx mới")
        again = settle(1)
        assert again.returncode == 0 and "TxHash" not in again.stdout and n_lines(again.stdout, "SKIPPED") == 2, again.stdout
        print("   OK")

        print("== Phiên 2: ask 50 @ 10; bid buyer1 20 @ 12; bid noAllowance 30 @ 12 (không allowance)")
        ask2 = place("seller", 1, 50, 10_000_000)
        bid3 = place("buyer1", 0, 20, 12_000_000, nonce=1)
        bid4 = place("noAllowance", 0, 30, 12_000_000)
        httpx.post(f"{API}/api/v1/sessions/run", json={"tokenId": 1}, headers=admin)
        res = settle(2)
        assert res.returncode == 1 and n_lines(res.stdout, "SETTLED") == 1 and n_lines(res.stdout, "FAILED") == 1, res.stdout + res.stderr
        assert (order(bid3)["settled_amount"], order(bid4)["settled_amount"], order(ask2)["settled_amount"]) == (20, 0, 20)
        assert order(bid4)["filled_amount"] == 30 and order(ask2)["filled_amount"] == 50
        print("   OK: trade thiếu allowance bị hợp đồng bỏ qua, bot báo FAILED, settled_amount lệch filled_amount")
        print("E2E PASSED")
        return 0
    finally:
        for p in (server, node):
            if p is not None:
                p.terminate()


if __name__ == "__main__":
    sys.exit(main())
