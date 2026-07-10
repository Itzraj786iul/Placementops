import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.modules.applications.enums import ApplicationStatus
from app.modules.imports.dependencies import get_import_service
from app.modules.imports.enums import MatchField
from app.modules.imports.exceptions import ImportValidationError
from app.modules.imports.schemas import ImportConfirmResponse, ImportPreviewResponse
from app.modules.imports.service import ImportService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

imports_router = APIRouter(prefix="/opportunities", tags=["shortlist-imports"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@imports_router.post(
    "/{opportunity_id}/shortlist-imports/preview",
    response_model=ImportPreviewResponse,
)
async def preview_shortlist_import(
    opportunity_id: uuid.UUID,
    file: UploadFile = File(...),
    match_field: MatchField = Form(...),
    target_status: ApplicationStatus = Form(...),
    current_user: User = Depends(get_current_user),
    service: ImportService = Depends(get_import_service),
) -> ImportPreviewResponse:
    """Staff-only: parse and match a shortlist file without applying updates."""
    filename = file.filename or "upload.csv"
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise ImportValidationError("File exceeds 5 MB limit")

    return service.preview(
        current_user,
        opportunity_id,
        filename=filename,
        content=content,
        match_field=match_field,
        target_status=target_status,
    )


@imports_router.post(
    "/{opportunity_id}/shortlist-imports/{import_id}/confirm",
    response_model=ImportConfirmResponse,
)
def confirm_shortlist_import(
    opportunity_id: uuid.UUID,
    import_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ImportService = Depends(get_import_service),
) -> ImportConfirmResponse:
    """Staff-only: apply previewed status updates in bulk."""
    return service.confirm(current_user, opportunity_id, import_id)
