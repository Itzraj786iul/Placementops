from app.modules.applications.exceptions import ApplicationForbiddenError
from app.modules.applications.models import Application
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
        raise ApplicationForbiddenError("Staff access required")


def ensure_application_read_access(
    user: User,
    application: Application | None,
) -> Application:
    from app.modules.applications.exceptions import ApplicationNotFoundError

    if application is None:
        raise ApplicationNotFoundError()
    if is_staff_user(user):
        return application
    if application.student_profile.user_id == user.id:
        return application
    raise ApplicationForbiddenError()


def ensure_student_profile_access(
    user: User,
    profile: StudentProfile | None,
) -> StudentProfile:
    from app.modules.students.exceptions import StudentNotFoundError

    if profile is None:
        raise StudentNotFoundError()
    if profile.user_id != user.id:
        raise ApplicationForbiddenError("You can only apply using your own profile")
    return profile
