from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from fastapi import Depends

from app.modules.users.exceptions import ForbiddenError
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

P = ParamSpec("P")
R = TypeVar("R")


def has_role(user: User, role_name: str) -> bool:
    return any(role.name == role_name for role in user.roles)


def has_any_role(user: User, role_names: list[str]) -> bool:
    user_roles = {role.name for role in user.roles}
    return any(role in user_roles for role in role_names)


def require_role(*role_names: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_user: User | None = kwargs.get("current_user")
            if current_user is None:
                raise ForbiddenError("Insufficient permissions")
            if not has_any_role(current_user, list(role_names)):
                raise ForbiddenError(
                    f"Requires one of the following roles: {', '.join(role_names)}"
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def RequireRole(*role_names: str):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not has_any_role(current_user, list(role_names)):
            raise ForbiddenError(
                f"Requires one of the following roles: {', '.join(role_names)}"
            )
        return current_user

    return dependency
