from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlmodel import SQLModel, Field, Column, DateTime, JSON
from pydantic import computed_field

from image_processing.settings import settings


class ImageBase(SQLModel):
    filename: str = Field(nullable=False)
    mimetype: str


class Image(ImageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), default_factory=lambda: datetime.now(ZoneInfo("UTC"))
    )
    filepath: str = Field(unique=True, nullable=False)
    filepath_preview: str = Field(default=None, nullable=True)
    embeddings: list[float] = Field(sa_column=Column(JSON, nullable=True))


class ImagePublic(ImageBase):
    id: int
    created_at: datetime

    @computed_field
    def url(self) -> str:
        return f"{settings.DOMAIN}/images/{self.id}"


class ImageUpdate(ImageBase):
    filename: str | None = None
