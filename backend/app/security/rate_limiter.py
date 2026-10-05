"""In-memory sliding window rate limiter."""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status

from ..config import settings


class InMemorySlidingWindowRateLimiter:
    def __init__(self):
        # Maps key -> list of float timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        
        # Clean up old timestamps
        timestamps = [t for t in self.requests[key] if t > window_start]
        self.requests[key] = timestamps
        
        if len(timestamps) >= max_requests:
            return True
            
        self.requests[key].append(now)
        return False


limiter = InMemorySlidingWindowRateLimiter()


def rate_limit_auth(request: Request) -> None:
    """Rate limiter dependency for authentication endpoints."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"auth:{client_ip}"
    if limiter.is_rate_limited(key, max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please wait a minute before trying again.",
            headers={"Retry-After": "60"},
        )


def rate_limit_analyses(request: Request) -> None:
    """Rate limiter dependency for code analysis endpoints."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"analysis:{client_ip}"
    if limiter.is_rate_limited(key, max_requests=settings.RATE_LIMIT_ANALYSES_PER_MINUTE, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for code analyses. Please slow down.",
            headers={"Retry-After": "60"},
        )
