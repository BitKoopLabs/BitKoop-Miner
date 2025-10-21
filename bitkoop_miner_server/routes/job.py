from fastapi import APIRouter
import httpx
from fiber.logging_utils import get_logger

from bitkoop_miner_server.config import get_config
from bitkoop_miner_server.constants import JobStatus
from bitkoop_miner_server.database import get_job
from bitkoop_miner_server.exceptions import JobNotFoundError
from bitkoop_miner_server.models import JobResponse

router = APIRouter(prefix="/job", tags=["job"])
logger = get_logger(__name__)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)

    result = job.get("result")

    if job["status"] == JobStatus.SUCCEEDED and result and result.get("proof_filename"):
        config = get_config()
        proof_filename = result["proof_filename"]
        proof_url = f"{config.tls_js_url}/api/proofs/{proof_filename}"

        try:
            logger.info(f"Fetching proof from {proof_url} for job {job_id}")
            async with httpx.AsyncClient(timeout=30) as client:
                proof_response = await client.get(proof_url)
                proof_response.raise_for_status()
                proof_data = proof_response.json()

            result = proof_data
            logger.info(f"Proof fetched successfully for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to fetch proof for job {job_id}: {e}")
            result = {"error": str(e)}

    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        job_start_time=job["job_start_time"],
        result=result,
        error=job.get("error"),
    )
