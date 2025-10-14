import asyncio
import json
from pathlib import Path
from typing import Dict


async def execute_validation(job_id: str, site_id: int, coupon_code: str) -> Dict:
    await asyncio.sleep(30)

    mock_file = Path("/app/FE512M1.75871226110500000000000000000000.json")

    if mock_file.exists():
        with open(mock_file, "r") as f:
            attestation_data = json.load(f)

        return attestation_data
    else:
        return {
            "version": "0.1.0-alpha.12",
            "data": "mock_attestation_data_" + job_id[:16],
            "meta": {
                "notaryUrl": "http://localhost:7047",
                "websocketProxyUrl": "ws://127.0.0.1:55688",
                "site_id": site_id,
                "coupon_code": coupon_code,
                "job_id": job_id,
            }
        }
