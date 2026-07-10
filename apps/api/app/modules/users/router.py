from fastapi import APIRouter, Depends

from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import RoleResponse
from app.modules.users.service import UserService
from app.platform.auth.dependencies import get_current_user, get_user_service

roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get("", response_model=list[RoleResponse])
def list_roles(
    _: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> list[RoleResponse]:
    return user_service.list_roles()


def seed_default_roles(db) -> None:
    UserRepository(db).seed_roles()
