from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.database.session import SessionLocal

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness — process is up (no dependency checks)."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, object]:
    """Readiness — database must accept connections before receiving traffic."""
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
        return {"status": "ready", "database": "ok"}
    except Exception as exc:  # noqa: BLE001 — surface type only
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": "error",
            "detail": type(exc).__name__,
        }
