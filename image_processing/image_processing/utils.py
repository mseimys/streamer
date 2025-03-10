from confluent_kafka import Consumer, Producer


def ensure_topics_exist(obj: Consumer | Producer, topics: list[str], timeout: int = 5) -> bool:
    """Ensure that the specified topics exist in the Kafka cluster."""
    try:
        metadata = obj.list_topics(timeout=timeout)
        for topic in topics:
            if topic not in metadata.topics:
                print(f"Error: Topic {topic} does not exist!")
                return False
        print(f"Successfully connected to Kafka cluster with {len(metadata.topics)} topics")
        print(f"Broker(s): {metadata.brokers}")
    except Exception as e:
        print(f"Failed to connect to Kafka: {str(e)}")
        return False

    return True
