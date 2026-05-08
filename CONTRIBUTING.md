# CONTRIBUTING.md

Guide to set up and run the pipeline locally.

## Prerequisites

| Tool | Minimum Version | Installation |
|------|-----------------|--------------|
| Docker Desktop | 4.x | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Python | 3.11+ | `brew install python@3.11` |
| Java | 11+ | `brew install openjdk@11` (required for local PySpark) |
| Make | any | pre-installed on macOS |

## 1. Clone the repository

```bash
git clone git@github.com:<your-org>/real_time_adtech_metrics_pipeline.git
cd real_time_adtech_metrics_pipeline
```

## 2. Running with Docker (recommended)

This is the fastest path — brings up the entire infrastructure + application.

### 2.1 Open Docker Desktop

Make sure Docker Desktop is **open and running** (stable whale icon in the menu bar).

Verify with:

```bash
docker info
```

If it returns an error, Docker is not ready yet.

### 2.2 Start the stack

```bash
make up
```

This starts:
- **Zookeeper** — Kafka coordination
- **Kafka** — message broker (port 9092)
- **MinIO** — S3-compatible storage (console on port 9001)
- **Producer** — generates fake events every 1s
- **Streaming** — consumes Kafka and writes Parquet to MinIO (silver)
- **API** — FastAPI with health check (port 8000)

### 2.3 Verify all services are up

```bash
docker compose ps
```

All services should show status `Up` or `running (healthy)`.

> **Boot time:** ~30-60s on first run (image downloads + health checks).

### 2.4 Validation

```bash
# Full health check (verifies Kafka + MinIO connectivity)
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","env":"docker","version":"0.1.0","checks":{"kafka":{"status":"ok"},"minio":{"status":"ok"}}}

# Prometheus metrics
curl http://localhost:8000/metrics

# View events in Kafka
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ad-events \
  --from-beginning \
  --max-messages 5
```

### 2.5 Access MinIO Console

- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

Check the `silver/` and `gold/` buckets — streaming should generate Parquet files in `silver/`.

### 2.6 Run batch manually

```bash
docker compose exec streaming python -m batch.batch_job
```

This reads the silver layer and writes the aggregated result to the gold layer.

### 2.7 View logs

```bash
# All services
make logs

# Specific service
docker compose logs -f producer
docker compose logs -f streaming
docker compose logs -f api
```

### 2.8 Stop everything

```bash
make down
```

## 3. Running without Docker (local development)

For developing/debugging individual components.

### 3.1 Install dependencies

```bash
make install
```

This installs all dependencies (streaming, batch, dashboard, dev tools).

### 3.2 Start infrastructure only

```bash
docker compose up -d zookeeper kafka minio minio-init
```

Wait ~20s for the health checks to pass.

### 3.3 Run individual components

```bash
# Producer (generates events to local Kafka)
make producer

# Streaming job (consumes Kafka → writes Parquet)
make run-streaming

# Batch job (silver → gold)
make run-batch

# Dashboard (Streamlit)
make dashboard

# API
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

### 3.4 Run tests

```bash
make test
```

### 3.5 Lint and formatting

```bash
make format   # auto-fix (black + isort + ruff)
make lint     # check only
```

## 4. Ports

| Service | Port | Description |
|---------|------|-------------|
| Kafka | 9092 | Broker (external access) |
| Kafka (internal) | 29092 | Inter-container communication |
| MinIO API | 9000 | S3 API |
| MinIO Console | 9001 | Web UI |
| Zookeeper | 2181 | Kafka coordination |
| API (FastAPI) | 8000 | Health + Config + Metrics |
| Producer metrics | 9091 | Prometheus endpoint |
| Streaming metrics | 9093 | Prometheus endpoint |

## 5. Troubleshooting

### Docker won't connect

```
Cannot connect to the Docker daemon
```

→ Open Docker Desktop and wait for the icon to stabilize.

### Kafka not ready

```
kafka  | ... broker not available
```

→ Wait ~30s. Kafka depends on Zookeeper being healthy first.

### Streaming restarting in a loop

Check if Kafka and MinIO are healthy:

```bash
docker compose ps
docker compose logs streaming --tail 20
```

### Port already in use

```bash
# Find what's using the port
lsof -i :8000

# Kill the process or change the port in docker-compose.yml
```

### Full reset

```bash
docker compose down -v   # removes volumes (Kafka/MinIO data)
docker system prune -f   # cleans orphan images/containers
make up                  # start fresh
```

## 6. Data flow

```
Producer → Kafka (ad-events) → Streaming Job → MinIO (silver/) → Batch Job → MinIO (gold/)
                                                                                    ↓
                                                                              Dashboard / API
```
## 7. Configuration

- `config/dev.yaml` — used locally (Kafka on localhost)
- `config/docker.yaml` — used inside containers (Kafka on `kafka:29092`)
- Selected via the `CONFIG_PATH` environment variable
