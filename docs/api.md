## BitKoop Miner Server API

This document specifies the HTTP API for the BitKoop Miner Server.

- Base URL: configurable (default `http://localhost:8080`)
- Content type: `application/json` for requests and responses unless stated otherwise
- Time: all timestamps are ISO-8601 in UTC


### Authentication and authorization

- Protected endpoints use Fiber's `verify_request` dependency (see `rayonlabs/fiber` miner dependencies).
- Additional check: the provided `miner_hotkey` in the request body must equal the server's active hotkey (the identity under which the process is running), as returned by `get_config()`. If it does not match, the request is rejected.
- Failure modes:
  - `401 Unauthorized`: request failed `verify_request` (missing/invalid auth)
  - `403 Forbidden`: `miner_hotkey` != server hotkey


### Jobs and staleness policy

- A validation "job" represents an execution of a Playwright flow for a given `(site_id, coupon_code)` pair.
- If N hours (configurable; default 24h) have passed since the last successful/attempted execution for a given pair, a new check MUST be forced when `/coupon/check` is called. Use `get_config()` to read the current staleness window.
- Implementations should deduplicate in-flight jobs for the same pair where possible (idempotency).

#### Job ID format

- Use an opaque, non-guessable string ID for `job_id` (e.g., ULID or UUIDv7). Do not use autoincrement integers or embed business fields in the ID.
- Benefits: avoids information leakage, supports global uniqueness and time-ordering (ULID/UUIDv7), and is safer for a public `GET /job/{id}`.

#### Per-coupon counters

- Maintain a counter keyed by `(site_id, coupon_code)` capturing:
  - `run_count`: total executions
  - `last_run_at`: timestamp of the most recent run
  - Optionally `last_job_id`
- Increment `run_count` when a new job starts (including forced runs). Use `last_run_at` for enforcing the staleness window.

### Status codes

```
1 = PENDING
2 = RUNNING
3 = SUCCEEDED
4 = FAILED
5 = CANCELLED
```


---

### POST /coupon/check

Trigger a coupon validation job. Protected by `verify_request` and hotkey match.

- Auth: protected
- Body:

```json
{
  "coupon_code": "ABC123",
  "site_id": 1,
  "miner_hotkey": "ss58_miner_hotkey..."
}
```

- Behavior:
  - If a recent job exists within the staleness window (N hours), the server MAY return the existing `job_id` without re-running, unless the window has elapsed; once elapsed, a new job MUST be started.
  - If no recent job exists, start a new job and return its `job_id`.

- Responses:
  - 200 OK

```json
{
  "job_id": "01HVH7QW8M5ZQ7S2S6W3P7J3ZK",
  "forced_run": true,
  "job_start_time": "2025-01-01T12:34:56Z",
  "staleness_seconds": 86400
}
```

  - 400 Bad Request: missing/invalid fields
  - 401 Unauthorized: failed `verify_request`
  - 403 Forbidden: `miner_hotkey` mismatch
  - 409 Conflict: an identical job is currently running (optional; implementation-specific)

- Notes:
  - `forced_run` indicates whether a new execution was forced due to staleness.


---

### GET /job/{id}

Fetch a job status and (if completed) its result. Public endpoint.

- Auth: none (public)
- Path params:
  - `id` (string): job identifier

- Response 200 OK:

```json
{
  "job_id": "01HVH7QW8M5ZQ7S2S6W3P7J3ZK",
  "status": 2,
  "job_start_time": "2025-01-01T12:34:56Z",
  "result": {
    "version": "0.1.0-alpha.12",
    "data": "...",
    "meta":
    {
        "notaryUrl": "http://localhost:7047",
        "websocketProxyUrl": "ws://127.0.0.1:55688?token=www.myprotein.ro"
    }
  },
  "error": null
}
```

- Response 404 Not Found: job not found

- Notes:
  - `result` is present only when `status` is 3 (SUCCEEDED). For 4 (FAILED), `result` may be partially present with diagnostic info.
  - Avoid returning sensitive raw transcripts; include only references/commitments.


---

### GET /health

Liveness/readiness probe. Public endpoint.

- Auth: none (public)
- Response 200 OK:

```json
{ "status": "ok" }
```

- Optional 503 Service Unavailable when dependencies are down (e.g., TLS Notary or browser pool unavailable) with a brief reason.


### Error model

Standard error shape for 4xx/5xx responses (except very simple health responses):

```json
{
  "error": {
    "code": "string",
    "message": "human-readable message",
    "details": {
      
    }
  }
}
```

- `code`: short machine-friendly identifier (e.g., `UNAUTHORIZED`, `HOTKEY_MISMATCH`, `VALIDATION_TIMEOUT`).
- `details`: optional object for structured metadata.


### Configuration knobs (server)
- `WALLET_NAME`: the server's active wallet name (used for hotkey match check)
- `HOTKEY_NAME`: the server's active hotkey name (used for hotkey match check)
- `CHECK_STALENESS_HOURS` (default 24): hours after which `/coupon/check` must force a new run
- `RUN_TIMEOUT_SECONDS`: max runtime for a single validation job
- `JOB_RETENTION_HOURS`: how long to keep completed jobs available via `/job/{id}`

### Configuration access

- Always obtain configuration via a dedicated `get_config()` method rather than reading environment variables directly inside handlers.
- `get_config()` should return the current effective configuration (wallet/hotkey names, staleness window, timeouts, etc.).
- Later, environment variables will be replaced by periodic configuration retrieval from the supervisor; centralizing access in `get_config()` avoids code churn and enables live updates.


### Notes for implementers

- Ensure idempotency where possible: dedupe concurrent `/coupon/check` requests for the same `(site_id, coupon_code)`.
- Provide stable `job_id`s that are safe to expose publicly (non-guessable if job data may be sensitive).
- Sanitize logs and responses; avoid leaking PII or raw TLS transcripts.
 - Use `get_config()` in all code paths that require configuration values (auth hotkey check, staleness window, timeouts) to support future supervisor-driven config refresh.


