import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

Base = declarative_base()

_engine = None
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def _build_database_url() -> str:
    """
    Build a SQLAlchemy database URL from environment variables.

    Supports:
      - DATABASE_URL (preferred; full SQLAlchemy URL)
      - SQLITE_PATH (fallback; local sqlite file path)
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    sqlite_path = os.getenv("SQLITE_PATH", "mobile_service.db")
    return f"sqlite:///{sqlite_path}"


# PUBLIC_INTERFACE
def init_db() -> None:
    """Initialize the database engine, session factory, and create all tables."""
    global _engine
    if _engine is not None:
        return

    url = _build_database_url()

    # Special handling for SQLite threading.
    connect_args = {}
    if url.startswith("sqlite:///"):
        connect_args = {"check_same_thread": False}

    _engine = create_engine(url, echo=False, future=True, connect_args=connect_args)
    SessionLocal.configure(bind=_engine)
    Base.metadata.create_all(bind=_engine)


# PUBLIC_INTERFACE
def get_db_session():
    """Get the current request-scoped SQLAlchemy session."""
    return SessionLocal


# PUBLIC_INTERFACE
def shutdown_db_session(exception: Exception | None = None) -> None:
    """Remove the scoped session (called on app context teardown)."""
    SessionLocal.remove()
