from app.modules.eligibility.exceptions import EligibilityForbiddenError
from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.students.models import StudentProfile
from app.modules.users.models import User
from app.platform.permissions.permissions import has_any_role, has_role

STAFF_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER"]


def is_staff_user(user: User) -> bool:
    return has_any_role(user, STAFF_ROLES)


def is_student_user(user: User) -> bool:
    return has_role(user, "STUDENT")


def ensure_staff_access(user: User) -> None:
    if not is_staff_user(user):
        raise EligibilityForbiddenError("Staff access required")


def ensure_opportunity_read_access(
    user: User,
    opportunity: HiringOpportunity | None,
) -> HiringOpportunity:
    from app.modules.eligibility.exceptions import EligibilityNotFoundError

    if opportunity is None:
        raise EligibilityNotFoundError("Hiring opportunity not found")
    if is_staff_user(user):
        return opportunity
    if opportunity.status == OpportunityStatus.PUBLISHED:
        return opportunity
    raise EligibilityForbiddenError()


def ensure_student_evaluation_access(
    user: User,
    profile: StudentProfile | None,
) -> StudentProfile:
    from app.modules.eligibility.exceptions import EligibilityNotFoundError

    if profile is None:
        raise EligibilityNotFoundError("Student profile not found")
    if is_staff_user(user):
        return profile
    if profile.user_id == user.id:
        return profile
    raise EligibilityForbiddenError(
        "You can only evaluate your own eligibility",
    )
