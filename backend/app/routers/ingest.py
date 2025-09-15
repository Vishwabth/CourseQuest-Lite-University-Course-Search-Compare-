from fastapi import APIRouter, Depends, UploadFile, File, Header, HTTPException
from sqlalchemy.orm import Session
import csv, io
from typing import Optional
from ..database import get_db
from ..models import Course
from ..settings import settings
from ..cache import clear_cache_prefix  
router = APIRouter(prefix="/api")

@router.post("/ingest")
async def ingest_csv(
    file: UploadFile = File(...),
    x_ingest_token:  Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if x_ingest_token != settings.INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid ingest token")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    count = 0

    for row in reader:
        course = Course(
            course_id=int(row["course_id"]),
            course_name=row["course_name"],
            department=row["department"],
            level=row["level"],
            delivery_mode=row["delivery_mode"],
            credits=int(row["credits"]),
            duration_weeks=int(row["duration_weeks"]),
            rating=float(row["rating"]),
            tuition_fee_inr=int(row["tuition_fee_inr"]),
            year_offered=int(row["year_offered"]),
        )

        # ⚡ Upsert by course_id
        existing = db.query(Course).filter(Course.course_id == course.course_id).first()
        if existing:
            for k, v in course.__dict__.items():
                if k not in ["_sa_instance_state", "id"]:
                    setattr(existing, k, v)
        else:
            db.add(course)

        count += 1

    db.commit()

    #  Invalidate all relevant cache namespaces
    clear_cache_prefix("courses:")
    clear_cache_prefix("meta")

    return {
        "status": "ok",
        "ingested": count,
        "cache_cleared": ["courses:*", "meta"],
    }
