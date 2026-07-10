from app.modules.applications.enums import ApplicationStatus

# Staff may set any status except WITHDRAWN (student-only action).
STAFF_ASSIGNABLE_STATUSES: set[ApplicationStatus] = {
    ApplicationStatus.APPLIED,
    ApplicationStatus.UNDER_REVIEW,
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.ASSESSMENT,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.SELECTED,
    ApplicationStatus.OFFER_RELEASED,
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.REJECTED,
}

TERMINAL_STATUSES: set[ApplicationStatus] = {
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.REJECTED,
    ApplicationStatus.WITHDRAWN,
}


def validate_staff_status_update(
    current: ApplicationStatus,
    target: ApplicationStatus,
) -> None:
    if target == ApplicationStatus.WITHDRAWN:
        raise ValueError("Withdrawn status can only be set by the student")
    if target not in STAFF_ASSIGNABLE_STATUSES:
        raise ValueError(f"Invalid application status: {target.value}")
    if current in TERMINAL_STATUSES:
        raise ValueError(
            f"Cannot update status from terminal state {current.value}",
        )


def can_withdraw(status: ApplicationStatus) -> bool:
    return status not in TERMINAL_STATUSES
