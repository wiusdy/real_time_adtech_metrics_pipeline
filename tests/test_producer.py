from unittest.mock import MagicMock, patch
from pyspark.sql import SparkSession
from streaming.processor import aggregate_events
from producer.producer import EventProducer


@patch("producer.producer.KafkaProducer")
def test_generate_event(mock_kafka_producer):
    # Mock do Kafka producer
    mock_kafka_producer.return_value = MagicMock()

    producer = EventProducer()

    event = producer.generate_event()

    assert isinstance(event, dict)

    assert "user_id" in event
    assert "value" in event
    assert "timestamp" in event

    assert isinstance(event["user_id"], int)
    assert isinstance(event["value"], float)
    assert isinstance(event["timestamp"], str)


def test_aggregate_events():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()

    data = [
        ("2026-01-01 10:00:00", 1, 10.0),
        ("2026-01-01 10:00:30", 1, 20.0),
    ]

    df = spark.createDataFrame(
        data,
        ["timestamp", "user_id", "value"]
    )

    result = aggregate_events(df)

    assert result is not None
