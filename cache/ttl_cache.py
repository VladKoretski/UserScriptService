import time
import threading
import logging

logger = logging.getLogger(__name__)

class TTLCache:
    def __init__(self, ttl: int = 600):
        self._cache: dict[str, tuple[str, float]] = {}
        self._ttl = ttl
        self._lock = threading.Lock()

    def _make_key(self, query: str, model: str, temp: float, sys_prompt: str) -> str:
        return f"{model}|{temp}|{sys_prompt}|{query}"

    def get(self, query: str, model: str, temp: float, sys_prompt: str) -> str | None:
        key = self._make_key(query, model, temp, sys_prompt)
        with self._lock:
            if key in self._cache:
                val, exp = self._cache[key]
                if time.time() < exp:
                    logger.info(f"CACHE_HIT: key={key[:40]}...")
                    return val
                else:
                    del self._cache[key]
        logger.info(f"CACHE_MISS: key={key[:40]}...")
        return None

    def set(self, query: str, model: str, temp: float, sys_prompt: str, value: str):
        key = self._make_key(query, model, temp, sys_prompt)
        with self._lock:
            self._cache[key] = (value, time.time() + self._ttl)