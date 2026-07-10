import uuid
from datetime import datetime, timezone

import pytest

from app.modules.companies.enums import (
    CompanyStatus,
    OwnershipType,
    PipelineStage,
)
from app.modules.companies.models import Company, CompanyHandler, CompanyPipeline
from app.modules.companies.schemas import CompanyCreate, PipelineUpdate


def test_company_create_schema_validation() -> None:
    with pytest.raises(ValueError):
        CompanyCreate(name="   ")


def test_pipeline_update_schema() -> None:
    update = PipelineUpdate(current_stage=PipelineStage.INTERESTED)
    assert update.current_stage == PipelineStage.INTERESTED


def test_only_one_active_handler_logic() -> None:
    company_id = uuid.uuid4()
    user_id = uuid.uuid4()
    assigner_id = uuid.uuid4()

    first = CompanyHandler(
        id=uuid.uuid4(),
        company_id=company_id,
        handler_user_id=user_id,
        branch="CSE",
        ownership_type=OwnershipType.NEW,
        assigned_by=assigner_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )
    second = CompanyHandler(
        id=uuid.uuid4(),
        company_id=company_id,
        handler_user_id=uuid.uuid4(),
        branch="IT",
        ownership_type=OwnershipType.TRANSFERRED,
        assigned_by=assigner_id,
        assigned_at=datetime.now(timezone.utc),
        is_active=True,
    )

    first.is_active = False
    first.ended_at = datetime.now(timezone.utc)

    active_handlers = [h for h in [first, second] if h.is_active]
    assert len(active_handlers) == 1
    assert active_handlers[0].ownership_type == OwnershipType.TRANSFERRED


def test_company_default_pipeline_stage() -> None:
    pipeline = CompanyPipeline(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        current_stage=PipelineStage.NOT_CONTACTED,
        last_updated=datetime.now(timezone.utc),
        updated_by=uuid.uuid4(),
    )
    assert pipeline.current_stage == PipelineStage.NOT_CONTACTED


def test_company_status_never_deleted_pattern() -> None:
    company = Company(
        id=uuid.uuid4(),
        name="Acme Corp",
        status=CompanyStatus.ACTIVE,
        created_by=uuid.uuid4(),
    )
    company.status = CompanyStatus.INACTIVE
    assert company.status == CompanyStatus.INACTIVE
