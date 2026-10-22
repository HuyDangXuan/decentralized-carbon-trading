"""
Sub-Agent 3: MRV & Project Verification Agent (Tác tử Giám sát & Xác thực Dự án)
Chịu trách nhiệm:
1. Thẩm định dữ liệu đo đạc, báo cáo, thẩm tra (MRV) của các dự án xanh.
2. Chuẩn hóa siêu dữ liệu (Metadata) theo chuẩn ERC-1155.
3. Tạo mã băm SHA-256 / IPFS CID giả lập và cấp quyền phê duyệt phát hành token (Mint Approval).
"""

import hashlib
import json
import os
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MRVVerificationAgent:
    def __init__(self, verifier_name: str = "EPU_Decentralized_Carbon_Auditor"):
        self.verifier_name = verifier_name

    def verify_and_package_project(self, project_data: dict) -> dict:
        """
        Thẩm tra hồ sơ dự án giảm phát thải và đóng gói chuẩn Metadata IPFS.
        """
        required_fields = ["project_id", "project_name", "standard", "vintage_year", "co2_reduction_tCO2e", "developer_address"]
        for field in required_fields:
            if field not in project_data:
                raise ValueError(f"Thiếu trường dữ liệu bắt buộc: {field}")

        # Kiểm tra tính hợp lệ cơ bản
        if project_data["co2_reduction_tCO2e"] <= 0:
            raise ValueError("Khối lượng giảm phát thải CO2 phải lớn hơn 0")

        # Tạo gói Metadata chuẩn ERC-1155
        metadata = {
            "name": f"Carbon Credit - {project_data['project_name']} ({project_data['vintage_year']})",
            "description": f"Verified Carbon Credit under standard {project_data['standard']}",
            "image": "ipfs://bafybeihdwdcefgh4dqkjv678projectcoverimage",
            "properties": {
                "project_id": project_data["project_id"],
                "standard": project_data["standard"],  # Verra / Gold Standard / CDM / Vietnam VCM
                "vintage_year": project_data["vintage_year"],
                "total_issued_tCO2e": project_data["co2_reduction_tCO2e"],
                "developer": project_data["developer_address"],
                "verifier": self.verifier_name,
                "verified_at": int(time.time()),
                "status": "VERIFIED_ACTIVE"
            }
        }

        # Tạo mã băm tính toàn vẹn (Integrity Hash)
        metadata_str = json.dumps(metadata, sort_keys=True)
        content_hash = hashlib.sha256(metadata_str.encode('utf-8')).hexdigest()
        simulated_ipfs_cid = f"ipfs://QmCarbon{content_hash[:40]}"

        result = {
            "is_valid": True,
            "project_id": project_data["project_id"],
            "ipfs_uri": simulated_ipfs_cid,
            "metadata_hash": "0x" + content_hash,
            "approved_amount": project_data["co2_reduction_tCO2e"],
            "metadata": metadata
        }
        return result

if __name__ == "__main__":
    agent = MRVVerificationAgent()
    sample_project = {
        "project_id": "VN-FOR-2026-001",
        "project_name": "Dự án Trồng Rừng Phòng Hộ Tây Bắc",
        "standard": "Verra VCS + CCB",
        "vintage_year": 2026,
        "co2_reduction_tCO2e": 5000,
        "developer_address": "0x71C...B29"
    }

    print("--- THẨM ĐỊNH HỒ SƠ DỰ ÁN GIẢM PHÁT THẢI (MRV AGENT) ---")
    verified = agent.verify_and_package_project(sample_project)
    print(f"Dự án: {sample_project['project_name']}")
    print(f"Trạng thái: ĐÃ XÁC THỰC (VALID)")
    print(f"Số lượng tín chỉ phê duyệt đúc: {verified['approved_amount']} tCO2e")
    print(f"IPFS CID sinh ra: {verified['ipfs_uri']}")
    print(f"Mã Hash toàn vẹn (On-chain proof): {verified['metadata_hash']}")
