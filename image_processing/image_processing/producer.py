import os
from confluent_kafka import Producer
import json
from datetime import datetime

from .config import BOOTSTRAP_SERVERS, TOPIC_IMAGE_PROCESSING, DATA_DIR
from .utils import ensure_topics_exist

# Kafka configuration
conf = {"bootstrap.servers": BOOTSTRAP_SERVERS, "client.id": "image-producer"}


def producer():
    # Initialize Kafka producer
    producer = Producer(conf)

    if not ensure_topics_exist(producer, [TOPIC_IMAGE_PROCESSING]):
        return

    def delivery_report(err, msg):
        """Called once for each message produced to indicate delivery result. Triggered by poll() or flush()."""
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    # Read images from the DATA folder and send to Kafka
    for filename in os.listdir(DATA_DIR):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(DATA_DIR, filename)
            file_size = os.path.getsize(file_path)
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

            message = {"path": file_path, "size": file_size, "date": file_date}

            print(f"Found file {file_path}")
            producer.produce(
                TOPIC_IMAGE_PROCESSING,
                value=json.dumps(message).encode("utf-8"),
                key=message["path"],
                callback=delivery_report,
            )

    # Wait for any outstanding messages to be delivered and delivery reports to be received
    producer.flush()
