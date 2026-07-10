from app.platform.exceptions import ApplicationError


class StorageError(ApplicationError):
    pass


class StorageNotConfiguredError(StorageError):
    def __init__(
        self,
        message: str = "Cloudinary is not configured. Set CLOUDINARY_* environment variables.",
    ) -> None:
        super().__init__(message, status_code=503)


class StorageValidationError(StorageError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class StorageUploadError(StorageError):
    def __init__(self, message: str = "File upload failed") -> None:
        super().__init__(message, status_code=502)
