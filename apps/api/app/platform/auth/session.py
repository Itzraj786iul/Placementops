import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.platform.auth.models import AuthCode, AuthIdentity, RefreshToken
from app.utils.datetime import utc_now


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_identity(
        self,
        provider: str,
        provider_user_id: str,
    ) -> AuthIdentity | None:
        stmt = select(AuthIdentity).where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_user_id == provider_user_id,
        )
        return self.db.scalars(stmt).first()

    def create_identity(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_user_id: str,
        provider_email: str,
    ) -> AuthIdentity:
        identity = AuthIdentity(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
        )
        self.db.add(identity)
        self.db.flush()
        return identity

    def create_auth_code(
        self,
        user_id: uuid.UUID,
        code: str,
        expires_at: datetime,
    ) -> AuthCode:
        auth_code = AuthCode(user_id=user_id, code=code, expires_at=expires_at)
        self.db.add(auth_code)
        self.db.flush()
        return auth_code

    def get_auth_code(self, code: str) -> AuthCode | None:
        stmt = select(AuthCode).where(AuthCode.code == code)
        return self.db.scalars(stmt).first()

    def mark_auth_code_used(self, auth_code: AuthCode) -> None:
        auth_code.used_at = utc_now()

    def create_refresh_token(
        self,
        user_id: uuid.UUID,
        token_jti: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_jti=token_jti,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.flush()
        return token

    def get_refresh_token(self, token_jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_jti == token_jti)
        return self.db.scalars(stmt).first()

    def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.revoked_at = utc_now()
