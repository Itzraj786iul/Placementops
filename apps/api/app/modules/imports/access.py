from app.modules.imports.exceptions import ImportForbiddenError
from app.modules.users.models import User
from app.platform.permissions.permissions import has_any_role

STAFF_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER"]


def ensure_staff_access(user: User) -> None:
    if not has_any_role(user, STAFF_ROLES):
        raise ImportForbiddenError()
