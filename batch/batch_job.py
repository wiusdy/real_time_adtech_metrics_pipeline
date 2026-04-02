import yaml
from pyspark.sql.functions import avg

from common.spark import create_spark


class BatchJob:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.spark = create_spark("batch-job")

    def run(self):
        df = self.spark.read.parquet(self.config["paths"]["silver"])

        result = df.groupBy("user_id").agg(avg("value").alias("avg_value"))

        result.write.mode("overwrite").parquet(self.config["paths"]["gold"])

        print("Batch job finished")


if __name__ == "__main__":
    BatchJob("config/dev.yaml").run()
