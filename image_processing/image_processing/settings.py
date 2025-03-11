import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

SETTINGS_FILE = Path(__file__).resolve()
BASE_DIR = SETTINGS_FILE.parent


class Settings:
    APP_NAME: str = "Image Processing API"
    BASE_DIR: Path = BASE_DIR
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    DATABASE = {
        "ASYNC_ENGINE": os.getenv("DB_ASYNC_ENGINE", "postgresql+asyncpg"),
        "ENGINE": os.getenv("DB_ENGINE", "postgresql+psycopg2"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": int(os.getenv("DB_PORT", "5432")),
    }
    UPLOAD_DIR: Path = BASE_DIR.parent / "DATA"
    DOMAIN: str = os.getenv("DOMAIN", "http://127.0.0.1:5000")
    DATABASE_URL: URL = None
    ASYNC_DATABASE_URL: URL = None

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092,localhost:9093,localhost:9094")
    KAFKA_TOPIC_IMAGES: str = "images"
    KAFKA_TOPIC_IMAGES_VECTOR: str = "images.vector"
    KAFKA_TOPIC_IMAGES_DLQ: str = "images.dlq"

    def __init__(self):
        print("Settings file loaded:", SETTINGS_FILE)
        print("Upload directory:", self.UPLOAD_DIR)
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.ASYNC_DATABASE_URL = URL.create(
            drivername=self.DATABASE["ASYNC_ENGINE"],
            username=self.DATABASE["USER"],
            password=self.DATABASE["PASSWORD"],
            host=self.DATABASE["HOST"],
            port=self.DATABASE["PORT"],
            database=self.DATABASE["NAME"],
        )
        self.DATABASE_URL = URL.create(
            drivername=self.DATABASE["ENGINE"],
            username=self.DATABASE["USER"],
            password=self.DATABASE["PASSWORD"],
            host=self.DATABASE["HOST"],
            port=self.DATABASE["PORT"],
            database=self.DATABASE["NAME"],
        )


settings = Settings()
