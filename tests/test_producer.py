from unittest.mock import MagicMock, patch

from producer.producer import EventProducer


@patch("producer.producer.KafkaProducer")
def test_generate_event(mock_kafka_producer):
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


@patch("producer.producer.KafkaProducer")
def test_generate_event_value_range(mock_kafka_producer):
    mock_kafka_producer.return_value = MagicMock()
    producer = EventProducer()

    for _ in range(50):
        event = producer.generate_event()
        assert 1 <= event["user_id"] <= 100
        assert 0.1 <= event["value"] <= 50.0


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
