from types import SimpleNamespace
from uuid import uuid4

from app.modules.users.workspace import (
    resolve_primary_role_name,
    resolve_workspace_path,
    role_display_label,
)


def _user(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        roles=[SimpleNamespace(name=name) for name in role_names],
    )


def test_role_priority_prefers_super_admin() -> None:
    user = _user("STUDENT", "SUPER_ADMIN", "PLACEMENT_CELL")
    assert resolve_primary_role_name(user) == "SUPER_ADMIN"
    assert resolve_workspace_path(user) == "/workspace/admin"


def test_role_priority_placement_cell_over_convener() -> None:
    user = _user("PLACEMENT_CONVENER", "PLACEMENT_CELL")
    assert resolve_primary_role_name(user) == "PLACEMENT_CELL"
    assert resolve_workspace_path(user) == "/workspace/placement-cell"


def test_role_priority_student_fallback() -> None:
    user = _user("STUDENT")
    assert resolve_primary_role_name(user) == "STUDENT"
    assert resolve_workspace_path(user) == "/workspace/student"


def test_no_roles_returns_none() -> None:
    user = _user()
    assert resolve_primary_role_name(user) is None
    assert resolve_workspace_path(user) is None


def test_role_display_label() -> None:
    assert role_display_label("STUDENT") == "Student"
    assert role_display_label(None) == "Unassigned"
