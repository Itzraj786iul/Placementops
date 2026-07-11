from uuid import uuid4

import jwt
import pytest

from app.core.config import Settings
from app.platform.auth.exceptions import UnauthorizedError
from app.platform.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_access_token_round_trip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    payload = decode_token(token, "access")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload


def test_refresh_token_requires_jti() -> None:
    user_id = uuid4()
    token, jti = create_refresh_token(user_id)
    payload = decode_token(token, "refresh")
    assert payload["jti"] == jti


def test_decode_rejects_wrong_type() -> None:
    token = create_access_token(uuid4())
    with pytest.raises(UnauthorizedError):
        decode_token(token, "refresh")


def test_decode_rejects_missing_jti_on_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import config as config_module
    from app.utils.datetime import utc_now
    from datetime import timedelta

    now = utc_now()
    raw = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": now,
            "exp": now + timedelta(days=1),
            "type": "refresh",
        },
        config_module.settings.JWT_SECRET_KEY,
        algorithm=config_module.settings.JWT_ALGORITHM,
    )
    with pytest.raises(UnauthorizedError):
        decode_token(raw, "refresh")


def test_decode_rejects_invalid_sub() -> None:
    from app.core import config as config_module
    from app.utils.datetime import utc_now
    from datetime import timedelta

    now = utc_now()
    raw = jwt.encode(
        {
            "sub": "not-a-uuid",
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "type": "access",
        },
        config_module.settings.JWT_SECRET_KEY,
        algorithm=config_module.settings.JWT_ALGORITHM,
    )
    with pytest.raises(UnauthorizedError):
        decode_token(raw, "access")


def test_production_security_rejects_dev_login() -> None:
    settings = Settings(
        ENVIRONMENT="production",
        ENABLE_DEV_LOGIN=True,
        COOKIE_SECURE=True,
        JWT_SECRET_KEY="x" * 48,
    )
    with pytest.raises(RuntimeError, match="ENABLE_DEV_LOGIN"):
        settings.assert_production_security()


def test_production_security_rejects_insecure_cookies() -> None:
    settings = Settings(
        ENVIRONMENT="production",
        ENABLE_DEV_LOGIN=False,
        COOKIE_SECURE=False,
        JWT_SECRET_KEY="x" * 48,
    )
    with pytest.raises(RuntimeError, match="COOKIE_SECURE"):
        settings.assert_production_security()


def test_production_security_rejects_weak_jwt() -> None:
    settings = Settings(
        ENVIRONMENT="production",
        ENABLE_DEV_LOGIN=False,
        COOKIE_SECURE=True,
        JWT_SECRET_KEY="short",
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        settings.assert_production_security()


def test_api_docs_disabled_in_production_by_default() -> None:
    settings = Settings(ENVIRONMENT="production", ENABLE_API_DOCS=None)
    assert settings.is_production is True
    assert settings.api_docs_enabled is False


def test_api_docs_enabled_locally_by_default() -> None:
    settings = Settings(ENVIRONMENT="local", ENABLE_API_DOCS=None)
    assert settings.api_docs_enabled is True


def test_create_app_hides_docs_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    import main as main_module

    prod = Settings(
        ENVIRONMENT="production",
        ENABLE_DEV_LOGIN=False,
        COOKIE_SECURE=True,
        JWT_SECRET_KEY="x" * 48,
        ENABLE_API_DOCS=None,
    )
    monkeypatch.setattr(main_module, "settings", prod)
    app = main_module.create_app()
    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None
