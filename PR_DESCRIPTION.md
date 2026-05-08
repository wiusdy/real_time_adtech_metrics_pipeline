# Refactor: Clean Architecture, Modularization & Production-Readiness

## Summary

Major refactoring of the pipeline codebase to establish clean architecture, remove technical debt, and prepare for production deployment with AWS Glue.

## Changes

### Architecture & Modularization
- Unified configuration system with Pydantic + YAML (`core/config.py`)
- Centralized Spark session factory with S3A/MinIO support (`core/spark.py`)
- Structured JSON logging (`core/logger.py`)
- Shared Prometheus metrics module (`core/metrics.py`)
- Fixed all broken imports and removed dead code

### Docker Compose (fully functional)
- Fixed Kafka dual-listener setup (INSIDE/OUTSIDE) for proper container networking
- Fixed MinIO healthcheck (was using `mc` which doesn't exist in `minio/minio` image)
- Added health checks with `depends_on` conditions for correct boot order
- Added application services: producer, streaming, api

### Observability
- FastAPI `/health` endpoint with real Kafka + MinIO connectivity checks
- `/metrics` endpoint exposing Prometheus counters and histograms
- Metrics instrumented in producer, streaming, and batch jobs
- All logs now emit structured JSON

### AWS Glue (production path)
- `glue/streaming_job.py` — Glue Streaming job (Kafka → S3 Silver)
- `glue/batch_job.py` — Glue ETL job (Silver → Gold + Data Catalog)
- `infra/` — Terraform for IAM, Glue jobs, Data Catalog, triggers

### Cleanup
- Removed duplicated files (`examples/`, duplicate Makefile targets)
- Removed deprecated `version: "3.8"` from docker-compose
- Fixed `pyproject.toml` (correct project name, all extras)
- Added `.gitignore`, `.env.example`, `CONTRIBUTING.md`

### CI/CD
- Added Java setup step for PySpark tests
- Added `isort --check` to match pre-commit hooks
- Updated deploy paths to match new naming

## How to test

```bash
make up                          # Start full stack
curl http://localhost:8000/health # Verify services
docker compose logs -f           # Watch pipeline
make down                        # Cleanup
```

## Ports

| Service | Port |
|---------|------|
| API | 8000 |
| MinIO Console | 9001 |
| Kafka | 9092 |
| Producer metrics | 9091 |
| Streaming metrics | 9093 |
