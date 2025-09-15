from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .models import Course
from .routers import courses, ingest, ask, admin
from .settings import settings
from .cache import init_cache 
import os
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CourseQuest Lite API")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Init Cache ----
@app.on_event("startup")
def startup_event():
    init_cache()

# ---- Routers ----
app.include_router(courses.router)
app.include_router(ingest.router)
app.include_router(ask.router)
app.include_router(admin.router)

# ---- Auto Ingest ----
if settings.AUTO_INGEST and os.path.exists(settings.AUTO_INGEST_PATH):
    def _auto_ingest():
        import csv
        with SessionLocal() as db:
            with open(settings.AUTO_INGEST_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    c = db.query(Course).filter(Course.course_id == int(row["course_id"])).first()
                    if not c:
                        c = Course(
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
                        db.add(c)
                db.commit()
    _auto_ingest()
