import json
from confluent_kafka import Consumer, KafkaError

BOOTSTRAP_SERVERS = "localhost:9092"


TOPIC = "scaler-results"


def start():
    consumer = Consumer(
        {"bootstrap.servers": BOOTSTRAP_SERVERS, "group.id": "results-consumer", "auto.offset.reset": "earliest"}
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
            message["count"] = str(message["count"]).zfill(5)
            print(message)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    start()
