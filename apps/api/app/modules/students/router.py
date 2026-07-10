from app.modules.students.router_entities import entity_router
from app.modules.students.router_profiles import students_router

students_router.include_router(entity_router)

__all__ = ["students_router"]
