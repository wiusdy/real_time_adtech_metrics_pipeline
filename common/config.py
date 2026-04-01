from pydantic import BaseModel
import yaml


class KafkaConfig(BaseModel):
    bootstrap_servers: str
    topic: str


class PathsConfig(BaseModel):
    bronze: str
    silver: str
    gold: str


class SparkConfig(BaseModel):
    checkpoint: str


class MinIOConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str


class AppConfig(BaseModel):
    env: str
    kafka: KafkaConfig
    paths: PathsConfig
    spark: SparkConfig
    minio: MinIOConfig

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            return cls(**yaml.safe_load(f))
