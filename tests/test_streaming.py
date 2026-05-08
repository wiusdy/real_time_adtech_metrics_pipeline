from pyspark.sql import SparkSession

from streaming.processor import aggregate_events


def test_aggregate_events():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()

    data = [
        ("2026-01-01 10:00:00", 1, 10.0),
        ("2026-01-01 10:00:30", 1, 20.0),
    ]

    df = spark.createDataFrame(data, ["timestamp", "user_id", "value"])

    result = aggregate_events(df)

    assert result is not None
    assert "avg_value" in result.columns
    assert "event_count" in result.columns
