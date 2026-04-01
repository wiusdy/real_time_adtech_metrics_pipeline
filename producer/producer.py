import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime
from common.config import AppConfig
import argparse


class Producer:
    """
    Kafka producer that generates random ad events.
    """

    def __init__(self, config: AppConfig):
        self.config = config

        self.producer = KafkaProducer(
            bootstrap_servers=self.config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

        self.topic = self.config.kafka.topic
        self.event_types = ["impression", "click"]

    def generate_event(self):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "campaign_id": random.randint(1, 5),
            "event_type": random.choice(self.event_types),
            "price": round(random.uniform(0.01, 1.0), 4)
        }

    def send_event(self, event):
        retries = 3

        for attempt in range(retries):
            try:
                self.producer.send(self.topic, event)
                print(f"Sent: {event}")
                return
            except Exception as e:
                print(f"Error (attempt {attempt+1}): {e}")
                time.sleep(1)

        print("Failed to send event.")

    def run(self):
        while True:
            event = self.generate_event()
            self.send_event(event)
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)

    args = parser.parse_args()

    config = AppConfig.from_yaml(args.config)

    producer = Producer(config)
    producer.run()
