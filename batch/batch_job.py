import yaml
from pyspark.sql.functions import avg

from common.config import AppConfig
from common.spark import create_spark


def load_config(path):
    with open(path) as f:
        return AppConfig(**yaml.safe_load(f))


class BatchJob:
    def __init__(self, config):
        self.config = config
        self.spark = create_spark(config.spark.app_name, config.minio)

    def run(self):
        df = self.spark.read.parquet(self.config.paths.silver)

        result = df.groupBy("campaign_id").agg(avg("price").alias("avg_price"))

        result.show()

        result.write.mode("overwrite").parquet(self.config.paths.gold)


if __name__ == "__main__":
    config = load_config("config/dev.yaml")
    BatchJob(config).run()
