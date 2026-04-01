import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType
from common.config import AppConfig
from common.logger import Logger


class StreamingJob:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = Logger("streaming")
        self.spark = self._create_spark_session()

    def _create_spark_session(self):
        return SparkSession.builder \
            .appName("StreamingJob") \
            .config("spark.hadoop.fs.s3a.endpoint", self.config.minio.endpoint) \
            .config("spark.hadoop.fs.s3a.access.key", self.config.minio.access_key) \
            .config("spark.hadoop.fs.s3a.secret.key", self.config.minio.secret_key) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .getOrCreate()

    def run(self):
        self.logger.info("Starting streaming job")

        schema = StructType() \
            .add("timestamp", StringType()) \
            .add("campaign_id", IntegerType()) \
            .add("event_type", StringType()) \
            .add("price", DoubleType())

        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.config.kafka.bootstrap_servers) \
            .option("subscribe", self.config.kafka.topic) \
            .load()

        parsed_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

        query = parsed_df.writeStream \
            .format("parquet") \
            .option("path", self.config.paths.silver) \
            .option("checkpointLocation", self.config.spark.checkpoint) \
            .outputMode("append") \
            .start()

        query.awaitTermination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = AppConfig.from_yaml(args.config)
    job = StreamingJob(config)
    job.run()
