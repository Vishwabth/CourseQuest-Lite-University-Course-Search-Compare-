from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CourseOut(BaseModel):
    id: int
    course_id: int
    course_name: str
    department: str
    level: str
    delivery_mode: str
    credits: int
    duration_weeks: int
    rating: float
    tuition_fee_inr: int
    year_offered: int
    class Config:
        from_attributes = True

class CoursesResponse(BaseModel):
    items: List[CourseOut]
    total: int
    page: int
    page_size: int

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2)

class AskResponse(BaseModel):
    parsed_filters: Dict[str, Any]
    results: CoursesResponse
    message: Optional[str] = None
