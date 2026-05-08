from prometheus_client import Counter, Histogram, start_http_server

# Shared pipeline metrics
EVENTS_PRODUCED = Counter(
    "kafka_events_produced_total",
    "Total events sent to Kafka",
)

EVENTS_CONSUMED = Counter(
    "kafka_events_consumed_total",
    "Total events consumed from Kafka",
)

STREAMING_BATCH_DURATION = Histogram(
    "streaming_batch_duration_seconds",
    "Duration of each streaming micro-batch",
)

BATCH_JOB_DURATION = Histogram(
    "batch_job_duration_seconds",
    "Duration of batch job execution",
)


def start_metrics_server(port: int = 9090):
    """Start a standalone Prometheus HTTP server for non-API services."""
    start_http_server(port)
