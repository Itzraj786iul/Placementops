from app.modules.users.models import User
from app.modules.students.exceptions import StudentForbiddenError, StudentNotFoundError
from app.modules.students.models import StudentProfile
from app.platform.permissions.permissions import has_any_role

STAFF_ROLES = ["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER"]


def is_staff_user(user: User) -> bool:
    return has_any_role(user, STAFF_ROLES)


def ensure_profile_access(user: User, profile: StudentProfile | None) -> StudentProfile:
    if profile is None:
        raise StudentNotFoundError()
    if not is_staff_user(user) and profile.user_id != user.id:
        raise StudentForbiddenError()
    return profile


def ensure_staff_access(user: User) -> None:
    if not is_staff_user(user):
        raise StudentForbiddenError("Staff access required")
