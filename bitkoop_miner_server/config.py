import os
from dataclasses import dataclass


@dataclass
class Config:
    wallet_name: str
    hotkey_name: str
    check_staleness_hours: int
    run_timeout_seconds: int
    job_retention_hours: int
    database_url: str
    tlsnotary_url: str
    tlsnotary_mode: str
    supervisor_api_url: str
    sync_sites_interval_seconds: int


def get_config() -> Config:
    return Config(
        wallet_name=os.getenv("WALLET_NAME", "default"),
        hotkey_name=os.getenv("HOTKEY_NAME", "default"),
        check_staleness_hours=int(os.getenv("CHECK_STALENESS_HOURS", "24")),
        run_timeout_seconds=int(os.getenv("RUN_TIMEOUT_SECONDS", "300")),
        job_retention_hours=int(os.getenv("JOB_RETENTION_HOURS", "168")),
        database_url=os.getenv(
            "DATABASE_URL", "postgresql://miner:miner_pass@localhost:5432/bitkoop_miner"
        ),
        tlsnotary_url=os.getenv("TLSNOTARY_URL", "http://localhost:7047"),
        tlsnotary_mode=os.getenv("TLSNOTARY_MODE", "mock"),
        supervisor_api_url=os.getenv("SUPERVISOR_API_URL", "http://91.99.203.36/api"),
        sync_sites_interval_seconds=int(os.getenv("SYNC_SITES_INTERVAL_SECONDS", "600")),
    )
