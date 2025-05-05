from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "FastAPI Assistant API"
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
