"""Database session management with SQLAlchemy 2.0 engine.

Supports both SQLite (WAL mode, foreign keys enabled) and PostgreSQL.
Uses standard synchronous sessions to ensure 100% compatibility across Python versions.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import settings
from ..logging import logger


class Base(DeclarativeBase):
    """Base declarative class for all DevLens ORM models."""
    pass


# Normalize database URL for sync driver if sqlite+aiosqlite was specified in default config
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite+aiosqlite:"):
    db_url = db_url.replace("sqlite+aiosqlite:", "sqlite:")
elif db_url.startswith("postgresql+asyncpg:"):
    db_url = db_url.replace("postgresql+asyncpg:", "postgresql+psycopg2:")

connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

# Synchronous engine
engine = create_engine(
    db_url,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforces SQLite Foreign Key cascade constraints and WAL mode."""
    if dbapi_connection.__class__.__module__ == "sqlite3":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.close()


def init_db() -> None:
    """Initializes tables on startup if they do not exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
