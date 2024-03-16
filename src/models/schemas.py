import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from starlette import status
from werkzeug.security import check_password_hash, generate_password_hash

from python_usernames import is_safe_username

from db.postgres import Base
from utils.validators import validate_login, validate_email, validate_password


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                unique=True,
                nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    social_network_login = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    birth_day = Column(Date, nullable=True)
    picture = Column(String(255), nullable=True)
    is_verified_email = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='user')
    token = relationship('Token', back_populates='user')
    login_history = relationship('LoginHistory',
                                 back_populates='user',
                                 cascade='all, delete',
                                 passive_deletes=True)
    is_active = Column(Boolean, default=False)
    social_network = relationship('SocialNetwork', back_populates='user')

    def __init__(self, username: str, login: str, password: str, birth_day: str | None, email: str, *args, **kwargs):
        if not validate_password(password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid password')

        if not validate_login(login):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid login')

        if not validate_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email address')

        if not is_safe_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid username')

        self.username = username
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.email = email
        if birth_day is not None:
            self.birth_day = datetime.fromisoformat(birth_day)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(100), nullable=False)
    is_subscriber = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='role')


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    refresh_token = Column(String(500), unique=True)
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', back_populates='token')


def get_device_type(user_agent):
    if 'Mobile' in user_agent or 'Android' in user_agent:
        return 'mobile'
    elif any(os in user_agent for os in ['Windows', 'Macintosh', 'Ubuntu']) and 'Xbox' not in user_agent:
        return 'desktop'
    else:
        return 'smart_tv'


class LoginHistory(Base):
    __tablename__ = 'login_histories'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)'
        }
    )

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    user_agent = Column(String(255))
    auth_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    user_device_type = Column(String(255), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='login_history')

    def __init__(self, user_agent: str, user_id: int, *args, **kwargs):
        self.user_agent = user_agent
        self.user_device_type = get_device_type(user_agent)
        self.user_id = user_id
        for key, value in kwargs.items():
            setattr(self, key, value)


class SocialNetwork(Base):
    __tablename__ = 'social_network'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', back_populates='social_network')