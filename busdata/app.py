import os
from flask import Flask, render_template, Response
from confluent_kafka import Consumer

import collections.abc

collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping

from ksql import KSQLAPI


TOPIC = "busdata"
KAFKA_SERVERS = os.environ.get("KAFKA_SERVERS", "localhost:9092")
KSQL_SERVER_URL = os.environ.get("KSQL_SERVER", "http://localhost:8088")


def get_kafka_client():
    config = {
        "bootstrap.servers": KAFKA_SERVERS,
        "group.id": "bus_consumer_group_1",
        "auto.offset.reset": "latest",
        "partition.assignment.strategy": "cooperative-sticky",
    }
    return Consumer(config)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/topic/<topicname>")
def get_messages(topicname: str):
    if topicname == "riderLocations":
        client = KSQLAPI(KSQL_SERVER_URL)
        query = client.query(
            "SELECT * FROM riderLocations  WHERE GEO_DISTANCE(latitude, longitude, 37.4133, -122.1162) <= 5 EMIT CHANGES"
        )
        # for item in query:
        #     print(item)
        return Response(query, mimetype="text/event-stream")

    consumer = get_kafka_client()
    consumer.subscribe([topicname])

    def events():
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("Waiting...")
            elif msg.error():
                print(f"ERROR: {msg.error()}")
            else:
                print("Got msg...")
                yield "data: {value}\n\n".format(value=msg.value().decode("utf-8"))

    return Response(events(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
