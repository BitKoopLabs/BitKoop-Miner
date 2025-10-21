from typing import Any, Optional

from pydantic import BaseModel, Field


class CouponCheckRequest(BaseModel):
    coupon_code: str
    site_id: int


class CouponCheckResponse(BaseModel):
    job_id: str
    forced_run: bool
    job_start_time: str
    staleness_seconds: int


class JobResponse(BaseModel):
    job_id: str
    status: int
    job_start_time: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
