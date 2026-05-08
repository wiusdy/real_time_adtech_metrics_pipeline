import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

from core.config import settings
from core.logger import get_logger
from core.metrics import EVENTS_PRODUCED, start_metrics_server

logger = get_logger(__name__)


class EventProducer:

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def generate_event(self) -> dict:
        return {
            "user_id": random.randint(1, 100),
            "value": round(random.uniform(0.1, 50.0), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def run(self):
        start_metrics_server(port=9091)
        logger.info(f"Producing events to topic '{settings.kafka.topic}'...")
        while True:
            event = self.generate_event()
            self.producer.send(settings.kafka.topic, event)
            EVENTS_PRODUCED.inc()
            logger.info(f"Sent: {event}")
            time.sleep(1)


if __name__ == "__main__":
    EventProducer().run()
