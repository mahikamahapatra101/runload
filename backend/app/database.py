"""
db setup. SQLite locally, zero setup needed, just a file on disk.

Render's free tier wipes the filesystem every time it spins down and
back up, which means local SQLite loses everything after a period of
inactivity -- found this out the hard way when my dashboard showed
"no data" a day after uploading. So in production DATABASE_URL gets
set as an env var pointing at a real Postgres instance (using Neon),
which actually persists.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./runload.db")

# Neon (and some other providers) hand back "postgres://" but
# SQLAlchemy wants "postgresql://" -- fixing that here so I don't
# have to remember to edit the connection string by hand every time.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """gives each request its own db session, closes it when done"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
