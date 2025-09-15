from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Dict, Any, Tuple
import json

from .cache import get_cache, set_cache
from .models import Course


# -----------------------
# Helpers
# -----------------------
def serialize_course(c: Course) -> Dict[str, Any]:
    """Convert SQLAlchemy Course object → dict (safe for cache)."""
    return {
        "id": c.id,
        "course_id": c.course_id,
        "course_name": c.course_name,
        "department": c.department,
        "level": c.level,
        "delivery_mode": c.delivery_mode,
        "credits": c.credits,
        "duration_weeks": c.duration_weeks,
        "rating": c.rating,
        "tuition_fee_inr": c.tuition_fee_inr,
        "year_offered": c.year_offered,
    }


def apply_filters(stmt, params: Dict[str, Any]):
    if dept := params.get("department"):
        stmt = stmt.where(Course.department == dept)
    if level := params.get("level"):
        stmt = stmt.where(Course.level == level)
    if mode := params.get("delivery_mode"):
        stmt = stmt.where(Course.delivery_mode == mode)
    if q := params.get("q"):
        like = f"%{q}%"
        stmt = stmt.where(Course.course_name.ilike(like))
    if min_rating := params.get("min_rating"):
        stmt = stmt.where(Course.rating >= float(min_rating))
    if max_fee := params.get("max_fee"):
        stmt = stmt.where(Course.tuition_fee_inr <= int(max_fee))
    if min_credits := params.get("min_credits"):
        stmt = stmt.where(Course.credits >= int(min_credits))
    if max_credits := params.get("max_credits"):
        stmt = stmt.where(Course.credits <= int(max_credits))
    if min_dur := params.get("min_duration_weeks"):
        stmt = stmt.where(Course.duration_weeks >= int(min_dur))
    if max_dur := params.get("max_duration_weeks"):
        stmt = stmt.where(Course.duration_weeks <= int(max_dur))
    if year := params.get("year"):
        stmt = stmt.where(Course.year_offered == int(year))
    return stmt


# -----------------------
# Core CRUD
# -----------------------
def list_courses(db: Session, params: Dict[str, Any], page: int, page_size: int) -> Tuple[List[Course], int]:
    """List courses with filters + pagination (cached)."""
    cache_key = f"courses:{json.dumps(params, sort_keys=True)}:p{page}:s{page_size}"
    cached = get_cache(cache_key)
    if cached:
        data = json.loads(cached)
        return [Course(**item) for item in data["items"]], data["total"]

    stmt = select(Course)
    stmt = apply_filters(stmt, params)

    total = db.scalar(
        select(func.count()).select_from(apply_filters(select(Course), params).subquery())
    )
    stmt = stmt.order_by(Course.rating.desc(), Course.tuition_fee_inr.asc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars())

    set_cache(
        cache_key,
        json.dumps({
            "items": [serialize_course(i) for i in items],
            "total": int(total or 0),
        }),
        ttl=60,
    )

    return items, int(total or 0)


def compare_courses(db: Session, ids: List[int]) -> List[Course]:
    """Compare courses by ID (no cache)."""
    if not ids:
        return []
    stmt = select(Course).where(Course.id.in_(ids))
    return list(db.execute(stmt).scalars())


def meta(db: Session) -> Dict[str, List[str]]:
    """Fetch distinct metadata values (cached)."""
    cache_key = "meta"
    cached = get_cache(cache_key)
    if cached:
        return json.loads(cached)

    deps = [r[0] for r in db.execute(select(Course.department).distinct()).all()]
    levels = [r[0] for r in db.execute(select(Course.level).distinct()).all()]
    modes = [r[0] for r in db.execute(select(Course.delivery_mode).distinct()).all()]

    result = {"departments": deps, "levels": levels, "delivery_modes": modes}

    set_cache(cache_key, json.dumps(result), ttl=3600)  # cache for 1h
    return result
