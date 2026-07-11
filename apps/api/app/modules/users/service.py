import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.users.exceptions import ForbiddenError, InvalidEmailDomainError, UserError
from app.modules.users.models import USER_STATUS_ACTIVE, LOGIN_BLOCKED_STATUSES, User
from app.modules.users.repository import DEFAULT_STUDENT_ROLE, UserRepository
from app.modules.users.schemas import CreateUserData, RoleResponse, UserResponse


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = UserRepository(db)

    def validate_college_email(self, email: str) -> str:
        normalized = email.strip().lower()
        domain = f"@{settings.ALLOWED_EMAIL_DOMAIN}"
        if not normalized.endswith(domain):
            raise InvalidEmailDomainError()
        return normalized

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_by_college_email(self, college_email: str) -> User | None:
        return self.repository.get_by_college_email(college_email)

    def require_active_user(self, user: User | None) -> User:
        if user is None:
            raise UserError("User account not found", status_code=404)
        if user.status in LOGIN_BLOCKED_STATUSES or user.status != USER_STATUS_ACTIVE:
            raise ForbiddenError("Your account is not allowed to sign in")
        return user

    def create_user(self, data: CreateUserData) -> User:
        user = self.repository.create_user(data)
        self.db.flush()
        return self.repository.get_by_id(user.id) or user

    def assign_default_student_role(self, user_id: uuid.UUID) -> None:
        role = self.repository.get_role_by_name(DEFAULT_STUDENT_ROLE)
        if role is None:
            raise UserError("Default role is not configured", status_code=500)
        self.repository.assign_role(user_id, role.id)

    def update_profile_from_sign_in(
        self,
        user: User,
        *,
        first_name: str,
        last_name: str,
        display_name: str,
        avatar_url: str | None,
    ) -> User:
        self.repository.update_profile(
            user,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        return user

    def update_last_login(self, user: User) -> User:
        self.repository.update_last_login(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def to_response(self, user: User) -> UserResponse:
        return UserResponse.from_user(user)

    def list_roles(self) -> list[RoleResponse]:
        return [
            RoleResponse.model_validate(role)
            for role in self.repository.list_roles()
        ]
