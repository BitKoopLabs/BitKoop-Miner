from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from bitkoop_miner_server.config import get_config
from bitkoop_miner_server.constants import JobStatus
from bitkoop_miner_server.utils import to_iso_utc

config = get_config()
engine = create_engine(config.database_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    site_id = Column(Integer, nullable=False, index=True)
    coupon_code = Column(String, nullable=False, index=True)
    status = Column(Integer, nullable=False)
    job_start_time = Column(DateTime, nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, index=True)


class CouponStats(Base):
    __tablename__ = "coupon_stats"

    site_id = Column(Integer, primary_key=True)
    coupon_code = Column(String, primary_key=True)
    run_count = Column(Integer, nullable=False, default=0)
    last_run_at = Column(DateTime, nullable=False, index=True)
    last_job_id = Column(String, nullable=True)


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    base_url = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    config = Column(JSON, nullable=True)
    miner_hotkey = Column(String, nullable=True)
    api_url = Column(String, nullable=True)
    total_coupon_slots = Column(Integer, nullable=False, default=15)
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_job(
    job_id: str, site_id: int, coupon_code: str, status: int = JobStatus.PENDING
) -> dict:
    now = datetime.now(timezone.utc)
    with get_session() as session:
        job = Job(
            job_id=job_id,
            site_id=site_id,
            coupon_code=coupon_code,
            status=status,
            job_start_time=now,
            created_at=now
        )
        session.add(job)
    return {"job_id": job_id, "status": status, "job_start_time": to_iso_utc(now)}


def get_job(job_id: str) -> Optional[dict]:
    with get_session() as session:
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "site_id": job.site_id,
            "coupon_code": job.coupon_code,
            "status": job.status,
            "job_start_time": to_iso_utc(job.job_start_time),
            "result": job.result,
            "error": job.error,
        }


def update_job_status(job_id: str, status: int, result: dict = None, error: str = None):
    with get_session() as session:
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = status
            job.result = result
            job.error = error


def get_coupon_stats(site_id: int, coupon_code: str) -> Optional[dict]:
    with get_session() as session:
        stats = session.query(CouponStats).filter(
            CouponStats.site_id == site_id,
            CouponStats.coupon_code == coupon_code
        ).first()
        if not stats:
            return None
        return {
            "site_id": stats.site_id,
            "coupon_code": stats.coupon_code,
            "run_count": stats.run_count,
            "last_run_at": to_iso_utc(stats.last_run_at),
            "last_job_id": stats.last_job_id,
        }


def upsert_coupon_stats(site_id: int, coupon_code: str, job_id: str):
    now = datetime.now(timezone.utc)
    with get_session() as session:
        stats = session.query(CouponStats).filter(
            CouponStats.site_id == site_id,
            CouponStats.coupon_code == coupon_code
        ).first()

        if stats:
            stats.run_count += 1
            stats.last_run_at = now
            stats.last_job_id = job_id
        else:
            stats = CouponStats(
                site_id=site_id,
                coupon_code=coupon_code,
                run_count=1,
                last_run_at=now,
                last_job_id=job_id
            )
            session.add(stats)


def get_pending_job() -> Optional[dict]:
    with get_session() as session:
        job = (
            session.query(Job)
            .filter(Job.status == JobStatus.PENDING)
            .order_by(Job.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
            .first()
        )
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "site_id": job.site_id,
            "coupon_code": job.coupon_code,
            "status": job.status,
            "job_start_time": job.job_start_time,
        }


def upsert_site(
    site_id: int,
    base_url: str,
    status: int,
    miner_hotkey: Optional[str],
    api_url: Optional[str],
    config: Optional[dict],
    total_coupon_slots: int,
):
    now = datetime.now(timezone.utc)
    with get_session() as session:
        site = session.query(Site).filter(Site.id == site_id).first()

        if site:
            site.base_url = base_url
            site.status = status
            site.miner_hotkey = miner_hotkey
            site.api_url = api_url
            site.config = config
            site.total_coupon_slots = total_coupon_slots
            site.updated_at = now
        else:
            site = Site(
                id=site_id,
                base_url=base_url,
                status=status,
                miner_hotkey=miner_hotkey,
                api_url=api_url,
                config=config,
                total_coupon_slots=total_coupon_slots,
                created_at=now,
                updated_at=now,
            )
            session.add(site)


def get_site(site_id: int) -> Optional[dict]:
    with get_session() as session:
        site = session.query(Site).filter(Site.id == site_id).first()
        if not site:
            return None
        return {
            "id": site.id,
            "base_url": site.base_url,
            "status": site.status,
            "miner_hotkey": site.miner_hotkey,
            "api_url": site.api_url,
            "config": site.config,
            "total_coupon_slots": site.total_coupon_slots,
        }
