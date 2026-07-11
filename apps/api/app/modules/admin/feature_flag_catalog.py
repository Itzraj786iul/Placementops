"""Catalog of known feature flags, defaults, and critical protections."""

from __future__ import annotations

from typing import Any

from app.modules.admin.feature_flag_models import FLAG_SCOPE_GLOBAL

# Defaults apply when a DB row is missing. Unknown keys default to True.
FLAG_DEFAULTS: dict[str, dict[str, Any]] = {
    "student_registration": {
        "name": "Student Registration",
        "description": "Allow new student account registration and onboarding.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "student_profile_editing": {
        "name": "Student Profile Editing",
        "description": "Allow students to edit their placement profiles.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "student_applications": {
        "name": "Student Applications",
        "description": "Allow students to apply to hiring opportunities.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "company_crm": {
        "name": "Company CRM",
        "description": "Enable company relationship management for conveners and cell.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "hiring_opportunities": {
        "name": "Hiring Opportunities",
        "description": "Enable creation and management of hiring opportunities.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "exports": {
        "name": "Exports",
        "description": "Allow generating and downloading placement exports.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "shortlist_import": {
        "name": "Shortlist Import",
        "description": "Allow importing shortlists for opportunities.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "notifications": {
        "name": "Notifications",
        "description": "Enable in-app notification delivery.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "email_delivery": {
        "name": "Email Delivery",
        "description": "Enable outbound email via the configured provider.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "cloud_uploads": {
        "name": "Cloud Uploads",
        "description": "Allow file uploads to cloud storage.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "audit_logging": {
        "name": "Audit Logging",
        "description": "Record audit events for sensitive actions (critical).",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "admin_portal": {
        "name": "Admin Portal",
        "description": "Enable Admin Control Center surfaces for operators.",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
    "authentication": {
        "name": "Authentication",
        "description": "Core authentication pipeline (critical).",
        "enabled": True,
        "scope": FLAG_SCOPE_GLOBAL,
    },
}

CRITICAL_FLAGS: frozenset[str] = frozenset({"audit_logging", "authentication"})


def humanize_key(key: str) -> str:
    return key.replace("_", " ").strip().title()
