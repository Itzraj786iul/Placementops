"""In-process TTL cache for feature flag enabled map (30s)."""

from __future__ import annotations

import threading
import time

CACHE_TTL_SECONDS = 30.0

_lock = threading.Lock()
_enabled_map: dict[str, bool] | None = None
_cached_at: float = 0.0


def get_cached_flag_map() -> dict[str, bool] | None:
    with _lock:
        if _enabled_map is None:
            return None
        if time.monotonic() - _cached_at > CACHE_TTL_SECONDS:
            return None
        return dict(_enabled_map)


def set_cached_flag_map(values: dict[str, bool]) -> None:
    global _enabled_map, _cached_at
    with _lock:
        _enabled_map = dict(values)
        _cached_at = time.monotonic()


def invalidate_feature_flag_cache() -> None:
    global _enabled_map, _cached_at
    with _lock:
        _enabled_map = None
        _cached_at = 0.0
