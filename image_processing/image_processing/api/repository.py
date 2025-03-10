from sqlmodel import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from image_processing.api.models import Image


class NotFoundError(ValueError):
    pass


async def save_image_record(db: Session, filename: str, filepath: str, mimetype: str):
    db_image = Image(filename=filename, filepath=filepath, mimetype=mimetype)
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    return db_image


async def get_image_record(db: Session, image_id: str):
    query = await db.execute(select(Image).where(Image.id == image_id))
    record = query.scalars().first()

    if record is None:
        raise NotFoundError()

    return record


async def get_image_records(db: AsyncSession):
    return (await db.execute(select(Image))).scalars().all()
