## BitKoop Miner Setup Guide

This guide will walk you through setting up a BitKoop miner node.

Note: For subnet registration and system overview, see the main README.

---

## 🟢 Quick Start: Remote Docker Compose Setup

1. Create a new directory for the miner and enter it:

   ```sh
   mkdir BitKoop-Miner
   cd BitKoop-Miner
   ```

2. Download the latest `docker-compose.yml` from the official repository:

   ```sh
   curl -L -o docker-compose.yml https://raw.githubusercontent.com/BitKoopLabs/BitKoop-Miner/main/docker-compose.yml
   ```

3. Start the miner (and watchtower) in the background:

   ```sh
   docker compose up -d
   ```

   ⚠️ Warning: By default, the miner will use the wallet name `default` and hotkey `default`. It is strongly recommended to set your own wallet name and hotkey for security and proper operation. See Wallet Customization below for instructions.

   Tip: You can customize the port by setting the `PORT` environment variable, either in your `.env` file or directly when starting Docker Compose:

   ```sh
   PORT=8081 docker compose up -d
   ```

   Or edit the `PORT` value in your `.env` file. This is the recommended way to change the port (default is `8080`).

4. Check if it's running:

   Use the following command to check a simple health endpoint from your server:

   ```sh
   curl http://localhost:8080/health
   ```

   You should see a JSON response:

   ```json
   {"status": "ok"}
   ```

---

## 🖥️ Hardware Requirements

- **Minimum**: 2 vCPU, 4 GB RAM, 20 GB SSD
- **Recommended**: 4+ vCPU, 8 GB RAM, 50 GB SSD

These values account for PostgreSQL database, async job processing, TLS-JS service with Playwright browser automation, and periodic validation tasks.

---

## 🛑 Alternative: Running Locally (Not Recommended)

- The recommended way to run the miner is with Docker Compose.
- Running locally is only for advanced users who need to run outside Docker.
- There is no autoupdate support when running locally.

If you still want to run locally:

1. Clone the repository and set up your environment:

   ```sh
   git clone https://github.com/BitKoopLabs/BitKoop-Miner.git
   cd BitKoop-Miner
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. Install Playwright browsers (required for validation):

   ```sh
   npx playwright install --with-deps
   ```

3. Create your environment file:

   ```sh
   cp .env.example .env
   # then edit .env to set WALLET_NAME, HOTKEY_NAME, and other variables
   ```

4. Start PostgreSQL (required):

   ```sh
   docker run -d \
     -e POSTGRES_DB=bitkoop_miner \
     -e POSTGRES_USER=miner \
     -e POSTGRES_PASSWORD=miner_pass \
     -p 5432:5432 \
     postgres:15-alpine
   ```

5. Run database migrations and start the API:

   ```sh
   alembic upgrade head
   uvicorn bitkoop_miner_server.app:app --host 0.0.0.0 --port 8080
   ```

6. Start the worker process in a separate terminal:

   ```sh
   source venv/bin/activate
   python -m bitkoop_miner_server.worker
   ```

7. Start TLS-JS service (in separate terminal):

   ```sh
   cd ../tls-js
   npm install
   PORT=3001 npm start
   ```

---

## ⚙️ Wallet Customization

You must set your Bittensor wallet name and hotkey for the miner to function correctly. There are two recommended ways to do this:

### 1. Using a `.env` File (Recommended)

1. Copy the example environment file and rename it:

   ```sh
   cp .env.example .env
   ```

2. Open `.env` in your editor and fill in your wallet details:

   ```env
   WALLET_NAME=my_wallet
   HOTKEY_NAME=my_hotkey
   # You can add other variables as needed
   ```

3. Start Docker Compose as usual:

   ```sh
   docker compose up -d
   ```

   The miner will automatically use the values from your `.env` file.

See the `.env.example` file for all available variables you can set.

### 2. Overriding via Command Line

You can also override these variables directly when starting Docker Compose:

```sh
WALLET_NAME=my_wallet HOTKEY_NAME=my_hotkey docker compose up -d
```

Replace `my_wallet` and `my_hotkey` with your actual wallet name and hotkey.

---

## 📁 Wallet Location

The miner needs access to your Bittensor wallet for authentication. By default, the docker-compose.yml mounts:

```yaml
volumes:
  - ~/.bittensor:/root/.bittensor
```

This maps your local `~/.bittensor` wallet directory to the container.

**Important:** Ensure your wallet exists at `~/.bittensor/wallets/` before starting the miner.

To check your wallet location:

```sh
ls -la ~/.bittensor/wallets/
```

You should see your wallet directories (e.g., `default`, `my_wallet`).

---

## Configuration

Most settings can be changed via environment variables used by `docker-compose.yml`:

**Required:**
- `WALLET_NAME`: Your Bittensor wallet name (default: `default`)
- `HOTKEY_NAME`: Your hotkey name (default: `default`)

**Network:**
- `NETUID`: Subnet ID (default: `1`)
- `SUBTENSOR_NETWORK`: Bittensor network (default: `finney`)
- `SUBTENSOR_ADDRESS`: Subtensor endpoint (default: `wss://entrypoint-finney.opentensor.ai:443`)

**Miner Settings:**
- `CHECK_STALENESS_HOURS`: How long before re-validating a coupon (default: `24`)
- `RUN_TIMEOUT_SECONDS`: Maximum time for validation job (default: `300`)
- `JOB_RETENTION_HOURS`: How long to keep job results (default: `168`)

**Database:**
- `DATABASE_URL`: PostgreSQL connection string

**Services:**
- `TLS_JS_URL`: TLS-JS service endpoint (default: `http://tls-js:3001`)
- `SUPERVISOR_API_URL`: Supervisor API for site configuration (default: `http://91.99.203.36/api`)
- `SYNC_SITES_INTERVAL_SECONDS`: How often to sync sites from supervisor (default: `600`)

---

## Monitoring

### View Logs

Check miner API logs:
```sh
docker compose logs -f miner
```

Check worker logs:
```sh
docker compose logs -f miner-worker
```

Check TLS-JS logs:
```sh
docker compose logs -f tls-js
```

Check all services:
```sh
docker compose logs -f
```

### Check Service Status

```sh
docker compose ps
```

All services should show "Up" status and postgres should be "healthy".

### Test Job Creation

Create a test job:
```sh
docker compose exec -T miner-worker python scripts/create_test_job.py
```

Then check job status:
```sh
curl http://localhost:8080/job/{job_id}
```

---

## Database Management

### Access Database

```sh
docker compose exec postgres psql -U miner -d bitkoop_miner
```

### Run Migrations Manually

Migrations run automatically on startup. To run manually:

```sh
docker compose exec miner alembic upgrade head
```

### Create New Migration

```sh
docker compose exec miner alembic revision --autogenerate -m "description"
```

### Database Credentials (default)

- Host: `postgres:5432` (within Docker network)
- Database: `bitkoop_miner`
- User: `miner`
- Password: `miner_pass`

---

## Troubleshooting

### Postgres not starting

Check logs:
```sh
docker compose logs postgres
```

Reset database (⚠️ deletes all data):
```sh
docker compose down -v
docker compose up -d
```

### Port already in use

Change port in `.env`:
```env
PORT=8081
```

Or modify `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"
```

### Worker not processing jobs

Check worker logs:
```sh
docker compose logs -f miner-worker
```

Restart worker:
```sh
docker compose restart miner-worker
```

### TLS-JS connection issues

Check if TLS-JS is running:
```sh
docker compose ps tls-js
curl http://localhost:3001/api/proofs
```

Check TLS-JS logs:
```sh
docker compose logs tls-js
```

### Database connection issues

Wait for postgres health check:
```sh
docker compose ps postgres
```

Ensure postgres shows "healthy" status.

---

## Stopping Services

Stop all services:
```sh
docker compose down
```

Stop and remove volumes (⚠️ deletes database):
```sh
docker compose down -v
```

---

## API Endpoints

- **GET /health** - Health check (public)
- **POST /coupon/check** - Submit validation job (protected, requires Fiber auth)
- **GET /job/{id}** - Get job status and proof (public)

See [api.md](api.md) for full API documentation.

---

## Requirements

- Docker and Docker Compose
- Bittensor wallet at `~/.bittensor/wallets/`
- (Advanced) Python 3.10+ and Node.js 18+ if running without Docker
