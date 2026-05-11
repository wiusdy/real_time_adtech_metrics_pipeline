# Real-Time AdTech Metrics Pipeline

Real-time metrics pipeline for AdTech using **Kafka**, **Spark Structured Streaming**, **MinIO** (S3-compatible) and **Streamlit**.

## Architecture

```
┌──────────┐     ┌───────┐     ┌────────────────────┐     ┌───────┐     ┌───────────┐
│ Producer │────▶│ Kafka │────▶│ Spark Streaming    │────▶│ MinIO │────▶│ Dashboard │
│ (events) │     │       │     │ (silver layer)     │     │ (S3)  │     │ Streamlit │
└──────────┘     └───────┘     └────────────────────┘     └───────┘     └───────────┘
                                                               │
                                                               ▼
                                                     ┌──────────────────┐
                                                     │ Batch Job        │
                                                     │ (gold layer)     │
                                                     └──────────────────┘
```

## Project Structure

```
.
├── api/                  # FastAPI - health check and status
├── batch/                # Spark batch job (silver → gold)
├── config/               # YAML configuration per environment
│   ├── dev.yaml
│   └── docker.yaml
├── core/                 # Config loader (Pydantic) + logger + metrics
├── dashboard/            # Streamlit dashboard
├── deploy/               # Deploy script (ECR/Docker)
├── glue/                 # AWS Glue jobs (streaming + batch)
├── infra/                # Terraform (Glue, IAM, Data Catalog)
├── producer/             # Kafka event producer
├── streaming/            # Spark Structured Streaming job (local)
├── tests/                # Unit tests
├── docker-compose.yml    # Full stack (infra + app)
├── Dockerfile
├── Makefile              # Useful commands
└── pyproject.toml        # Dependencies and tooling
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Java 17+ (for local PySpark)

### Running with Docker (recommended)

```bash
# Start the full stack: Kafka, MinIO, Producer, Streaming, API
make up

# View logs
make logs

# Stop everything
make down
```

### Local Development

```bash
# Install dependencies
make install

# Run producer (generates events to Kafka)
make producer

# Run streaming job (consumes Kafka → writes to Silver)
make run-streaming

# Run batch job (Silver → Gold)
make run-batch

# Run dashboard
make dashboard
```

## Configuration

The project uses YAML + Pydantic for typed configuration. The file is selected via:
- Environment variable: `CONFIG_PATH=config/docker.yaml`
- Default: `config/dev.yaml`

```yaml
kafka:
  bootstrap_servers: localhost:9092
  topic: ad-events

paths:
  silver: s3a://silver/events/
  gold: s3a://gold/aggregated/
  checkpoint: /tmp/checkpoint

streaming:
  watermark: "1 minute"
  window: "1 minute"
```

## Data Pipeline

| Layer   | Description                                    | Storage        |
|---------|------------------------------------------------|----------------|
| Bronze  | Raw events from Kafka (JSON)                   | Kafka topic    |
| Silver  | Parsed events + windowed aggregations          | MinIO/Parquet  |
| Gold    | Per-user metrics (batch aggregation)           | MinIO/Parquet  |

## API

```bash
# Health check
curl http://localhost:8000/health

# Config info
curl http://localhost:8000/config
```

## Tests

```bash
make test
```

## Lint & Format

```bash
make format   # auto-fix
make lint     # check only
```

## Tech Stack

| Component     | Technology                   |
|---------------|------------------------------|
| Streaming     | PySpark Structured Streaming |
| Messaging     | Apache Kafka                 |
| Storage       | MinIO (S3-compatible)        |
| Batch         | PySpark                      |
| API           | FastAPI                      |
| Dashboard     | Streamlit                    |
| Config        | Pydantic + YAML              |
| CI/Lint       | Black, isort, Ruff           |
| Cloud ETL     | AWS Glue 4.0                 |
| IaC           | Terraform                    |
| Observability | Prometheus + JSON logs       |

## AWS Glue (Production)

The `glue/` directory contains jobs ready to deploy on AWS Glue, and `infra/` contains the Terraform to provision everything.

### AWS Architecture

```
┌──────────┐     ┌───────┐     ┌──────────────────┐     ┌────┐     ┌──────────────┐
│ Producer │────▶│  MSK  │────▶│ Glue Streaming   │────▶│ S3 │────▶│ Glue Batch   │
│          │     │(Kafka)│     │ (Silver layer)   │     │    │     │ (Gold layer) │
└──────────┘     └───────┘     └──────────────────┘     └────┘     └──────────────┘
                                                                          │
                                                                          ▼
                                                                   ┌──────────────┐
                                                                   │ Glue Catalog │
                                                                   │ (Athena/QS)  │
                                                                   └──────────────┘
```

### Infrastructure Deploy

```bash
# Copy and fill in variables
cp infra/terraform.tfvars.example infra/terraform.tfvars

# Provision
make infra-init
make infra-plan
make infra-apply
```

### Glue Operations

```bash
# Upload scripts to S3
make glue-upload GLUE_SCRIPTS_BUCKET=adtech-glue-scripts-dev

# Start jobs
make glue-start-streaming ENV=dev
make glue-start-batch ENV=dev

# Check status
make glue-status ENV=dev
```

### Job Parameters

| Job | Parameter | Description |
|-----|-----------|-------------|
| Streaming | `KAFKA_BOOTSTRAP_SERVERS` | MSK broker endpoint |
| Streaming | `KAFKA_TOPIC` | Events topic |
| Streaming | `OUTPUT_PATH` | S3 path for silver layer |
| Streaming | `WINDOW_DURATION` | Aggregation window |
| Streaming | `WATERMARK` | Late arrival tolerance |
| Batch | `SILVER_PATH` | S3 path for silver layer |
| Batch | `GOLD_PATH` | S3 path for gold layer |
| Batch | `GLUE_DATABASE` | Data Catalog database |
| Batch | `GLUE_TABLE` | Output table |
