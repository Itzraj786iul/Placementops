import uuid

import pytest

from app.modules.applications.enums import ApplicationStatus, QuestionType
from app.modules.applications.models import ApplicationQuestion
from app.modules.applications.exceptions import ApplicationValidationError
from app.modules.applications.schemas import ApplicationAnswerInput, ApplyRequest
from app.modules.applications.transitions import (
    can_withdraw,
    validate_staff_status_update,
)


def test_apply_request_accepts_valid_payload() -> None:
    payload = ApplyRequest(
        selected_resume_id=uuid.uuid4(),
        answers=[],
    )
    assert payload.selected_resume_id is not None


def test_application_answer_rejects_blank() -> None:
    with pytest.raises(ValueError):
        ApplicationAnswerInput(
            application_question_id=uuid.uuid4(),
            answer="   ",
        )


def test_staff_status_update_rejects_withdrawn() -> None:
    with pytest.raises(ValueError, match="Withdrawn"):
        validate_staff_status_update(
            ApplicationStatus.APPLIED,
            ApplicationStatus.WITHDRAWN,
        )


def test_staff_status_update_rejects_terminal_source() -> None:
    with pytest.raises(ValueError, match="terminal"):
        validate_staff_status_update(
            ApplicationStatus.ACCEPTED,
            ApplicationStatus.UNDER_REVIEW,
        )


def test_staff_status_update_allows_progression() -> None:
    validate_staff_status_update(
        ApplicationStatus.APPLIED,
        ApplicationStatus.UNDER_REVIEW,
    )


def test_can_withdraw_from_active_status() -> None:
    assert can_withdraw(ApplicationStatus.APPLIED) is True


def test_cannot_withdraw_from_terminal_status() -> None:
    assert can_withdraw(ApplicationStatus.WITHDRAWN) is False
    assert can_withdraw(ApplicationStatus.REJECTED) is False


def test_validate_boolean_answer() -> None:
    from app.modules.applications.service import ApplicationService

    service = ApplicationService(db=None)  # type: ignore[arg-type]
    question = ApplicationQuestion(
        id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        question="Available?",
        question_type=QuestionType.BOOLEAN,
        is_required=True,
        display_order=1,
    )
    service._validate_answer_value(question, "true")
    with pytest.raises(ApplicationValidationError, match="true/false"):
        service._validate_answer_value(question, "maybe")


def test_validate_number_answer() -> None:
    from app.modules.applications.service import ApplicationService

    service = ApplicationService(db=None)  # type: ignore[arg-type]
    question = ApplicationQuestion(
        id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        question="Years of experience?",
        question_type=QuestionType.NUMBER,
        is_required=True,
        display_order=1,
    )
    service._validate_answer_value(question, "2.5")
    with pytest.raises(ApplicationValidationError, match="numeric"):
        service._validate_answer_value(question, "abc")


def test_validate_choice_answer() -> None:
    from app.modules.applications.service import ApplicationService

    service = ApplicationService(db=None)  # type: ignore[arg-type]
    question = ApplicationQuestion(
        id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        question="Preferred location?",
        question_type=QuestionType.CHOICE,
        is_required=True,
        display_order=1,
        choices=["Remote", "Onsite"],
    )
    service._validate_answer_value(question, "Remote")
    with pytest.raises(ApplicationValidationError, match="allowed choices"):
        service._validate_answer_value(question, "Hybrid")


def test_new_application_starts_as_applied() -> None:
    assert ApplicationStatus.APPLIED.value == "APPLIED"
