import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, count
from common.config import AppConfig
from common.logger import Logger


class BatchJob:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = Logger("batch")
        self.spark = self._create_spark_session()

    def _create_spark_session(self):
        return SparkSession.builder \
            .appName("BatchJob") \
            .config("spark.hadoop.fs.s3a.endpoint", self.config.minio.endpoint) \
            .config("spark.hadoop.fs.s3a.access.key", self.config.minio.access_key) \
            .config("spark.hadoop.fs.s3a.secret.key", self.config.minio.secret_key) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .getOrCreate()

    def run(self):
        self.logger.info("Starting batch job")

        df = self.spark.read.parquet(self.config.paths.silver)

        agg_df = df.groupBy("campaign_id").agg(
            _sum("price").alias("total_revenue"),
            count("*").alias("total_events")
        )

        agg_df.write.mode("overwrite").parquet(self.config.paths.gold)

        self.logger.info("Batch job finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = AppConfig.from_yaml(args.config)
    job = BatchJob(config)
    job.run()
