from bitkoop_miner_server.routes.coupon import router as coupon_router
from bitkoop_miner_server.routes.health import router as health_router
from bitkoop_miner_server.routes.job import router as job_router

__all__ = ["health_router", "coupon_router", "job_router"]
