from datetime import datetime

from pydantic import BaseModel


class AccessTokenCreate(BaseModel):
    access_token: str


class AccessTokenInDB(BaseModel):
    id: int
    access_token: str
    user_agent: str
    created_at: datetime
    modified_at: datetime
