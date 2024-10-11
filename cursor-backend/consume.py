from confluent_kafka import Consumer, KafkaError
import json
import os

# Kafka configuration
KAFKA_TOPIC = "cursor"
KAFKA_SERVER = "localhost:9092"

conf = {
    "bootstrap.servers": KAFKA_SERVER,
    "group.id": "heatmap-consumer",
    "enable.auto.commit": "false",
    "auto.offset.reset": "earliest",
}
# Create Kafka consumer
consumer = Consumer(conf)

# List to hold all messages
messages = []

consumer.subscribe([KAFKA_TOPIC])

try:
    while True:
        # Poll for messages
        msg = consumer.poll(1.0)

        if msg is None:
            break  # No more messages
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
        print("Received message: {}".format(msg.value().decode("utf-8")))
        messages.append(json.loads(decoded))

except KeyboardInterrupt:
    print("Aborted by user")

finally:
    # Close the consumer
    consumer.close()

output_file = os.path.join(os.path.dirname(__file__), "messages.json")
with open(output_file, "w") as f:
    json.dump(messages, f, indent=4)
