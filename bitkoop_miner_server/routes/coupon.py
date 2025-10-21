from datetime import datetime

from fastapi import APIRouter, Depends
from fiber.miner.dependencies import verify_request

from bitkoop_miner_server.config import get_config
from bitkoop_miner_server.constants import JobStatus
from bitkoop_miner_server.database import (
    create_job,
    get_coupon_stats,
    get_job,
    get_site,
    upsert_coupon_stats,
)
from bitkoop_miner_server.exceptions import SiteNotFoundError
from bitkoop_miner_server.models import CouponCheckRequest, CouponCheckResponse
from bitkoop_miner_server.utils import (
    calculate_staleness_seconds,
    generate_job_id,
    is_stale,
)

router = APIRouter(prefix="/coupon", tags=["coupon"])


@router.post("/check", response_model=CouponCheckResponse)
async def check_coupon(
    request: CouponCheckRequest,
    _verified: dict = Depends(verify_request),
):
    config = get_config()

    site = get_site(request.site_id)
    if not site:
        raise SiteNotFoundError(request.site_id)

    stats = get_coupon_stats(request.site_id, request.coupon_code)
    forced_run = True

    if stats and not is_stale(
        datetime.fromisoformat(stats["last_run_at"].replace("Z", "+00:00")),
        config.check_staleness_hours,
    ):
        forced_run = False
        existing_job = get_job(stats["last_job_id"])
        if existing_job:
            return CouponCheckResponse(
                job_id=existing_job["job_id"],
                forced_run=forced_run,
                job_start_time=existing_job["job_start_time"],
                staleness_seconds=calculate_staleness_seconds(
                    config.check_staleness_hours
                ),
            )

    job_id = generate_job_id()
    job_data = create_job(
        job_id, request.site_id, request.coupon_code, status=JobStatus.PENDING
    )
    upsert_coupon_stats(request.site_id, request.coupon_code, job_id)

    return CouponCheckResponse(
        job_id=job_data["job_id"],
        forced_run=forced_run,
        job_start_time=job_data["job_start_time"],
        staleness_seconds=calculate_staleness_seconds(config.check_staleness_hours),
    )
