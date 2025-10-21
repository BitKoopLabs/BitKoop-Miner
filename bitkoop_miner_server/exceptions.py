from typing import Any, Optional


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class HotkeyMismatchError(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            code="HOTKEY_MISMATCH",
            message="Provided miner_hotkey does not match server hotkey",
        )


class JobNotFoundError(AppException):
    def __init__(self, job_id: str):
        super().__init__(
            status_code=404,
            code="JOB_NOT_FOUND",
            message="Job not found",
            details={"job_id": job_id},
        )


class SiteNotFoundError(AppException):
    def __init__(self, site_id: int):
        super().__init__(
            status_code=404,
            code="SITE_NOT_FOUND",
            message="Site not found",
            details={"site_id": site_id},
        )
