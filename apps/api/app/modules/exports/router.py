import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.modules.exports.dependencies import get_export_service
from app.modules.exports.schemas import ExportRequest
from app.modules.exports.service import ExportService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

exports_router = APIRouter(prefix="/opportunities", tags=["exports"])


@exports_router.post("/{opportunity_id}/exports")
def export_opportunity_applications(
    opportunity_id: uuid.UUID,
    payload: ExportRequest,
    current_user: User = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> Response:
    """Staff-only: generate CSV or XLSX export of applications."""
    content, media_type, filename = service.export_applications(
        current_user,
        opportunity_id,
        payload,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
