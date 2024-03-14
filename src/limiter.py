from http import HTTPStatus

from fastapi import Request, HTTPException
from redis import Redis
from functools import wraps
from core.config import settings


redis = Redis(host=settings.redis.host, port=settings.redis.port)


def rate_limit(limit=settings.rate_limit.limit, interval=settings.rate_limit.interval):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            ip_address = request.client.host
            key = f"rate_limit:{ip_address}"

            current_count = redis.get(key)
            if current_count is None:
                redis.setex(key, interval, 1)
            else:
                current_count = int(current_count) + 1
                redis.setex(key, interval, current_count)

                if current_count > limit:
                    raise HTTPException(status_code=HTTPStatus.TOO_MANY_REQUESTS, detail="Too many requests")

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
