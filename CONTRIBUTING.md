# CONTRIBUTING.md

Guia para configurar e executar o pipeline localmente.

## Pré-requisitos

| Ferramenta | Versão mínima | Instalação |
|-----------|---------------|------------|
| Docker Desktop | 4.x | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Python | 3.11+ | `brew install python@3.11` |
| Java | 11+ | `brew install openjdk@11` (necessário para PySpark local) |
| Make | qualquer | já vem no macOS |

## 1. Clonar o repositório

```bash
git clone git@github.com:<seu-org>/real_time_adtech_metrics_pipeline.git
cd real_time_adtech_metrics_pipeline
```

## 2. Executar com Docker (recomendado)

Este é o caminho mais rápido — sobe toda a infraestrutura + aplicação.

### 2.1 Abrir Docker Desktop

Certifique-se de que o Docker Desktop está **aberto e rodando** (ícone da baleia estável na barra de menu).

Verifique com:

```bash
docker info
```

Se retornar erro, o Docker não está pronto ainda.

### 2.2 Subir a stack

```bash
make up
```

Isso sobe:
- **Zookeeper** — coordenação do Kafka
- **Kafka** — message broker (porta 9092)
- **MinIO** — storage S3-compatible (console na porta 9001)
- **Producer** — gera eventos fake a cada 1s
- **Streaming** — consome Kafka e escreve Parquet no MinIO (silver)
- **API** — FastAPI com health check (porta 8000)

### 2.3 Verificar se tudo subiu

```bash
docker compose ps
```

Todos os serviços devem estar com status `Up` ou `running (healthy)`.

> **Tempo de boot:** ~30-60s na primeira vez (download de imagens + health checks).

### 2.4 Validações

```bash
# Health check completo (verifica Kafka + MinIO)
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy","env":"docker","version":"0.1.0","checks":{"kafka":{"status":"ok"},"minio":{"status":"ok"}}}

# Métricas Prometheus
curl http://localhost:8000/metrics

# Ver eventos no Kafka
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ad-events \
  --from-beginning \
  --max-messages 5
```

### 2.5 Acessar MinIO Console

- URL: http://localhost:9001
- Login: `minioadmin`
- Senha: `minioadmin`

Verifique os buckets `silver/` e `gold/` — o streaming deve gerar arquivos Parquet em `silver/`.

### 2.6 Executar batch manualmente

```bash
docker compose exec streaming python -m batch.batch_job
```

Isso lê a silver layer e escreve o resultado agregado na gold layer.

### 2.7 Ver logs

```bash
# Todos os serviços
make logs

# Serviço específico
docker compose logs -f producer
docker compose logs -f streaming
docker compose logs -f api
```

### 2.8 Parar tudo

```bash
make down
```

## 3. Executar sem Docker (desenvolvimento local)

Para desenvolver/debugar componentes individuais.

### 3.1 Instalar dependências

```bash
make install
```

Isso instala todas as dependências (streaming, batch, dashboard, dev tools).

### 3.2 Subir apenas a infraestrutura

```bash
docker compose up -d zookeeper kafka minio minio-init
```

Espere ~20s para os health checks passarem.

### 3.3 Rodar componentes individuais

```bash
# Producer (gera eventos no Kafka local)
make producer

# Streaming job (consome Kafka → escreve Parquet)
make run-streaming

# Batch job (silver → gold)
make run-batch

# Dashboard (Streamlit)
make dashboard

# API
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

### 3.4 Rodar testes

```bash
make test
```

### 3.5 Lint e formatação

```bash
make format   # auto-fix (black + isort + ruff)
make lint     # check only
```

## 4. Portas utilizadas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Kafka | 9092 | Broker (acesso externo) |
| Kafka (interno) | 29092 | Comunicação entre containers |
| MinIO API | 9000 | S3 API |
| MinIO Console | 9001 | Web UI |
| Zookeeper | 2181 | Coordenação Kafka |
| API (FastAPI) | 8000 | Health + Config + Metrics |
| Producer metrics | 9091 | Prometheus endpoint |
| Streaming metrics | 9093 | Prometheus endpoint |

## 5. Troubleshooting

### Docker não conecta

```
Cannot connect to the Docker daemon
```

→ Abra o Docker Desktop e espere o ícone estabilizar.

### Kafka não está ready

```
kafka  | ... broker not available
```

→ Espere ~30s. O Kafka depende do Zookeeper estar healthy primeiro.

### Streaming reiniciando em loop

Verifique se o Kafka e MinIO estão healthy:

```bash
docker compose ps
docker compose logs streaming --tail 20
```

### Porta já em uso

```bash
# Descubra o que está usando a porta
lsof -i :8000

# Mate o processo ou mude a porta no docker-compose.yml
```

### Limpar tudo (reset completo)

```bash
docker compose down -v   # remove volumes (dados do Kafka/MinIO)
docker system prune -f   # limpa imagens/containers órfãos
make up                  # sobe limpo
```

## 6. Fluxo de dados

```
Producer → Kafka (ad-events) → Streaming Job → MinIO (silver/) → Batch Job → MinIO (gold/)
                                                                                    ↓
                                                                              Dashboard / API
```

## 7. Estrutura de configuração

- `config/dev.yaml` — usado localmente (Kafka em localhost)
- `config/docker.yaml` — usado dentro dos containers (Kafka em `kafka:29092`)
- Seleção via variável `CONFIG_PATH`
