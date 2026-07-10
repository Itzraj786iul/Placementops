"""Email provider abstraction — swap Resend for another vendor without changing callers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str


@dataclass(frozen=True)
class EmailSendResult:
    success: bool
    provider_id: str | None = None
    error: str | None = None


class EmailProvider(ABC):
    @abstractmethod
    def send(self, message: EmailMessage) -> EmailSendResult:
        raise NotImplementedError


class NullEmailProvider(EmailProvider):
    """Used when email is not configured — deliveries are skipped."""

    def send(self, message: EmailMessage) -> EmailSendResult:
        return EmailSendResult(success=False, error="Email provider not configured")
