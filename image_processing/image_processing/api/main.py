import re
from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from image_processing.settings import settings
from image_processing.api.database import get_db, init_db
from image_processing.api import repository, utils, models, producer
from image_processing.workers.models import ImageForProcessing


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    kafka_producer = producer.KafkaProducer(topics=[settings.KAFKA_TOPIC_IMAGES])
    app.state.producer = kafka_producer
    yield
    kafka_producer.close()
    print("Shutting down...")


# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan, debug=settings.DEBUG)


async def get_kafka_producer():
    yield app.state.producer


@app.get("/images/", response_model=list[models.ImagePublic])
async def get_images(db: Session = Depends(get_db)):
    records = await repository.get_image_records(db)
    return [models.ImagePublic(**r.model_dump()) for r in records]


@app.post("/images/", response_model=models.ImagePublic)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    producer: producer.KafkaProducer = Depends(get_kafka_producer),
):
    # Replace odd characters in filename
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    safe_filepath = uuid4().hex + "_" + safe_filename
    file_path: Path = settings.UPLOAD_DIR / safe_filepath

    # Save file to disk
    await utils.async_save_file(file.file, file_path)

    # Save record in database
    image_record = await repository.save_image_record(
        db,
        filename=safe_filename,
        filepath=str(file_path),
        mimetype=file.content_type or "application/octet-stream",
    )

    message = ImageForProcessing(id=image_record.id, filename=image_record.filename, filepath=image_record.filepath)
    producer.send(
        topic=settings.KAFKA_TOPIC_IMAGES,
        key=image_record.filepath,
        value=message.model_dump_json().encode(),
    )
    print("Message sent:", message)

    return models.ImagePublic(**image_record.model_dump())


@app.get("/images/{image_id}/metadata", response_model=models.ImagePublic)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """Retrieve image metadata by ID."""
    try:
        image = await repository.get_image_record(db, image_id)
    except repository.NotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")

    return models.ImagePublic(**image.model_dump())


@app.get("/images/{image_id}")
async def get_image_content(image_id: int, db: Session = Depends(get_db)):
    """Serve the actual image file."""
    try:
        image = await repository.get_image_record(db, image_id)
    except repository.NotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(image.filepath)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    return StreamingResponse(
        utils.file_reader(file_path),
        media_type=image.mimetype,
        headers={"Content-Disposition": f'inline; filename="{image.filename}"'},
    )


@app.get("/images/{image_id}/preview")
async def get_image_preview(image_id: int, db: Session = Depends(get_db)):
    """Serve a file preview."""
    try:
        image = await repository.get_image_record(db, image_id)
    except repository.NotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(image.filepath_preview)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    return StreamingResponse(
        utils.file_reader(file_path),
        media_type="image/jpeg",
        headers={"Content-Disposition": f'inline; filename="{file_path.name}"'},
    )


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}!"}
