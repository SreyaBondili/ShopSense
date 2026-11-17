"""
Lightweight thread-safe in-memory TTL cache with stampede protection for analytical endpoints.
Optimizes response times under heavy simulated marketplace load (Locust)
while preserving real database query execution and data freshness.
"""
import time
from typing import Any, Callable, Dict, Tuple
from functools import wraps
import threading

class InMemoryTTLCache:
    def __init__(self, default_ttl_seconds: int = 60):
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any:
        now = time.time()
        with self._lock:
            if key in self._cache:
                expires_at, value = self._cache[key]
                if now < expires_at:
                    return value
                else:
                    del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = None):
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl
        with self._lock:
            self._cache[key] = (expires_at, value)

    def clear(self):
        with self._lock:
            self._cache.clear()

analytics_cache = InMemoryTTLCache(default_ttl_seconds=60)
_stampede_locks: Dict[str, threading.Lock] = {}
_meta_lock = threading.Lock()

def _get_key_lock(key: str) -> threading.Lock:
    with _meta_lock:
        if key not in _stampede_locks:
            _stampede_locks[key] = threading.Lock()
        return _stampede_locks[key]

def cached_endpoint(cache_key_prefix: str, ttl_seconds: int = 60):
    """Decorator to cache results of read-only analytic computations with stampede protection."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key_parts = [cache_key_prefix]
            for a in args:
                # Include primitive identifiers, skip sessions/connections
                if isinstance(a, (int, str, float, bool)):
                    key_parts.append(str(a))
                elif hasattr(a, "role"):
                    u_role = getattr(a.role, "value", str(a.role))
                    u_id = getattr(a, "user_id", getattr(a, "id", "anon"))
                    v_id = getattr(getattr(a, "vendor", None), "vendor_id", "none")
                    key_parts.append(f"user={u_id}:role={u_role}:vendor={v_id}")
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (int, str, float, bool)):
                    key_parts.append(f"{k}={v}")
                elif hasattr(v, "role"):
                    u_role = getattr(v.role, "value", str(v.role))
                    u_id = getattr(v, "user_id", getattr(v, "id", "anon"))
                    v_id = getattr(getattr(v, "vendor", None), "vendor_id", "none")
                    key_parts.append(f"{k}_user={u_id}:role={u_role}:vendor={v_id}")
            cache_key = ":".join(key_parts)

            # Fast path: cache hit
            cached_val = analytics_cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            # Slow path: stampede-protected execution
            key_lock = _get_key_lock(cache_key)
            with key_lock:
                # Double-check inside lock
                cached_val = analytics_cache.get(cache_key)
                if cached_val is not None:
                    return cached_val

                result = func(*args, **kwargs)
                analytics_cache.set(cache_key, result, ttl_seconds)
                return result
        return wrapper
    return decorator
