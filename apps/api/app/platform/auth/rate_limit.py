"""Simple in-process rate limiter for auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from app.platform.auth.exceptions import AuthError

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(
    key: str,
    *,
    limit: int = 10,
    window_seconds: int = 60,
) -> None:
    """Raise 429 when `key` exceeds `limit` events within `window_seconds`."""
    now = time.monotonic()
    with _lock:
        stamps = [t for t in _buckets[key] if now - t < window_seconds]
        if len(stamps) >= limit:
            _buckets[key] = stamps
            raise AuthError(
                "Too many attempts. Please wait a minute and try again.",
                status_code=429,
            )
        stamps.append(now)
        _buckets[key] = stamps
