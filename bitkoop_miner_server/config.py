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
    )
