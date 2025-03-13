import logging
import os

from confluent_kafka import Consumer
from sqlmodel import Session, create_engine, select
from sqlalchemy.orm import sessionmaker

from image_processing.settings import settings
from image_processing.utils import ensure_topics_exist
from image_processing.workers import models
from image_processing.api import models as api_models
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

log = logging.getLogger(__name__)


def generate_and_save_preview_path(session: Session, image: models.ImageForProcessing):
    log.info(f"Processing image ID={image.id}")
    statement = select(api_models.Image).where(api_models.Image.id == image.id)
    db_image = session.scalars(statement).first()
    if db_image.filepath_preview:
        try:
            os.remove(db_image.filepath_preview)
        except OSError as e:
            log.error(f"Error deleting file {db_image.filepath_preview}: {e}")

    # Open the image file
    with Image.open(image.filepath) as img:
        # Resize the image to a maximum of 256x256, maintaining aspect ratio
        img.thumbnail((256, 256))
        preview_path = f"{image.filepath}_preview.jpg"
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(preview_path, "JPEG")

    db_image.filepath_preview = preview_path
    session.add(db_image)
    session.commit()


def consumer():
    consumer = Consumer(
        {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "generate-preview",
            "auto.offset.reset": "earliest",
        }
    )
    engine = create_engine(settings.DATABASE_URL, future=True)
    Session = sessionmaker(engine)

    if not ensure_topics_exist(consumer, [settings.KAFKA_TOPIC_IMAGES]):
        return

    consumer.subscribe([settings.KAFKA_TOPIC_IMAGES])
    log.info(f"Waiting for messages on {settings.KAFKA_TOPIC_IMAGES}. To exit press CTRL+C")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                log.error(f"Consumer error: {msg.error()}")
                continue

            try:
                image = models.ImageForProcessing.model_validate_json(msg.value())
                with Session() as session:
                    generate_and_save_preview_path(session, image)
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
