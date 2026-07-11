import re

_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def error_code_from_class_name(name: str) -> str:
    clean = name[:-5] if name.endswith("Error") and len(name) > 5 else name
    snake = _CAMEL_BOUNDARY.sub("_", clean).upper()
    return snake or "APPLICATION_ERROR"


class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        *,
        error_code: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or error_code_from_class_name(type(self).__name__)
        super().__init__(message)
