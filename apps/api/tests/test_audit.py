"""Unit tests for the centralized Audit Log module."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

# Ensure related mappers are registered before AuditLog instantiation.
from app.modules.applications import models as _applications_models  # noqa: F401
from app.modules.companies import models as _companies_models  # noqa: F401
from app.modules.hiring_opportunities import models as _opportunity_models  # noqa: F401
from app.modules.imports import models as _imports_models  # noqa: F401
from app.modules.students import models as _students_models  # noqa: F401
from app.modules.users import models as _users_models  # noqa: F401
from app.modules.audit.access import ensure_staff_access
from app.modules.audit.context import (
    clear_audit_request_context,
    get_audit_request_context,
    set_audit_request_context,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.exceptions import AuditForbiddenError, AuditValidationError
from app.modules.audit.models import AuditLog
from app.modules.audit.recorder import record_audit
from app.modules.audit.schemas import AuditLogResponse, build_list_response
from app.modules.audit.serialize import json_safe, snapshot_fields
from app.modules.audit.service import AuditService
from app.modules.companies.enums import CompanyStatus


def test_json_safe_handles_common_types() -> None:
    entity_id = uuid.uuid4()
    payload = {
        "id": entity_id,
        "status": CompanyStatus.ACTIVE,
        "when": datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
        "nested": {"ok": True},
    }
    safe = json_safe(payload)
    assert safe["id"] == str(entity_id)
    assert safe["status"] == "ACTIVE"
    assert safe["when"].startswith("2026-07-10")
    assert safe["nested"]["ok"] is True


def test_snapshot_fields() -> None:
    obj = SimpleNamespace(name="Acme", status=CompanyStatus.INACTIVE, ignored=1)
    assert snapshot_fields(obj, ["name", "status"]) == {
        "name": "Acme",
        "status": "INACTIVE",
    }


def test_record_audit_uses_request_context() -> None:
    set_audit_request_context("203.0.113.10", "pytest-agent")
    db = MagicMock()
    entry = record_audit(
        db,
        entity_type=AuditEntityType.COMPANY,
        entity_id=uuid.uuid4(),
        action=AuditAction.CREATE,
        performed_by=uuid.uuid4(),
        new_values={"name": "Acme"},
    )
    db.add.assert_called_once_with(entry)
    assert isinstance(entry, AuditLog)
    assert entry.action == AuditAction.CREATE
    assert entry.ip_address == "203.0.113.10"
    assert entry.user_agent == "pytest-agent"
    assert entry.new_values == {"name": "Acme"}
    clear_audit_request_context()
    assert get_audit_request_context().ip_address is None


def test_record_audit_export_and_shortlist_actions() -> None:
    db = MagicMock()
    export_entry = record_audit(
        db,
        entity_type=AuditEntityType.EXPORT,
        entity_id=uuid.uuid4(),
        action=AuditAction.EXPORT_GENERATED,
        performed_by=uuid.uuid4(),
        new_values={"format": "xlsx", "row_count": 3},
    )
    import_entry = record_audit(
        db,
        entity_type=AuditEntityType.SHORTLIST_IMPORT,
        entity_id=uuid.uuid4(),
        action=AuditAction.SHORTLIST_IMPORTED,
        performed_by=uuid.uuid4(),
        new_values={"rows_updated": 2, "rows_skipped": 1},
    )
    assert export_entry.action == AuditAction.EXPORT_GENERATED
    assert import_entry.action == AuditAction.SHORTLIST_IMPORTED
    assert db.add.call_count == 2


def test_build_list_response_pagination() -> None:
    items = [
        AuditLogResponse(
            id=uuid.uuid4(),
            entity_type=AuditEntityType.APPLICATION,
            entity_id=uuid.uuid4(),
            action=AuditAction.APPLY,
            performed_by=uuid.uuid4(),
            performed_at=datetime.now(timezone.utc),
        )
        for _ in range(2)
    ]
    page = build_list_response(items, page=2, page_size=20, total=45)
    assert page.page == 2
    assert page.page_size == 20
    assert page.total == 45
    assert page.total_pages == 3
    assert len(page.items) == 2


def test_audit_service_rejects_invalid_pagination() -> None:
    service = AuditService(MagicMock())
    user = SimpleNamespace(id=uuid.uuid4())
    with pytest.raises(AuditValidationError):
        service._validate_pagination(0, 20)
    with pytest.raises(AuditValidationError):
        service._validate_pagination(1, 0)
    with pytest.raises(AuditValidationError):
        service._validate_pagination(1, 101)


def test_audit_service_list_newest_first_offset() -> None:
    db = MagicMock()
    service = AuditService(db)
    service.repository = MagicMock()
    row = AuditLog(
        id=uuid.uuid4(),
        entity_type=AuditEntityType.HIRING_OPPORTUNITY,
        entity_id=uuid.uuid4(),
        action=AuditAction.PUBLISH,
        performed_by=uuid.uuid4(),
        performed_at=datetime.now(timezone.utc),
        old_values={"status": "DRAFT"},
        new_values={"status": "PUBLISHED"},
        metadata_=None,
    )
    service.repository.list_logs.return_value = ([row], 21)

    class FakeUser:
        def __init__(self) -> None:
            self.id = uuid.uuid4()
            self.roles = [SimpleNamespace(name="SUPER_ADMIN")]

    result = service.list_audit_logs(FakeUser(), page=2, page_size=10)  # type: ignore[arg-type]
    service.repository.list_logs.assert_called_once()
    kwargs = service.repository.list_logs.call_args.kwargs
    assert kwargs["offset"] == 10
    assert kwargs["limit"] == 10
    assert result.total == 21
    assert result.total_pages == 3
    assert result.items[0].action == AuditAction.PUBLISH
    assert result.items[0].metadata is None


def test_entity_list_requires_staff() -> None:
    class StudentUser:
        id = uuid.uuid4()
        roles = [SimpleNamespace(name="STUDENT")]

    with pytest.raises(AuditForbiddenError):
        ensure_staff_access(StudentUser())  # type: ignore[arg-type]


def test_audit_log_response_maps_metadata_alias() -> None:
    row = AuditLog(
        id=uuid.uuid4(),
        entity_type=AuditEntityType.STUDENT_PROFILE,
        entity_id=uuid.uuid4(),
        action=AuditAction.UPDATE,
        performed_by=uuid.uuid4(),
        performed_at=datetime.now(timezone.utc),
        metadata_={"submitted": True},
    )
    response = AuditLogResponse.model_validate(row)
    assert response.metadata == {"submitted": True}
    dumped = response.model_dump(by_alias=True)
    assert dumped["metadata"] == {"submitted": True}


def test_required_entity_types_and_actions_present() -> None:
    assert {
        AuditEntityType.COMPANY,
        AuditEntityType.HIRING_OPPORTUNITY,
        AuditEntityType.APPLICATION,
        AuditEntityType.STUDENT_PROFILE,
        AuditEntityType.SHORTLIST_IMPORT,
        AuditEntityType.EXPORT,
        AuditEntityType.USER,
    } == set(AuditEntityType)
    assert AuditAction.SHORTLIST_IMPORTED in AuditAction
    assert AuditAction.EXPORT_GENERATED in AuditAction
    assert AuditAction.STATUS_CHANGED in AuditAction
    assert AuditAction.ROLE_ASSIGNED in AuditAction
    assert AuditAction.ROLE_REMOVED in AuditAction
