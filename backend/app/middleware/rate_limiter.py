"""
Rate limiting middleware for preventing DoS attacks.
"""
import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter using sliding window algorithm."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if request from client IP is allowed.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests outside the window
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """
        Get remaining requests for client IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))


# Global rate limiter instances - more permissive to avoid timeouts
general_rate_limiter = RateLimiter(max_requests=200, window_seconds=60)  # 200 req/min
chat_rate_limiter = RateLimiter(max_requests=50, window_seconds=60)      # 50 req/min for chat
auth_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)      # 30 req/min for auth


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Choose appropriate rate limiter based on endpoint
    if request.url.path.startswith("/chat/"):
        limiter = chat_rate_limiter
    elif request.url.path.startswith("/auth/"):
        limiter = auth_rate_limiter
    else:
        limiter = general_rate_limiter
    
    # Check rate limit
    if not limiter.is_allowed(client_ip):
        remaining = limiter.get_remaining_requests(client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again later.",
                "retry_after": 60,
                "remaining_requests": remaining
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = limiter.get_remaining_requests(client_ip)
    
    response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response
