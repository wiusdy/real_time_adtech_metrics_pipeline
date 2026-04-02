import yaml
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructType

from common.config import AppConfig
from common.spark import create_spark


def load_config(path):
    with open(path) as f:
        return AppConfig(**yaml.safe_load(f))


class StreamingJob:
    def __init__(self, config):
        self.config = config
        self.spark = create_spark(config.spark.app_name, config.minio)

    def run(self):
        schema = (
            StructType()
            .add("timestamp", StringType())
            .add("campaign_id", IntegerType())
            .add("event_type", StringType())
            .add("price", DoubleType())
        )

        df = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", self.config.kafka.bootstrap_servers)
            .option("subscribe", self.config.kafka.topic)
            .load()
        )

        parsed = (
            df.selectExpr("CAST(value AS STRING)")
            .select(from_json(col("value"), schema).alias("data"))
            .select("data.*")
        )

        (
            parsed.writeStream.format("parquet")
            .option("path", self.config.paths.silver)
            .option("checkpointLocation", self.config.spark.checkpoint)
            .outputMode("append")
            .start()
            .awaitTermination()
        )


if __name__ == "__main__":
    config = load_config("config/dev.yaml")
    StreamingJob(config).run()
