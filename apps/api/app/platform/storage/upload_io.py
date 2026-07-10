"""Helpers for reading multipart uploads with a hard size cap."""

from __future__ import annotations

from fastapi import UploadFile

from app.platform.storage.exceptions import StorageValidationError
from app.platform.storage.types import CATEGORY_MAX_BYTES, UploadCategory

CHUNK_SIZE = 64 * 1024


async def read_upload_capped(
    file: UploadFile,
    category: UploadCategory,
) -> tuple[str, bytes, str | None]:
    max_bytes = CATEGORY_MAX_BYTES[category]
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            mb = max_bytes / (1024 * 1024)
            raise StorageValidationError(
                f"File exceeds maximum size of {mb:g} MB for {category.value.lower()}",
            )
        chunks.append(chunk)

    filename = file.filename or "upload.bin"
    return filename, b"".join(chunks), file.content_type
