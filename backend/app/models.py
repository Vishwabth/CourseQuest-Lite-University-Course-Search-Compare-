from sqlalchemy import Column, Integer, String, Float, Index
from .database import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, unique=True, index=True, nullable=False)
    course_name = Column(String(255), index=True, nullable=False)
    department = Column(String(100), index=True, nullable=False)
    level = Column(String(10), index=True, nullable=False)  # UG/PG
    delivery_mode = Column(String(20), index=True, nullable=False)  # online/offline/hybrid
    credits = Column(Integer, index=True, nullable=False)
    duration_weeks = Column(Integer, index=True, nullable=False)
    rating = Column(Float, index=True, nullable=False)
    tuition_fee_inr = Column(Integer, index=True, nullable=False)
    year_offered = Column(Integer, index=True, nullable=False)

Index("ix_courses_dept_level_mode", Course.department, Course.level, Course.delivery_mode)
Index("ix_courses_fee_rating", Course.tuition_fee_inr, Course.rating)
