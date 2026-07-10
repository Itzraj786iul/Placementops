from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse
from app.modules.users.service import UserService
from app.platform.auth.exceptions import UnauthorizedError
from app.platform.auth.service import AuthService

security = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(db)


def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials is not None:
        return credentials.credentials
    return request.cookies.get("access_token")


async def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    token = _extract_token(request, credentials)
    if not token:
        raise UnauthorizedError()
    return auth_service.get_user_from_access_token(token)


async def get_optional_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User | None:
    token = _extract_token(request, credentials)
    if not token:
        return None
    try:
        return auth_service.get_user_from_access_token(token)
    except UnauthorizedError:
        return None


def CurrentUser() -> type[User]:
    return Annotated[User, Depends(get_current_user)]


def OptionalUser() -> type[User | None]:
    return Annotated[User | None, Depends(get_optional_user)]


def to_user_response(user: User) -> UserResponse:
    return UserResponse.from_user(user)
