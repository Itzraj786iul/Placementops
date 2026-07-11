"""Centralized role priority and workspace path resolution."""

from __future__ import annotations

from app.modules.users.models import User

ROLE_PRIORITY: tuple[str, ...] = (
    "SUPER_ADMIN",
    "PLACEMENT_CELL",
    "PLACEMENT_CONVENER",
    "STUDENT",
)

ROLE_WORKSPACE_MAP: dict[str, str] = {
    "SUPER_ADMIN": "/workspace/admin",
    "PLACEMENT_CELL": "/workspace/placement-cell",
    "PLACEMENT_CONVENER": "/workspace/convener",
    "STUDENT": "/workspace/student",
}

ROLE_DISPLAY_LABELS: dict[str, str] = {
    "SUPER_ADMIN": "Super Admin",
    "PLACEMENT_CELL": "Placement Cell",
    "PLACEMENT_CONVENER": "Placement Convener",
    "STUDENT": "Student",
}


def resolve_primary_role_name(user: User) -> str | None:
    """Highest-priority role from the user's assigned roles (DB-backed)."""
    names = {role.name for role in user.roles}
    if not names:
        return None
    for role_name in ROLE_PRIORITY:
        if role_name in names:
            return role_name
    return None


def resolve_workspace_path(user: User) -> str | None:
    """Workspace path for the highest-priority role, or None if no roles."""
    role_name = resolve_primary_role_name(user)
    if role_name is None:
        return None
    return ROLE_WORKSPACE_MAP[role_name]


def role_display_label(role_name: str | None) -> str:
    if not role_name:
        return "Unassigned"
    return ROLE_DISPLAY_LABELS.get(role_name, role_name)
