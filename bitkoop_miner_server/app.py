from fastapi import Request
from fastapi.responses import JSONResponse
from fiber.logging_utils import get_logger
from fiber.miner.server import factory_app

from bitkoop_miner_server.exceptions import AppException
from bitkoop_miner_server.models import ErrorDetail, ErrorResponse
from bitkoop_miner_server.routes import coupon_router, health_router, job_router

logger = get_logger(__name__)

app = factory_app(debug=True)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    error_response = ErrorResponse(
        error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


app.include_router(health_router)
app.include_router(coupon_router)
app.include_router(job_router)
