import os
from pathlib import Path

import yaml
from pydantic import BaseModel


class KafkaConfig(BaseModel):
    bootstrap_servers: str = "localhost:9092"
    topic: str = "ad-events"


class PathsConfig(BaseModel):
    silver: str = "s3a://silver/events/"
    gold: str = "s3a://gold/aggregated/"
    checkpoint: str = "/tmp/checkpoint"


class StreamingConfig(BaseModel):
    watermark: str = "1 minute"
    window: str = "1 minute"


class SparkConfig(BaseModel):
    app_name: str = "adtech-pipeline"


class MinioConfig(BaseModel):
    endpoint: str = "http://localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"


class AppConfig(BaseModel):
    env: str = "dev"
    app_name: str = "adtech-pipeline"
    kafka: KafkaConfig = KafkaConfig()
    paths: PathsConfig = PathsConfig()
    streaming: StreamingConfig = StreamingConfig()
    spark: SparkConfig = SparkConfig()
    minio: MinioConfig = MinioConfig()


def load_config(config_path: str | None = None) -> AppConfig:
    path = config_path or os.getenv("CONFIG_PATH", "config/dev.yaml")
    config_file = Path(path)

    if config_file.exists():
        with open(config_file) as f:
            data = yaml.safe_load(f)
        return AppConfig(**data)

    return AppConfig()


settings = load_config()
