"""
AWS Glue Batch Job — Aggregates Silver layer into Gold layer.

Usage (deployed via AWS Glue Console or Terraform):
    - Job Type: Spark
    - Glue Version: 4.0
    - Worker Type: G.1X
    - Number of Workers: 2
    - Job Parameters:
        --SILVER_PATH=s3://silver/events/
        --GOLD_PATH=s3://gold/aggregated/
        --GLUE_DATABASE=adtech
        --GLUE_TABLE=metrics_gold
"""

import sys

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import avg, col, sum as spark_sum

# ===========================
# Job Parameters
# ===========================

args = getResolvedOptions(sys.argv, [
    "JOB_NAME",
    "SILVER_PATH",
    "GOLD_PATH",
    "GLUE_DATABASE",
    "GLUE_TABLE",
])

# ===========================
# Glue Context
# ===========================

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

logger = glue_context.get_logger()

# ===========================
# Read Silver Layer
# ===========================

logger.info(f"Reading silver layer from: {args['SILVER_PATH']}")

silver_df = spark.read.parquet(args["SILVER_PATH"])

# ===========================
# Aggregate (Silver → Gold)
# ===========================

gold_df = silver_df.groupBy("user_id").agg(
    avg("avg_value").alias("total_revenue"),
    spark_sum("event_count").alias("total_events"),
)

logger.info(f"Aggregated {gold_df.count()} user records")

# ===========================
# Write Gold Layer to S3
# ===========================

gold_df.write.mode("overwrite").parquet(args["GOLD_PATH"])

logger.info(f"Gold layer written to: {args['GOLD_PATH']}")

# ===========================
# Register in Glue Data Catalog
# ===========================

gold_dynamic_frame = DynamicFrame.fromDF(gold_df, glue_context, "gold_output")

glue_context.write_dynamic_frame.from_catalog(
    frame=gold_dynamic_frame,
    database=args["GLUE_DATABASE"],
    table_name=args["GLUE_TABLE"],
)

logger.info(f"Registered in Glue Catalog: {args['GLUE_DATABASE']}.{args['GLUE_TABLE']}")

job.commit()
