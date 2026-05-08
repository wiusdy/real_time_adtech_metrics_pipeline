from pyspark.sql.functions import avg, col, count, to_timestamp, window


def aggregate_events(df, watermark="1 minute", window_duration="1 minute"):

    parsed_df = df.withColumn("timestamp", to_timestamp(col("timestamp")))

    return (
        parsed_df.withWatermark("timestamp", watermark)
        .groupBy(window(col("timestamp"), window_duration), col("user_id"))
        .agg(avg("value").alias("avg_value"), count("*").alias("event_count"))
    )
