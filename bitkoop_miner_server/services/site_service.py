from fiber.logging_utils import get_logger

from bitkoop_miner_server.clients.supervisor_client import SupervisorSite
from bitkoop_miner_server.database import upsert_site

logger = get_logger(__name__)


class SiteService:
    async def sync_sites_from_supervisor(self, supervisor_client) -> int:
        page = 1
        total_processed = 0

        while True:
            try:
                response = await supervisor_client.get_sites(page=page, page_size=100)

                if not response.data:
                    break

                for site_data in response.data:
                    try:
                        site = SupervisorSite(**site_data)
                        upsert_site(
                            site_id=site.store_id,
                            base_url=site.store_domain,
                            status=site.store_status,
                            miner_hotkey=site.miner_hotkey,
                            api_url=site.api_url,
                            config=site.config,
                            total_coupon_slots=site.total_coupon_slots,
                        )
                        total_processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process site {site_data.get('store_id')}: {e}")
                        continue

                if not response.has_next_page:
                    break

                page += 1

            except Exception as e:
                logger.error(f"Failed to fetch sites from supervisor: {e}")
                break

        logger.info(f"Synced {total_processed} sites from supervisor")
        return total_processed
