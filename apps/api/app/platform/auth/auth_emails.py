"""Transactional auth emails (verification, reset, activation)."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.platform.notifications.email_service import EmailService

logger = logging.getLogger(__name__)


def _frontend(path: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def send_verification_email(*, to: str, token: str) -> None:
    link = _frontend(f"/verify-email?token={token}")
    _send(
        to=to,
        subject="Verify your PlacementOS email",
        html=(
            "<p>Welcome to PlacementOS.</p>"
            f"<p><a href=\"{link}\">Verify your email</a> to activate password sign-in.</p>"
            f"<p>Or open: {link}</p>"
            "<p>This link expires in 24 hours.</p>"
        ),
        text=f"Verify your PlacementOS email:\n{link}\nThis link expires in 24 hours.\n",
    )


def send_password_reset_email(*, to: str, token: str) -> None:
    link = _frontend(f"/reset-password?token={token}")
    _send(
        to=to,
        subject="Reset your PlacementOS password",
        html=(
            "<p>We received a password reset request for your PlacementOS account.</p>"
            f"<p><a href=\"{link}\">Reset password</a></p>"
            f"<p>Or open: {link}</p>"
            "<p>If you did not request this, you can ignore this email.</p>"
            "<p>This link expires in 1 hour.</p>"
        ),
        text=(
            f"Reset your PlacementOS password:\n{link}\n"
            "If you did not request this, ignore this email.\n"
            "This link expires in 1 hour.\n"
        ),
    )


def send_activation_email(*, to: str, token: str, role_label: str) -> None:
    link = _frontend(f"/activate?token={token}")
    _send(
        to=to,
        subject="Activate your PlacementOS account",
        html=(
            f"<p>You have been invited to PlacementOS as <strong>{role_label}</strong>.</p>"
            f"<p><a href=\"{link}\">Create your password</a> to activate the account.</p>"
            f"<p>Or open: {link}</p>"
            "<p>This link expires in 72 hours.</p>"
        ),
        text=(
            f"You have been invited to PlacementOS as {role_label}.\n"
            f"Create your password: {link}\n"
            "This link expires in 72 hours.\n"
        ),
    )


def _send(*, to: str, subject: str, html: str, text: str) -> None:
    try:
        result = EmailService().send(to=to, subject=subject, html=html, text=text)
        if not result.success:
            logger.warning("Auth email not sent to %s: %s", to, result.error)
    except Exception:  # noqa: BLE001
        logger.exception("Auth email failed for %s", to)
