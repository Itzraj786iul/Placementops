from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.applications.router import applications_router
from app.modules.audit.router import audit_router
from app.modules.companies.router import companies_router
from app.modules.eligibility.router import eligibility_router
from app.modules.exports.router import exports_router
from app.modules.hiring_opportunities.router import opportunities_router
from app.modules.imports.router import imports_router
from app.modules.students.router import students_router
from app.modules.users.router import roles_router
from app.platform.auth.router import router as auth_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(roles_router)
api_router.include_router(students_router)
api_router.include_router(companies_router)
api_router.include_router(opportunities_router)
api_router.include_router(applications_router)
api_router.include_router(eligibility_router)
api_router.include_router(exports_router)
api_router.include_router(imports_router)
api_router.include_router(audit_router)
