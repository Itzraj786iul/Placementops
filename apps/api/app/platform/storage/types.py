from enum import Enum


class UploadCategory(str, Enum):
    RESUME = "RESUME"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"


# extension (lowercase, no dot) -> MIME types accepted
ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "doc": {"application/msword"},
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
}

CATEGORY_EXTENSIONS: dict[UploadCategory, set[str]] = {
    UploadCategory.RESUME: {"pdf", "doc", "docx"},
    UploadCategory.DOCUMENT: {"pdf", "doc", "docx", "png", "jpg", "jpeg"},
    UploadCategory.IMAGE: {"png", "jpg", "jpeg"},
}

CATEGORY_MAX_BYTES: dict[UploadCategory, int] = {
    UploadCategory.RESUME: 10 * 1024 * 1024,
    UploadCategory.DOCUMENT: 10 * 1024 * 1024,
    UploadCategory.IMAGE: 5 * 1024 * 1024,
}

DANGEROUS_EXTENSIONS = {
    "exe",
    "bat",
    "cmd",
    "com",
    "msi",
    "scr",
    "js",
    "jar",
    "sh",
    "ps1",
    "php",
    "asp",
    "aspx",
    "html",
    "htm",
    "svg",
}
