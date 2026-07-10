import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.hiring_opportunities.access import (
    ensure_opportunity_read_access,
    ensure_staff_access,
    is_staff_user,
)
from app.modules.hiring_opportunities.enums import OpportunityStatus, TimelineStage
from app.modules.hiring_opportunities.exceptions import (
    OpportunityNotFoundError,
    OpportunityValidationError,
)
from app.modules.hiring_opportunities.models import (
    EligibilityRule,
    HiringOpportunity,
    OpportunityDocument,
    OpportunityTimeline,
)
from app.modules.hiring_opportunities.repository import HiringOpportunityRepository
from app.modules.hiring_opportunities.schemas import (
    EligibilityRuleResponse,
    EligibilityRuleUpdate,
    OpportunityCreate,
    OpportunityDocumentCreate,
    OpportunityDocumentResponse,
    OpportunityListItem,
    OpportunityResponse,
    OpportunityUpdate,
    TimelineEntryResponse,
    TimelineUpdate,
)
from app.modules.hiring_opportunities.transitions import (
    validate_status_transition,
    validate_timeline_transition,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.audit.serialize import snapshot_fields
from app.modules.users.models import User
from app.utils.datetime import utc_now

_OPPORTUNITY_AUDIT_FIELDS = [
    "company_id",
    "title",
    "role",
    "employment_type",
    "location",
    "mode",
    "ctc_min",
    "ctc_max",
    "bond_details",
    "application_deadline",
    "status",
]


class HiringOpportunityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = HiringOpportunityRepository(db)

    def list_opportunities(
        self,
        user: User,
        status: OpportunityStatus | None = None,
    ) -> list[OpportunityListItem]:
        if is_staff_user(user):
            opportunities = self.repository.list_opportunities(status=status)
        else:
            opportunities = self.repository.list_opportunities(published_only=True)
        return [self._list_item(o) for o in opportunities]

    def create_opportunity(
        self,
        user: User,
        payload: OpportunityCreate,
    ) -> OpportunityResponse:
        ensure_staff_access(user)
        self._validate_company(payload.company_id)
        self._validate_deadline_future(payload.application_deadline)

        opportunity = HiringOpportunity(
            company_id=payload.company_id,
            title=payload.title,
            role=payload.role,
            employment_type=payload.employment_type,
            location=payload.location,
            mode=payload.mode,
            ctc_min=payload.ctc_min,
            ctc_max=payload.ctc_max,
            bond_details=payload.bond_details,
            job_description=payload.job_description,
            application_deadline=payload.application_deadline,
            status=OpportunityStatus.DRAFT,
            created_by=user.id,
        )
        self.repository.save_opportunity(opportunity)

        self.repository.save_eligibility(
            EligibilityRule(
                hiring_opportunity_id=opportunity.id,
                allow_backlog_history=True,
            ),
        )
        self._add_timeline_entry(
            opportunity.id,
            user.id,
            TimelineStage.DRAFT,
            "Opportunity created",
        )

        record_audit(
            self.db,
            entity_type=AuditEntityType.HIRING_OPPORTUNITY,
            entity_id=opportunity.id,
            action=AuditAction.CREATE,
            performed_by=user.id,
            new_values=snapshot_fields(opportunity, _OPPORTUNITY_AUDIT_FIELDS),
        )
        self.db.commit()
        return self._opportunity_response(self.repository.get_by_id(opportunity.id))

    def get_opportunity(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> OpportunityResponse:
        opportunity = ensure_opportunity_read_access(
            user,
            self.repository.get_by_id(opportunity_id),
        )
        return self._opportunity_response(opportunity)

    def update_opportunity(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: OpportunityUpdate,
    ) -> OpportunityResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)
        old_values = snapshot_fields(opportunity, _OPPORTUNITY_AUDIT_FIELDS)

        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise OpportunityValidationError("Archived opportunities cannot be edited")

        if payload.title is not None:
            opportunity.title = payload.title
        if payload.role is not None:
            opportunity.role = payload.role
        if payload.employment_type is not None:
            opportunity.employment_type = payload.employment_type
        if payload.location is not None:
            opportunity.location = payload.location
        if payload.mode is not None:
            opportunity.mode = payload.mode
        if payload.ctc_min is not None:
            opportunity.ctc_min = payload.ctc_min
        if payload.ctc_max is not None:
            opportunity.ctc_max = payload.ctc_max
        if payload.bond_details is not None:
            opportunity.bond_details = payload.bond_details
        if payload.job_description is not None:
            opportunity.job_description = payload.job_description
        if payload.application_deadline is not None:
            self._validate_deadline_future(payload.application_deadline)
            opportunity.application_deadline = payload.application_deadline

        if (
            opportunity.ctc_min is not None
            and opportunity.ctc_max is not None
            and opportunity.ctc_max < opportunity.ctc_min
        ):
            raise OpportunityValidationError(
                "ctc_max must be greater than or equal to ctc_min",
            )

        opportunity.updated_at = utc_now()
        record_audit(
            self.db,
            entity_type=AuditEntityType.HIRING_OPPORTUNITY,
            entity_id=opportunity.id,
            action=AuditAction.UPDATE,
            performed_by=user.id,
            old_values=old_values,
            new_values=snapshot_fields(opportunity, _OPPORTUNITY_AUDIT_FIELDS),
        )
        self.db.commit()
        return self._opportunity_response(self.repository.get_by_id(opportunity_id))

    def publish_opportunity(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> OpportunityResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)
        old_status = opportunity.status

        try:
            validate_status_transition(opportunity.status, OpportunityStatus.PUBLISHED)
        except ValueError as exc:
            raise OpportunityValidationError(str(exc)) from exc

        self._validate_deadline_future(opportunity.application_deadline)

        opportunity.status = OpportunityStatus.PUBLISHED
        opportunity.updated_at = utc_now()
        self._add_timeline_entry(
            opportunity_id,
            user.id,
            TimelineStage.PUBLISHED,
            "Opportunity published",
        )
        record_audit(
            self.db,
            entity_type=AuditEntityType.HIRING_OPPORTUNITY,
            entity_id=opportunity.id,
            action=AuditAction.PUBLISH,
            performed_by=user.id,
            old_values={"status": old_status.value},
            new_values={"status": opportunity.status.value},
        )
        self.db.commit()
        return self._opportunity_response(self.repository.get_by_id(opportunity_id))

    def archive_opportunity(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> OpportunityResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)
        old_status = opportunity.status

        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise OpportunityValidationError("Opportunity is already archived")

        try:
            validate_status_transition(opportunity.status, OpportunityStatus.ARCHIVED)
        except ValueError as exc:
            raise OpportunityValidationError(str(exc)) from exc

        opportunity.status = OpportunityStatus.ARCHIVED
        opportunity.updated_at = utc_now()
        record_audit(
            self.db,
            entity_type=AuditEntityType.HIRING_OPPORTUNITY,
            entity_id=opportunity.id,
            action=AuditAction.ARCHIVE,
            performed_by=user.id,
            old_values={"status": old_status.value},
            new_values={"status": opportunity.status.value},
        )
        self.db.commit()
        return self._opportunity_response(self.repository.get_by_id(opportunity_id))

    def get_eligibility(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> EligibilityRuleResponse:
        ensure_opportunity_read_access(user, self.repository.get_by_id(opportunity_id))
        rule = self.repository.get_eligibility(opportunity_id)
        if rule is None:
            raise OpportunityNotFoundError("Eligibility rules not found")
        return EligibilityRuleResponse.model_validate(rule)

    def update_eligibility(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: EligibilityRuleUpdate,
    ) -> EligibilityRuleResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)

        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise OpportunityValidationError(
                "Cannot update eligibility on archived opportunities",
            )

        rule = self.repository.get_eligibility(opportunity_id)
        if rule is None:
            raise OpportunityNotFoundError("Eligibility rules not found")

        if payload.allowed_departments is not None:
            if not self.repository.departments_exist(payload.allowed_departments):
                raise OpportunityValidationError(
                    "One or more selected departments do not exist",
                )
            rule.allowed_departments = [str(d) for d in payload.allowed_departments]

        if payload.minimum_cgpa is not None:
            rule.minimum_cgpa = payload.minimum_cgpa
        if payload.allowed_graduation_years is not None:
            rule.allowed_graduation_years = payload.allowed_graduation_years
        if payload.maximum_active_backlogs is not None:
            rule.maximum_active_backlogs = payload.maximum_active_backlogs
        if payload.allow_backlog_history is not None:
            rule.allow_backlog_history = payload.allow_backlog_history
        if payload.gender_restriction is not None:
            rule.gender_restriction = payload.gender_restriction or None
        if payload.education_requirements is not None:
            rule.education_requirements = payload.education_requirements

        opportunity.updated_at = utc_now()
        self.db.commit()
        return EligibilityRuleResponse.model_validate(rule)

    def add_document(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: OpportunityDocumentCreate,
    ) -> OpportunityDocumentResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)

        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise OpportunityValidationError(
                "Cannot upload documents to archived opportunities",
            )

        document = OpportunityDocument(
            hiring_opportunity_id=opportunity_id,
            document_type=payload.document_type,
            file_url=payload.file_url,
            uploaded_by=user.id,
        )
        self.repository.save_document(document)
        opportunity.updated_at = utc_now()
        self.db.commit()
        return OpportunityDocumentResponse.model_validate(document)

    def get_timeline(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> list[TimelineEntryResponse]:
        ensure_opportunity_read_access(user, self.repository.get_by_id(opportunity_id))
        return [
            TimelineEntryResponse.model_validate(entry)
            for entry in self.repository.list_timeline(opportunity_id)
        ]

    def update_timeline(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: TimelineUpdate,
    ) -> TimelineEntryResponse:
        ensure_staff_access(user)
        opportunity = self._get_or_raise(opportunity_id)

        if opportunity.status == OpportunityStatus.ARCHIVED:
            raise OpportunityValidationError(
                "Cannot update timeline on archived opportunities",
            )

        current_stage = self._current_timeline_stage(opportunity)
        try:
            validate_timeline_transition(current_stage, payload.stage)
        except ValueError as exc:
            raise OpportunityValidationError(str(exc)) from exc

        entry = self._add_timeline_entry(
            opportunity_id,
            user.id,
            payload.stage,
            payload.remarks,
        )
        opportunity.updated_at = utc_now()
        self.db.commit()
        return TimelineEntryResponse.model_validate(entry)

    def _get_or_raise(self, opportunity_id: uuid.UUID) -> HiringOpportunity:
        opportunity = self.repository.get_by_id(opportunity_id)
        if opportunity is None:
            raise OpportunityNotFoundError()
        return opportunity

    def _validate_company(self, company_id: uuid.UUID) -> None:
        if not self.repository.company_exists(company_id):
            raise OpportunityValidationError("Selected company does not exist")

    def _validate_deadline_future(self, deadline: datetime) -> None:
        now = utc_now()
        if deadline.tzinfo is None:
            raise OpportunityValidationError(
                "application_deadline must include timezone information",
            )
        if deadline <= now:
            raise OpportunityValidationError(
                "application_deadline must be in the future",
            )

    def _add_timeline_entry(
        self,
        opportunity_id: uuid.UUID,
        user_id: uuid.UUID,
        stage: TimelineStage,
        remarks: str | None,
    ) -> OpportunityTimeline:
        entry = OpportunityTimeline(
            hiring_opportunity_id=opportunity_id,
            stage=stage,
            created_by=user_id,
            remarks=remarks,
        )
        return self.repository.save_timeline_entry(entry)

    def _current_timeline_stage(
        self,
        opportunity: HiringOpportunity,
    ) -> TimelineStage | None:
        if not opportunity.timeline_entries:
            return None
        latest = max(opportunity.timeline_entries, key=lambda e: e.created_at)
        return latest.stage

    def _opportunity_response(
        self,
        opportunity: HiringOpportunity | None,
    ) -> OpportunityResponse:
        if opportunity is None:
            raise OpportunityNotFoundError()
        data = OpportunityResponse.model_validate(opportunity)
        data.current_timeline_stage = self._current_timeline_stage(opportunity)
        return data

    def _list_item(self, opportunity: HiringOpportunity) -> OpportunityListItem:
        item = OpportunityListItem.model_validate(opportunity)
        item.current_timeline_stage = self._current_timeline_stage(opportunity)
        return item
