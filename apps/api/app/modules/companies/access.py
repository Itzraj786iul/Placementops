from app.modules.companies.exceptions import CompanyForbiddenError
from app.modules.users.models import User
from app.platform.permissions.permissions import has_any_role

STAFF_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER"]


def is_staff_user(user: User) -> bool:
    return has_any_role(user, STAFF_ROLES)


def ensure_staff_access(user: User) -> None:
    if not is_staff_user(user):
        raise CompanyForbiddenError()
