"""
Database setup for RunLoad.

Uses SQLite by default so the whole project runs with zero external
setup. Swapping to Postgres later just means changing DATABASE_URL
to something like postgresql://user:pass@host/dbname and installing
psycopg2-binary -- everything else (models, queries) stays the same.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Keep it local and simple for development. Generates 'runload.db' in the root directory.
DATABASE_URL = "sqlite:///./runload.db"

# Create the engine to talk to the database.
engine = create_engine(
    DATABASE_URL,
    # SQLite is single-threaded by default, but FastAPI requests run on different threads.
    # This arg tells SQLite to let multiple threads access the database safely.
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)

# Session factory for creating temporary database connections.
# autocommit/autoflush are False so we have explicit control over when we save data.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our SQL Models (like Run, User, etc.) will inherit from.
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # Crucial to close this so we don't leak database connections and lock the file.
        db.close()