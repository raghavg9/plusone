from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./plusone.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# New enrichment columns added after the first deploy. SQLite can't add
# them via create_all() once the table exists, so patch them in on startup.
_EVENT_COLUMNS = {
    "performer": "VARCHAR DEFAULT ''",
    "venue": "VARCHAR DEFAULT ''",
    "city": "VARCHAR DEFAULT ''",
    "description": "TEXT DEFAULT ''",
    "image_url": "VARCHAR DEFAULT ''",
    "match_key": "VARCHAR DEFAULT ''",
    "source_urls": "TEXT DEFAULT ''",
    "ai_enriched": "BOOLEAN DEFAULT 0",
}


def ensure_schema():
    inspector = inspect(engine)
    if "events" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("events")}
    with engine.begin() as conn:
        for name, ddl in _EVENT_COLUMNS.items():
            if name not in existing:
                conn.execute(
                    text(f"ALTER TABLE events ADD COLUMN {name} {ddl}")
                )
