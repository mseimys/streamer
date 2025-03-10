from pydantic import BaseModel


class ImageForProcessing(BaseModel):
    id: int
    filename: str
    filepath: str
