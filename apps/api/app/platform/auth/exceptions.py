from app.platform.exceptions import ApplicationError


class AuthError(ApplicationError):
    pass


class UnauthorizedError(AuthError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, status_code=401)


class InvalidAuthCodeError(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid or expired authentication code", status_code=400)
