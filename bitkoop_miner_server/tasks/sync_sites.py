import asyncio
import threading
from typing import Optional

from fiber.logging_utils import get_logger

from bitkoop_miner_server.clients import SupervisorClient
from bitkoop_miner_server.services import SiteService

logger = get_logger(__name__)

_stop_event: Optional[threading.Event] = None
_sync_thread: Optional[threading.Thread] = None


async def sync_sites_task():
    supervisor_client = SupervisorClient(timeout=30)
    site_service = SiteService()

    try:
        await site_service.sync_sites_from_supervisor(supervisor_client)
    except Exception as e:
        logger.error(f"Site sync task error: {e}")


def _run_sync_loop(stop_event: threading.Event, interval_seconds: int):
    logger.info(f"Sync loop starting (thread: {threading.current_thread().name})")
    logger.info(f"Stop event is_set: {stop_event.is_set()}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Event loop created successfully")
    except Exception as e:
        logger.error(f"Failed to create event loop: {e}", exc_info=True)
        return

    iteration = 0
    logger.info(f"Entering main loop, stop_event.is_set()={stop_event.is_set()}")

    while not stop_event.is_set():
        iteration += 1
        logger.info(f"Sync loop iteration {iteration} starting")

        try:
            logger.info(f"About to call sync_sites_task() for iteration {iteration}")
            loop.run_until_complete(sync_sites_task())
            logger.info(f"Sync loop iteration {iteration} completed successfully")
        except Exception as e:
            logger.error(f"Error in sync sites loop iteration {iteration}: {e}", exc_info=True)

        logger.info(f"Iteration {iteration} finished, about to wait {interval_seconds}s")

        logger.debug(f"Waiting {interval_seconds}s before next sync (iteration {iteration})")
        elapsed = 0
        while elapsed < interval_seconds and not stop_event.is_set():
            stop_event.wait(min(5, interval_seconds - elapsed))
            elapsed += 5

        logger.debug(f"Wait complete for iteration {iteration}, elapsed: {elapsed}s")

    logger.info(f"Sync loop stopped after {iteration} iterations")
    loop.close()


def start_sync_sites_task(interval_seconds: int = 600):
    global _stop_event, _sync_thread

    if _sync_thread and _sync_thread.is_alive():
        logger.warning("Site sync task already running")
        return

    _stop_event = threading.Event()
    _sync_thread = threading.Thread(
        target=_run_sync_loop,
        args=(_stop_event, interval_seconds),
        daemon=True,
        name="SiteSyncThread",
    )
    _sync_thread.start()
    logger.info(f"Site sync task started (interval: {interval_seconds}s)")


def stop_sync_sites_task():
    global _stop_event, _sync_thread

    if _stop_event:
        _stop_event.set()

    if _sync_thread and _sync_thread.is_alive():
        _sync_thread.join(timeout=10)
        logger.info("Site sync task stopped")
