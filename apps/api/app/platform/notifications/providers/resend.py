from __future__ import annotations

import httpx

from app.platform.notifications.email_provider import (
    EmailMessage,
    EmailProvider,
    EmailSendResult,
)


class ResendEmailProvider(EmailProvider):
    """Resend HTTP API implementation of EmailProvider."""

    def __init__(self, *, api_key: str, from_email: str) -> None:
        self._api_key = api_key
        self._from_email = from_email

    def send(self, message: EmailMessage) -> EmailSendResult:
        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": self._from_email,
                    "to": [message.to],
                    "subject": message.subject,
                    "html": message.html,
                    "text": message.text,
                },
                timeout=20.0,
            )
        except httpx.HTTPError as exc:
            return EmailSendResult(success=False, error=str(exc))

        if response.status_code >= 400:
            detail = response.text[:500]
            return EmailSendResult(success=False, error=detail)

        data = response.json() if response.content else {}
        return EmailSendResult(
            success=True,
            provider_id=str(data.get("id")) if isinstance(data, dict) else None,
        )
