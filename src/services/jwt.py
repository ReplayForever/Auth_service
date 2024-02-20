from async_fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import UserInDB
from models.tokens import AccessTokenCreate, AccessTokenInDB
from models.schemas import Token, User


class JWTService:
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.authorize = authorize
        self.redis = redis

    async def create_access_token(self, user: UserInDB) -> str:
        access_token = await self.authorize.create_access_token(subject=user.id)
        return access_token

    async def create_refresh_token(self, user: UserInDB) -> str:
        refresh_token = await self.authorize.create_refresh_token(subject=user.id)
        return refresh_token

    async def set_access_token(self, token: str, user_id: str):
        await self.redis.set(name=user_id, value=token)

    async def set_refresh_token(self, token_create: AccessTokenCreate):
        token_dto = jsonable_encoder(token_create)
        token = Token(**token_dto)
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)

    async def get_access_token(self, user_id: str):
        await self.redis.get(name=user_id)

    async def get_refresh_token(self, user_id: str) -> AccessTokenInDB:
        stmt = select(Token).join(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        token = result.scalars().first()
        return token


