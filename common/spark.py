from pyspark.sql import SparkSession


def create_spark(app_name: str, minio_config):
    spark = (
        SparkSession.builder.appName(app_name)
        .config(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
                    "org.apache.hadoop:hadoop-aws:3.3.4",
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
                ]
            ),
        )
        .getOrCreate()
    )

    # MinIO (S3 local)
    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.endpoint", minio_config.endpoint)
    hadoop_conf.set("fs.s3a.access.key", minio_config.access_key)
    hadoop_conf.set("fs.s3a.secret.key", minio_config.secret_key)
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    return spark
