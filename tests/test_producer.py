from unittest.mock import MagicMock, patch

from common.config import AppConfig
from producer.producer import Producer


@patch("producer.producer.KafkaProducer")
def test_generate_event(mock_kafka):
    mock_kafka.return_value = MagicMock()

    config = AppConfig(
        env="test",
        kafka={"bootstrap_servers": "localhost:9092", "topic": "test"},
        paths={"bronze": "", "silver": "", "gold": "", "checkpoint": ""},
        streaming={"watermark": "1 minute", "window": "1 minute"},
        spark={
            "app_name": "test",
            "checkpoint": "/tmp/checkpoint",
        },
        minio={
            "endpoint": "localhost:9000",
            "access_key": "test",
            "secret_key": "test",
        },
    )

    producer = Producer(config)
    event = producer.generate_event()

    assert isinstance(event, dict)
    assert "timestamp" in event
