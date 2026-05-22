import time
import threading
from typing import Dict, Optional, Tuple
from src.core.contracts.auth.request.cache_request import CacheRequest
from src.core.contracts.auth.response.cache_response import CacheResponse


class InMemoryCache(CacheRequest, CacheResponse):
    def __init__(self):
        self._lock = threading.Lock()

        self._cache: Dict[int, Tuple[str, float]] = {}

    def save_session(self, user_id: int, token: str, ttl_seconds: int) -> None:
        with self._lock:
            expiration_timestamp = time.time() + ttl_seconds
            self._cache[user_id] = (token, expiration_timestamp)

    def get_session(self, user_id: int) -> Optional[str]:
        with self._lock:
            if user_id not in self._cache:
                return None
            token, expiration_timestamp = self._cache[user_id]
            if time.time() > expiration_timestamp:
                del self._cache[user_id]
                return None
            return token

    def delete_session(self, user_id: int) -> None:
        with self._lock:
            if user_id in self._cache:
                del self._cache[user_id]
