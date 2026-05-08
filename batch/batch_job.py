from pyspark.sql import SparkSession
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

class BatchJob:

    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("BatchPipeline") \
            .getOrCreate()

    def run(self):
        logger.info("Running batch job...")

        df = self.spark.read.parquet(settings.OUTPUT_PATH)

        result = df.groupBy("user_id").count()

        result.show()


if __name__ == "__main__":
    BatchJob().run()
