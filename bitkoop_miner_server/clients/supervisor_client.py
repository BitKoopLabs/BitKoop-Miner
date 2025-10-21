from typing import Any, Dict, List, Optional

import httpx
from fiber.logging_utils import get_logger
from pydantic import BaseModel, Field

from bitkoop_miner_server.config import get_config

logger = get_logger(__name__)


class PagedResponse(BaseModel):
    page: int
    limit: int
    total: int
    has_next_page: bool = Field(alias="hasNextPage")
    data: List[Dict[str, Any]]

    class Config:
        populate_by_name = True


class SupervisorSite(BaseModel):
    store_id: int
    store_domain: str
    store_status: int
    miner_hotkey: Optional[str] = None
    api_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    total_coupon_slots: int = 15


class ProductCategory(BaseModel):
    category_id: int
    category_name: str


class SupervisorClient:
    def __init__(self, timeout: int = 30):
        config = get_config()
        self.base_url = config.supervisor_api_url
        self.timeout = timeout

    async def get_sites(
        self, page: int = 1, page_size: int = 100
    ) -> PagedResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"page": page, "page_size": page_size}
            response = await client.get(f"{self.base_url}/sites", params=params)
            response.raise_for_status()
            return PagedResponse(**response.json())

    async def get_product_categories(
        self, page: int = 1, page_size: int = 100
    ) -> PagedResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"page": page, "page_size": page_size}
            response = await client.get(
                f"{self.base_url}/product-categories", params=params
            )
            response.raise_for_status()
            return PagedResponse(**response.json())
