from pydantic import BaseModel


class KafkaConfig(BaseModel):
    bootstrap_servers: str
    topic: str


class PathsConfig(BaseModel):
    bronze: str
    silver: str
    gold: str
    checkpoint: str


class StreamingConfig(BaseModel):
    watermark: str
    window: str


class SparkConfig(BaseModel):
    app_name: str
    checkpoint: str


class MinioConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str


class AppConfig(BaseModel):
    env: str
    kafka: KafkaConfig
    paths: PathsConfig
    streaming: StreamingConfig
    spark: SparkConfig
    minio: MinioConfig
