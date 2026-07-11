from fastapi import APIRouter

from app.modules.admin.maintenance_schemas import MaintenancePublicStatus
from app.modules.admin.maintenance_state import get_maintenance_state

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("/status", response_model=MaintenancePublicStatus)
def get_maintenance_status() -> MaintenancePublicStatus:
    """Public maintenance banner — no authentication required."""
    state = get_maintenance_state()
    return MaintenancePublicStatus(**state.public_payload)
