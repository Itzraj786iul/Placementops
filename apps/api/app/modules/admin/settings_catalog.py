"""Typed defaults, validators, and sensitive-key rules for system settings."""

from __future__ import annotations

from typing import Any, Callable

# Writable operational settings (DB-backed). Secrets stay in env.
SETTING_DEFAULTS: dict[str, Any] = {
    "general.college_name": "NIT Raipur",
    "general.college_logo_url": None,
    "general.placement_office_email": "placement@nitrr.ac.in",
    "general.support_email": "support@nitrr.ac.in",
    "general.timezone": "Asia/Kolkata",
    "general.academic_year_format": "YYYY-YYYY",
    "auth.google_oauth_enabled": True,
    "auth.allowed_email_domains": ["nitrr.ac.in"],
    "auth.session_timeout_minutes": 15,
    "auth.login_message": "",
    "notifications.default_email_enabled": True,
    "notifications.default_in_app_enabled": True,
    "notifications.daily_digest_enabled": False,
    "placement.default_deadline_offset_days": 7,
    "placement.default_resume_required": True,
    "placement.default_eligibility_behaviour": "strict",
    "placement.auto_close_applications": False,
    "maintenance.enabled": False,
    "maintenance.title": "Scheduled maintenance",
    "maintenance.message": (
        "PlacementOS is temporarily unavailable while we perform maintenance. "
        "Please try again later."
    ),
    "maintenance.estimated_completion": None,
    "maintenance.support_contact": None,
    "maintenance.starts_at": None,
    "maintenance.ends_at": None,
    "maintenance.allowed_roles": [],
    "maintenance.updated_by": None,
}

# Changes that require confirm_sensitive=true on PATCH
SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "auth.google_oauth_enabled",
        "auth.allowed_email_domains",
        "auth.session_timeout_minutes",
        "placement.auto_close_applications",
        "placement.default_eligibility_behaviour",
        "maintenance.enabled",
    },
)

# Keys that must never be stored or returned via settings API
BLOCKED_KEYS: frozenset[str] = frozenset(
    {
        "jwt_secret",
        "jwt_secret_key",
        "google_client_secret",
        "cloudinary_api_secret",
        "database_url",
        "resend_api_key",
        "api_key",
        "password",
        "secret",
    },
)

SECTION_KEYS: dict[str, list[str]] = {
    "general": [
        "general.college_name",
        "general.college_logo_url",
        "general.placement_office_email",
        "general.support_email",
        "general.timezone",
        "general.academic_year_format",
    ],
    "authentication": [
        "auth.google_oauth_enabled",
        "auth.allowed_email_domains",
        "auth.session_timeout_minutes",
        "auth.login_message",
    ],
    "notifications": [
        "notifications.default_email_enabled",
        "notifications.default_in_app_enabled",
        "notifications.daily_digest_enabled",
    ],
    "placement": [
        "placement.default_deadline_offset_days",
        "placement.default_resume_required",
        "placement.default_eligibility_behaviour",
        "placement.auto_close_applications",
    ],
    "maintenance": [
        "maintenance.enabled",
        "maintenance.title",
        "maintenance.message",
        "maintenance.estimated_completion",
        "maintenance.support_contact",
        "maintenance.starts_at",
        "maintenance.ends_at",
        "maintenance.allowed_roles",
    ],
}


def _require_str(value: Any, *, allow_empty: bool = False) -> str:
    if value is None:
        raise ValueError("must be a string")
    if not isinstance(value, str):
        raise ValueError("must be a string")
    text = value.strip()
    if not allow_empty and not text:
        raise ValueError("must not be empty")
    return text


def _require_optional_str(value: Any) -> str | None:
    if value is None or value == "":
        return None
    return _require_str(value)


def _require_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError("must be a boolean")


def _require_int(value: Any, *, min_v: int, max_v: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("must be an integer")
    if value < min_v or value > max_v:
        raise ValueError(f"must be between {min_v} and {max_v}")
    return value


def _require_email(value: Any) -> str:
    text = _require_str(value)
    if "@" not in text or "." not in text.split("@")[-1]:
        raise ValueError("must be a valid email")
    return text.lower()


def _require_domains(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("must be a non-empty list of domains")
    domains: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("domains must be non-empty strings")
        domain = item.strip().lower().lstrip("@")
        if "." not in domain:
            raise ValueError(f"invalid domain: {domain}")
        domains.append(domain)
    return domains


def _require_eligibility(value: Any) -> str:
    text = _require_str(value).lower()
    if text not in {"strict", "advisory", "off"}:
        raise ValueError("must be one of: strict, advisory, off")
    return text


def _require_optional_datetime(value: Any) -> str | None:
    if value is None or value == "":
        return None
    text = _require_str(value)
    # Accept ISO-8601 strings; full parse deferred to consumers
    return text


def _require_role_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("must be a list of role names")
    roles: list[str] = []
    allowed = {
        "SUPER_ADMIN",
        "PLACEMENT_CELL",
        "PLACEMENT_CONVENER",
        "STUDENT",
    }
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("roles must be non-empty strings")
        role = item.strip().upper()
        if role not in allowed:
            raise ValueError(f"unsupported role: {role}")
        if role not in roles:
            roles.append(role)
    return roles


VALIDATORS: dict[str, Callable[[Any], Any]] = {
    "general.college_name": lambda v: _require_str(v),
    "general.college_logo_url": _require_optional_str,
    "general.placement_office_email": _require_email,
    "general.support_email": _require_email,
    "general.timezone": lambda v: _require_str(v),
    "general.academic_year_format": lambda v: _require_str(v),
    "auth.google_oauth_enabled": _require_bool,
    "auth.allowed_email_domains": _require_domains,
    "auth.session_timeout_minutes": lambda v: _require_int(v, min_v=5, max_v=1440),
    "auth.login_message": lambda v: _require_str(v, allow_empty=True),
    "notifications.default_email_enabled": _require_bool,
    "notifications.default_in_app_enabled": _require_bool,
    "notifications.daily_digest_enabled": _require_bool,
    "placement.default_deadline_offset_days": lambda v: _require_int(
        v, min_v=0, max_v=365
    ),
    "placement.default_resume_required": _require_bool,
    "placement.default_eligibility_behaviour": _require_eligibility,
    "placement.auto_close_applications": _require_bool,
    "maintenance.enabled": _require_bool,
    "maintenance.title": lambda v: _require_str(v),
    "maintenance.message": lambda v: _require_str(v),
    "maintenance.estimated_completion": _require_optional_str,
    "maintenance.support_contact": _require_optional_str,
    "maintenance.starts_at": _require_optional_datetime,
    "maintenance.ends_at": _require_optional_datetime,
    "maintenance.allowed_roles": _require_role_list,
    "maintenance.updated_by": _require_optional_str,
}


def is_blocked_key(key: str) -> bool:
    lowered = key.lower().replace(".", "_").replace("-", "_")
    if lowered in BLOCKED_KEYS:
        return True
    return any(
        token in lowered
        for token in (
            "secret",
            "password",
            "api_key",
            "database_url",
            "jwt_",
            "client_secret",
        )
    )


def validate_setting_value(key: str, value: Any) -> Any:
    validator = VALIDATORS.get(key)
    if validator is None:
        # Unknown keys allowed; store JSON-serializable values as-is
        return value
    return validator(value)
