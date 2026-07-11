"""Password strength checks for PlacementOS auth."""

from __future__ import annotations

import re

from app.platform.auth.exceptions import AuthError

MIN_PASSWORD_LENGTH = 8


def validate_password_strength(password: str) -> str:
    value = password or ""
    if len(value) < MIN_PASSWORD_LENGTH:
        raise AuthError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
            status_code=422,
        )
    if not re.search(r"[A-Za-z]", value):
        raise AuthError("Password must include a letter", status_code=422)
    if not re.search(r"\d", value):
        raise AuthError("Password must include a number", status_code=422)
    return value
