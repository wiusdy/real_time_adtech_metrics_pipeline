import json
import random
import time

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

while True:
    event = {"user_id": random.randint(1, 10), "value": random.random()}

    producer.send("events", event)
    print("Sent:", event)

    time.sleep(1)
