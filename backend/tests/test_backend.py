# backend/tests/test_backend.py
import os, sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from collections.abc import Generator

# Force SQLite test DB before any app import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Ensure app is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database import Base, get_db
from app.models import Course
from app.settings import settings

# ------------------------
# Shared in-memory SQLite
# ------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # ensures all sessions share same in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ------------------------
# Dependency override
# ------------------------
def override_get_db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ------------------------
# Pytest fixture to seed DB
# ------------------------
@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    course = Course(
        course_id=999,
        course_name="Test Course",
        department="CS",
        level="UG",
        delivery_mode="online",
        credits=4,
        duration_weeks=12,
        rating=4.2,
        tuition_fee_inr=10000,
        year_offered=2025,
    )
    db.add(course)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


# ------------------------
# Core API Tests
# ------------------------
def test_root():
    r = client.get("/")
    assert r.status_code in (200, 404)


def test_list_courses():
    r = client.get("/api/courses?page=1&page_size=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_filter_courses():
    r = client.get("/api/courses?page=1&page_size=5&department=CS")
    assert r.status_code == 200
    data = r.json()
    for c in data["items"]:
        assert c["department"] == "CS"


def test_compare_courses():
    r = client.get("/api/courses?page=1&page_size=5")
    cid = r.json()["items"][0]["id"]

    r = client.get(f"/api/compare?ids={cid}")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(c["course_name"] == "Test Course" for c in data)


def test_meta():
    r = client.get("/api/meta")
    assert r.status_code == 200
    data = r.json()
    assert "departments" in data
    assert "levels" in data
    assert "delivery_modes" in data


def test_ask():
    r = client.post("/api/ask", json={"question": "Show CS courses"})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert "parsed_filters" in data


def test_ingest_csv(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "course_id,course_name,department,level,delivery_mode,credits,duration_weeks,rating,tuition_fee_inr,year_offered\n"
        "1234,CSV Course,CS,UG,offline,3,8,4.1,15000,2025\n"
    )

    with open(csv_file, "rb") as f:
        r = client.post(
            "/api/ingest",
            headers={"x-ingest-token": settings.INGEST_TOKEN},
            files={"file": ("sample.csv", f, "text/csv")},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["ingested"] >= 1


def test_admin_cache_clear():
    r = client.post("/api/cache/clear", headers={"x-admin-token": settings.INGEST_TOKEN})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
