import time

from core.config import settings
from core.logger import get_logger
from core.metrics import BATCH_JOB_DURATION
from core.spark import create_spark_session

logger = get_logger(__name__)


class BatchJob:

    def __init__(self):
        self.spark = create_spark_session(f"{settings.spark.app_name}-batch")

    def run(self):
        logger.info("Running batch aggregation (silver -> gold)...")
        start = time.perf_counter()

        df = self.spark.read.parquet(settings.paths.silver)

        result = df.groupBy("user_id").agg(
            {"avg_value": "avg", "event_count": "sum"}
        ).withColumnRenamed("avg(avg_value)", "total_revenue") \
         .withColumnRenamed("sum(event_count)", "total_events")

        result.write.mode("overwrite").parquet(settings.paths.gold)

        duration = time.perf_counter() - start
        BATCH_JOB_DURATION.observe(duration)
        logger.info(f"Batch job finished in {duration:.2f}s. Output: {settings.paths.gold}")


if __name__ == "__main__":
    BatchJob().run()
