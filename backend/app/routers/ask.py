from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from ..database import get_db
from ..schemas import AskRequest, AskResponse, CoursesResponse
from ..crud import list_courses
from ..utils.nl_parser import parse_question
from ..cache import get_cache, set_cache

router = APIRouter(prefix="/api")

@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_db)):
    # ---- Cache key
    cache_key = f"ask:{req.question.strip().lower()}"
    cached = get_cache(cache_key)
    if cached:
        return json.loads(cached)

    filters: Dict[str, Any] = parse_question(req.question)
    items, total = list_courses(db, filters, page=1, page_size=10)
    message = None
    if total == 0:
        message = "No matching courses found."

    result = AskResponse(
        parsed_filters=filters,
        results=CoursesResponse(items=items, total=total, page=1, page_size=10),
        message=message
    ).dict()

    set_cache(cache_key, json.dumps(result), ttl=120)  
    return result
