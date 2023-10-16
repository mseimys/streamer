from time import sleep
from confluent_kafka import Consumer, OFFSET_BEGINNING

# Replication and partition count information:
# https://www.conduktor.io/kafka/kafka-topics-choosing-the-replication-factor-and-partitions-count/
# docker exec -t streamer-kafka-1 kafka-topics --bootstrap-server localhost:9092 --topic busdata --describe

TOPIC = "busdata"


if __name__ == "__main__":
    config = {
        "bootstrap.servers": "localhost:29092",
        "group.id": "new_group",
        # 'auto.offset.reset=earliest' to start reading from the beginning of
        # the topic if no committed offsets exist.
        "auto.offset.reset": "earliest",
    }

    # Create Consumer instance
    consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Subscribe to topic
    consumer.subscribe([TOPIC])  # , on_assign=reset_offset

    # Poll for new messages from Kafka and print them.
    i = 0
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print(i, "Waiting...")
            elif msg.error():
                print(f"ERROR: {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.
                print(
                    i,
                    "Consumed event from topic {topic}: key = {key} value = {value}".format(
                        topic=msg.topic(),
                        key=msg.key().decode("utf-8") if msg.key() else None,
                        value=msg.value().decode("utf-8") if msg.value() else None,
                    ),
                )
                sleep(1)
            i += 1
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
