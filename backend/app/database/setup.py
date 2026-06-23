from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_CONNECTION_STRING
from app.database.base import Base

engine = create_engine(DB_CONNECTION_STRING,pool_pre_ping=True,pool_recycle=1800)

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
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)