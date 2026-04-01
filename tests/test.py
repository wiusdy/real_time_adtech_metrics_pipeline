from producer.producer import Producer
from common.config import AppConfig


def test_generate_event():
    config = AppConfig(
        kafka={"bootstrap_servers": "localhost:9092", "topic": "test"},
        paths={"bronze": "", "silver": "", "gold": "", "checkpoint": ""},
        streaming={"watermark": "1 minute", "window": "1 minute"}
    )

    producer = Producer(config)
    event = producer.generate_event()

    assert "timestamp" in event
    assert "campaign_id" in event
    assert "event_type" in event
    assert "price" in event
