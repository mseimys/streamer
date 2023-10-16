from flask import Flask, render_template, Response
from confluent_kafka import Consumer

TOPIC = "busdata"


def get_kafka_client():
    config = {
        "bootstrap.servers": "localhost:29092",
        "group.id": "bus_consumer_group_1",
        "auto.offset.reset": "earliest",
    }
    return Consumer(config)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/topic/<topicname>")
def get_messages(topicname: str):
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
