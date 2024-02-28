from sqlalchemy.ext.asyncio import AsyncSession

from models.schemas import Token
from services.abstract import AbstractStorage


class PostgresToken(AbstractStorage):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def set_data(self, token: str, user_id: str, user_agent: str):
        refresh_token = Token(refresh_token=token, user_id=user_id, user_agent=user_agent)
        self._db.add(refresh_token)
        await self._db.commit()
