from http import HTTPStatus

from fastapi import HTTPException
from redis.exceptions import ResponseError


class AccessCheckCommon:
    _authorize = None
    _redis_token = None

    async def check_access(self):
        await self._authorize.jwt_required()
        raw_token = await self._authorize.get_raw_jwt()
        access_jti = (raw_token)["jti"]
        try:
            if await self._redis_token.exists(access_jti):
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Access token is invalid or expired")
        except ResponseError:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error connecting to Redis")
