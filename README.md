## BitKoop Miner Server

A lightweight server that enables BitKoop miners to:

- Validate coupon codes by executing real browser flows with Playwright
- Notarize validation sessions via TLS Notary
- Forward proofs to subnet validators

This service is a child project of `BitKoop` and follows the miner/validator model described in the parent repository.

- Parent project: [`BitKoopLabs/BitKoop`](https://github.com/BitKoopLabs/BitKoop)
- Built on: Fiber Framework [`rayonlabs/fiber`](https://github.com/rayonlabs/fiber)
- TLS Notary: [`tlsnotary.org`](https://tlsnotary.org)


### Documentation

- API: [docs/api.md](docs/api.md)
- Architecture: [docs/architecture.md](docs/architecture.md)


### Why this exists

- Validate coupons end-to-end against real merchant checkout flows (headless or headed, anti-bot aware).
- Produce cryptographic proofs (TLS Notary) tying session evidence to a verifiable transcript.
- Submit proofs to BitKoop subnet validators for independent verification and scoring.


### High-level architecture

1. Miner submits a coupon for a given site.
2. This server runs a Playwright script that follows the store’s flow to check coupon validity.
3. The session and relevant HTTPs transcript are notarized via TLS Notary.
4. A proof bundle (evidence + transcript commitments) is sent to subnet validators.


### Features

- Playwright-driven validation flows with flexible per-site scripts
- TLS Notary integration to notarize session evidence
- Simple HTTP API to trigger validations and retrieve results
- Pluggable proof-forwarding to BitKoop subnet validators


### Prerequisites

- Python 3.10+
- Node.js 18+ (for Playwright browsers install)
- Playwright browsers installed

Install Playwright browsers (once):

```bash
npx playwright install --with-deps
```


### Writing/authoring site flows

- Each supported merchant may have a dedicated Playwright script encapsulating its checkout flow and coupon application step.
- Use robust selectors and reasonable timeouts; consider anti-automation measures.
- Keep flows deterministic and fail-fast; return a structured outcome:
  - `VALID` with observed discount and context
  - `INVALID` with failure reason
  - `PENDING` if prerequisites are missing (e.g., site config)


### TLS Notary integration

- The server collects necessary session artifacts (e.g., relevant HTTPs transcript data) and requests a notarization from the TLS Notary service.
- The returned attestation/commitment is attached to the proof bundle.
- See `tlsnotary.org` for documentation and service options.



### Containerization

If shipping a container, ensure Playwright dependencies are baked in. Example base:

```Dockerfile
FROM mcr.microsoft.com/playwright/python:latest

WORKDIR /app
COPY . /app

RUN pip install -U pip \
    && pip install -r requirements.txt \
    && playwright install --with-deps

EXPOSE 8080
CMD ["uvicorn", "bitkoop_miner_server.app:app", "--host", "0.0.0.0", "--port", "8080"]
```


### Security considerations

- Treat coupons and session data as sensitive; avoid logging secrets or full transcripts.
- Store only minimum necessary artifacts for notarization and proof generation.
- Rotate `BITKOOP_MINER_SECRET` and TLS Notary credentials regularly.


### Links

- Parent project: [`BitKoopLabs/BitKoop`](https://github.com/BitKoopLabs/BitKoop)
- Fiber framework: [`rayonlabs/fiber`](https://github.com/rayonlabs/fiber)
- TLS Notary: [`tlsnotary.org`](https://tlsnotary.org)


