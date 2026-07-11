from app.modules.admin.exceptions import AdminForbiddenError
from app.modules.users.models import User
from app.platform.permissions.permissions import has_any_role, has_role

ADMIN_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL"]


def ensure_admin_access(user: User) -> None:
    if not has_any_role(user, ADMIN_ROLES):
        raise AdminForbiddenError("Admin access required")


def is_super_admin(user: User) -> bool:
    return has_role(user, "SUPER_ADMIN")


def target_has_role(target: User, role_name: str) -> bool:
    return any(role.name == role_name for role in target.roles)
