## TLS Notary Integration

BitKoop Miner uses TLS Notary to create cryptographic attestations of coupon validation sessions.

### Architecture

```
Miner Python Service → TLS Notary Server (Docker) → Attestation
```

### Configuration

Set via environment variables:

- `TLSNOTARY_URL` - Notary server URL (default: `http://notary-server:7047` in docker-compose)
- `TLSNOTARY_MODE` - Mode of operation:
  - `mock` - Returns mock attestations (development)
  - `local` - Uses local notary-server container
  - `hosted` - Uses public PSE notary at `notary.pse.dev`

### Docker Setup

The `docker-compose.yml` includes a TLS Notary server:

```yaml
notary-server:
  image: ghcr.io/tlsnotary/tlsn/notary-server:v0.1.0-alpha.7
  ports:
    - "7047:7047"
```

### Usage

```python
from bitkoop_miner_server.notary import create_attestation

# Create attestation for a validation session
attestation = await create_attestation(
    job_id="01JBQXYZ...",
    session_evidence={
        "transcript": "...",
        "server": "example.com",
        "timestamp": "2025-01-15T10:30:00Z"
    }
)

# Returns:
# {
#   "attestation_id": "attest_...",
#   "commitment": "0x...",
#   "notary_pubkey": "...",
#   "version": "v0.1.0-alpha.7"
# }
```

### Development vs Production

**Development (Mock Mode)**
```bash
export TLSNOTARY_MODE=mock
```
- Returns mock attestations instantly
- No real notarization
- Useful for testing executor logic

**Production (Local Notary)**
```bash
export TLSNOTARY_MODE=local
export TLSNOTARY_URL=http://notary-server:7047
```
- Uses containerized notary server
- Real attestations
- Full cryptographic proof

**Production (Hosted Notary)**
```bash
export TLSNOTARY_MODE=hosted
export TLSNOTARY_URL=https://notary.pse.dev/v0.1.0-alpha.7
```
- Uses PSE-hosted notary
- Not recommended for production per TLS Notary docs
- Useful for testing without running local notary

