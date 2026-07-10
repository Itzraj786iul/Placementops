from app.modules.hiring_opportunities.exceptions import OpportunityForbiddenError
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.users.models import User
from app.platform.permissions.permissions import has_any_role, has_role

STAFF_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER"]


def is_staff_user(user: User) -> bool:
    return has_any_role(user, STAFF_ROLES)


def is_student_user(user: User) -> bool:
    return has_role(user, "STUDENT")


def ensure_staff_access(user: User) -> None:
    if not is_staff_user(user):
        raise OpportunityForbiddenError("Staff access required")


def ensure_opportunity_read_access(
    user: User,
    opportunity: HiringOpportunity | None,
) -> HiringOpportunity:
    from app.modules.hiring_opportunities.exceptions import OpportunityNotFoundError

    if opportunity is None:
        raise OpportunityNotFoundError()
    if is_staff_user(user):
        return opportunity
    if opportunity.status == OpportunityStatus.PUBLISHED:
        return opportunity
    raise OpportunityForbiddenError()
