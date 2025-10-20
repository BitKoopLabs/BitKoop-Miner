#!/usr/bin/env python3
"""
Create a test job for demonstrating the mock executor.

Usage:
    docker-compose exec -T miner-api python scripts/create_test_job.py
"""

from ulid import ULID
from bitkoop_miner_server.database import create_job
from bitkoop_miner_server.constants import JobStatus

if __name__ == "__main__":
    job_id = str(ULID())

    print("Creating test job...")
    create_job(job_id, site_id=1, coupon_code="TESTCOUPON", status=JobStatus.PENDING)

    print(f"✅ Created job: {job_id}")
    print(f"   Site ID: 1")
    print(f"   Coupon: TESTCOUPON")
    print(f"   Status: PENDING")
    print()
    print("The worker will process this job in ~30 seconds.")
    print(f"Check status: curl http://localhost:8080/job/{job_id}")
