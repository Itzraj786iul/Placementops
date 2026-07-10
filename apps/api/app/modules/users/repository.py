import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.users.models import Role, User, UserRole
from app.modules.users.schemas import CreateUserData
from app.utils.datetime import utc_now

DEFAULT_ROLES = [
    ("SUPER_ADMIN", "Full system administrator with unrestricted access"),
    ("PLACEMENT_CELL", "Placement cell staff managing recruitment operations"),
    ("PLACEMENT_CONVENER", "Placement convener overseeing placement activities"),
    ("STUDENT", "Student user with default access level"),
]

DEFAULT_STUDENT_ROLE = "STUDENT"


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_college_email(self, college_email: str) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.college_email == college_email)
        )
        return self.db.scalars(stmt).first()

    def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self.db.scalars(stmt).first()

    def list_roles(self) -> list[Role]:
        stmt = select(Role).order_by(Role.name)
        return list(self.db.scalars(stmt).all())

    def create_user(self, data: CreateUserData) -> User:
        user = User(
            college_email=data.college_email,
            personal_email=data.personal_email,
            first_name=data.first_name,
            last_name=data.last_name,
            display_name=data.display_name,
            avatar_url=data.avatar_url,
            email_verified=data.email_verified,
            last_login=utc_now(),
        )
        self.db.add(user)
        self.db.flush()
        return user

    def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        self.db.add(UserRole(user_id=user_id, role_id=role_id))

    def clear_roles(self, user_id: uuid.UUID) -> None:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        for user_role in self.db.scalars(stmt).all():
            self.db.delete(user_role)

    def set_password_hash(self, user: User, password_hash: str) -> None:
        user.password_hash = password_hash
        user.updated_at = utc_now()

    def update_last_login(self, user: User) -> None:
        user.last_login = utc_now()
        user.updated_at = utc_now()

    def update_profile(
        self,
        user: User,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if display_name is not None:
            user.display_name = display_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        user.updated_at = utc_now()

    def seed_roles(self) -> None:
        for name, description in DEFAULT_ROLES:
            if self.get_role_by_name(name) is None:
                self.db.add(Role(name=name, description=description))
        self.db.commit()
