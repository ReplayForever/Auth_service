from functools import lru_cache

from fastapi import Depends

from services.abstract import DeleteAbstractService
from services.jwt import JWT, get_jwt


class LogoutService(DeleteAbstractService):
    def __init__(self, jwt: JWT):
        self._jwt = jwt

    async def delete(self):
        await self._jwt.authorize.jwt_required()

        await self._jwt.authorize.unset_jwt_cookies()


@lru_cache()
def get_logout_service(
        jwt: JWT = Depends(get_jwt),
) -> LogoutService:
    return LogoutService(jwt)
