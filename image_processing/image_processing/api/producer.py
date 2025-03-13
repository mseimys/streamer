from confluent_kafka import Producer

from image_processing.settings import settings
from image_processing.utils import ensure_topics_exist


class KafkaProducer:
    def __init__(self, topics: list[str]):
        self.topics = topics
        self.producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
        ensure_topics_exist(self.producer, self.topics)

    def send(self, topic: str, key: str, value: str, flush: bool = True):
        assert topic in self.topics
        self.producer.produce(topic, key=key, value=value)
        if flush:
            self.producer.flush()  # Ensure message is sent immediately

    def close(self):
        self.producer.flush()
