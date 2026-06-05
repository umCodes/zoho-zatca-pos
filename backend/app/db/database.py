from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_CONNECTION_STRING
from app.db.base import Base
from app.db.models import Contact


engine = create_engine(DB_CONNECTION_STRING)

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