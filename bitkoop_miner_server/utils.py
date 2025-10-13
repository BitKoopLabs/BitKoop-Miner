from datetime import datetime, timedelta, timezone

from ulid import ULID


def generate_job_id() -> str:
    return str(ULID())


def is_stale(last_run_at: datetime, staleness_hours: int) -> bool:
    return datetime.now(timezone.utc) - last_run_at > timedelta(hours=staleness_hours)


def calculate_staleness_seconds(staleness_hours: int) -> int:
    return staleness_hours * 3600


def to_iso_utc(dt: datetime) -> str:
    return dt.isoformat() + "Z"
