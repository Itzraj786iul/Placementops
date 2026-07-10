import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.applications.access import (
    ensure_application_read_access,
    ensure_staff_access,
    ensure_student_profile_access,
)
from app.modules.applications.enums import ApplicationStatus, QuestionType
from app.modules.applications.exceptions import (
    ApplicationConflictError,
    ApplicationNotFoundError,
    ApplicationValidationError,
)
from app.modules.applications.models import (
    Application,
    ApplicationAnswer,
    ApplicationQuestion,
    ApplicationSnapshot,
)
from app.modules.applications.repository import ApplicationRepository
from app.modules.applications.schemas import (
    ApplicationListItem,
    ApplicationResponse,
    ApplicationSnapshotResponse,
    ApplicationStatusUpdate,
    ApplyRequest,
)
from app.modules.applications.snapshots import (
    build_eligibility_snapshot,
    build_profile_snapshot,
    build_resume_snapshot,
)
from app.modules.applications.transitions import (
    can_withdraw,
    validate_staff_status_update,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.students.repository import StudentRepository
from app.modules.users.models import User
from app.utils.datetime import utc_now


class ApplicationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ApplicationRepository(db)
        self.student_repository = StudentRepository(db)

    def list_my_applications(self, user: User) -> list[ApplicationListItem]:
        profile = self.student_repository.get_profile_by_user_id(user.id)
        ensure_student_profile_access(user, profile)
        applications = self.repository.list_by_student_profile(profile.id)
        return [ApplicationListItem.model_validate(app) for app in applications]

    def apply_to_opportunity(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: ApplyRequest,
    ) -> ApplicationResponse:
        profile = self.student_repository.get_profile_by_user_id(user.id)
        ensure_student_profile_access(user, profile)

        opportunity = self.repository.get_opportunity(opportunity_id)
        if opportunity is None:
            raise ApplicationNotFoundError("Hiring opportunity not found")

        self._validate_opportunity_for_apply(opportunity)

        existing = self.repository.get_by_student_and_opportunity(profile.id, opportunity_id)
        if existing is not None:
            raise ApplicationConflictError(
                "You have already applied to this hiring opportunity",
            )

        resume = self.student_repository.get_resume_by_id(payload.selected_resume_id)
        if resume is None or resume.student_profile_id != profile.id:
            raise ApplicationValidationError("Selected resume does not exist")
        if not resume.is_active:
            raise ApplicationValidationError("Selected resume must be active")

        profile_full = self.student_repository.get_profile_by_id(profile.id)
        if profile_full is None:
            raise ApplicationValidationError("Student profile not found")

        questions = self.repository.list_questions(opportunity_id)
        self._validate_answers(questions, payload.answers)

        application = Application(
            student_profile_id=profile.id,
            hiring_opportunity_id=opportunity_id,
            selected_resume_id=resume.id,
            status=ApplicationStatus.APPLIED,
            submitted_by=user.id,
        )
        self.repository.save_application(application)

        snapshot = ApplicationSnapshot(
            application_id=application.id,
            student_profile_snapshot=build_profile_snapshot(profile_full),
            resume_snapshot=build_resume_snapshot(resume),
            eligibility_snapshot=build_eligibility_snapshot(opportunity.eligibility_rule),
        )
        self.repository.save_snapshot(snapshot)

        for answer_input in payload.answers:
            self.repository.save_answer(
                ApplicationAnswer(
                    application_id=application.id,
                    application_question_id=answer_input.application_question_id,
                    answer=answer_input.answer,
                ),
            )

        record_audit(
            self.db,
            entity_type=AuditEntityType.APPLICATION,
            entity_id=application.id,
            action=AuditAction.APPLY,
            performed_by=user.id,
            new_values={
                "status": application.status.value,
                "hiring_opportunity_id": str(opportunity_id),
                "student_profile_id": str(profile.id),
                "selected_resume_id": str(resume.id),
            },
        )
        from app.platform.notifications.triggers import notify_application_submitted

        try:
            notify_application_submitted(
                self.db,
                recipient_user_id=user.id,
                application_id=application.id,
                opportunity=opportunity,
            )
        except Exception:  # noqa: BLE001
            pass
        self.db.commit()
        return self._application_response(
            self.repository.get_by_id(application.id),
        )

    def get_application(
        self,
        user: User,
        application_id: uuid.UUID,
    ) -> ApplicationResponse:
        application = ensure_application_read_access(
            user,
            self.repository.get_by_id(application_id),
        )
        return self._application_response(application)

    def withdraw_application(
        self,
        user: User,
        application_id: uuid.UUID,
    ) -> ApplicationResponse:
        application = ensure_application_read_access(
            user,
            self.repository.get_by_id(application_id),
        )

        if application.student_profile.user_id != user.id:
            raise ApplicationValidationError(
                "Only the applicant can withdraw an application",
            )

        opportunity = self.repository.get_opportunity(application.hiring_opportunity_id)
        if opportunity is None:
            raise ApplicationNotFoundError("Hiring opportunity not found")

        self._validate_deadline_not_passed(opportunity.application_deadline)

        if not can_withdraw(application.status):
            raise ApplicationValidationError(
                f"Cannot withdraw application in {application.status.value} status",
            )

        old_status = application.status
        application.status = ApplicationStatus.WITHDRAWN
        application.withdrawn_at = utc_now()
        record_audit(
            self.db,
            entity_type=AuditEntityType.APPLICATION,
            entity_id=application.id,
            action=AuditAction.WITHDRAW,
            performed_by=user.id,
            old_values={"status": old_status.value},
            new_values={"status": application.status.value},
        )
        from app.platform.notifications.triggers import notify_application_withdrawn

        try:
            notify_application_withdrawn(
                self.db,
                recipient_user_id=user.id,
                application_id=application.id,
                opportunity=opportunity,
            )
        except Exception:  # noqa: BLE001
            pass
        self.db.commit()
        return self._application_response(
            self.repository.get_by_id(application_id),
        )

    def list_opportunity_applications(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> list[ApplicationListItem]:
        ensure_staff_access(user)
        opportunity = self.repository.get_opportunity(opportunity_id)
        if opportunity is None:
            raise ApplicationNotFoundError("Hiring opportunity not found")

        applications = self.repository.list_by_opportunity(opportunity_id)
        return [ApplicationListItem.model_validate(app) for app in applications]

    def update_application_status(
        self,
        user: User,
        application_id: uuid.UUID,
        payload: ApplicationStatusUpdate,
    ) -> ApplicationResponse:
        ensure_staff_access(user)
        application = self.repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError()

        try:
            validate_staff_status_update(application.status, payload.status)
        except ValueError as exc:
            raise ApplicationValidationError(str(exc)) from exc

        old_status = application.status
        application.status = payload.status
        record_audit(
            self.db,
            entity_type=AuditEntityType.APPLICATION,
            entity_id=application.id,
            action=AuditAction.STATUS_CHANGED,
            performed_by=user.id,
            old_values={"status": old_status.value},
            new_values={"status": application.status.value},
            metadata={"remarks": payload.remarks} if payload.remarks else None,
        )
        from app.platform.notifications.triggers import notify_application_status_changed

        opportunity = self.repository.get_opportunity(application.hiring_opportunity_id)
        try:
            notify_application_status_changed(
                self.db,
                recipient_user_id=application.student_profile.user_id,
                application_id=application.id,
                opportunity=opportunity,
                old_status=old_status,
                new_status=payload.status,
            )
        except Exception:  # noqa: BLE001
            pass
        self.db.commit()
        return self._application_response(
            self.repository.get_by_id(application_id),
        )

    def get_application_snapshot(
        self,
        user: User,
        application_id: uuid.UUID,
    ) -> ApplicationSnapshotResponse:
        ensure_staff_access(user)
        application = self.repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError()

        if application.snapshot is None:
            raise ApplicationNotFoundError("Application snapshot not found")

        return ApplicationSnapshotResponse.model_validate(application.snapshot)

    def _validate_opportunity_for_apply(self, opportunity) -> None:
        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise ApplicationValidationError(
                "Applications are not accepted for archived opportunities",
            )
        if opportunity.status != OpportunityStatus.PUBLISHED:
            raise ApplicationValidationError(
                "Applications are only accepted for published opportunities",
            )
        self._validate_deadline_not_passed(opportunity.application_deadline)

    def _validate_deadline_not_passed(self, deadline: datetime) -> None:
        now = utc_now()
        if deadline.tzinfo is None:
            raise ApplicationValidationError(
                "Opportunity deadline must include timezone information",
            )
        if deadline <= now:
            raise ApplicationValidationError(
                "The application deadline for this opportunity has passed",
            )

    def _validate_answers(
        self,
        questions: list[ApplicationQuestion],
        answers: list,
    ) -> None:
        questions_by_id = {question.id: question for question in questions}
        answered_ids: set[uuid.UUID] = set()

        for answer_input in answers:
            question = questions_by_id.get(answer_input.application_question_id)
            if question is None:
                raise ApplicationValidationError(
                    "One or more answers reference invalid questions",
                )
            if answer_input.application_question_id in answered_ids:
                raise ApplicationValidationError(
                    "Duplicate answers provided for the same question",
                )
            answered_ids.add(answer_input.application_question_id)
            self._validate_answer_value(question, answer_input.answer)

        missing_required = [
            question
            for question in questions
            if question.is_required and question.id not in answered_ids
        ]
        if missing_required:
            raise ApplicationValidationError(
                "Required application questions must be answered",
            )

    def _validate_answer_value(
        self,
        question: ApplicationQuestion,
        answer: str,
    ) -> None:
        if question.question_type == QuestionType.BOOLEAN:
            if answer.lower() not in {"true", "false"}:
                raise ApplicationValidationError(
                    f"Question '{question.question}' requires a true/false answer",
                )
            return

        if question.question_type == QuestionType.NUMBER:
            try:
                float(answer)
            except ValueError as exc:
                raise ApplicationValidationError(
                    f"Question '{question.question}' requires a numeric answer",
                ) from exc
            return

        if question.question_type == QuestionType.CHOICE:
            if not question.choices:
                raise ApplicationValidationError(
                    f"Question '{question.question}' has no configured choices",
                )
            if answer not in question.choices:
                raise ApplicationValidationError(
                    f"Answer for '{question.question}' must be one of the allowed choices",
                )

    def _application_response(
        self,
        application: Application | None,
    ) -> ApplicationResponse:
        if application is None:
            raise ApplicationNotFoundError()
        return ApplicationResponse.model_validate(application)
