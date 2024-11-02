import os
import json
import argparse
from time import sleep
from datetime import datetime
from uuid import uuid4

from confluent_kafka import Producer

TOPIC = "scaler"
KAFKA_SERVERS = os.environ.get("KAFKA_SERVERS", "localhost:9092")
COUNT_FILE = "count.txt"


def read_count():
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r") as f:
            return int(f.read().strip())
    return 0


def write_count(count):
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kafka message producer")
    parser.add_argument("--message-count", type=int, default=None, help="Number of messages to produce")
    args = parser.parse_args()

    config = {
        "bootstrap.servers": KAFKA_SERVERS,
        "client.id": "scaler-producer",
        "partition.assignment.strategy": "range",
        # "batch.size": 15,
        # "enable.auto.offset.store": False,
    }
    producer = Producer(config)
    count = read_count()
    try:
        produced_count = 0
        while args.message_count is None or produced_count < args.message_count:
            data = uuid4().hex
            d = {"timestamp": datetime.now().isoformat(), "data": data, "count": count}
            print(d)
            message = json.dumps(d).encode()
            producer.produce(TOPIC, value=message, key=data)
            count += 1
            produced_count += 1
            write_count(count)
            if args.message_count is None:
                sleep(1)
    except KeyboardInterrupt:
        pass

    print("Shutting down...")
    # Typically, flush() should be called prior to shutting down the producer to ensure all outstanding/queued/in-flight messages are delivered.
    producer.flush(10)
    print("Done")
