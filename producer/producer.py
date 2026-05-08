import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

from core.config import settings

class EventProducer:

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def generate_event(self):
        return {
            "user_id": random.randint(1, 10),
            "value": random.random(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def run(self):
        while True:
            event = self.generate_event()
            self.producer.send(settings.KAFKA_TOPIC, event)
            print("Sent:", event)
            time.sleep(1)


if __name__ == "__main__":
    EventProducer().run()
