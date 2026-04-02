import yaml
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StructType

from common.spark import create_spark


class StreamingJob:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.spark = create_spark("streaming-job")

    def run(self):
        schema = StructType().add("user_id", IntegerType()).add("value", DoubleType())

        df = (
            self.spark.readStream.format("kafka")
            .option(
                "kafka.bootstrap.servers", self.config["kafka"]["bootstrap_servers"]
            )
            .option("subscribe", self.config["kafka"]["topic"])
            .load()
        )

        parsed = (
            df.selectExpr("CAST(value AS STRING)")
            .select(from_json(col("value"), schema).alias("data"))
            .select("data.*")
        )

        query = (
            parsed.writeStream.format("parquet")
            .option("path", self.config["paths"]["silver"])
            .option("checkpointLocation", "checkpoint/")
            .outputMode("append")
            .start()
        )

        query.awaitTermination()


if __name__ == "__main__":
    StreamingJob("config/dev.yaml").run()
