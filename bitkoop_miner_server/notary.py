from typing import Any, Dict

import httpx

from bitkoop_miner_server.config import get_config


async def create_attestation(
    job_id: str, session_evidence: Dict[str, Any]
) -> Dict[str, str]:
    config = get_config()

    if config.tlsnotary_mode == "mock":
        return _mock_attestation(job_id)

    return await _request_attestation(
        session_evidence, config.tlsnotary_url, config.run_timeout_seconds
    )


def _mock_attestation(job_id: str) -> Dict[str, str]:
    return {
        "attestation_id": f"mock_attest_{job_id}",
        "commitment": f"mock_commitment_{job_id[:8]}",
        "notary_pubkey": "mock_notary_key",
        "version": "mock",
    }


async def _request_attestation(
    session_evidence: Dict[str, Any], notary_url: str, timeout: int
) -> Dict[str, str]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{notary_url}/attest", json=session_evidence, timeout=float(timeout)
        )
        response.raise_for_status()
        return response.json()
