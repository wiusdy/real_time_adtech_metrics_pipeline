from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import *

from core.config import settings
from core.logger import get_logger
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
            .appName("StreamingPipeline") \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")

    def read_stream(self):
        return self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", settings.KAFKA_BOOTSTRAP) \
            .option("subscribe", settings.KAFKA_TOPIC) \
            .load()

    def parse(self, df):
        return df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")

    def write(self, df):
        return df.writeStream \
            .format("parquet") \
            .option("path", settings.OUTPUT_PATH) \
            .option("checkpointLocation", settings.CHECKPOINT_PATH) \
            .outputMode("append") \
            .start()

    def run(self):
        logger.info("Starting streaming job...")

        raw_df = self.read_stream()
        parsed_df = self.parse(raw_df)
        aggregated_df = aggregate_events(parsed_df)

        query = self.write(aggregated_df)

        query.awaitTermination()


if __name__ == "__main__":
    StreamingJob().run()
