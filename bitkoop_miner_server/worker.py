import asyncio
from fiber.logging_utils import get_logger

from bitkoop_miner_server.constants import JobStatus
from bitkoop_miner_server.database import get_pending_job, update_job_status
from bitkoop_miner_server.executor import execute_validation

logger = get_logger(__name__)


async def process_job(job):
    job_id = job["job_id"]

    try:
        logger.info(f"Processing job {job_id}")

        update_job_status(job_id, JobStatus.RUNNING)

        result = await execute_validation(job_id, job["site_id"], job["coupon_code"])

        update_job_status(job_id, JobStatus.SUCCEEDED, result=result)
        logger.info(f"Job {job_id} succeeded")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        update_job_status(job_id, JobStatus.FAILED, error=str(e))


async def run_worker():
    logger.info("Worker started")

    while True:
        try:
            job = get_pending_job()

            if job:
                await process_job(job)
            else:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_worker())
