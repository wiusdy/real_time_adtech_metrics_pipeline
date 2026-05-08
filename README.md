# Real-Time AdTech Metrics Pipeline

Pipeline de métricas em tempo real para AdTech usando **Kafka**, **Spark Structured Streaming**, **MinIO** (S3-compatible) e **Streamlit**.

## Arquitetura

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

## Estrutura do Projeto

```
.
├── api/                  # FastAPI - health check e status
├── batch/                # Spark batch job (silver → gold)
├── config/               # Configurações YAML por ambiente
│   ├── dev.yaml
│   └── docker.yaml
├── core/                 # Config loader (Pydantic) + logger + metrics
├── dashboard/            # Streamlit dashboard
├── deploy/               # Script de deploy (ECR/Docker)
├── glue/                 # AWS Glue jobs (streaming + batch)
├── infra/                # Terraform (Glue, IAM, Data Catalog)
├── producer/             # Kafka event producer
├── streaming/            # Spark Structured Streaming job (local)
├── tests/                # Testes unitários
├── docker-compose.yml    # Stack completa (infra + app)
├── Dockerfile
├── Makefile              # Comandos úteis
└── pyproject.toml        # Dependências e tooling
```

## Quick Start

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- Java 11+ (para PySpark local)

### Rodando com Docker (recomendado)

```bash
# Sobe toda a stack: Kafka, MinIO, Producer, Streaming, API
make up

# Ver logs
make logs

# Parar tudo
make down
```

### Desenvolvimento Local

```bash
# Instalar dependências
make install

# Rodar producer (gera eventos no Kafka)
make producer

# Rodar streaming job (consome Kafka → salva em Silver)
make run-streaming

# Rodar batch job (Silver → Gold)
make run-batch

# Rodar dashboard
make dashboard
```

## Configuração

O projeto usa YAML + Pydantic para configuração tipada. O arquivo é selecionado via:
- Variável de ambiente: `CONFIG_PATH=config/docker.yaml`
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

## Pipeline de Dados

| Camada  | Descrição                                      | Storage        |
|---------|------------------------------------------------|----------------|
| Bronze  | Eventos raw do Kafka (JSON)                    | Kafka topic    |
| Silver  | Eventos parseados + agregados por janela       | MinIO/Parquet  |
| Gold    | Métricas por usuário (batch aggregation)       | MinIO/Parquet  |

## API

```bash
# Health check
curl http://localhost:8000/health

# Config info
curl http://localhost:8000/config
```

## Testes

```bash
make test
```

## Lint & Formato

```bash
make format   # auto-fix
make lint     # check only
```

## Tech Stack

| Componente | Tecnologia              |
|-----------|--------------------------|
| Streaming | PySpark Structured Streaming |
| Messaging | Apache Kafka             |
| Storage   | MinIO (S3-compatible)    |
| Batch     | PySpark                  |
| API       | FastAPI                  |
| Dashboard | Streamlit                |
| Config    | Pydantic + YAML          |
| CI/Lint   | Black, isort, Ruff       |
| Cloud ETL | AWS Glue 4.0             |
| IaC       | Terraform                |
| Observability | Prometheus + JSON logs |

## AWS Glue (Produção)

O diretório `glue/` contém os jobs prontos para deploy no AWS Glue, e `infra/` contém o Terraform para provisionar tudo.

### Arquitetura AWS

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

### Deploy da Infraestrutura

```bash
# Copiar e preencher variáveis
cp infra/terraform.tfvars.example infra/terraform.tfvars

# Provisionar
make infra-init
make infra-plan
make infra-apply
```

### Operações Glue

```bash
# Upload de scripts para S3
make glue-upload GLUE_SCRIPTS_BUCKET=adtech-glue-scripts-dev

# Iniciar jobs
make glue-start-streaming ENV=dev
make glue-start-batch ENV=dev

# Verificar status
make glue-status ENV=dev
```

### Parâmetros dos Jobs

| Job | Parâmetro | Descrição |
|-----|-----------|-----------|
| Streaming | `KAFKA_BOOTSTRAP_SERVERS` | MSK broker endpoint |
| Streaming | `KAFKA_TOPIC` | Topic de eventos |
| Streaming | `OUTPUT_PATH` | S3 path silver layer |
| Streaming | `WINDOW_DURATION` | Janela de agregação |
| Streaming | `WATERMARK` | Tolerância de atraso |
| Batch | `SILVER_PATH` | S3 path silver layer |
| Batch | `GOLD_PATH` | S3 path gold layer |
| Batch | `GLUE_DATABASE` | Database no Data Catalog |
| Batch | `GLUE_TABLE` | Tabela de output |
