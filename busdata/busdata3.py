import json
from time import sleep
from datetime import datetime
from uuid import uuid4

from confluent_kafka import Producer

# http://geojson.io/#map=14.49/54.67732/25.28783

TOPIC = "busdata"
BUS = "3"


def delivery_callback(err, msg):
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        print(
            "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode("utf-8"), value=msg.value().decode("utf-8")
            )
        )


if __name__ == "__main__":
    config = {"bootstrap.servers": "localhost:29092", "client.id": "busdata1"}

    # Create Producer instance
    producer = Producer(config)

    with open(f"data/bus{BUS}.json") as f:
        data = json.load(f)

    def generate_bus_data():
        for feature in data["features"]:
            coordinates = feature["geometry"]["coordinates"][0]
            while True:
                for coord in coordinates:
                    unique_id = str(uuid4().hex)
                    yield {
                        "id": unique_id,
                        "busline": f"0000{BUS}",
                        "key": f"0000{BUS}-{unique_id}",
                        "timestamp": datetime.now().isoformat(),
                        "latitude": coord[0],
                        "longitude": coord[1],
                    }

    count = 0
    for d in generate_bus_data():
        message = json.dumps(d)
        # print(message)
        producer.produce(TOPIC, value=message.encode(), key=d["key"], callback=delivery_callback)
        producer.poll(1)
        sleep(1)
        count += 1
    # Typically, flush() should be called prior to shutting down the producer to ensure all outstanding/queued/in-flight messages are delivered.
    print("Waiting for 10s...")
    producer.flush(10)
    print("Done")
