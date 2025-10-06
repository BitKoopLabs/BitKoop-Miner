## BitKoop Miner Server – Architecture

This document illustrates the high-level architecture and request flows of the Miner Server.


### Component overview

```mermaid
flowchart LR

  subgraph Server[Miner Server]
    A["HTTP API<br>(Fiber)"]
    D["get_config()<br>Config Accessor"]
    V["verify_request<br>Auth Dependency"]
    Q["Job Orchestrator<br>+ Queue"]
    E["Executor<br>(Playwright Runner)"]
    S["(Storage/DB)"]
    T["TLS Notary Service"]
  end

  subgraph External
    R["Subnet Validators"]
    X["Supervisor<br>(Periodic Config Source)"]
  end

  R -->|POST /coupon/check| A
  A -.-> V
  A -.-> D
  D -.-> X
  A -->|create/read| S
  A --> Q
  Q --> E
  E -->|fetch site flow| X
  E -->|request notarization| T
  E -->|persist result| S
  R -->|"GET /job/{id}"| A
  A -->|read job| S
  A -->|GET /health| R
```

Key points:
- `get_config()` is the single source for configuration (hotkey, staleness window, timeouts). It can later poll from the Supervisor without changing call sites.
- `verify_request` protects privileged endpoints; `/job/{id}` and `/health` are public.
- The Executor retrieves site flows from the Supervisor, performs Playwright executions, and coordinates with TLS Notary; only references/commitments are stored and exposed.
- Validators poll job results (pull model). Miners do not fan-out to validators.


### Request/Job lifecycle (sequence)

```mermaid
sequenceDiagram
  participant VAL as Subnet Validator
  participant API as Miner API (Fiber)
  participant CFG as get_config()
  participant DB as Storage/DB
  participant Q as Job Orchestrator
  participant EX as Executor (Playwright)
  participant TN as TLS Notary
  participant SUP as Supervisor

  VAL->>API: POST /coupon/check {coupon_code, site_id, miner_hotkey}
  API->>CFG: load HOTKEY_NAME, CHECK_STALENESS_HOURS
  API-->>API: verify_request + hotkey match
  API->>DB: read last_run_at for (site_id, coupon_code)
  API-->>API: if stale -> forced_run = true
  API->>DB: insert job (job_id ULID), upsert run_count, last_run_at
  API->>Q: enqueue job(job_id)
  API-->>VAL: 200 { job_id, forced_run, job_start_time }

  Note over Q,EX: async execution
  Q->>EX: start job(job_id)
  EX->>DB: load job details
  EX->>CFG: load config
  EX->>SUP: fetch site flow definition
  SUP-->>EX: flow config/version
  EX->>TN: request notarization (session evidence)
  TN-->>EX: attestation refs
  EX->>DB: persist result {status, result, evidence_refs}

  VAL->>API: GET /job/{id}
  API->>DB: fetch job
  DB-->>API: status, result (no raw transcripts)
  API-->>VAL: 200 job document
```


### Data model highlights

- Job
  - `job_id` (ULID/UUIDv7, opaque string)
  - `site_id` (int), `coupon_code` (text)
  - `status` (int)  :
     - PENDING - 1
     - RUNNING - 2
     - SUCCEEDED - 3
     - FAILED - 4
     - CANCELLED - 5
  - `job_start_time` (timestamp)
  - `result` (versioned payload, minimal evidence references)

- Coupon stats (per `(site_id, coupon_code)`)
  - `run_count` (int)
  - `last_run_at` (timestamp)
  - `last_job_id` (string, optional)


### Operational notes

- Use `get_config()` in all code paths needing configuration.
- Enforce staleness with `last_run_at`; dedupe concurrent checks.
- Keep `/job/{id}` public but non-leaky: return attestations/commitments only.
- Consider rate limiting `/coupon/check` and set `JOB_RETENTION_HOURS` for data lifecycle.


