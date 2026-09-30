from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from dictionary.db_models import Base

DATABASE_URL = "..."

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    with engine.begin() as conn:
        # Enable the pg_trgm extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
