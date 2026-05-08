"""
AWS Glue Streaming Job — Consumes Kafka events and writes to S3 Silver layer.

Usage (deployed via AWS Glue Console or Terraform):
    - Job Type: Glue Streaming
    - Glue Version: 4.0
    - Worker Type: G.1X
    - Number of Workers: 2
    - Job Parameters:
        --KAFKA_BOOTSTRAP_SERVERS=<broker>:9092
        --KAFKA_TOPIC=ad-events
        --OUTPUT_PATH=s3://silver/events/
        --CHECKPOINT_PATH=s3://silver/checkpoints/
        --WINDOW_DURATION=5 minutes
        --WATERMARK=10 minutes
"""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import avg, col, count, from_json, to_timestamp, window
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StructField,
    StructType,
    TimestampType,
)

# ===========================
# Job Parameters
# ===========================

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "KAFKA_BOOTSTRAP_SERVERS",
        "KAFKA_TOPIC",
        "OUTPUT_PATH",
        "CHECKPOINT_PATH",
        "WINDOW_DURATION",
        "WATERMARK",
    ],
)

# ===========================
# Glue Context
# ===========================

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

spark.sparkContext.setLogLevel("WARN")

# ===========================
# Schema
# ===========================

EVENT_SCHEMA = StructType(
    [
        StructField("user_id", IntegerType()),
        StructField("value", DoubleType()),
        StructField("timestamp", TimestampType()),
    ]
)

# ===========================
# Read Stream from Kafka
# ===========================

raw_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", args["KAFKA_BOOTSTRAP_SERVERS"])
    .option("subscribe", args["KAFKA_TOPIC"])
    .option("startingOffsets", "latest")
    .load()
)

# ===========================
# Parse & Aggregate
# ===========================

parsed_df = (
    raw_df.selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), EVENT_SCHEMA).alias("data"))
    .select("data.*")
)

parsed_df = parsed_df.withColumn("timestamp", to_timestamp(col("timestamp")))

aggregated_df = (
    parsed_df.withWatermark("timestamp", args["WATERMARK"])
    .groupBy(
        window(col("timestamp"), args["WINDOW_DURATION"]),
        col("user_id"),
    )
    .agg(
        avg("value").alias("avg_value"),
        count("*").alias("event_count"),
    )
)

# ===========================
# Write to S3 (Silver Layer)
# ===========================

query = (
    aggregated_df.writeStream.format("parquet")
    .option("path", args["OUTPUT_PATH"])
    .option("checkpointLocation", args["CHECKPOINT_PATH"])
    .outputMode("append")
    .start()
)

query.awaitTermination()

job.commit()
