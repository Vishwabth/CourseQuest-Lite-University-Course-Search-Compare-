from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from ..database import get_db
from ..schemas import CoursesResponse, CourseOut
from ..crud import list_courses, compare_courses, meta, serialize_course
from ..cache import get_cache, set_cache

router = APIRouter(prefix="/api")

@router.get("/courses", response_model=CoursesResponse)
def get_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    department: Optional[str] = None,
    level: Optional[str] = None,
    delivery_mode: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_fee: Optional[int] = None,
    min_credits: Optional[int] = None,
    max_credits: Optional[int] = None,
    min_duration_weeks: Optional[int] = None,
    max_duration_weeks: Optional[int] = None,
    year: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    params: Dict[str, Any] = {
        "department": department,
        "level": level,
        "delivery_mode": delivery_mode,
        "min_rating": min_rating,
        "max_fee": max_fee,
        "min_credits": min_credits,
        "max_credits": max_credits,
        "min_duration_weeks": min_duration_weeks,
        "max_duration_weeks": max_duration_weeks,
        "year": year,
        "q": q,
    }

    cache_key = f"courses:{page}:{page_size}:{json.dumps(params, sort_keys=True)}"
    cached = get_cache(cache_key)
    if cached:
        return json.loads(cached)

    items, total = list_courses(db, params, page, page_size)
    result = {
        "items": [serialize_course(i) for i in items],  # ✅ dicts, not models
        "total": total,
        "page": page,
        "page_size": page_size,
    }

    set_cache(cache_key, json.dumps(result), ttl=60)
    return result


@router.get("/compare", response_model=List[CourseOut])
def compare(ids: str, db: Session = Depends(get_db)):
    try:
        id_list = [int(x) for x in ids.split(",") if x.strip()]
    except:
        id_list = []

    cache_key = f"compare:{','.join(map(str, sorted(id_list)))}"
    cached = get_cache(cache_key)
    if cached:
        return json.loads(cached)

    # 🔑 FIX: query using course_id instead of id
    from ..models import Course
    items = db.query(Course).filter(Course.course_id.in_(id_list)).all()

    result = [serialize_course(i) for i in items]
    set_cache(cache_key, json.dumps(result), ttl=60)
    return result



@router.get("/meta")
def get_meta(db: Session = Depends(get_db)):
    cache_key = "meta"
    cached = get_cache(cache_key)
    if cached:
        return json.loads(cached)

    result = meta(db)
    set_cache(cache_key, json.dumps(result), ttl=300)
    return result
