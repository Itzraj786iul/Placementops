"""Domain trigger helpers — call from services after business events (before commit)."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.modules.applications.enums import ApplicationStatus
from app.modules.applications.models import Application
from app.modules.eligibility.evaluator import evaluate_student, is_eligible
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.students.models import StudentProfile
from app.modules.users.models import User
from app.platform.notifications.enums import NotificationEntityType, NotificationType
from app.platform.notifications.notification_service import NotificationService

logger = logging.getLogger(__name__)


def _frontend_url(path: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}{path}"


def _user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def _opportunity_title(opportunity: HiringOpportunity | None) -> str:
    if opportunity is None:
        return "Hiring opportunity"
    return opportunity.title or "Hiring opportunity"


def notify_opportunity_published(db: Session, opportunity: HiringOpportunity) -> None:
    """Notify eligible students when an opportunity is published."""
    service = NotificationService(db)
    rule = opportunity.eligibility_rule
    stmt = select(StudentProfile).options(
        selectinload(StudentProfile.academic_information),
        selectinload(StudentProfile.personal_information),
        selectinload(StudentProfile.education_history),
        selectinload(StudentProfile.department),
    )
    profiles = list(db.scalars(stmt).all())

    deadline = opportunity.application_deadline
    deadline_line = (
        f"Application deadline: {deadline.strftime('%d %b %Y %H:%M %Z')}."
        if deadline
        else ""
    )
    deadline_clause = f" (deadline {deadline.strftime('%d %b %Y')})" if deadline else ""
    action_url = _frontend_url(f"/opportunities/{opportunity.id}")
    title = _opportunity_title(opportunity)

    notified = 0
    for profile in profiles:
        if not is_eligible(evaluate_student(rule, profile)):
            continue
        user = _user_by_id(db, profile.user_id)
        if user is None:
            continue
        try:
            service.notify(
                recipient=user,
                notification_type=NotificationType.OPPORTUNITY_PUBLISHED,
                context={
                    "opportunity_title": title,
                    "action_url": action_url,
                    "deadline_line": deadline_line,
                    "deadline_clause": deadline_clause,
                },
                entity_type=NotificationEntityType.HIRING_OPPORTUNITY,
                entity_id=opportunity.id,
            )
            notified += 1
        except Exception:  # noqa: BLE001 — never block publish
            logger.exception("Failed to notify user %s on publish", profile.user_id)

    logger.info(
        "Opportunity %s published: notified %s eligible students",
        opportunity.id,
        notified,
    )


def notify_application_submitted(
    db: Session,
    *,
    recipient_user_id: uuid.UUID,
    application_id: uuid.UUID,
    opportunity: HiringOpportunity | None,
) -> None:
    user = _user_by_id(db, recipient_user_id)
    if user is None:
        return
    title = _opportunity_title(opportunity)
    NotificationService(db).notify(
        recipient=user,
        notification_type=NotificationType.APPLICATION_SUBMITTED,
        context={
            "opportunity_title": title,
            "action_url": _frontend_url("/applications"),
        },
        entity_type=NotificationEntityType.APPLICATION,
        entity_id=application_id,
    )


def notify_application_withdrawn(
    db: Session,
    *,
    recipient_user_id: uuid.UUID,
    application_id: uuid.UUID,
    opportunity: HiringOpportunity | None,
) -> None:
    user = _user_by_id(db, recipient_user_id)
    if user is None:
        return
    NotificationService(db).notify(
        recipient=user,
        notification_type=NotificationType.APPLICATION_WITHDRAWN,
        context={
            "opportunity_title": _opportunity_title(opportunity),
            "action_url": _frontend_url("/applications"),
        },
        entity_type=NotificationEntityType.APPLICATION,
        entity_id=application_id,
    )


def notify_application_status_changed(
    db: Session,
    *,
    recipient_user_id: uuid.UUID,
    application_id: uuid.UUID,
    opportunity: HiringOpportunity | None,
    old_status: ApplicationStatus,
    new_status: ApplicationStatus,
) -> None:
    user = _user_by_id(db, recipient_user_id)
    if user is None:
        return

    if new_status == ApplicationStatus.SHORTLISTED:
        ntype = NotificationType.SHORTLISTED
    elif new_status == ApplicationStatus.OFFER_RELEASED:
        ntype = NotificationType.OFFER_RELEASED
    else:
        ntype = NotificationType.APPLICATION_STATUS_CHANGED

    NotificationService(db).notify(
        recipient=user,
        notification_type=ntype,
        context={
            "opportunity_title": _opportunity_title(opportunity),
            "action_url": _frontend_url("/applications"),
            "old_status": old_status.value.replace("_", " ").title(),
            "new_status": new_status.value.replace("_", " ").title(),
        },
        entity_type=NotificationEntityType.APPLICATION,
        entity_id=application_id,
    )


def notify_shortlist_import_affected(
    db: Session,
    *,
    updates: list[tuple[uuid.UUID, ApplicationStatus, ApplicationStatus]],
    opportunity: HiringOpportunity | None,
) -> None:
    """updates: list of (application_id, old_status, new_status)."""
    if not updates:
        return
    app_ids = [item[0] for item in updates]
    status_map = {item[0]: (item[1], item[2]) for item in updates}
    stmt = (
        select(Application)
        .options(selectinload(Application.student_profile))
        .where(Application.id.in_(app_ids))
    )
    applications = list(db.scalars(stmt).all())
    for application in applications:
        profile = application.student_profile
        if profile is None:
            continue
        old_status, new_status = status_map[application.id]
        notify_application_status_changed(
            db,
            recipient_user_id=profile.user_id,
            application_id=application.id,
            opportunity=opportunity,
            old_status=old_status,
            new_status=new_status,
        )


def notify_offer_released_for_opportunity(
    db: Session,
    opportunity: HiringOpportunity,
) -> None:
    """Notify students in SELECTED / OFFER_RELEASED when timeline hits offer stage."""
    stmt = (
        select(Application)
        .options(selectinload(Application.student_profile))
        .where(
            Application.hiring_opportunity_id == opportunity.id,
            Application.status.in_(
                [
                    ApplicationStatus.SELECTED,
                    ApplicationStatus.OFFER_RELEASED,
                ],
            ),
        )
    )
    applications = list(db.scalars(stmt).all())
    service = NotificationService(db)
    title = _opportunity_title(opportunity)
    action_url = _frontend_url("/applications")

    for application in applications:
        profile = application.student_profile
        if profile is None:
            continue
        user = _user_by_id(db, profile.user_id)
        if user is None:
            continue
        try:
            service.notify(
                recipient=user,
                notification_type=NotificationType.OFFER_RELEASED,
                context={
                    "opportunity_title": title,
                    "action_url": action_url,
                },
                entity_type=NotificationEntityType.HIRING_OPPORTUNITY,
                entity_id=opportunity.id,
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed offer notification for application %s",
                application.id,
            )


def _staff_recipients(db: Session) -> list[User]:
    from app.modules.users.models import Role, UserRole

    stmt = (
        select(User)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .where(Role.name.in_(("PLACEMENT_CELL", "PLACEMENT_CONVENER", "SUPER_ADMIN")))
        .options(selectinload(User.roles))
        .distinct()
    )
    return list(db.scalars(stmt).all())


def notify_profile_submitted(db: Session, profile: StudentProfile) -> None:
    """Notify placement staff when a student submits their profile for review."""
    service = NotificationService(db)
    personal = profile.personal_information
    if personal is not None:
        student_name = f"{personal.first_name} {personal.last_name}".strip()
    else:
        owner = _user_by_id(db, profile.user_id)
        student_name = (
            owner.display_name
            if owner is not None
            else profile.roll_number
        )
    action_url = _frontend_url("/workspace/convener")
    context = {
        "student_name": student_name or "Student",
        "roll_number": profile.roll_number,
        "action_url": action_url,
    }

    notified = 0
    for recipient in _staff_recipients(db):
        # Do not notify the submitting student if they somehow hold a staff role.
        if recipient.id == profile.user_id:
            continue
        try:
            service.notify(
                recipient=recipient,
                notification_type=NotificationType.PROFILE_SUBMITTED,
                context=context,
                entity_type=NotificationEntityType.STUDENT_PROFILE,
                entity_id=profile.id,
            )
            notified += 1
        except Exception:  # noqa: BLE001 — never block submit
            logger.exception(
                "Failed profile-submit notification for user %s",
                recipient.id,
            )

    logger.info(
        "Profile %s submitted: notified %s staff recipients",
        profile.id,
        notified,
    )
