from confluent_kafka import Consumer, KafkaError
import json
import sys
import argparse

from heatmapper.drawing import CursorPoint, regenerate_heatmap

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Kafka consumer for heatmap generation")
parser.add_argument("consumer_id", type=str, help="Consumer ID for the Kafka group")
args = parser.parse_args()

# Kafka configuration
KAFKA_TOPIC = "cursor"
KAFKA_SERVER = "localhost:9092"

conf = {
    "bootstrap.servers": KAFKA_SERVER,
    "group.id": f"heatmap-consumer-{args.consumer_id}",  # Use consumer ID in group.id
    "enable.auto.commit": "false",
    "auto.offset.reset": "earliest",
}
# Create Kafka consumer
consumer = Consumer(conf)

# List to hold all messages
messages = []

consumer.subscribe([KAFKA_TOPIC])

print("Subscribed to topic", KAFKA_TOPIC)
first_run = True

batch_size = 20
batch = []

try:
    while True:
        # Poll for messages
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            if first_run:
                # If no more messages and it's the first run, regenerate heatmap
                if batch:
                    messages.extend(batch)
                    batch = []
                regenerate_heatmap(messages)
                first_run = False
            continue  # No message, continue polling
        if msg.error():
            # Handle any errors
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print("End of partition reached {0}/{1}".format(msg.topic(), msg.partition()))
            else:
                print("Error: {}".format(msg.error()))
            continue

        # Process the message
        decoded = msg.value().decode("utf-8")
        batch.append(CursorPoint(**json.loads(decoded)))

        print(".", end="", file=sys.stderr)  # Write dot to sys.stderr
        sys.stderr.flush()  # Flush sys.stderr to ensure immediate output

        if len(batch) >= batch_size:
            messages.extend(batch)
            batch = []
            if not first_run:
                regenerate_heatmap(messages)

except KeyboardInterrupt:
    print("Aborted by user")

finally:
    # Close the consumer
    consumer.close()
