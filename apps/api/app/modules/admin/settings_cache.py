"""In-process cache for system settings. Invalidate after every write."""

from __future__ import annotations

import threading
from typing import Any

_lock = threading.Lock()
_cache: dict[str, Any] | None = None


def get_cached_settings() -> dict[str, Any] | None:
    with _lock:
        if _cache is None:
            return None
        return dict(_cache)


def set_cached_settings(values: dict[str, Any]) -> None:
    global _cache
    with _lock:
        _cache = dict(values)


def invalidate_settings_cache() -> None:
    global _cache
    with _lock:
        _cache = None
