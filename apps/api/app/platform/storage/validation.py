from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import PurePosixPath

from app.platform.storage.exceptions import StorageValidationError
from app.platform.storage.types import (
    ALLOWED_EXTENSIONS,
    CATEGORY_EXTENSIONS,
    CATEGORY_MAX_BYTES,
    DANGEROUS_EXTENSIONS,
    UploadCategory,
)


@dataclass(frozen=True)
class ValidatedFile:
    filename: str
    extension: str
    content_type: str
    size: int
    content: bytes


def _extension(filename: str) -> str:
    name = PurePosixPath(filename.replace("\\", "/")).name
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1].lower().strip()


def validate_upload(
    *,
    filename: str,
    content: bytes,
    content_type: str | None,
    category: UploadCategory,
) -> ValidatedFile:
    if not filename or not filename.strip():
        raise StorageValidationError("Filename is required")

    safe_name = PurePosixPath(filename.replace("\\", "/")).name
    ext = _extension(safe_name)

    if not ext:
        raise StorageValidationError("File must have an extension")

    if ext in DANGEROUS_EXTENSIONS:
        raise StorageValidationError(f"File type .{ext} is not allowed")

    allowed_exts = CATEGORY_EXTENSIONS[category]
    if ext not in allowed_exts:
        raise StorageValidationError(
            f"Unsupported file type .{ext} for {category.value.lower()}. "
            f"Allowed: {', '.join(sorted(allowed_exts))}",
        )

    max_bytes = CATEGORY_MAX_BYTES[category]
    size = len(content)
    if size == 0:
        raise StorageValidationError("Uploaded file is empty")
    if size > max_bytes:
        mb = max_bytes / (1024 * 1024)
        raise StorageValidationError(
            f"File exceeds maximum size of {mb:g} MB for {category.value.lower()}",
        )

    declared = (content_type or "").split(";")[0].strip().lower()
    allowed_mimes = ALLOWED_EXTENSIONS[ext]
    guessed, _ = mimetypes.guess_type(safe_name)
    effective = declared or (guessed or "")

    if declared and declared not in allowed_mimes and declared != "application/octet-stream":
        raise StorageValidationError(
            f"MIME type '{declared}' does not match extension .{ext}",
        )

    if not effective:
        effective = next(iter(allowed_mimes))

    return ValidatedFile(
        filename=safe_name,
        extension=ext,
        content_type=effective if effective in allowed_mimes else next(iter(allowed_mimes)),
        size=size,
        content=content,
    )
