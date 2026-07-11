from app.modules.admin.access import ensure_admin_access, is_super_admin
from app.modules.admin.exceptions import AdminForbiddenError
from app.modules.users.models import Role, User


def _user_with_roles(*role_names: str) -> User:
    user = User(
        college_email="test@nitrr.ac.in",
        first_name="Test",
        last_name="User",
        display_name="Test User",
    )
    user.roles = [Role(name=name, description=name) for name in role_names]
    return user


def test_ensure_admin_access_allows_cell_and_super() -> None:
    ensure_admin_access(_user_with_roles("SUPER_ADMIN"))
    ensure_admin_access(_user_with_roles("PLACEMENT_CELL"))


def test_ensure_admin_access_rejects_student() -> None:
    try:
        ensure_admin_access(_user_with_roles("STUDENT"))
        raise AssertionError("expected AdminForbiddenError")
    except AdminForbiddenError:
        pass


def test_is_super_admin() -> None:
    assert is_super_admin(_user_with_roles("SUPER_ADMIN")) is True
    assert is_super_admin(_user_with_roles("PLACEMENT_CELL")) is False
