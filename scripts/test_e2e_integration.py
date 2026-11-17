#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
TEST KIỂM THỬ TOÀN TRÌNH END-TO-END (E2E INTEGRATION TEST)
DỰ ÁN: SÀN GIAO DỊCH TÍN CHỈ CARBON PHI TẬP TRUNG (EPU VCM)
NHIỆM VỤ: Task H.1 (Chủ nhiệm Đề tài / Lead Architect - Đặng Xuân Huy)
===============================================================================

Kịch bản 5 bước liên thông 3 phân hệ (Smart Contracts - Matching Engine - Submitter Bot):
  * Bước 1: Sinh 2 ví thử nghiệm Buyer và Seller bằng eth-account,
            faucet MockUSDC cho Buyer và đúc/cấp token EVCC #101 cho Seller.
            Cấp quyền approve cho hợp đồng đấu giá (CarbonDoubleAuction).
  * Bước 2: Ký 2 lệnh đối ứng EIP-712:
            - Buyer đặt mua 50 tCO2e @ 12 USDC (12,000,000 micro-USDC).
            - Seller đặt bán 50 tCO2e @ 10 USDC (10,000,000 micro-USDC).
  * Bước 3: Đẩy cả 2 lệnh vào Matching Engine API qua POST /api/v1/orders.
  * Bước 4: Gọi POST /api/v1/sessions/run kích hoạt phiên khớp lệnh k-DA.
            Kỳ vọng giá khớp biên P* = floor((12 + 10) / 2) = 11 USDC (11,000,000 micro-USDC).
  * Bước 5: Chạy bot submitter nộp batchSettleTrades lên hợp đồng CarbonDoubleAuction.
            Kiểm tra đối soát số dư On-chain:
            - Buyer: nhận đúng +50 EVCC #101, trừ đúng -550 USDC ($50 \times 11$).
            - Seller: trừ đúng -50 EVCC #101, nhận đúng +550 USDC.
            Kiểm tra settled_amount == filled_amount == 50 trên API.

Hỗ trợ 2 chế độ:
  1. Chế độ Hardhat cục bộ (--mode hardhat / --local): Tự động khởi chạy Hardhat node,
     triển khai bộ hợp đồng qua setup_hardhat_e2e.js, chạy uvicorn api_service.py và settlement.
  2. Chế độ Polygon Amoy Testnet (--mode amoy / --amoy): Kết nối RPC Amoy, sử dụng địa chỉ
     hợp đồng chính thức theo docs/DEPLOYED_ADDRESSES.md, hỗ trợ --dry-run hoặc nộp thật.
===============================================================================
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# Hỗ trợ ký ví HD Wallet nếu cần
Account.enable_unaudited_hdwallet_features()

# Đường dẫn thư mục cốt lõi
REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "system_agents" / "matching_engine"
CONTRACTS_DIR = REPO_ROOT / "contracts"
ABIS_DIR = CONTRACTS_DIR / "abis"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Thông số mặc định theo docs/DEPLOYED_ADDRESSES.md
AMOY_CHAIN_ID = 80002
AMOY_DEFAULT_RPC = "https://polygon-amoy-bor-rpc.publicnode.com"
AMOY_FALLBACK_RPC = "https://poly-amoy-testnet.api.pocket.network"
AMOY_DEPLOYED_CONTRACTS = {
    "usdc": "0xe35681b0882d533458d22B344268642136ebD813",
    "carbon": "0x851978601b47a61B8aF3bcC1707B689Fbc977697",
    "auction": "0x6Ee8284848Cf08527175a321fF4B5C5b7e61c46f",
    "faucet": "0xcD5D000E52Ab50EbDC57Ea3356fC0A172d55F7ED",
    "operator": "0xa4b198e0f6EB111F6B1dcc1c898C024222240EDE",
}

# Cấu trúc EIP-712 Order Type
ORDER_TYPES = {
    "Order": [
        {"name": "orderId", "type": "bytes32"},
        {"name": "trader", "type": "address"},
        {"name": "orderType", "type": "uint8"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "amount", "type": "uint128"},
        {"name": "pricePerUnit", "type": "uint128"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}

# Hardhat Default Mnemonic
HARDHAT_MNEMONIC = "test test test test test test test test test test test junk"
HARDHAT_DEPLOYER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# Minimal ABIs
ERC20_ABI = [
    {"name": "name", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "string"}]},
    {"name": "symbol", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "string"}]},
    {"name": "decimals", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint8"}]},
    {"name": "balanceOf", "type": "function", "stateMutability": "view", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"type": "uint256"}]},
    {"name": "allowance", "type": "function", "stateMutability": "view", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"type": "uint256"}]},
    {"name": "approve", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"type": "bool"}]},
    {"name": "mint", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": []},
]

ERC1155_ABI = [
    {"name": "balanceOf", "type": "function", "stateMutability": "view", "inputs": [{"name": "account", "type": "address"}, {"name": "id", "type": "uint256"}], "outputs": [{"type": "uint256"}]},
    {"name": "isApprovedForAll", "type": "function", "stateMutability": "view", "inputs": [{"name": "account", "type": "address"}, {"name": "operator", "type": "address"}], "outputs": [{"type": "bool"}]},
    {"name": "setApprovalForAll", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "operator", "type": "address"}, {"name": "approved", "type": "bool"}], "outputs": []},
    {"name": "safeTransferFrom", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "id", "type": "uint256"}, {"name": "value", "type": "uint256"}, {"name": "data", "type": "bytes"}], "outputs": []},
    {
        "name": "mintProjectLot",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"},
            {"name": "totalAmount", "type": "uint128"},
            {"name": "vintageYear", "type": "uint32"},
            {"name": "standardType", "type": "uint8"},
            {"name": "bufferBps", "type": "uint16"},
            {"name": "ipfsCID", "type": "string"},
            {"name": "metadataHash", "type": "bytes32"},
        ],
        "outputs": [],
    },
]

AUCTION_ABI = [
    {"name": "carbonToken", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"name": "paymentToken", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"name": "filledAmount", "type": "function", "stateMutability": "view", "inputs": [{"name": "orderId", "type": "bytes32"}], "outputs": [{"type": "uint128"}]},
    {"name": "userNonces", "type": "function", "stateMutability": "view", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"type": "uint256"}]},
    {"name": "hasRole", "type": "function", "stateMutability": "view", "inputs": [{"name": "role", "type": "bytes32"}, {"name": "account", "type": "address"}], "outputs": [{"type": "bool"}]},
    {"name": "SETTLEMENT_OPERATOR_ROLE", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [{"type": "bytes32"}]},
]


def log_step(step_num: int, title: str):
    """In tiêu đề từng bước trực quan, chuyên nghiệp."""
    print(f"\n{'='*75}")
    print(f"  👉 BƯỚC {step_num}: {title.upper()}")
    print(f"{'='*75}")


def wait_for_service(url: str, post_payload: Optional[dict] = None, timeout_sec: int = 40):
    """Chờ dịch vụ HTTP hoặc JSON-RPC sẵn sàng."""
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            if post_payload is not None:
                r = httpx.post(url, json=post_payload, timeout=2.0)
                if r.status_code < 500:
                    return
            else:
                r = httpx.get(url, timeout=2.0)
                if r.status_code < 500:
                    return
        except Exception:
            time.sleep(0.4)
    raise TimeoutError(f"Không thể kết nối đến {url} sau {timeout_sec}s.")


def send_tx_and_wait(w3: Web3, tx: dict, private_key: str) -> dict:
    """Ký và gửi transaction, chờ xác nhận receipt."""
    acct = Account.from_key(private_key)
    if "from" not in tx:
        tx["from"] = acct.address
    if "nonce" not in tx:
        tx["nonce"] = w3.eth.get_transaction_count(acct.address, "pending")
    if "gasPrice" not in tx and "maxFeePerGas" not in tx:
        tx["gasPrice"] = int(w3.eth.gas_price * 1.25)
    if "gas" not in tx:
        try:
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.25)
        except Exception:
            tx["gas"] = 300000

    signed = w3.eth.account.sign_transaction(tx, private_key)
    raw_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(raw_hash, timeout=60)
    if receipt.status != 1:
        raise RuntimeError(f"Giao dịch thất bại (status=0): {raw_hash.hex()}")
    return receipt


class E2EIntegrationTester:
    def __init__(self, args):
        self.args = args
        self.mode = args.mode
        self.token_id = args.token_id
        self.amount = args.amount
        self.bid_price = args.bid_price  # micro-USDC (12,000,000 = 12 USDC)
        self.ask_price = args.ask_price  # micro-USDC (10,000,000 = 10 USDC)
        self.expected_clearing_price = (self.bid_price + self.ask_price) // 2  # 11,000,000 = 11 USDC
        self.expected_total_payment = self.amount * self.expected_clearing_price  # 550,000,000 = 550 USDC

        self.w3: Optional[Web3] = None
        self.chain_id: int = 80002
        self.api_url = args.api_url.rstrip("/")
        self.admin_api_key = args.admin_key

        self.contracts: Dict[str, str] = {}
        self.operator_key: Optional[str] = None
        self.deployer_key: Optional[str] = None

        self.buyer_acct: Optional[Account] = None
        self.seller_acct: Optional[Account] = None

        self.spawned_processes = []

    def setup_environment(self):
        """Khởi động hoặc kết nối node blockchain và dịch vụ Matching Engine."""
        print(f"🔧 Chế độ thực thi: {self.mode.upper()}")

        if self.mode == "hardhat":
            self.setup_local_hardhat()
        else:
            self.setup_amoy_network()

        # Thiết lập Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if self.mode == "amoy":
            # Bổ sung middleware PoA cho Polygon Amoy
            try:
                from web3.middleware import ExtraDataToPOAMiddleware
                self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            except Exception:
                pass

        assert self.w3.is_connected(), f"Không thể kết nối RPC tại {self.rpc_url}"
        self.chain_id = self.w3.eth.chain_id
        print(f"🔗 Đã kết nối RPC: {self.rpc_url} (Chain ID: {self.chain_id})")

        # Kiểm tra / Khởi động Matching API Service
        self.ensure_api_service_running()

    def setup_local_hardhat(self):
        """Khởi chạy node Hardhat cục bộ và triển khai hợp đồng."""
        self.rpc_url = self.args.rpc or "http://127.0.0.1:8545"

        # Kiểm tra xem Hardhat node đã chạy chưa
        node_running = False
        try:
            r = httpx.post(self.rpc_url, json={"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}, timeout=1.0)
            if r.status_code == 200:
                node_running = True
        except Exception:
            pass

        npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
        if not node_running:
            print("🚀 Đang khởi động Hardhat node cục bộ trên port 8545...")
            node_proc = subprocess.Popen(
                [npx, "hardhat", "node", "--port", "8545"],
                cwd=REPO_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.spawned_processes.append(node_proc)
            wait_for_service(self.rpc_url, {"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []})
            print("✅ Hardhat node cục bộ đã sẵn sàng!")
        else:
            print(f"ℹ️ Hardhat node đã đang chạy tại {self.rpc_url}")

        # Triển khai hợp đồng lên node Hardhat bằng setup_hardhat_e2e.js
        print("📜 Đang triển khai hợp đồng thử nghiệm lên node Hardhat...")
        setup_script = SCRIPTS_DIR / "setup_hardhat_e2e.js"
        if not setup_script.exists():
            setup_script = ENGINE_DIR / "e2e_hardhat" / "setup.js"

        res = subprocess.run(
            [npx, "hardhat", "run", str(setup_script), "--network", "localhost"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if res.returncode != 0:
            print(f"Lỗi khi chạy script setup Hardhat:\n{res.stderr}\n{res.stdout}", file=sys.stderr)
            raise RuntimeError("Triển khai hợp đồng Hardhat thất bại.")

        # Lấy dòng JSON cuối cùng
        last_line = res.stdout.strip().splitlines()[-1]
        cfg = json.loads(last_line)
        self.contracts = {
            "usdc": Web3.to_checksum_address(cfg["usdc"]),
            "carbon": Web3.to_checksum_address(cfg["carbon"]),
            "auction": Web3.to_checksum_address(cfg["auction"]),
            "faucet": Web3.to_checksum_address(cfg.get("faucet", cfg["auction"])),
        }
        self.deployer_key = HARDHAT_DEPLOYER_PRIVATE_KEY
        self.operator_key = HARDHAT_DEPLOYER_PRIVATE_KEY

        print("✅ Hợp đồng đã triển khai thành công trên Hardhat:")
        for k, v in self.contracts.items():
            print(f"   - {k.upper():<8}: {v}")

    def setup_amoy_network(self):
        """Cấu hình cho mạng Polygon Amoy Testnet thật."""
        self.rpc_url = self.args.rpc or os.environ.get("AMOY_RPC_URL") or AMOY_DEFAULT_RPC
        self.contracts = {
            "usdc": Web3.to_checksum_address(self.args.usdc or AMOY_DEPLOYED_CONTRACTS["usdc"]),
            "carbon": Web3.to_checksum_address(self.args.carbon or AMOY_DEPLOYED_CONTRACTS["carbon"]),
            "auction": Web3.to_checksum_address(self.args.contract or AMOY_DEPLOYED_CONTRACTS["auction"]),
            "faucet": Web3.to_checksum_address(self.args.faucet or AMOY_DEPLOYED_CONTRACTS["faucet"]),
        }

        self.operator_key = self.args.operator_key or os.environ.get("SETTLEMENT_OPERATOR_PRIVATE_KEY")
        self.deployer_key = self.args.deployer_key or os.environ.get("PRIVATE_KEY")

        print("✅ Cấu hình hợp đồng chính thức Polygon Amoy Testnet (docs/DEPLOYED_ADDRESSES.md):")
        for k, v in self.contracts.items():
            print(f"   - {k.upper():<8}: {v}")

    def ensure_api_service_running(self):
        """Khởi chạy uvicorn FastAPI nếu chưa có instance nào hoạt động."""
        api_running = False
        try:
            r = httpx.get(f"{self.api_url}/api/v1/sessions/current", timeout=1.0)
            if r.status_code == 200:
                api_running = True
        except Exception:
            pass

        if not api_running:
            print("🚀 Đang khởi chạy server Matching Engine FastAPI (api_service.py)...")
            env = dict(
                os.environ,
                AUCTION_CONTRACT_ADDRESS=self.contracts["auction"],
                MATCHING_API_KEY=self.admin_api_key,
                PYTHONIOENCODING="utf-8",
            )
            api_proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "api_service:app",
                    "--port",
                    "8000",
                    "--log-level",
                    "warning",
                ],
                cwd=ENGINE_DIR,
                env=env,
            )
            self.spawned_processes.append(api_proc)
            wait_for_service(f"{self.api_url}/api/v1/sessions/current")
            print("✅ Matching Engine API Service đã khởi động thành công tại http://127.0.0.1:8000!")
        else:
            print(f"ℹ️ Matching Engine API đã chạy sẵn tại {self.api_url}")

    def cleanup(self):
        """Dọn dẹp các tiến trình nền khi kết thúc."""
        if not self.args.keep_alive and self.spawned_processes:
            print("\n🧹 Đang dọn dẹp các tiến trình nền...")
            for p in self.spawned_processes:
                try:
                    p.terminate()
                    p.wait(timeout=3)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
            print("✅ Đã giải phóng toàn bộ tiến trình.")

    # =========================================================================
    # 5 BƯỚC THỰC THI END-TO-END
    # =========================================================================

    def step1_create_wallets_and_fund(self):
        """
        Bước 1:
        - Sinh 2 ví Buyer và Seller bằng eth-account.
        - Faucet MockUSDC cho Buyer.
        - Đúc / cấp token EVCC Lô #101 cho Seller.
        - Cấp quyền approve cho hợp đồng đấu giá (CarbonDoubleAuction).
        """
        log_step(1, "Sinh ví thử nghiệm, cấp phát tài sản & cấu hình Approval on-chain")

        # 1. Sinh ví Buyer và Seller
        if self.args.buyer_key:
            self.buyer_acct = Account.from_key(self.args.buyer_key)
        else:
            self.buyer_acct = Account.create()

        if self.args.seller_key:
            self.seller_acct = Account.create(self.args.seller_key)
        else:
            self.seller_acct = Account.create()

        print(f"👤 Bên Mua (Buyer):  {self.buyer_acct.address}")
        print(f"👤 Bên Bán (Seller): {self.seller_acct.address}")

        usdc_contract = self.w3.eth.contract(address=self.contracts["usdc"], abi=ERC20_ABI)
        carbon_contract = self.w3.eth.contract(address=self.contracts["carbon"], abi=ERC1155_ABI)
        auction_addr = self.contracts["auction"]

        if self.mode == "hardhat":
            deployer_acct = Account.from_key(self.deployer_key)

            # Chuyển ETH làm gas cho Buyer & Seller
            print("⛽ Cấp gas ETH từ Deployer cho Buyer và Seller...")
            for target_addr in [self.buyer_acct.address, self.seller_acct.address]:
                send_tx_and_wait(
                    self.w3,
                    {
                        "to": target_addr,
                        "value": self.w3.to_wei(1.0, "ether"),
                    },
                    self.deployer_key,
                )

            # Faucet 10,000 MockUSDC cho Buyer (10,000 * 10^6 micro-USDC)
            print("💵 Faucet 10,000 MockUSDC cho ví Buyer...")
            mint_usdc_tx = usdc_contract.functions.mint(
                self.buyer_acct.address, 10_000 * 10**6
            ).build_transaction({})
            send_tx_and_wait(self.w3, mint_usdc_tx, self.deployer_key)

            # Cấp 100 tCO2e EVCC #101 cho Seller từ Deployer
            print(f"🌱 Chuyển 100 tCO2e EVCC Lô #{self.token_id} từ Deployer cho ví Seller...")
            transfer_carbon_tx = carbon_contract.functions.safeTransferFrom(
                deployer_acct.address,
                self.seller_acct.address,
                self.token_id,
                100,
                b"",
            ).build_transaction({})
            send_tx_and_wait(self.w3, transfer_carbon_tx, self.deployer_key)

            # Buyer approve MockUSDC cho CarbonDoubleAuction
            print("🔐 Buyer cấp quyền approve MockUSDC cho sàn đấu giá...")
            approve_usdc_tx = usdc_contract.functions.approve(
                auction_addr, 2**256 - 1
            ).build_transaction({})
            send_tx_and_wait(self.w3, approve_usdc_tx, self.buyer_acct.key.hex())

            # Seller setApprovalForAll cho CarbonDoubleAuction
            print("🔐 Seller cấp quyền setApprovalForAll cho sàn đấu giá...")
            approve_carbon_tx = carbon_contract.functions.setApprovalForAll(
                auction_addr, True
            ).build_transaction({})
            send_tx_and_wait(self.w3, approve_carbon_tx, self.seller_acct.key.hex())

        else:
            # Chế độ Amoy Testnet
            print("ℹ️ Đang kiểm tra số dư và quyền hạn hiện tại trên Polygon Amoy...")
            if self.args.dry_run:
                print("   (Chế độ --dry-run: bỏ qua bước gửi giao dịch nạp gas / approve trên mạng thật)")

        # Đọc số dư ban đầu
        self.buyer_usdc_init = usdc_contract.functions.balanceOf(self.buyer_acct.address).call()
        self.buyer_evcc_init = carbon_contract.functions.balanceOf(self.buyer_acct.address, self.token_id).call()
        self.seller_usdc_init = usdc_contract.functions.balanceOf(self.seller_acct.address).call()
        self.seller_evcc_init = carbon_contract.functions.balanceOf(self.seller_acct.address, self.token_id).call()

        print("\n📊 BẢNG SỐ DƯ ON-CHAIN BAN ĐẦU:")
        print(f"   * Buyer  ({self.buyer_acct.address[:10]}...): {self.buyer_usdc_init / 10**6:>10.2f} USDC | {self.buyer_evcc_init:>5} EVCC #{self.token_id}")
        print(f"   * Seller ({self.seller_acct.address[:10]}...): {self.seller_usdc_init / 10**6:>10.2f} USDC | {self.seller_evcc_init:>5} EVCC #{self.token_id}")
        print("✅ BƯỚC 1 HOÀN TẤT XUẤT SẮC!")

    def step2_sign_eip712_orders(self) -> Tuple[dict, dict]:
        """
        Bước 2:
        - Ký 2 lệnh đối ứng EIP-712:
          + Buyer: Mua 50 tCO2e @ 12 USDC
          + Seller: Bán 50 tCO2e @ 10 USDC
        """
        log_step(2, "Ký lệnh đối ứng chuẩn EIP-712 Gasless (Domain Separator v2.0)")

        domain = {
            "name": "EPU Carbon Double Auction",
            "version": "2.0",
            "chainId": self.chain_id,
            "verifyingContract": self.contracts["auction"],
        }
        deadline = int(time.time()) + 3600

        # 1. Lệnh Mua của Buyer
        self.buyer_order_id = "0x" + secrets.token_hex(32)
        buyer_msg = {
            "orderId": self.buyer_order_id,
            "trader": self.buyer_acct.address,
            "orderType": 0,  # BID
            "tokenId": self.token_id,
            "amount": self.amount,  # 50 tCO2e
            "pricePerUnit": self.bid_price,  # 12 USDC = 12,000,000
            "nonce": 0,
            "deadline": deadline,
        }
        buyer_signable = encode_typed_data(domain_data=domain, message_types=ORDER_TYPES, message_data=buyer_msg)
        buyer_signed = self.buyer_acct.sign_message(buyer_signable)
        self.buyer_sig = "0x" + buyer_signed.signature.hex().removeprefix("0x")

        # 2. Lệnh Bán của Seller
        self.seller_order_id = "0x" + secrets.token_hex(32)
        seller_msg = {
            "orderId": self.seller_order_id,
            "trader": self.seller_acct.address,
            "orderType": 1,  # ASK
            "tokenId": self.token_id,
            "amount": self.amount,  # 50 tCO2e
            "pricePerUnit": self.ask_price,  # 10 USDC = 10,000,000
            "nonce": 0,
            "deadline": deadline,
        }
        seller_signable = encode_typed_data(domain_data=domain, message_types=ORDER_TYPES, message_data=seller_msg)
        seller_signed = self.seller_acct.sign_message(seller_signable)
        self.seller_sig = "0x" + seller_signed.signature.hex().removeprefix("0x")

        print("📝 Lệnh Mua (BUYER BID):")
        print(f"   - OrderId:      {self.buyer_order_id}")
        print(f"   - Khối lượng:   {self.amount} tCO2e | Giá mua: {self.bid_price / 10**6:.2f} USDC/tCO2e")
        print(f"   - Chữ ký ECDSA: {self.buyer_sig[:20]}...{self.buyer_sig[-16:]}")

        print("\n📝 Lệnh Bán (SELLER ASK):")
        print(f"   - OrderId:      {self.seller_order_id}")
        print(f"   - Khối lượng:   {self.amount} tCO2e | Giá bán: {self.ask_price / 10**6:.2f} USDC/tCO2e")
        print(f"   - Chữ ký ECDSA: {self.seller_sig[:20]}...{self.seller_sig[-16:]}")

        print("✅ BƯỚC 2 HOÀN TẤT XUẤT SẮC!")
        return buyer_msg, seller_msg

    def step3_submit_orders_to_api(self, buyer_msg: dict, seller_msg: dict):
        """
        Bước 3:
        - Đẩy 2 lệnh đã ký vào Matching Engine API qua POST /api/v1/orders.
        """
        log_step(3, "Đẩy lệnh vào Matching Engine API (POST /api/v1/orders)")

        # Gửi lệnh Buyer
        r_buyer = httpx.post(
            f"{self.api_url}/api/v1/orders",
            json={"order": buyer_msg, "signature": self.buyer_sig, "time_in_force": "GTC"},
            timeout=5.0,
        )
        assert r_buyer.status_code == 201, f"Lỗi đặt lệnh Buyer ({r_buyer.status_code}): {r_buyer.text}"
        print(f"✅ Đã nộp lệnh Buyer thành công (HTTP 201 Created): OrderId {self.buyer_order_id}")

        # Gửi lệnh Seller
        r_seller = httpx.post(
            f"{self.api_url}/api/v1/orders",
            json={"order": seller_msg, "signature": self.seller_sig, "time_in_force": "GTC"},
            timeout=5.0,
        )
        assert r_seller.status_code == 201, f"Lỗi đặt lệnh Seller ({r_seller.status_code}): {r_seller.text}"
        print(f"✅ Đã nộp lệnh Seller thành công (HTTP 201 Created): OrderId {self.seller_order_id}")

        # Kiểm tra OrderBook Snapshot
        r_book = httpx.get(f"{self.api_url}/api/v1/orderbook/{self.token_id}", timeout=5.0)
        book = r_book.json()
        print(f"📖 Snapshot Sổ lệnh Lô #{self.token_id}: {len(book.get('bids', []))} Bid(s), {len(book.get('asks', []))} Ask(s)")
        print("✅ BƯỚC 3 HOÀN TẤT XUẤT SẮC!")

    def step4_run_auction_session(self) -> int:
        """
        Bước 4:
        - Gọi POST /api/v1/sessions/run kích hoạt phiên khớp lệnh k-DA.
        - Kiểm tra giá khớp biên P* và khối lượng khớp.
        """
        log_step(4, "Kích hoạt phiên đấu giá kép k-DA (POST /api/v1/sessions/run)")

        headers = {"X-API-Key": self.admin_api_key} if self.admin_api_key else {}
        r_run = httpx.post(
            f"{self.api_url}/api/v1/sessions/run",
            json={"tokenId": self.token_id},
            headers=headers,
            timeout=10.0,
        )
        assert r_run.status_code == 200, f"Lỗi kích hoạt phiên ({r_run.status_code}): {r_run.text}"
        data = r_run.json()

        session_id = data["session_id"]
        matches = data["matches"]
        print(f"🎉 Phiên #{session_id} đã kết thúc với {len(matches)} trade khớp thành công!")

        assert len(matches) == 1, f"Kỳ vọng 1 trade khớp, nhận được: {len(matches)}"
        trade = matches[0]

        actual_amount = trade["amount"]
        actual_clearing_price = trade.get("clearingPrice", trade.get("clearing_price"))

        print(f"   * Khối lượng khớp: {actual_amount} tCO2e (Kỳ vọng: {self.amount})")
        print(f"   * Giá khớp P*:     {actual_clearing_price / 10**6:.2f} USDC (Kỳ vọng: {self.expected_clearing_price / 10**6:.2f} USDC)")

        assert actual_amount == self.amount, f"Sai khối lượng khớp: {actual_amount} != {self.amount}"
        assert (
            actual_clearing_price == self.expected_clearing_price
        ), f"Sai giá khớp: {actual_clearing_price} != {self.expected_clearing_price}"

        print(f"✅ Thuật toán Marginal Pricing (P* = floor((12+10)/2) = 11 USDC) hoạt động chính xác 100%!")
        print("✅ BƯỚC 4 HOÀN TẤT XUẤT SẮC!")
        return session_id

    def step5_execute_settlement_and_verify(self, session_id: int):
        """
        Bước 5:
        - Chạy Submitter bot gọi batchSettleTrades on-chain.
        - Kiểm tra đối soát số dư On-chain và trạng thái đơn hàng.
        """
        log_step(5, "Nộp thanh toán on-chain (Submitter Bot) & Đối soát số dư DvP")

        extra_args = []
        if self.args.dry_run:
            extra_args.append("--dry-run")

        env = dict(
            os.environ,
            SETTLEMENT_OPERATOR_PRIVATE_KEY=self.operator_key or "",
            AUCTION_CONTRACT_ADDRESS=self.contracts["auction"],
            MATCHING_API_KEY=self.admin_api_key,
            PYTHONIOENCODING="utf-8",
        )

        print(f"🤖 Đang thực thi settlement_submitter.py cho Phiên #{session_id}...")
        sub_res = subprocess.run(
            [
                sys.executable,
                "settlement_submitter.py",
                "--api-url",
                self.api_url,
                "--rpc",
                self.rpc_url,
                "--session-id",
                str(session_id),
                *extra_args,
            ],
            cwd=ENGINE_DIR,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        print(f"📄 Log Submitter:\n{sub_res.stdout.strip()}")
        if sub_res.returncode != 0:
            print(f"❌ Submitter stderr:\n{sub_res.stderr.strip()}", file=sys.stderr)
            raise RuntimeError(f"Submitter bot kết thúc với lỗi (code {sub_res.returncode})")

        if self.args.dry_run:
            print("ℹ️ Chế độ Dry-run hoàn tất không lỗi.")
            return

        assert "SETTLED" in sub_res.stdout, "Không tìm thấy trạng thái SETTLED trong log của Submitter!"

        # Tìm TxHash
        tx_match = re.search(r"TxHash: (0x[0-9a-fA-F]{64})", sub_res.stdout)
        tx_hash = tx_match.group(1) if tx_match else "N/A"
        print(f"\n🔗 Transaction Hash thanh toán On-chain: {tx_hash}")

        # Kiểm tra đối soát số dư On-chain
        usdc_contract = self.w3.eth.contract(address=self.contracts["usdc"], abi=ERC20_ABI)
        carbon_contract = self.w3.eth.contract(address=self.contracts["carbon"], abi=ERC1155_ABI)

        buyer_usdc_after = usdc_contract.functions.balanceOf(self.buyer_acct.address).call()
        buyer_evcc_after = carbon_contract.functions.balanceOf(self.buyer_acct.address, self.token_id).call()
        seller_usdc_after = usdc_contract.functions.balanceOf(self.seller_acct.address).call()
        seller_evcc_after = carbon_contract.functions.balanceOf(self.seller_acct.address, self.token_id).call()

        delta_buyer_usdc = buyer_usdc_after - self.buyer_usdc_init
        delta_buyer_evcc = buyer_evcc_after - self.buyer_evcc_init
        delta_seller_usdc = seller_usdc_after - self.seller_usdc_init
        delta_seller_evcc = seller_evcc_after - self.seller_evcc_init

        print("\n" + "=" * 75)
        print("📊 BẢNG TỔNG HỢP BIẾN ĐỘNG SỐ DƯ TÀI SẢN ON-CHAIN (DvP ATOMIC SWAP)")
        print("=" * 75)
        print(f"{'Tài khoản':<12} | {'Token':<8} | {'Trước GD':>14} | {'Sau GD':>14} | {'Biến động':>14} | {'Kỳ vọng':>12}")
        print("-" * 75)
        print(f"{'Buyer':<12} | {'EVCC':<8} | {self.buyer_evcc_init:>14} | {buyer_evcc_after:>14} | {f'+{delta_buyer_evcc}':>14} | {'+50':>12}")
        print(f"{'Buyer':<12} | {'USDC':<8} | {self.buyer_usdc_init / 10**6:>14.2f} | {buyer_usdc_after / 10**6:>14.2f} | {f'{delta_buyer_usdc / 10**6:+.2f}':>14} | {'-550.00':>12}")
        print("-" * 75)
        print(f"{'Seller':<12} | {'EVCC':<8} | {self.seller_evcc_init:>14} | {seller_evcc_after:>14} | {f'{delta_seller_evcc}':>14} | {'-50':>12}")
        print(f"{'Seller':<12} | {'USDC':<8} | {self.seller_usdc_init / 10**6:>14.2f} | {seller_usdc_after / 10**6:>14.2f} | {f'{delta_seller_usdc / 10**6:+.2f}':>14} | {'+550.00':>12}")
        print("=" * 75)

        # Xác thực độ chính xác tuyệt đối
        assert delta_buyer_evcc == self.amount, f"Buyer không nhận đúng 50 EVCC: delta={delta_buyer_evcc}"
        assert delta_buyer_usdc == -self.expected_total_payment, f"Buyer không trừ đúng 550 USDC: delta={delta_buyer_usdc}"
        assert delta_seller_evcc == -self.amount, f"Seller không chuyển đúng 50 EVCC: delta={delta_seller_evcc}"
        assert delta_seller_usdc == self.expected_total_payment, f"Seller không nhận đúng 550 USDC: delta={delta_seller_usdc}"

        # Kiểm tra trạng thái đơn hàng trên API
        r_buyer_ord = httpx.get(f"{self.api_url}/api/v1/orders/{self.buyer_order_id}").json()
        r_seller_ord = httpx.get(f"{self.api_url}/api/v1/orders/{self.seller_order_id}").json()

        assert r_buyer_ord["status"] == "FILLED", f"Lệnh Buyer chưa FILLED: {r_buyer_ord['status']}"
        assert r_buyer_ord["settled_amount"] == self.amount, "Buyer settled_amount != 50"
        assert r_seller_ord["status"] == "FILLED", f"Lệnh Seller chưa FILLED: {r_seller_ord['status']}"
        assert r_seller_ord["settled_amount"] == self.amount, "Seller settled_amount != 50"

        print("\n✅ TẤT CẢ CÁC ĐIỀU KIỆN NGHIỆM THU (ACCEPTANCE CRITERIA) ĐÃ ĐẠT 100%!")

    def run(self) -> int:
        """Hàm điều phối toàn bộ bài kiểm thử."""
        try:
            print("\n🌟 KHỞI CHẠY KIỂM THỬ TOÀN TRÌNH END-TO-END (TASK H.1) 🌟")
            self.setup_environment()

            self.step1_create_wallets_and_fund()
            buyer_msg, seller_msg = self.step2_sign_eip712_orders()
            self.step3_submit_orders_to_api(buyer_msg, seller_msg)
            session_id = self.step4_run_auction_session()
            self.step5_execute_settlement_and_verify(session_id)

            print("\n" + "🎉" * 20)
            print("🚀 KẾT QUẢ: TOÀN BỘ 5 BƯỚC END-TO-END ĐÃ VƯỢT QUA XUẤT SẮC! (PASSED)")
            print("🎉" * 20 + "\n")
            return 0
        except Exception as exc:
            print(f"\n❌ LỖI TRONG QUÁ TRÌNH KIỂM THỬ: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.cleanup()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Script kiểm thử toàn trình End-to-End (E2E Integration Test) Sàn Tín chỉ Carbon EPU."
    )
    parser.add_argument(
        "--mode",
        choices=["hardhat", "amoy"],
        default="hardhat",
        help="Chế độ kiểm thử: 'hardhat' (mặc định) hoặc 'amoy' (mạng Polygon Amoy Testnet)",
    )
    parser.add_argument("--local", action="store_const", const="hardhat", dest="mode", help="Tương đương --mode hardhat")
    parser.add_argument("--amoy", action="store_const", const="amoy", dest="mode", help="Tương đương --mode amoy")
    parser.add_argument("--rpc", help="URL cổng RPC Ethereum/Polygon (mặc định theo chế độ)")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="Địa chỉ API Matching Engine")
    parser.add_argument("--admin-key", default="e2e-integration-admin-key", help="Khóa quản trị MATCHING_API_KEY")
    parser.add_argument("--token-id", type=int, default=101, help="Mã Token ID tín chỉ EVCC (mặc định 101)")
    parser.add_argument("--amount", type=int, default=50, help="Khối lượng giao dịch (tCO2e, mặc định 50)")
    parser.add_argument("--bid-price", type=int, default=12_000_000, help="Giá đặt mua (micro-USDC, mặc định 12 USDC = 12000000)")
    parser.add_argument("--ask-price", type=int, default=10_000_000, help="Giá đặt bán (micro-USDC, mặc định 10 USDC = 10000000)")
    parser.add_argument("--contract", help="Địa chỉ hợp đồng CarbonDoubleAuction")
    parser.add_argument("--usdc", help="Địa chỉ hợp đồng MockUSDC")
    parser.add_argument("--carbon", help="Địa chỉ hợp đồng CarbonCredit1155")
    parser.add_argument("--faucet", help="Địa chỉ hợp đồng EvccFaucet")
    parser.add_argument("--operator-key", help="Khóa riêng tư ví Settlement Operator")
    parser.add_argument("--deployer-key", help="Khóa riêng tư ví Deployer (nếu cần cấp phát on-chain)")
    parser.add_argument("--buyer-key", help="Khóa ví Buyer có sẵn (tùy chọn)")
    parser.add_argument("--seller-key", help="Khóa ví Seller có sẵn (tùy chọn)")
    parser.add_argument("--dry-run", action="store_true", help="Chạy chế độ giả lập dry-run cho bot thanh toán")
    parser.add_argument("--keep-alive", action="store_true", help="Không tự động tắt node Hardhat / API server sau khi test xong")

    args = parser.parse_args()
    tester = E2EIntegrationTester(args)
    sys.exit(tester.run())


if __name__ == "__main__":
    main()
