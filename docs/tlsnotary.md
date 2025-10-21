## TLS Notary Integration

BitKoop Miner uses TLS Notary to create cryptographic attestations of coupon validation sessions.

### Architecture

```
Miner Python Service → TLS-JS Service → Notary Server → Attestation
```

The miner uses a dedicated Node.js service (tls-js) to handle TLS notarization. This service:
- Runs Playwright browser automation
- Captures HTTP traffic during coupon validation
- Requests attestations from the notary server
- Returns cryptographic proofs to the miner

### Configuration

TLS-JS service is configured via environment variables in `docker-compose.yml`:

**Miner Services:**
- `TLS_JS_URL` - TLS-JS service endpoint (default: `http://tls-js:3001`)

**TLS-JS Service:**
- `PORT` - Service port (default: `3001`)
- `PROOFS_DIR` - Directory for storing proof files (default: `/app/output/proofs`)
- `NOTARY_HOST` - Notary server URL (default: `http://notary-server:7047`)

### Docker Setup

The `docker-compose.yml` includes both the TLS-JS service and notary server:

```yaml
notary-server:
  image: ghcr.io/tlsnotary/tlsn/notary-server:v0.1.0-alpha.12

tls-js:
  build:
    context: ../tls-js
    dockerfile: Dockerfile
  ports:
    - "3001:3001"
  environment:
    - PORT=3001
    - PROOFS_DIR=/app/output/proofs
    - NOTARY_HOST=${NOTARY_HOST:-http://notary-server:7047}
  volumes:
    - ./artifacts/proofs:/app/output/proofs
  depends_on:
    - notary-server
```

### Usage

The miner communicates with TLS-JS via HTTP API:

```python
# Executor calls TLS-JS service
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{tls_js_url}/api/notarize",
        json={
            "url": "https://example.com/cart",
            "method": "POST",
            "headers": {...},
            "body": {...}
        },
        timeout=300
    )
    proof_data = response.json()
```

The TLS-JS service returns:
- Cryptographic proof of the HTTP session
- Attestation data signed by the notary server
- Evidence that can be verified by validators

### Proof Storage

Proof files are stored in the `artifacts/proofs/` directory and mounted as a volume:

```
artifacts/
└── proofs/
    ├── proof_01JBQXYZ....json
    ├── proof_01JBQXYZ....json
    └── ...
```

These proofs contain:
- Session transcript commitments
- Notary signatures
- Verification data for validators

### Service Dependencies

The validation flow requires all services to be healthy:

1. **postgres** - Database for job tracking
2. **notary-server** - TLS Notary attestation service
3. **tls-js** - Browser automation and notarization
4. **miner-worker** - Job executor that calls tls-js

Health checks ensure services start in the correct order and are ready before processing jobs.
