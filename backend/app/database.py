import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://bustler_pulse_db_user:jeuv7Xya1cTxhvEQdydoeQbAXTWoZCNW@dpg-d8jf9bpkh4rs73djr65g-a/bustler_pulse_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ── Auto-migrate new columns ─────────────────────────────
from sqlalchemy import text

def add_missing_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS screenshot_url VARCHAR"
            ))
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'product_team'"
            ))
            conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")

add_missing_columns()        