from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Any

import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.platform.storage.exceptions import (
    StorageNotConfiguredError,
    StorageUploadError,
)
from app.platform.storage.types import UploadCategory
from app.platform.storage.validation import ValidatedFile, validate_upload

_PUBLIC_ID_RE = re.compile(
    r"/upload/(?:(?:v\d+|[^/]+)/)*(.+?)(?:\.[a-zA-Z0-9]+)?$",
)


@dataclass(frozen=True)
class StoredFile:
    url: str
    public_id: str
    bytes: int
    format: str | None
    resource_type: str
    original_filename: str


class CloudinaryService:
    """Upload / delete / replace files in Cloudinary and return secure URLs."""

    def __init__(self) -> None:
        self._configured = False
        if settings.cloudinary_configured:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            self._configured = True

    def ensure_configured(self) -> None:
        if not self._configured:
            raise StorageNotConfiguredError()

    def upload(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        category: UploadCategory,
        folder: str,
        public_id: str | None = None,
    ) -> StoredFile:
        self.ensure_configured()
        validated = validate_upload(
            filename=filename,
            content=content,
            content_type=content_type,
            category=category,
        )
        resource_type = self._resource_type(validated.extension)
        options: dict[str, Any] = {
            "folder": folder.strip("/"),
            "resource_type": resource_type,
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if public_id:
            options["public_id"] = public_id
            options["overwrite"] = True
            options["unique_filename"] = False

        try:
            result = cloudinary.uploader.upload(
                io.BytesIO(validated.content),
                **options,
            )
        except Exception as exc:  # noqa: BLE001 — surface Cloudinary failures
            raise StorageUploadError(str(exc) or "Cloudinary upload failed") from exc

        return StoredFile(
            url=str(result.get("secure_url") or result.get("url") or ""),
            public_id=str(result.get("public_id") or ""),
            bytes=int(result.get("bytes") or validated.size),
            format=result.get("format"),
            resource_type=str(result.get("resource_type") or resource_type),
            original_filename=validated.filename,
        )

    def replace(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        category: UploadCategory,
        folder: str,
        old_url: str | None = None,
    ) -> StoredFile:
        stored = self.upload(
            filename=filename,
            content=content,
            content_type=content_type,
            category=category,
            folder=folder,
        )
        if old_url:
            try:
                self.delete(old_url)
            except StorageUploadError:
                # New file is already stored; orphan cleanup is best-effort.
                pass
        return stored

    def delete(self, file_url: str) -> None:
        self.ensure_configured()
        public_id, resource_type = self._parse_cloudinary_url(file_url)
        if not public_id:
            return
        try:
            cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type,
                invalidate=True,
            )
        except Exception as exc:  # noqa: BLE001
            raise StorageUploadError(str(exc) or "Cloudinary delete failed") from exc

    def secure_url(self, file_url: str) -> str:
        """Return HTTPS URL; Cloudinary secure_url is already HTTPS when configured."""
        if file_url.startswith("http://res.cloudinary.com/"):
            return "https://" + file_url[len("http://") :]
        return file_url

    @staticmethod
    def _resource_type(extension: str) -> str:
        if extension in {"png", "jpg", "jpeg"}:
            return "image"
        return "raw"

    @staticmethod
    def _parse_cloudinary_url(file_url: str) -> tuple[str | None, str]:
        if "cloudinary.com" not in file_url or "/upload/" not in file_url:
            return None, "raw"
        resource_type = "raw"
        if "/image/upload/" in file_url:
            resource_type = "image"
        elif "/video/upload/" in file_url:
            resource_type = "video"
        elif "/raw/upload/" in file_url:
            resource_type = "raw"
        match = _PUBLIC_ID_RE.search(file_url)
        if not match:
            return None, resource_type
        public_id = match.group(1)
        # Strip version segment if captured oddly
        if public_id.startswith("v") and "/" in public_id:
            maybe_version, rest = public_id.split("/", 1)
            if maybe_version[1:].isdigit():
                public_id = rest
        return public_id, resource_type
