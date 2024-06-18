import time
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request

def rate_limit(limit: int, window_seconds: int):
    def rate_limit_decorator(func: Callable):
        request_history = {}

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host

            if client_ip not in request_history:
                request_history[client_ip] = []

            now = time.time()

            # Remove timestamps older than the window
            request_history[client_ip] = [timestamp for timestamp in request_history[client_ip] if now - timestamp < window_seconds]

            if len(request_history[client_ip]) >= limit:
                raise HTTPException(429, "Too Many Requests")

            request_history[client_ip].append(now)

            # Call the original function with arguments
            return await func(request, *args, **kwargs)

        return wrapper

    return rate_limit_decorator
