from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.schemas import User
from models.users import UserCreate
from services.abstract import AbstractService


class SignUpService(AbstractService):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_data(self, user_create: UserCreate):
        user = User(**user_create.dict())
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user


@lru_cache()
def get_sign_up_service(
        db: AsyncSession = Depends(get_session),
) -> SignUpService:
    return SignUpService(db)
