"""In-memory failed-login rate limiter (T4.6)."""
from __future__ import annotations

import time
from collections import defaultdict

WINDOW_SECONDS = 15 * 60
MAX_FAILURES = 10


class LoginRateLimiter:
    def __init__(self, max_failures: int = MAX_FAILURES, window: int = WINDOW_SECONDS):
        self.max_failures = max_failures
        self.window = window
        self._failures: dict[tuple[str, str], list[float]] = defaultdict(list)

    def _key(self, ip: str, username: str) -> tuple[str, str]:
        return (ip, username.strip().lower())

    def _prune(self, key: tuple[str, str], now: float) -> list[float]:
        kept = [t for t in self._failures[key] if now - t < self.window]
        if kept:
            self._failures[key] = kept
        else:
            self._failures.pop(key, None)
        return kept

    def is_blocked(self, ip: str, username: str) -> bool:
        key = self._key(ip, username)
        return len(self._prune(key, time.time())) >= self.max_failures

    def record_failure(self, ip: str, username: str) -> None:
        key = self._key(ip, username)
        now = time.time()
        self._prune(key, now)
        self._failures[key].append(now)

    def clear(self, ip: str, username: str) -> None:
        self._failures.pop(self._key(ip, username), None)

    def reset(self) -> None:
        self._failures.clear()


login_limiter = LoginRateLimiter()
