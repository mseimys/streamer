from confluent_kafka import Producer

from image_processing.settings import settings


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send(self, topic: str, key: str, value: str):
        self.producer.produce(topic, key=key, value=value)
        self.producer.flush()  # Ensure message is sent immediately

    def close(self):
        self.producer.flush()


async def get_kafka_producer():  # NOT USED
    producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    yield producer
    producer.close()
