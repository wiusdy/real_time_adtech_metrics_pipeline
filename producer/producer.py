import json
import random
import time

from kafka import KafkaProducer


class Producer:
    def __init__(self, bootstrap_servers="localhost:9092", topic="events"):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send(self, event: dict):
        self.producer.send(self.topic, event)
        print("Sent:", event)

    def generate_event(self):
        return {
            "user_id": random.randint(1, 10),
            "value": random.random(),
        }

    def run(self, interval=1):
        while True:
            event = self.generate_event()
            self.send(event)
            time.sleep(interval)


# 👇 Permite rodar como script
if __name__ == "__main__":
    producer = Producer()
    producer.run()
