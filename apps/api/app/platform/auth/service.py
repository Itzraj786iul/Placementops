import secrets
import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.users.models import USER_STATUS_ACTIVE, User
from app.modules.users.schemas import CreateUserData, UserResponse
from app.modules.users.service import UserService
from app.platform.auth.exceptions import AuthError, InvalidAuthCodeError, UnauthorizedError
from app.platform.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.platform.auth.password import verify_password
from app.platform.auth.models import PROVIDER_GOOGLE
from app.platform.auth.schemas import TokenResponse
from app.platform.auth.session import AuthRepository
from app.utils.datetime import utc_now


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.auth_repository = AuthRepository(db)
        self.user_service = UserService(db)

    def authenticate_dev_login(self, email: str, password: str) -> User:
        if not settings.ENABLE_DEV_LOGIN:
            raise AuthError("Dev login is not enabled", status_code=404)

        college_email = self.user_service.validate_college_email(email)
        user = self.user_service.get_by_college_email(college_email)
        if user is None or not user.password_hash:
            raise AuthError("Invalid email or password", status_code=401)

        if not verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password", status_code=401)

        user = self.user_service.require_active_user(user)
        self.user_service.update_last_login(user)
        from app.modules.admin.maintenance_service import MaintenanceService

        MaintenanceService.assert_user_may_authenticate(user)
        return user

    def authenticate_google_user(self, user_info: dict) -> User:
        provider_user_id = user_info.get("sub")
        email = user_info.get("email")
        if not provider_user_id or not email:
            raise AuthError("Google account information is incomplete", status_code=400)

        college_email = self.user_service.validate_college_email(email)
        identity = self.auth_repository.get_identity(
            PROVIDER_GOOGLE,
            provider_user_id,
        )

        if identity is not None:
            user = self.user_service.get_by_id(identity.user_id)
        else:
            user = self.user_service.get_by_college_email(college_email)
            if user is not None:
                self.auth_repository.create_identity(
                    user.id,
                    PROVIDER_GOOGLE,
                    provider_user_id,
                    email,
                )
            else:
                user = self._create_user_from_provider(user_info, college_email)
                self.auth_repository.create_identity(
                    user.id,
                    PROVIDER_GOOGLE,
                    provider_user_id,
                    email,
                )

        user = self.user_service.require_active_user(user)
        self._sync_profile_from_provider(user, user_info)
        self.user_service.update_last_login(user)
        from app.modules.admin.maintenance_service import MaintenanceService

        MaintenanceService.assert_user_may_authenticate(user)
        return user

    def create_auth_code(self, user: User) -> str:
        code = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(minutes=settings.AUTH_CODE_EXPIRE_MINUTES)
        self.auth_repository.create_auth_code(user.id, code, expires_at)
        self.db.commit()
        return code

    def exchange_auth_code(self, code: str) -> TokenResponse:
        auth_code = self.auth_repository.get_auth_code(code)
        if auth_code is None or auth_code.used_at is not None:
            raise InvalidAuthCodeError()
        if auth_code.expires_at < utc_now():
            raise InvalidAuthCodeError()

        user = self.user_service.get_by_id(auth_code.user_id)
        if user is None or user.status != USER_STATUS_ACTIVE:
            raise InvalidAuthCodeError()

        self.auth_repository.mark_auth_code_used(auth_code)
        self.db.commit()
        from app.modules.admin.maintenance_service import MaintenanceService

        MaintenanceService.assert_user_may_authenticate(user)
        return self.create_tokens(user)

    def create_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token, jti = create_refresh_token(user.id)
        expires_at = utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.auth_repository.create_refresh_token(user.id, jti, expires_at)
        self.db.commit()
        needs_welcome = user.welcome_completed_at is None
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self.user_service.to_response(user),
            is_new_user=needs_welcome,
        )

    def complete_welcome(self, user: User) -> UserResponse:
        updated = self.user_service.complete_welcome(user)
        return self.user_service.to_response(updated)

    def refresh_session(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = uuid.UUID(payload["sub"])
        jti = payload["jti"]

        stored = self.auth_repository.get_refresh_token(jti)
        if stored is None or stored.revoked_at is not None:
            raise UnauthorizedError("Session has expired. Please sign in again")
        if stored.expires_at < utc_now():
            raise UnauthorizedError("Session has expired. Please sign in again")

        user = self.user_service.get_by_id(user_id)
        if user is None or user.status != USER_STATUS_ACTIVE:
            raise UnauthorizedError("Account is no longer active")

        self.auth_repository.revoke_refresh_token(stored)
        return self.create_tokens(user)

    def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            stored = self.auth_repository.get_refresh_token(payload["jti"])
            if stored is not None:
                self.auth_repository.revoke_refresh_token(stored)
                self.db.commit()
        except UnauthorizedError:
            return

    def get_user_from_access_token(self, token: str) -> User:
        payload = decode_token(token, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
        user = self.user_service.get_by_id(user_id)
        if user is None or user.status != USER_STATUS_ACTIVE:
            raise UnauthorizedError("Account is no longer active")
        return user

    def _create_user_from_provider(
        self,
        user_info: dict,
        college_email: str,
    ) -> User:
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        display_name = user_info.get("name") or f"{first_name} {last_name}".strip()
        user = self.user_service.create_user(
            CreateUserData(
                college_email=college_email,
                personal_email=None,
                first_name=first_name,
                last_name=last_name,
                display_name=display_name,
                avatar_url=user_info.get("picture"),
                email_verified=user_info.get("email_verified", False),
            ),
        )
        self.user_service.assign_default_student_role(user.id)
        self.db.flush()
        created = self.user_service.get_by_id(user.id)
        if created is None:
            raise AuthError("Failed to create user account", status_code=500)
        return created

    def _sync_profile_from_provider(self, user: User, user_info: dict) -> None:
        first_name = user_info.get("given_name", user.first_name)
        last_name = user_info.get("family_name", user.last_name)
        display_name = user_info.get("name") or f"{first_name} {last_name}".strip()
        self.user_service.update_profile_from_sign_in(
            user,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            avatar_url=user_info.get("picture", user.avatar_url),
        )
