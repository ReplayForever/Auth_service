from functools import lru_cache
import uuid

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from db.postgres import get_session
from models.schemas import User, Role
from models.users import UserCreate
from services.abstract import AbstractService


class SignUpService(AbstractService):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_data(self, user_create: UserCreate):
        user = User(**jsonable_encoder(user_create))

        try:
            result = await self._db.execute(select(Role).where(
                Role.is_admin == False,
                Role.is_subscriber == False,
                Role.is_superuser == False,
                Role.is_manager == False
            ))
            role = result.fetchone()
            if role is None:
                raise NoResultFound('')
        except NoResultFound:
            unique_name = str(uuid.uuid4())
            role = Role(name = unique_name, 
                        description = "Base user role", 
                        is_admin=False, 
                        is_superuser = False, 
                        is_subscriber = False,
                        is_manager = False)
            self._db.add(role)
            await self._db.commit()
            await self._db.refresh(role)
        
        user.role_id = role[0].id 
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        
        return user


@lru_cache()
def get_sign_up_service(
        db: AsyncSession = Depends(get_session),
) -> SignUpService:
    return SignUpService(db)
