# BitKoop Miner Server - Setup Guide

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd BitKoop-Miner
```

### 2. Start Services

```bash
docker-compose up --build
```

This will:
- Build the miner server image
- Start PostgreSQL database
- Run Alembic migrations
- Start the server on http://localhost:8080

### 3. Verify

```bash
curl http://localhost:8080/health
```

Expected response: `{"status":"ok"}`

## Environment Variables

Create a `.env` file in the project root (optional):

```env
NETUID=1
SUBTENSOR_NETWORK=finney
SUBTENSOR_ADDRESS=wss://entrypoint-finney.opentensor.ai:443
WALLET_NAME=default
HOTKEY_NAME=default
CHECK_STALENESS_HOURS=24
```

## Database

### PostgreSQL Credentials (default)

- Host: `localhost:5432`
- Database: `bitkoop_miner`
- User: `miner`
- Password: `miner_pass`

### Access Database

```bash
docker-compose exec postgres psql -U miner -d bitkoop_miner
```

### Run Migrations

Migrations run automatically on startup. To run manually:

```bash
docker-compose exec miner alembic upgrade head
```

### Create New Migration

```bash
docker-compose exec miner alembic revision --autogenerate -m "description"
```

## Development

### Install Dependencies Locally (optional)

```bash
pip install -e ".[dev]"
```

```

### Restart Server

```bash
docker-compose restart miner
```

### View Logs

```bash
docker-compose logs -f miner
docker-compose logs -f postgres
```

## Production Deployment

### 1. Update Environment Variables

Set production values in `.env`:

```env
WALLET_NAME=your_wallet
HOTKEY_NAME=your_hotkey
SUBTENSOR_NETWORK=finney
```

### 2. Mount Wallet

Update `docker-compose.yml` to mount your actual wallet:

```yaml
volumes:
  - ~/.bittensor:/root/.bittensor:ro
```

### 3. Start in Production Mode

```bash
docker-compose up -d
```

### 4. Monitor

```bash
docker-compose ps
docker-compose logs -f
```

## Stopping Services

```bash
docker-compose down
```

To remove volumes (deletes database):

```bash
docker-compose down -v
```

## Troubleshooting

### Postgres not starting

```bash
docker-compose logs postgres
docker volume rm bitkoop-miner_postgres_data
docker-compose up --build
```

### Port already in use

Change port in `docker-compose.yml`:

```yaml
ports:
  - "8081:8080"
```

### Database connection issues

Wait for postgres health check:

```bash
docker-compose ps
```

Ensure postgres shows "healthy" status.

## API Endpoints

- **GET /health** - Health check (public)
- **POST /coupon/check** - Submit validation job (protected)
- **GET /job/{id}** - Get job status (public)

See [api.md](api.md) for full API documentation.
