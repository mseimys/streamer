import json
import os

from confluent_kafka import Consumer, Producer
import torch
from PIL import Image
import open_clip


from image_processing.settings import settings
from image_processing.utils import ensure_topics_exist
from image_processing.workers import models

ALL_TOPICS = [settings.KAFKA_TOPIC_IMAGES, settings.KAFKA_TOPIC_IMAGES_VECTOR, settings.KAFKA_TOPIC_IMAGES_DLQ]

clip_model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
clip_model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active


def process_image(file_path: str) -> models.ImageFeatures:
    with Image.open(file_path) as image:
        width, height = image.size
        is_square = width == height
        preprocessed_image = preprocess(image).unsqueeze(0)
        with torch.no_grad(), torch.amp.autocast("cuda"):
            # preprocessed_image.shape = [1, 3, 224, 224]
            image_features = clip_model.encode_image(preprocessed_image)
            image_features_list = image_features.tolist()[0]
    return models.ImageFeatures(width=width, height=height, is_square=is_square, embeddings=image_features_list)


def callback(image: models.ImageForProcessing, producer: Producer):
    print("Processing image:", image.filepath)

    if image.filepath and os.path.exists(image.filepath):
        features = process_image(image.filepath)

        result = models.ImageResult(id=image.id, features=features)
        message = result.model_dump_json().encode()
        producer.produce(settings.KAFKA_TOPIC_IMAGES_VECTOR, message, key=image.filepath)


def image_processing_consumer():
    producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
    consumer = Consumer(
        {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "image-processor",
            "auto.offset.reset": "earliest",
        }
    )

    if not ensure_topics_exist(consumer, ALL_TOPICS):
        return

    consumer.subscribe([settings.KAFKA_TOPIC_IMAGES])
    print(f"Waiting for messages on {settings.KAFKA_TOPIC_IMAGES}. To exit press CTRL+C")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            try:
                message = models.ImageForProcessing.model_validate_json(msg.value())
                callback(message, producer)
            except Exception as e:
                error_message = json.dumps({"error": str(e), "message": message.model_dump()})
                print("Error:", str(e))
                producer.produce(
                    settings.KAFKA_TOPIC_IMAGES_DLQ,
                    error_message.encode("utf-8"),
                    key=message.filepath,
                )
            consumer.commit()
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
        consumer.close()


if __name__ == "__main__":
    image_processing_consumer()
