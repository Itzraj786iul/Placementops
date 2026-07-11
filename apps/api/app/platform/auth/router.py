from urllib.parse import quote

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request as StarletteRequest

from app.core.config import settings
from app.dependencies.database import get_db_session
from app.modules.users.exceptions import AccountInactiveError
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse
from app.platform.auth.cookies import clear_auth_cookies, set_auth_cookies
from app.platform.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_optional_user,
    to_user_response,
)
from app.platform.auth.exceptions import AuthError, UnauthorizedError
from app.platform.auth.oauth import oauth
from app.platform.auth.rate_limit import check_rate_limit
from app.platform.auth.schemas import (
    ActivateAccountRequest,
    AuthCodeExchangeRequest,
    ChangePasswordRequest,
    CreatePasswordRequest,
    DevLoginRequest,
    ForgotPasswordRequest,
    MessageResponse,
    PasswordLoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.platform.auth.service import AuthService
from app.platform.exceptions import ApplicationError

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_key(request: Request, suffix: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    return f"{ip}:{suffix}"


def _google_oauth_configured() -> bool:
    client_id = (settings.GOOGLE_CLIENT_ID or "").strip()
    client_secret = (settings.GOOGLE_CLIENT_SECRET or "").strip()
    if not client_id or not client_secret:
        return False
    invalid_markers = (
        "your-google-client",
        "paste_full_secret",
        "****",
        "…",
        "...",
    )
    lowered_id = client_id.lower()
    lowered_secret = client_secret.lower()
    if any(marker in lowered_id or marker in lowered_secret for marker in invalid_markers):
        return False
    if len(client_secret) < 16:
        return False
    return True


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
    except AccountInactiveError as exc:
        inactive_url = (
            f"{settings.FRONTEND_URL}/account-inactive"
            f"?message={quote(exc.message)}"
        )
        return RedirectResponse(url=inactive_url, status_code=302)
    except ApplicationError as exc:
        error_url = f"{settings.FRONTEND_URL}/login?error={quote(exc.message)}"
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/login", response_model=TokenResponse)
def password_login(
    request: Request,
    payload: PasswordLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    check_rate_limit(_client_key(request, "login"), limit=20, window_seconds=60)
    user = auth_service.authenticate_password_login(payload.email, payload.password)
    tokens = auth_service.create_tokens(user, remember_me=payload.remember_me)
    set_auth_cookies(response, tokens)
    return tokens


@router.post("/register", response_model=MessageResponse)
def register(
    request: Request,
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    check_rate_limit(_client_key(request, "register"), limit=10, window_seconds=60)
    return auth_service.register_with_password(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    check_rate_limit(_client_key(request, "verify"), limit=20, window_seconds=60)
    return auth_service.verify_email(payload.token)


@router.post("/verify-email/resend", response_model=MessageResponse)
def resend_verification(
    request: Request,
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    check_rate_limit(_client_key(request, "verify-resend"), limit=5, window_seconds=60)
    return auth_service.resend_verification(payload.email)


@router.post("/password/forgot", response_model=MessageResponse)
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    check_rate_limit(_client_key(request, "forgot"), limit=5, window_seconds=60)
    return auth_service.request_password_reset(payload.email)


@router.post("/password/reset", response_model=MessageResponse)
def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    check_rate_limit(_client_key(request, "reset"), limit=10, window_seconds=60)
    return auth_service.reset_password(payload.token, payload.password)


@router.post("/password", response_model=UserResponse)
def create_password(
    payload: CreatePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return auth_service.create_password(
        current_user,
        payload.password,
        payload.confirm_password,
    )


@router.post("/password/change", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    return auth_service.change_password(
        current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
    )


@router.post("/activate", response_model=TokenResponse)
def activate_account(
    request: Request,
    payload: ActivateAccountRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    check_rate_limit(_client_key(request, "activate"), limit=10, window_seconds=60)
    tokens = auth_service.activate_account(
        raw_token=payload.token,
        password=payload.password,
        confirm_password=payload.confirm_password,
    )
    set_auth_cookies(response, tokens)
    return tokens


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


@router.post("/welcome/complete", response_model=UserResponse)
def complete_welcome(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return auth_service.complete_welcome(current_user)


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
    current_user: User | None = Depends(get_optional_user),
) -> MessageResponse:
    refresh_token = request.cookies.get("refresh_token")
    auth_service.logout(refresh_token, user=current_user)
    clear_auth_cookies(response)
    return MessageResponse(message="Signed out successfully")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return to_user_response(current_user)
