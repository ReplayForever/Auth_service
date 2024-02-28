# from functools import lru_cache
#
# from fastapi import Depends
#
# from services.abstract import PostAbstractService
# from services.jwt import JWT, get_jwt
#
#
# class RefreshService(PostAbstractService):
#     def __init__(self, jwt: JWT):
#         self._jwt = jwt
#
#     async def post(self):
#         await self._jwt.authorize.jwt_refresh_token_required()
#
#         user = await self._jwt.authorize.get_jwt_subject()
#         new_access_token = await self._jwt.authorize.create_access_token(subject=user)
#
#         await self._jwt.authorize.set_access_cookies(new_access_token)
#
#
# @lru_cache()
# def get_refresh_service(
#         jwt: JWT = Depends(get_jwt),
# ) -> RefreshService:
#     return RefreshService(jwt)
