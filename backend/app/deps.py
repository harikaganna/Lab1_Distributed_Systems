from sqlalchemy.orm import Session
from typing import Generator
from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
