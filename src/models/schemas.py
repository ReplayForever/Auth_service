import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    birth_day = Column(Date)
    picture = Column(String(255))
    is_verified_email = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='user')
    token_id = Column(Integer, ForeignKey('tokens.id'))
    token = relationship('Token', back_populates='user')
    login_history = relationship('LoginHistory', back_populates='user')
    is_active = Column(Boolean, default=False)

    def __init__(self, username: str, login: str, password: str, email: str, *args, **kwargs):
        if not validate_login(login=self.login):
            raise ValueError('Invalid login')

        if not validate_email(self.email):
            raise ValueError('Invalid email address')

        if not validate_password(self.password):
            raise ValueError('Password too simple')

        self.username = self.username = is_safe_username(username)
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.email = email

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
    modified_at = Column(DateTime)
    user = relationship('User', back_populates='role')


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    refresh_token = Column(String(255), unique=True)
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime)
    user = relationship('User', back_populates='token')


class LoginHistory(Base):
    __tablename__ = 'login_histories'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    user_agent = Column(String(255))
    auth_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime)
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', back_populates='login_history')
