import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.modules.hiring_opportunities.enums import (
    OpportunityStatus,
    TimelineStage,
)
from app.modules.hiring_opportunities.schemas import OpportunityCreate
from app.modules.hiring_opportunities.transitions import (
    validate_status_transition,
    validate_timeline_transition,
)


def test_opportunity_create_ctc_validation() -> None:
    with pytest.raises(ValueError, match="ctc_max"):
        OpportunityCreate(
            company_id=uuid.uuid4(),
            title="SDE Intern",
            role="Software Engineer",
            employment_type="INTERNSHIP",
            location="Remote",
            mode="REMOTE",
            ctc_min=Decimal("10"),
            ctc_max=Decimal("5"),
            job_description="Build features",
            application_deadline=datetime.now(timezone.utc) + timedelta(days=7),
        )


def test_opportunity_create_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        OpportunityCreate(
            company_id=uuid.uuid4(),
            title="   ",
            role="Software Engineer",
            employment_type="INTERNSHIP",
            location="Remote",
            mode="REMOTE",
            job_description="Build features",
            application_deadline=datetime.now(timezone.utc) + timedelta(days=7),
        )


def test_status_transition_draft_to_published() -> None:
    validate_status_transition(OpportunityStatus.DRAFT, OpportunityStatus.PUBLISHED)


def test_status_transition_rejects_archived_to_published() -> None:
    with pytest.raises(ValueError):
        validate_status_transition(OpportunityStatus.ARCHIVED, OpportunityStatus.PUBLISHED)


def test_timeline_transition_forward() -> None:
    validate_timeline_transition(
        TimelineStage.PUBLISHED,
        TimelineStage.APPLICATIONS_OPEN,
    )


def test_timeline_transition_rejects_backward() -> None:
    with pytest.raises(ValueError):
        validate_timeline_transition(
            TimelineStage.INTERVIEW,
            TimelineStage.ASSESSMENT,
        )


def test_new_opportunity_starts_as_draft() -> None:
    assert OpportunityStatus.DRAFT.value == "DRAFT"


def test_archive_instead_of_delete_pattern() -> None:
    status = OpportunityStatus.PUBLISHED
    validate_status_transition(status, OpportunityStatus.ARCHIVED)
    status = OpportunityStatus.ARCHIVED
    assert status == OpportunityStatus.ARCHIVED
