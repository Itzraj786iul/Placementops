from app.platform.exceptions import ApplicationError


class StudentError(ApplicationError):
    pass


class StudentNotFoundError(StudentError):
    def __init__(self, message: str = "Student profile not found") -> None:
        super().__init__(message, status_code=404)


class StudentConflictError(StudentError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)


class StudentForbiddenError(StudentError):
    def __init__(self, message: str = "You do not have access to this student profile") -> None:
        super().__init__(message, status_code=403)


class StudentValidationError(StudentError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
