from sqlmodel import create_engine, Session
from sqlmodel import *  # noqa: F403, F401
import code

from image_processing.settings import settings
from image_processing.api.models import Image  # noqa: F403, F401

# Create the database engine
engine = create_engine(settings.DATABASE_URL)


def main():
    # Create a session
    session = Session(engine)
    print("""
Shell for Image Processing API
==============================
Example usage:

statement = select(Image).where(Image.id == 10)
image = session.scalars(statement).first()
image.filename = "new_filename.jpg"
session.add(image)
session.commit()

# select(Image).where(Image.id.in_([1,2]))
# images = session.scalars(statement).all()
""")
    # Start an interactive shell with the session in the local namespace
    try:
        code.interact(local=dict(globals(), **locals()), exitmsg="Exiting the shell...")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
