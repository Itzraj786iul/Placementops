import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.models import USER_STATUS_ACTIVE, User


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str


class UserResponse(BaseModel):
    id: uuid.UUID
    college_email: EmailStr
    personal_email: EmailStr | None
    first_name: str
    last_name: str
    profile_picture: str | None
    is_active: bool
    roles: list[RoleResponse]
    last_login: datetime | None
    created_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            college_email=user.college_email,
            personal_email=user.personal_email,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_picture=user.avatar_url,
            is_active=user.status == USER_STATUS_ACTIVE,
            roles=[RoleResponse.model_validate(role) for role in user.roles],
            last_login=user.last_login,
            created_at=user.created_at,
        )


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    personal_email: EmailStr | None = None


class CreateUserData(BaseModel):
    college_email: EmailStr
    personal_email: EmailStr | None = None
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    avatar_url: str | None = None
    email_verified: bool = False
