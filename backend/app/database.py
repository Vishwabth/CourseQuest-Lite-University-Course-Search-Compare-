import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError

from .settings import settings

DATABASE_URL = settings.DATABASE_URL

# ---------------------------
# Engine init with fallback
# ---------------------------
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    print("✅ Using SQLite database:", DATABASE_URL)
else:
    engine = None
    for attempt in range(10):
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)
            connection = engine.connect()
            connection.close()
            print("✅ Database connected")
            break
        except OperationalError:
            print(f"❌ Database not ready (attempt {attempt+1}/10). Retrying...")
            time.sleep(5)
    else:
        raise Exception("Database connection failed after 10 attempts")

# ORM Session + Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
