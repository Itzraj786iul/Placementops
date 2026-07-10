from __future__ import annotations

from app.core.config import settings
from app.platform.notifications.email_provider import (
    EmailMessage,
    EmailProvider,
    EmailSendResult,
    NullEmailProvider,
)
from app.platform.notifications.providers.resend import ResendEmailProvider


def build_email_provider() -> EmailProvider:
    if settings.email_configured:
        return ResendEmailProvider(
            api_key=settings.RESEND_API_KEY,
            from_email=settings.EMAIL_FROM,
        )
    return NullEmailProvider()


class EmailService:
    """Send email via the configured EmailProvider (Resend by default)."""

    def __init__(self, provider: EmailProvider | None = None) -> None:
        self._provider = provider or build_email_provider()

    @property
    def is_configured(self) -> bool:
        return settings.email_configured

    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        text: str,
    ) -> EmailSendResult:
        if not to.strip():
            return EmailSendResult(success=False, error="Recipient email is empty")
        if not self.is_configured:
            return EmailSendResult(success=False, error="Email provider not configured")
        return self._provider.send(
            EmailMessage(to=to.strip(), subject=subject, html=html, text=text),
        )
