import json
import random
import time
from datetime import datetime

from kafka import KafkaProducer


class Producer:
    def __init__(self, config, kafka_producer=None):
        self.config = config
        self.producer = kafka_producer or KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def generate_event(self):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "campaign_id": random.randint(1, 10),
            "event_type": random.choice(["click", "impression"]),
            "price": round(random.random() * 10, 2),
        }

    def run(self):
        while True:
            event = self.generate_event()
            self.producer.send(self.config.kafka.topic, event)
            print(f"Sent: {event}")
            time.sleep(1)
