import hashlib
import secrets
import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.users.exceptions import AccountInactiveError
from app.modules.users.models import USER_STATUS_ACTIVE, User
from app.modules.users.schemas import CreateUserData, UserResponse
from app.modules.users.service import UserService
from app.platform.auth.auth_emails import (
    send_activation_email,
    send_password_reset_email,
    send_verification_email,
)
from app.platform.auth.exceptions import AuthError, InvalidAuthCodeError, UnauthorizedError
from app.platform.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.platform.auth.models import (
    PROVIDER_GOOGLE,
    TOKEN_ACCOUNT_ACTIVATION,
    TOKEN_EMAIL_VERIFY,
    TOKEN_PASSWORD_RESET,
)
from app.platform.auth.password import hash_password, verify_password
from app.platform.auth.password_policy import validate_password_strength
from app.platform.auth.schemas import MessageResponse, TokenResponse
from app.platform.auth.session import AuthRepository
from app.utils.datetime import utc_now

_GENERIC_LOGIN_ERROR = "Invalid email or password"
_MAX_FAILED_LOGINS = 5
_LOCKOUT_MINUTES = 15


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.auth_repository = AuthRepository(db)
        self.user_service = UserService(db)

    # ------------------------------------------------------------------
    # Google OAuth (unchanged behavior)
    # ------------------------------------------------------------------

    def authenticate_dev_login(self, email: str, password: str) -> User:
        if not settings.ENABLE_DEV_LOGIN:
            raise AuthError("Dev login is not enabled", status_code=404)
        return self._authenticate_password(email, password, audit_method="dev")

    def authenticate_password_login(self, email: str, password: str) -> User:
        return self._authenticate_password(email, password, audit_method="password")

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
        linked_existing = False

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
                linked_existing = True
            else:
                user = self._create_user_from_provider(user_info, college_email)
                self.auth_repository.create_identity(
                    user.id,
                    PROVIDER_GOOGLE,
                    provider_user_id,
                    email,
                )

        user = self.user_service.require_active_user(user)
        if not user.email_verified:
            user.email_verified = True
        self._sync_profile_from_provider(user, user_info)
        self.user_service.update_last_login(user)
        from app.modules.admin.maintenance_service import MaintenanceService

        MaintenanceService.assert_user_may_authenticate(user)

        if linked_existing:
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=user.id,
                action=AuditAction.GOOGLE_LINKED,
                performed_by=user.id,
                metadata={"provider": PROVIDER_GOOGLE},
            )
            self.db.commit()

        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.LOGIN,
            performed_by=user.id,
            metadata={"method": "google"},
        )
        self.db.commit()
        return user

    # ------------------------------------------------------------------
    # Password registration / verification
    # ------------------------------------------------------------------

    def register_with_password(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> MessageResponse:
        college_email = self.user_service.validate_college_email(email)
        validate_password_strength(password)

        existing = self.user_service.get_by_college_email(college_email)
        if existing is not None:
            # Generic response — do not reveal account existence.
            if existing.password_hash is None and not existing.email_verified:
                self._issue_email_verification(existing)
            return MessageResponse(
                message=(
                    "If this email can be registered, a verification link "
                    "has been sent."
                ),
            )

        display_name = f"{first_name.strip()} {last_name.strip()}".strip()
        user = self.user_service.create_user(
            CreateUserData(
                college_email=college_email,
                personal_email=None,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                display_name=display_name or college_email,
                avatar_url=None,
                email_verified=False,
            ),
        )
        self.user_service.assign_default_student_role(user.id)
        self.user_service.repository.set_password_hash(user, hash_password(password))
        self.db.flush()
        created = self.user_service.get_by_id(user.id)
        if created is None:
            raise AuthError("Failed to create user account", status_code=500)

        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=created.id,
            action=AuditAction.CREATE,
            performed_by=created.id,
            metadata={"method": "password_register"},
        )
        self._issue_email_verification(created)
        self.db.commit()
        return MessageResponse(
            message=(
                "If this email can be registered, a verification link has been sent."
            ),
        )

    def verify_email(self, raw_token: str) -> MessageResponse:
        user = self._consume_security_token(raw_token, TOKEN_EMAIL_VERIFY)
        user.email_verified = True
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.EMAIL_VERIFIED,
            performed_by=user.id,
        )
        self.db.commit()
        return MessageResponse(message="Email verified. You can sign in now.")

    def resend_verification(self, email: str) -> MessageResponse:
        college_email = self.user_service.validate_college_email(email)
        user = self.user_service.get_by_college_email(college_email)
        if user is not None and not user.email_verified and user.password_hash:
            self._issue_email_verification(user)
            self.db.commit()
        return MessageResponse(
            message="If an unverified account exists, a new link has been sent.",
        )

    # ------------------------------------------------------------------
    # Password create / change / reset
    # ------------------------------------------------------------------

    def create_password(self, user: User, password: str, confirm: str) -> UserResponse:
        if password != confirm:
            raise AuthError("Passwords do not match", status_code=422)
        validate_password_strength(password)
        if user.password_hash:
            raise AuthError(
                "Password already set. Use change password instead.",
                status_code=409,
            )
        self.user_service.repository.set_password_hash(user, hash_password(password))
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.PASSWORD_CREATED,
            performed_by=user.id,
        )
        self.db.commit()
        refreshed = self.user_service.get_by_id(user.id) or user
        return self.user_service.to_response(refreshed)

    def change_password(
        self,
        user: User,
        *,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> MessageResponse:
        if not user.password_hash:
            raise AuthError(
                "No password set. Create a password first.",
                status_code=400,
            )
        if new_password != confirm_password:
            raise AuthError("Passwords do not match", status_code=422)
        validate_password_strength(new_password)
        if not verify_password(current_password, user.password_hash):
            raise AuthError("Current password is incorrect", status_code=400)
        self.user_service.repository.set_password_hash(user, hash_password(new_password))
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.PASSWORD_CHANGED,
            performed_by=user.id,
        )
        self.db.commit()
        return MessageResponse(message="Password updated successfully")

    def request_password_reset(self, email: str) -> MessageResponse:
        # Always return the same message.
        message = MessageResponse(
            message=(
                "If an account exists for that email, a reset link has been sent."
            ),
        )
        try:
            college_email = self.user_service.validate_college_email(email)
        except Exception:  # noqa: BLE001
            return message

        user = self.user_service.get_by_college_email(college_email)
        if user is None or not user.password_hash:
            return message

        raw = secrets.token_urlsafe(32)
        self.auth_repository.create_security_token(
            user_id=user.id,
            purpose=TOKEN_PASSWORD_RESET,
            token_hash=_hash_token(raw),
            expires_at=utc_now() + timedelta(hours=1),
        )
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.PASSWORD_RESET_REQUESTED,
            performed_by=user.id,
        )
        self.db.commit()
        send_password_reset_email(to=user.college_email, token=raw)
        return message

    def reset_password(self, raw_token: str, password: str) -> MessageResponse:
        validate_password_strength(password)
        user = self._consume_security_token(raw_token, TOKEN_PASSWORD_RESET)
        self.user_service.repository.set_password_hash(user, hash_password(password))
        user.failed_login_attempts = 0
        user.locked_until = None
        if not user.email_verified:
            user.email_verified = True
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.PASSWORD_RESET_COMPLETED,
            performed_by=user.id,
        )
        self.db.commit()
        return MessageResponse(message="Password reset successfully. You can sign in.")

    def activate_account(
        self,
        *,
        raw_token: str,
        password: str,
        confirm_password: str,
    ) -> TokenResponse:
        if password != confirm_password:
            raise AuthError("Passwords do not match", status_code=422)
        validate_password_strength(password)
        user = self._consume_security_token(raw_token, TOKEN_ACCOUNT_ACTIVATION)
        self.user_service.repository.set_password_hash(user, hash_password(password))
        user.email_verified = True
        user.status = USER_STATUS_ACTIVE
        user.failed_login_attempts = 0
        user.locked_until = None
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.PASSWORD_CREATED,
            performed_by=user.id,
            metadata={"method": "activation"},
        )
        self.db.commit()
        user = self.user_service.require_active_user(
            self.user_service.get_by_id(user.id),
        )
        self.user_service.update_last_login(user)
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.LOGIN,
            performed_by=user.id,
            metadata={"method": "activation"},
        )
        self.db.commit()
        return self.create_tokens(user)

    def invite_staff_user(
        self,
        *,
        actor: User,
        email: str,
        first_name: str,
        last_name: str,
        role_name: str,
    ) -> UserResponse:
        from app.modules.admin.access import ensure_admin_access, is_super_admin
        from app.modules.users.workspace import ROLE_DISPLAY_LABELS

        ensure_admin_access(actor)
        if not is_super_admin(actor):
            raise AuthError("Only Super Admin can invite users", status_code=403)
        if role_name not in {
            "PLACEMENT_CELL",
            "PLACEMENT_CONVENER",
            "SUPER_ADMIN",
            "STUDENT",
        }:
            raise AuthError("Invalid role", status_code=422)
        if role_name == "SUPER_ADMIN" and not is_super_admin(actor):
            raise AuthError("Only Super Admin can invite Super Admins", status_code=403)

        college_email = self.user_service.validate_college_email(email)
        if self.user_service.get_by_college_email(college_email) is not None:
            raise AuthError("A user with this email already exists", status_code=409)

        display_name = f"{first_name.strip()} {last_name.strip()}".strip()
        user = self.user_service.create_user(
            CreateUserData(
                college_email=college_email,
                personal_email=None,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                display_name=display_name or college_email,
                avatar_url=None,
                email_verified=False,
            ),
        )
        role = self.user_service.repository.get_role_by_name(role_name)
        if role is None:
            raise AuthError("Role is not configured", status_code=500)
        self.user_service.repository.assign_role(user.id, role.id)
        self.db.flush()

        raw = secrets.token_urlsafe(32)
        self.auth_repository.create_security_token(
            user_id=user.id,
            purpose=TOKEN_ACCOUNT_ACTIVATION,
            token_hash=_hash_token(raw),
            expires_at=utc_now() + timedelta(hours=72),
        )
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.CREATE,
            performed_by=actor.id,
            metadata={"method": "admin_invite", "role": role_name},
        )
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.ROLE_ASSIGNED,
            performed_by=actor.id,
            new_values={"role": role_name},
        )
        self.db.commit()
        created = self.user_service.get_by_id(user.id)
        send_activation_email(
            to=college_email,
            token=raw,
            role_label=ROLE_DISPLAY_LABELS.get(role_name, role_name),
        )
        return self.user_service.to_response(created)

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

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

    def create_tokens(
        self,
        user: User,
        *,
        remember_me: bool = False,
    ) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token, jti = create_refresh_token(user.id)
        days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        if remember_me:
            days = max(days, 30)
        expires_at = utc_now() + timedelta(days=days)
        self.auth_repository.create_refresh_token(user.id, jti, expires_at)
        self.db.commit()
        needs_welcome = user.welcome_completed_at is None
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self.user_service.to_response(user),
            is_new_user=needs_welcome,
        )

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

    def logout(self, refresh_token: str | None, user: User | None = None) -> None:
        if refresh_token:
            try:
                payload = decode_token(refresh_token, expected_type="refresh")
                stored = self.auth_repository.get_refresh_token(payload["jti"])
                if stored is not None:
                    self.auth_repository.revoke_refresh_token(stored)
                    if user is None:
                        user = self.user_service.get_by_id(stored.user_id)
                    self.db.commit()
            except UnauthorizedError:
                return
        if user is not None:
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=user.id,
                action=AuditAction.LOGOUT,
                performed_by=user.id,
            )
            self.db.commit()

    def get_user_from_access_token(self, token: str) -> User:
        payload = decode_token(token, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
        user = self.user_service.get_by_id(user_id)
        if user is None or user.status != USER_STATUS_ACTIVE:
            raise UnauthorizedError("Account is no longer active")
        return user

    def complete_welcome(self, user: User) -> UserResponse:
        updated = self.user_service.complete_welcome(user)
        return self.user_service.to_response(updated)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _authenticate_password(
        self,
        email: str,
        password: str,
        *,
        audit_method: str,
    ) -> User:
        college_email = self.user_service.validate_college_email(email)
        user = self.user_service.get_by_college_email(college_email)

        if user is None or not user.password_hash:
            raise AuthError(_GENERIC_LOGIN_ERROR, status_code=401)

        if user.locked_until and user.locked_until > utc_now():
            raise AuthError(
                "Account temporarily locked due to failed sign-in attempts. "
                "Try again later.",
                status_code=423,
            )

        if not verify_password(password, user.password_hash):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= _MAX_FAILED_LOGINS:
                user.locked_until = utc_now() + timedelta(minutes=_LOCKOUT_MINUTES)
                user.failed_login_attempts = 0
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=user.id,
                action=AuditAction.LOGIN_FAILED,
                performed_by=user.id,
                metadata={"method": audit_method},
            )
            self.db.commit()
            raise AuthError(_GENERIC_LOGIN_ERROR, status_code=401)

        if not user.email_verified:
            raise AuthError(
                "Please verify your email before signing in.",
                status_code=403,
            )

        try:
            user = self.user_service.require_active_user(user)
        except AccountInactiveError:
            raise AuthError(
                "Your account is currently inactive. Please contact the Placement Cell.",
                status_code=403,
            ) from None

        user.failed_login_attempts = 0
        user.locked_until = None
        self.user_service.update_last_login(user)
        from app.modules.admin.maintenance_service import MaintenanceService

        MaintenanceService.assert_user_may_authenticate(user)
        record_audit(
            self.db,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.LOGIN,
            performed_by=user.id,
            metadata={"method": audit_method},
        )
        self.db.commit()
        return user

    def _issue_email_verification(self, user: User) -> None:
        raw = secrets.token_urlsafe(32)
        self.auth_repository.create_security_token(
            user_id=user.id,
            purpose=TOKEN_EMAIL_VERIFY,
            token_hash=_hash_token(raw),
            expires_at=utc_now() + timedelta(hours=24),
        )
        send_verification_email(to=user.college_email, token=raw)

    def _consume_security_token(self, raw_token: str, purpose: str) -> User:
        token = self.auth_repository.get_security_token(
            token_hash=_hash_token(raw_token),
            purpose=purpose,
        )
        if token is None or token.used_at is not None:
            raise AuthError("Invalid or expired link", status_code=400)
        if token.expires_at < utc_now():
            raise AuthError("Invalid or expired link", status_code=400)
        user = self.user_service.get_by_id(token.user_id)
        if user is None:
            raise AuthError("Invalid or expired link", status_code=400)
        self.auth_repository.mark_security_token_used(token)
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
                email_verified=True,
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
