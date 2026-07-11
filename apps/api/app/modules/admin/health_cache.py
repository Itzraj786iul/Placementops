"""In-process TTL cache for system health (30s)."""

from __future__ import annotations

import threading
import time
from typing import Any

CACHE_TTL_SECONDS = 30.0

_lock = threading.Lock()
_cached: dict[str, Any] | None = None
_cached_at: float = 0.0


def get_cached_health() -> dict[str, Any] | None:
    with _lock:
        if _cached is None:
            return None
        if time.monotonic() - _cached_at > CACHE_TTL_SECONDS:
            return None
        return dict(_cached)


def set_cached_health(payload: dict[str, Any]) -> None:
    global _cached, _cached_at
    with _lock:
        _cached = dict(payload)
        _cached_at = time.monotonic()


def invalidate_health_cache() -> None:
    global _cached, _cached_at
    with _lock:
        _cached = None
        _cached_at = 0.0
