from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_PASSWORD, DB_NAME
from app.db.base import Base
from app.db.models import Contact

DATABASE_URL = (
    f"postgresql+psycopg://postgres:{DB_PASSWORD}@localhost:5433/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)