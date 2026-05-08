from pyspark.sql import SparkSession

from core.config import settings


def create_spark_session(app_name: str | None = None) -> SparkSession:
    """Create a SparkSession with S3A/MinIO configuration."""
    name = app_name or settings.spark.app_name

    builder = SparkSession.builder \
        .appName(name) \
        .config("spark.hadoop.fs.s3a.endpoint", settings.minio.endpoint) \
        .config("spark.hadoop.fs.s3a.access.key", settings.minio.access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", settings.minio.secret_key) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.3.4,"
                "com.amazonaws:aws-java-sdk-bundle:1.12.262")

    return builder.getOrCreate()
