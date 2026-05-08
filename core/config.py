import os

class Settings:
    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "events")

    CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "/tmp/checkpoints")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/tmp/output")

settings = Settings()
