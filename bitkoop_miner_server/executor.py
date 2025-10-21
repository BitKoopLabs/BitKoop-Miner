from typing import Dict

import httpx
from fiber.logging_utils import get_logger

from bitkoop_miner_server.config import get_config
from bitkoop_miner_server.database import get_site

logger = get_logger(__name__)


async def execute_validation(job_id: str, site_id: int, coupon_code: str) -> Dict:
    config = get_config()

    site = get_site(site_id)
    if not site:
        logger.error(f"Site {site_id} not found in database")
        raise ValueError(f"Site {site_id} not found")

    domain = site["domain"]
    site_config = site.get("config")

    filename = f"proof_{site_id}_{coupon_code}_{job_id}"
    logger.info(f"Validating coupon {coupon_code} for domain {domain} (site_id={site_id})")

    payload = {
        "coupon": coupon_code,
        "domain": domain,
        "filename": filename
    }

    if site_config:
        payload["customActions"] = site_config

    async with httpx.AsyncClient(timeout=config.run_timeout_seconds) as client:
        response = await client.post(
            f"{config.tls_js_url}/api/validate-coupon",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            logger.error(f"Validation failed: {result.get('error', 'Unknown error')}")
            raise RuntimeError(f"Validation failed: {result.get('error', 'Unknown error')}")

    logger.info(f"Validation successful for job {job_id}")

    return {
        "success": True,
        "proof_filename": f"{filename}.json",
        "validation_result": result
    }
