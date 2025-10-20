
import asyncio
from contextlib import asynccontextmanager
from functools import partial

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fiber.logging_utils import get_logger

from bitkoop_miner_server.config import get_config
from bitkoop_miner_server.exceptions import AppException
from bitkoop_miner_server.models import ErrorDetail, ErrorResponse
from bitkoop_miner_server.routes import coupon_router, health_router, job_router
from bitkoop_miner_server.tasks import start_sync_sites_task, stop_sync_sites_task

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    try:
        config = get_config()
        start_sync_sites_task(config.sync_sites_interval_seconds)
        logger.info("Site sync task started")

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    stop_sync_sites_task()
    logger.info("Site sync task stopped")


app = FastAPI(
    title="BitKoop Miner",
    description="Miner service for BitKoop subnet",
    version="0.1.0",
    lifespan=lifespan,
)

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
