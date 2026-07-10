from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.students.service import StudentService


def get_student_service(db: Session = Depends(get_db_session)) -> StudentService:
    return StudentService(db)
