from typing import Optional
from pydantic import BaseModel


class ImageForProcessing(BaseModel):
    id: int
    filename: str
    filepath: str


class ImageFeatures(BaseModel):
    width: int
    height: int
    is_square: bool
    embeddings: list[float]


class ImageResult(BaseModel):
    id: int
    features: ImageFeatures
    error: Optional[str] = None
