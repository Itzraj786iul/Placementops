import secrets
import uuid
from datetime import timedelta

import jwt

from app.core.config import settings
from app.platform.auth.exceptions import UnauthorizedError
from app.utils.datetime import utc_now


def create_access_token(user_id: uuid.UUID) -> str:
    expires_at = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "access",
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str]:
    jti = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "refresh",
        "jti": jti,
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid authentication token") from exc

    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid authentication token")
    return payload
