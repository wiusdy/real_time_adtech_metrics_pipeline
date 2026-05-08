from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StructField, StructType, TimestampType

from core.config import settings
from core.logger import get_logger
from core.metrics import EVENTS_CONSUMED, STREAMING_BATCH_DURATION, start_metrics_server
from streaming.processor import aggregate_events

logger = get_logger(__name__)

schema = StructType([
    StructField("user_id", IntegerType()),
    StructField("value", DoubleType()),
    StructField("timestamp", TimestampType())
])


class StreamingJob:

    def __init__(self):
        self.spark = SparkSession.builder \
            .appName(settings.spark.app_name) \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")

    def read_stream(self):
        return self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", settings.kafka.bootstrap_servers) \
            .option("subscribe", settings.kafka.topic) \
            .load()

    def parse(self, df):
        return df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

    def write(self, df):
        return df.writeStream \
            .format("parquet") \
            .option("path", settings.paths.silver) \
            .option("checkpointLocation", settings.paths.checkpoint) \
            .outputMode("append") \
            .foreachBatch(self._on_batch) \
            .start()

    def _on_batch(self, batch_df, batch_id):
        import time

        start = time.perf_counter()
        count = batch_df.count()
        batch_df.write.mode("append").parquet(settings.paths.silver)
        duration = time.perf_counter() - start

        EVENTS_CONSUMED.inc(count)
        STREAMING_BATCH_DURATION.observe(duration)
        logger.info(f"Batch {batch_id}: {count} events in {duration:.3f}s")

    def run(self):
        start_metrics_server(port=9093)
        logger.info("Starting streaming job...")

        raw_df = self.read_stream()
        parsed_df = self.parse(raw_df)
        aggregated_df = aggregate_events(
            parsed_df,
            watermark=settings.streaming.watermark,
            window_duration=settings.streaming.window,
        )

        query = self.write(aggregated_df)
        query.awaitTermination()


if __name__ == "__main__":
    StreamingJob().run()
