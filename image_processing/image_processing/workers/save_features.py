import logging

from confluent_kafka import Consumer
from sqlmodel import Session, create_engine, select
from sqlalchemy.orm import sessionmaker

from image_processing.settings import settings
from image_processing.utils import ensure_topics_exist
from image_processing.workers import models
from image_processing.api import models as api_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])

log = logging.getLogger(__name__)


def save_features_to_db(session: Session, image_result: models.ImageResult):
    print("Processing image:", image_result.id, image_result.features.embeddings)
    statement = select(api_models.Image).where(api_models.Image.id == image_result.id)
    image = session.scalars(statement).first()
    image.embeddings = image_result.features.embeddings
    session.add(image)
    session.commit()


def consumer():
    consumer = Consumer(
        {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "save-vectors-to-db",
            "auto.offset.reset": "earliest",
        }
    )
    engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
    Session = sessionmaker(engine)

    if not ensure_topics_exist(consumer, [settings.KAFKA_TOPIC_IMAGES_VECTOR]):
        return

    consumer.subscribe([settings.KAFKA_TOPIC_IMAGES_VECTOR])
    log.info(f"Waiting for messages on {settings.KAFKA_TOPIC_IMAGES_VECTOR}. To exit press CTRL+C")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                log.error(f"Consumer error: {msg.error()}")
                continue

            try:
                image_result = models.ImageResult.model_validate_json(msg.value())
                with Session() as session:
                    save_features_to_db(session, image_result)
            except Exception as e:
                # die on error
                raise e
            consumer.commit()
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    consumer()
