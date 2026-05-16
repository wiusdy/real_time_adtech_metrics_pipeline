from pyspark.sql import SparkSession

from core.config import settings


def create_spark_session(app_name: str):

    packages = [
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
        "org.apache.hadoop:hadoop-aws:3.3.4",
        "com.amazonaws:aws-java-sdk-bundle:1.12.262",
    ]

    spark = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config(
            "spark.jars.packages",
            ",".join(packages),
        )
        # -------------------------
        # S3 / MinIO
        # -------------------------
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            settings.minio.endpoint,
        )
        .config(
            "spark.hadoop.fs.s3a.access.key",
            settings.minio.access_key,
        )
        .config(
            "spark.hadoop.fs.s3a.secret.key",
            settings.minio.secret_key,
        )
        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            "true",
        )
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        # -------------------------
        # Optional stability configs
        # -------------------------
        .config(
            "spark.sql.shuffle.partitions",
            "2",
        )
        .config(
            "spark.default.parallelism",
            "2",
        )
        .getOrCreate()
    )

    return spark
