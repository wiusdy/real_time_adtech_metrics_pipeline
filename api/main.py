import time

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="AdTech Metrics API", version="0.1.0")

# ===========================
# Prometheus Metrics
# ===========================

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


# ===========================
# Middleware
# ===========================


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    endpoint = request.url.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint,
    ).observe(duration)

    logger.info(
        f"{request.method} {endpoint} -> {response.status_code} ({duration:.3f}s)"
    )

    return response


# ===========================
# Endpoints
# ===========================


@app.get("/health")
def health():
    checks = {"kafka": _check_kafka(), "minio": _check_minio()}
    all_healthy = all(c["status"] == "ok" for c in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "env": settings.env,
        "version": app.version,
        "checks": checks,
    }


@app.get("/config")
def config():
    return {
        "kafka_topic": settings.kafka.topic,
        "kafka_bootstrap": settings.kafka.bootstrap_servers,
        "paths": {
            "silver": settings.paths.silver,
            "gold": settings.paths.gold,
        },
    }


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ===========================
# Health Check Helpers
# ===========================


def _check_kafka() -> dict:
    try:
        from kafka import KafkaConsumer

        consumer = KafkaConsumer(
            bootstrap_servers=settings.kafka.bootstrap_servers,
            request_timeout_ms=3000,
        )
        consumer.topics()
        consumer.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _check_minio() -> dict:
    try:
        import urllib.request

        url = f"{settings.minio.endpoint}/minio/health/live"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
