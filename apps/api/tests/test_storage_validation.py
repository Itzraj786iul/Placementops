from app.platform.storage.exceptions import StorageValidationError
from app.platform.storage.types import UploadCategory
from app.platform.storage.validation import validate_upload


def test_validate_pdf_resume() -> None:
    result = validate_upload(
        filename="resume.pdf",
        content=b"%PDF-1.4 fake",
        content_type="application/pdf",
        category=UploadCategory.RESUME,
    )
    assert result.extension == "pdf"
    assert result.content_type == "application/pdf"


def test_reject_dangerous_extension() -> None:
    try:
        validate_upload(
            filename="malware.exe",
            content=b"MZ",
            content_type="application/octet-stream",
            category=UploadCategory.DOCUMENT,
        )
        raise AssertionError("expected StorageValidationError")
    except StorageValidationError as exc:
        assert "not allowed" in str(exc)


def test_reject_wrong_type_for_resume() -> None:
    try:
        validate_upload(
            filename="photo.png",
            content=b"\x89PNG\r\n\x1a\n",
            content_type="image/png",
            category=UploadCategory.RESUME,
        )
        raise AssertionError("expected StorageValidationError")
    except StorageValidationError as exc:
        assert "Unsupported" in str(exc)


def test_reject_oversized_image() -> None:
    oversized = b"x" * (5 * 1024 * 1024 + 1)
    try:
        validate_upload(
            filename="big.jpg",
            content=oversized,
            content_type="image/jpeg",
            category=UploadCategory.IMAGE,
        )
        raise AssertionError("expected StorageValidationError")
    except StorageValidationError as exc:
        assert "maximum size" in str(exc)


def test_reject_mime_mismatch() -> None:
    try:
        validate_upload(
            filename="doc.pdf",
            content=b"%PDF",
            content_type="image/png",
            category=UploadCategory.DOCUMENT,
        )
        raise AssertionError("expected StorageValidationError")
    except StorageValidationError as exc:
        assert "MIME" in str(exc)


def test_image_category_allows_jpeg() -> None:
    result = validate_upload(
        filename="avatar.jpeg",
        content=b"\xff\xd8\xff",
        content_type="image/jpeg",
        category=UploadCategory.IMAGE,
    )
    assert result.extension == "jpeg"
