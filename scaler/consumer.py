import sys
import json
from time import sleep
from random import randint
from confluent_kafka import Consumer, Producer, KafkaError

BOOTSTRAP_SERVERS = "localhost:9092"


TOPIC = "scaler"
RESULT_TOPIC = "scaler-results"


def consume_message(message):
    count = message["count"]
    print(f"[{count}] Starting... ", end="")
    sys.stdout.flush()
    sleep(2)
    if randint(0, 10) > 8:
        raise Exception(f"Random failure - {count}")
    print("Done!")
    return {"count": count, "status": "done"}


def start():
    consumer = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
            "group.id": "my-group",
            "auto.offset.reset": "earliest",
            "auto.commit.interval.ms": 5000,
            "enable.auto.offset.store": False,
            "partition.assignment.strategy": "cooperative-sticky",
        }
    )
    producer = Producer(
        {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
        }
    )

    consumer.subscribe([TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise Exception(msg.error())
            message = json.loads(msg.value().decode("utf-8"))
            try:
                result = consume_message(message)
                result_message = json.dumps(result).encode()
                producer.produce(RESULT_TOPIC, value=result_message)
                consumer.store_offsets(msg)
            except Exception as e:
                print(e)
                raise e
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        producer.flush(10)


if __name__ == "__main__":
    start()
