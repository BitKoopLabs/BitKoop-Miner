from fastapi import APIRouter

from bitkoop_miner_server.database import get_job
from bitkoop_miner_server.exceptions import JobNotFoundError
from bitkoop_miner_server.models import JobResponse

router = APIRouter(prefix="/job", tags=["job"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)

    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        job_start_time=job["job_start_time"],
        result=job.get("result"),
        error=job.get("error"),
    )
