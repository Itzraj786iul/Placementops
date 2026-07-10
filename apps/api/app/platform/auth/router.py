from urllib.parse import quote

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request as StarletteRequest

from app.core.config import settings
from app.dependencies.database import get_db_session
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse
from app.platform.auth.cookies import clear_auth_cookies, set_auth_cookies
from app.platform.auth.dependencies import (
    get_auth_service,
    get_current_user,
    to_user_response,
)
from app.platform.auth.exceptions import AuthError, UnauthorizedError
from app.platform.auth.oauth import oauth
from app.platform.auth.schemas import (
    AuthCodeExchangeRequest,
    DevLoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from app.platform.auth.service import AuthService
from app.platform.exceptions import ApplicationError

router = APIRouter(prefix="/auth", tags=["auth"])


def _google_oauth_configured() -> bool:
    client_id = (settings.GOOGLE_CLIENT_ID or "").strip()
    client_secret = (settings.GOOGLE_CLIENT_SECRET or "").strip()
    return bool(
        client_id
        and client_secret
        and "your-google-client" not in client_id
        and "your-google-client" not in client_secret
    )


@router.get("/google/login")
async def google_login(request: StarletteRequest) -> RedirectResponse:
    if not _google_oauth_configured():
        error_url = (
            f"{settings.FRONTEND_URL}/login?error="
            f"{quote('Google sign-in is not configured. Contact the administrator.')}"
        )
        return RedirectResponse(url=error_url, status_code=302)

    return await oauth.google.authorize_redirect(
        request,
        settings.GOOGLE_REDIRECT_URI,
    )


@router.get("/google/callback")
async def google_callback(
    request: StarletteRequest,
    db: Session = Depends(get_db_session),
) -> RedirectResponse:
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        if user_info is None:
            raise AuthError("Failed to retrieve Google account information", 400)

        service = AuthService(db)
        user = service.authenticate_google_user(user_info)
        auth_code = service.create_auth_code(user)
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?code={auth_code}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except ApplicationError as exc:
        error_url = f"{settings.FRONTEND_URL}/login?error={quote(exc.message)}"
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/dev/login", response_model=TokenResponse)
def dev_login(
    payload: DevLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    if not settings.ENABLE_DEV_LOGIN:
        raise AuthError("Dev login is not enabled", status_code=404)
    user = auth_service.authenticate_dev_login(payload.email, payload.password)
    tokens = auth_service.create_tokens(user)
    set_auth_cookies(response, tokens)
    return tokens


@router.post("/exchange", response_model=TokenResponse)
def exchange_auth_code(
    payload: AuthCodeExchangeRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    tokens = auth_service.exchange_auth_code(payload.code)
    set_auth_cookies(response, tokens)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(
    request: Request,
    response: Response,
    payload: RefreshTokenRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    refresh_token = (
        payload.refresh_token if payload else None
    ) or request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedError("Session has expired. Please sign in again")
    tokens = auth_service.refresh_session(refresh_token)
    set_auth_cookies(response, tokens)
    return tokens


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    refresh_token = request.cookies.get("refresh_token")
    auth_service.logout(refresh_token)
    clear_auth_cookies(response)
    return MessageResponse(message="Signed out successfully")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return to_user_response(current_user)
